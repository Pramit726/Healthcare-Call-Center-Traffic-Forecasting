from fastapi import APIRouter, status

from .. import schemas
from ..repository import forecast

router = APIRouter(prefix="/forecast", tags=["Forecast"])


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
