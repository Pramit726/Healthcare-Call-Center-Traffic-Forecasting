import json
import os
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
from evidently.test_suite import TestSuite
from evidently.tests import TestColumnDrift
from fastapi import HTTPException, status
from pymongo import MongoClient, UpdateOne

from ml.pipeline.prediction_pipeline import Predictor

from .. import schemas
from .utils import get_recent_logs_from_db

load_dotenv()  # Load environment variables from .env file
# Initialize predictor
predictor = Predictor()

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client["staffing_forecast_db"]
logs_collection = db["forecast_logs"]
# Cache to store forecast results
forecast_cache = {}


async def predict_calls(request: schemas.ForecastRequest):
    """
    Generates call volume forecasts for the requested number of months.
    Stores the forecasted values in cache for future reference.
    """
    try:
        forecast = predictor.predict(fh=request.n_months)
        last_actual_calls = predictor.get_train_dataframe().iloc[-1]["Healthcare"]
        forecast_dates = [
            predictor.get_train_dataframe().index[-1] + timedelta(days=30 * i)
            for i in range(1, request.n_months + 1)
        ]

        change_percentage = [
            (forecast[i] - (forecast[i - 1] if i > 0 else last_actual_calls))
            / (forecast[i - 1] if i > 0 else last_actual_calls)
            * 100
            for i in range(request.n_months)
        ]

        result = [
            schemas.ForecastResponseItem(
                month=forecast_dates[i].strftime("%b %Y"),
                forecasted_calls=int(forecast[i]),
                change_from_previous_month=round(change_percentage[i], 2),
            )
            for i in range(request.n_months)
        ]

        # SAVE TO MONGODB
        log_entries = []
        for item in result:
            log_entries.append(
                {
                    "timestamp": datetime.utcnow(),  # When the prediction was made
                    "target_month": item.month,  # e.g., "Apr 2026"
                    "prediction": item.forecasted_calls,  # The forecast
                    "actual_calls": None,  # Placeholder! Updated later.
                }
            )

        if log_entries:
            logs_collection.insert_many(log_entries)

        # Store forecast results in cache
        forecast_cache["forecast"] = {
            result[i].month: result[i].forecasted_calls for i in range(request.n_months)
        }
        forecast_cache["n_months"] = request.n_months

        return schemas.ForecastResponse(forecast=result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during forecasting: {e}",
        )


def workforce_requirement(request: schemas.WorkforceRequest):
    """
    Estimates workforce requirements based on cached call volume forecasts.
    Ensures forecast data is available before computation.
    """
    # Check if forecast data is available in cache
    if "forecast" not in forecast_cache:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forecast data not found. Please run the forecast endpoint first.",
        )
    if "n_months" not in forecast_cache:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of months data not found. Please run the forecast endpoint first.",
        )

    try:

        # Retrieve stored forecasted values
        forecasted_values = list(forecast_cache["forecast"].values())
        forecast_dates = list(forecast_cache["forecast"].keys())

        agents_needed = [
            (forecasted_values[i] * request.avg_call_time)
            / (request.work_hours_per_agent * 60)  # Convert hours to minutes
            for i in range(forecast_cache["n_months"])
        ]

        result = [
            schemas.WorkforceResponseItem(
                month=forecast_dates[i],
                forecasted_calls=forecasted_values[i],
                agents_needed=round(agents_needed[i]),
            )
            for i in range(forecast_cache["n_months"])
        ]

        return schemas.WorkforceResponse(workforce=result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while calculating workforce requirements: {e}",
        )


async def get_model_metrics():
    """
    Retrieves model performance metrics including Mean Absolute Error (MAE)
    and Directional Accuracy (DA).
    """
    try:
        mae, da = predictor.model_metrics()
        return schemas.ShowModelMetrics(mae=mae, da=da)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during metrics retrieval: {e}",
        )


def update_actual_calls(request: schemas.UpdateActualCallsRequest):
    """
    Updates an existing forecast record with the actual number of calls.
    """
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["staffing_forecast_db"]

    # We use 'target_month' to match MongoDB document structure
    result = db.forecast_logs.update_one(
        {"target_month": request.target_month},
        {"$set": {"actual_calls": request.actual_count}},
    )

    if result.matched_count == 0:
        return {
            "status": "error",
            "message": f"No forecast found for {request.target_month}",
        }

    return {
        "status": "success",
        "message": f"Updated {request.target_month} with actual count {request.actual_count}",
    }


def batch_update_actual_calls(request: schemas.BatchUpdateActualCallsRequest):
    """
    Updates multiple months of ground truth data in a single MongoDB operation.
    """
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["staffing_forecast_db"]
    collection = db["forecast_logs"]

    # 1. Prepare the bulk operations
    operations = [
        UpdateOne(
            {"target_month": item.target_month},
            {"$set": {"actual_calls": item.actual_count}},
        )
        for item in request.updates
    ]

    if not operations:
        return {"status": "error", "message": "No data provided"}

    # 2. Execute all updates at once
    result = collection.bulk_write(operations)

    return {
        "status": "success",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "message": f"Successfully processed {len(request.updates)} records.",
    }


async def check_for_drift():
    # Load original training data (Reference)
    # Load recent database logs (Current)
    # ref_df = predictor.get_train_dataframe()
    # print("Reference DataFrame head:", ref_df.head())
    # if isinstance(ref_df, pd.Series):
    #     ref_df = ref_df.to_frame(name="Calls")
    # elif "Healthcare" in ref_df.columns:
    #     ref_df = ref_df.rename(columns={"Healthcare": "Calls"})

    curr_df = get_recent_logs_from_db()

    # print("Current DataFrame head:", curr_df.head())
    ref_df = curr_df[
        ["Calls"]
    ].copy()  # Use actual calls as reference for drift detection
    curr_df.drop(columns=["Calls"], inplace=True)
    curr_df.rename(columns={"Predicted_Calls": "Calls"}, inplace=True)
    column_drift_test = TestSuite(tests=[TestColumnDrift(column_name="Calls")])

    # print(curr_df.head())
    # print("==========")
    # print(ref_df.head())
    column_drift_test.run(reference_data=ref_df, current_data=curr_df)
    results_dict = column_drift_test.as_dict()
    # print(results_dict)

    test_info = results_dict["tests"][0]
    params = test_info["parameters"]
    # json_results = json.dumps(test_info, indent=4)
    # print("Evidently Test Results:")

    # Save to file
    # with open("drift_test_results.json", "w") as f:
    #     f.write(json_results)

    # Check if the 'Target Drift' test failed
    drift_score = params["score"]
    # print(f"Drift Score: {drift_score}")
    drift_detected = params["detected"]

    return {
        "drift_detected": drift_detected,
        "score": drift_score,
        "status": test_info["status"],
    }
