from typing import List, Optional

from pydantic import BaseModel, Field


class ShowInsights(BaseModel):
    points: List[str]
    info_message: str


class ForecastRequest(BaseModel):
    n_months: int  # Number of months to predict


class ForecastResponseItem(BaseModel):
    month: str
    forecasted_calls: int
    change_from_previous_month: float  # in %


# Full response model for forecast endpoint
class ForecastResponse(BaseModel):
    forecast: List[ForecastResponseItem]


class WorkforceRequest(BaseModel):
    avg_call_time: float  # Avg. handling time (mins)
    work_hours_per_agent: float  # Monthly working hours per agent


# Response model for each workforce calculation
class WorkforceResponseItem(BaseModel):
    month: str
    forecasted_calls: int
    agents_needed: int


# Full response model for workforce requirement endpoint
class WorkforceResponse(BaseModel):
    workforce: List[WorkforceResponseItem]


class ShowModelMetrics(BaseModel):
    mae: float
    da: float


class MonitorResponse(BaseModel):
    drift_detected: bool
    retraining_triggered: bool
    message: str
    drift_score: Optional[float] = None


class UpdateActualCallsRequest(BaseModel):
    target_month: str = Field(
        ..., example="Jan 2024", description="The month to update"
    )
    actual_count: int = Field(
        ..., example=16250, description="The actual number of calls recorded"
    )


class BatchUpdateActualCallsRequest(BaseModel):
    updates: List[UpdateActualCallsRequest]
