import json
import sys
from pathlib import Path

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
