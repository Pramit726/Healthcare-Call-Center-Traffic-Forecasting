from fastapi import APIRouter, status

from ..repository import home
from ..schemas import ShowInsights

router = APIRouter(prefix="/home", tags=["Home"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=ShowInsights,
    summary="Get Home Page Insights",
    description="Retrieves insights for the home page.",
)
async def get_home_info():
    """
    Retrieves information for the home page.
    """
    return await home.get_home_info()
