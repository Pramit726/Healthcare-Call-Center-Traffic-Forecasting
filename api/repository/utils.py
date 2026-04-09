import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import dagshub
import matplotlib.pyplot as plt
import mlflow
import numpy as np
import optuna
import pandas as pd
from mlflow.models.signature import infer_signature
from pymongo import MongoClient
from sktime.forecasting.arima import ARIMA
from sktime.forecasting.compose import TransformedTargetForecaster
from sktime.performance_metrics.forecasting import mean_absolute_error
from sktime.transformations.series.difference import Differencer
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from ml.exception.exception import CallForecastException


def load_json_data(filename: str) -> dict:
    """Loads JSON data from the specified file.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        dict: A dictionary containing the JSON data, or an empty dictionary if an error occurs.
    """
    try:
        file_path = Path(__file__).parent / filename
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        raise CallForecastException(e, sys)


def load_latest_dataset(base_df):
    """
    Combines historical CSV data with the latest ground truth from MongoDB.
    """
    # 1. Ensure 'Date' is a column, not an index
    if "Date" not in base_df.columns:
        # If 'Date' is the index name, move it to columns
        if base_df.index.name == "Date" or base_df.index.name is None:
            base_df = base_df.reset_index()
            # If resetting index created a column named 'index', rename it
            if "index" in base_df.columns:
                base_df = base_df.rename(columns={"index": "Date"})

    # 2. Standardize column names
    # Rename 'Healthcare' if it exists, otherwise assume 'Calls' is already there
    if "Healthcare" in base_df.columns:
        base_df = base_df.rename(columns={"Healthcare": "Calls"})

    # Select only the columns we need
    base_df = base_df[["Date", "Calls"]].copy()

    # 3. Fetch New Ground Truth from MongoDB
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME", "staffing_forecast_db")]
    collection = db["forecast_logs"]

    cursor = collection.find({"actual_calls": {"$ne": None}})

    new_data = []
    for doc in cursor:
        new_data.append({"Date": doc["timestamp"], "Calls": doc["actual_calls"]})

    # 4. Merge and Clean
    if new_data:
        prod_df = pd.DataFrame(new_data)
        prod_df["Date"] = pd.to_datetime(prod_df["Date"])
        combined_df = pd.concat([base_df, prod_df], ignore_index=True)
    else:
        combined_df = base_df

    # 5. Final Preparation
    combined_df["Date"] = pd.to_datetime(combined_df["Date"])
    combined_df = combined_df.drop_duplicates(subset=["Date"], keep="last")
    combined_df = combined_df.sort_values("Date")
    combined_df.set_index("Date", inplace=True)

    # Return as a Series for the ARIMA pipeline
    return combined_df["Calls"]


