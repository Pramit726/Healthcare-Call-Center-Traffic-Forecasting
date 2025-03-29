from typing import List

from pydantic import BaseModel


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
