from fastapi import HTTPException, status

from .utils import load_json_data

data = load_json_data("data.json")


async def get_home_info():
    # Check if data is empty or None
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error loading data.json. Check file or format.",
        )
    return data


