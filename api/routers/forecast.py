from fastapi import APIRouter, BackgroundTasks, status

from .. import schemas
from ..repository import forecast
from ..repository.utils import run_retraining_pipeline

router = APIRouter(prefix="/forecast", tags=["Forecast"])

from ml.pipeline.prediction_pipeline import Predictor

predictor = Predictor()


@router.post(
    "/forecast",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ForecastResponse,
    summary="Forecast Call Volume",
    description="Predicts call volume for the next N months based on historical data.",
)
async def forecast_calls(request: schemas.ForecastRequest):
    """
    Forecasts call volume for the next N months.
    """
    return await forecast.predict_calls(request)


@router.post(
    "/workforce-requirement",
    status_code=status.HTTP_200_OK,
    response_model=schemas.WorkforceResponse,
    summary="Forecast Workforce Requirement",
    description="Predicts the number of agents needed based on forecasted call volume, average handling time, and working hours per agent.",
)
def workforce_requirement(request: schemas.WorkforceRequest):
    """
    Forecasts workforce requirements for the next N months.
    """
    return forecast.workforce_requirement(request)


@router.get(
    "/model_metrics",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ShowModelMetrics,
    summary="Get Model Performance Metrics",
    description="Retrieves model performance metrics, including Mean Absolute Error (MAE) and Directional Accuracy(DA).",
)
async def get_model_metrics():
    """
    Retrieves model metrics.
    """
    return await forecast.get_model_metrics()


@router.post(
    "/monitor-and-retrain",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MonitorResponse,
    summary="Monitor Drift and Trigger Retraining",
)
async def monitor_and_retrain(background_tasks: BackgroundTasks):
    """
    Analyzes recent call patterns using Evidently AI.
    If drift is detected, triggers an Optuna-based retraining loop.
    """
    # 1. Run the monitoring check
    drift_status = await forecast.check_for_drift()
    print(f"Drift Status: {drift_status['score']}")

    if drift_status["drift_detected"]:
        # 2. Trigger retraining in the background
        background_tasks.add_task(run_retraining_pipeline(predictor=predictor))
        return {
            "drift_detected": True,
            "retraining_triggered": True,
            "message": "Drift detected. Retraining pipeline started in background.",
            "drift_score": float(drift_status["score"]),
        }

    return {
        "drift_detected": False,
        "retraining_triggered": False,
        "message": "Model performance is stable. No retraining needed.",
        "drift_score": float(drift_status["score"]),
    }


@router.post(
    "/update_ground_truth",
    status_code=status.HTTP_200_OK,
    summary="Update Ground Truth Data",
    description="Updates the actual call counts for a specific date, allowing for accurate performance tracking and retraining.",
)
async def update_actual_calls(request: schemas.UpdateActualCallsRequest):
    """
    Updates the actual call counts for a specific date.
    """
    return forecast.update_actual_calls(request)


@router.post(
    "/batch_update_ground_truth",
    status_code=status.HTTP_200_OK,
    summary="Batch Update Ground Truth",
)
def batch_update_actual_calls(request: schemas.BatchUpdateActualCallsRequest):
    """
    Accepts a list of target months and their actual call counts.
    """
    return forecast.batch_update_actual_calls(request)