def run_retraining_pipeline(predictor):
    """
    Full automated retraining using sktime, Optuna, and MLflow nested runs.
    """
    dagshub.init(
        repo_owner="pramitde726",
        repo_name="Healthcare-Call-Center-Traffic-Forecasting",
        mlflow=True,
    )

    base_df = predictor.get_train_dataframe()
    print("Base DataFrame head:", base_df.head())
    y = load_latest_dataset(base_df)
    print("Combined DataFrame head:", y.head())

    # Split for validation (80/20)
    train_size = int(len(y) * 0.8)
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

    # Define Forecast Horizon for optimization
    fh_opt = np.arange(1, len(y_test) + 1)

    # 1. Optuna Objective Function
    def objective(trial):
        p = trial.suggest_int("p", 0, 5)
        q = trial.suggest_int("q", 0, 5)
        d = 1  # Fixed differencing as per your requirement

        try:
            # Nested run for each trial in MLflow
            with mlflow.start_run(nested=True):
                model = TransformedTargetForecaster(
                    [
                        ("differencer", Differencer(lags=d)),
                        ("forecaster", ARIMA(order=(p, 0, q))),
                    ]
                )

                model.fit(y_train)
                y_pred = model.predict(fh=fh_opt)

                # Metric calculation
                mae = mean_absolute_error(y_test, y_pred)

                # Log trial parameters & metrics
                mlflow.log_params({"p": p, "d": d, "q": q})
                mlflow.log_metric("MAE", mae)

                return mae
        except Exception:
            return np.inf

    # 2. Run Optimization
    # We wrap the study in a parent MLflow run
    with mlflow.start_run(run_name="ARIMA_Hyperparameter_Tuning") as parent:
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=20)

        # 3. Best Model Logic
        best_p, best_q = study.best_params["p"], study.best_params["q"]
        mlflow.log_params({"best_p": best_p, "best_q": best_q, "d": 1})

        # Train final model on full training set to validate
        best_model = TransformedTargetForecaster(
            [
                ("differencer", Differencer(lags=1)),
                ("forecaster", ARIMA(order=(best_p, 0, best_q))),
            ]
        )
        best_model.fit(y_train)

        # 4. Generate Production Metrics & Artifacts
        y_pred_final = best_model.predict(fh=fh_opt)
        final_mae = mean_absolute_error(y_test, y_pred_final)
        final_da = calculate_directional_accuracy(y_test.values, y_pred_final.values)

        mlflow.log_metric("final_MAE", final_mae)
        mlflow.log_metric("final_DA", final_da)

        # Residual Plots
        residuals = y_test - y_pred_final
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        plot_acf(residuals.dropna(), lags=min(12, len(residuals) - 1), ax=axes[0])
        plot_pacf(
            residuals.dropna(), lags=min(12, (len(residuals) // 2) - 1), ax=axes[1]
        )
        mlflow.log_figure(fig, "best_model_residuals.png")
        plt.close(fig)

        # 5. Model Registration
        # Infer signature correctly
        signature = infer_signature(y_train.to_frame(), y_pred_final.to_frame())

        mlflow.sklearn.log_model(
            sk_model=best_model, artifact_path="best_model", signature=signature
        )

        # Register the model to DagsHub Model Registry
        model_uri = f"runs:/{parent.info.run_id}/best_model"
        result = mlflow.register_model(model_uri, "healthcare_staffing_production")

        print(f"Retraining complete. Registered Version: {result.version}")

    return {
        "status": "success",
        "version": result.version,
        "da": final_da,
        "best_order": (best_p, 1, best_q),
    }


def calculate_directional_accuracy(y_true, y_pred):
    """
    Calculate Directional Accuracy (DA) between true and predicted values.
    DA is the percentage of times the model correctly predicts the direction of change.
    """
    y_true_diff = np.diff(y_true)
    y_pred_diff = np.diff(y_pred)

    da = np.mean(np.sign(y_true_diff) == np.sign(y_pred_diff))
    return da


def get_recent_logs_from_db(days=180):
    """
    Retrieves records from MongoDB where 'actual_calls' have been populated.
    Returns a DataFrame indexed by Date for Monitoring/Retraining.
    """
    # 1. Connect to MongoDB
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME", "staffing_forecast_db")]
    collection = db["forecast_logs"]

    # 2. Filter: data from the last N days where 'actual' is NOT null
    now_utc = datetime.now(timezone.utc)
    start_date = now_utc - timedelta(days=days)
    query = {
        "timestamp": {"$gte": start_date},
        "actual_calls": {"$ne": None},  # Only pull records where truth is known
    }

    cursor = collection.find(query).sort("timestamp", 1)

    # 3. Convert to List then DataFrame
    data = []
    for doc in cursor:
        data.append(
            {
                "Date": doc["timestamp"],
                "Calls": doc["actual_calls"],  # Ground Truth
                "Predicted_Calls": doc["prediction"],  # What the model originally said
            }
        )

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # 4. Format for Time Series (sktime/ARIMA compatibility)
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    df = df.sort_index()

    return df


def update_actual_calls(date_str: str, actual_count: int):
    """
    Updates an existing forecast record with the actual number of calls.
    Used for calculating Directional Accuracy later.
    """
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["staffing_forecast_db"]

    # Find the record for that specific date and add the actual_calls
    db.forecast_logs.update_one(
        {"date_string": date_str}, {"$set": {"actual_calls": actual_count}}
    )
