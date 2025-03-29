import logging
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
logging.info(f"API_BASE_URL: {API_BASE_URL}")
logging.info("Loaded config.py")
