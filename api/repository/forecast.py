from datetime import timedelta

from fastapi import HTTPException, status

from ml.pipeline.prediction_pipeline import Predictor

from .. import schemas

# Initialize predictor
predictor = Predictor()


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
