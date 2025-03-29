from pathlib import Path

import requests
import streamlit as st
from config import API_BASE_URL

METRICS_URL = f"{API_BASE_URL}/forecast/model_metrics"
DA_IMG_PATH = Path(__file__).parent.parent / "assets" / "da_exp.png"
MAE_IMG_PATH = Path(__file__).parent.parent / "assets" / "mae_exp.png"


def get_metrics():
    try:
        response = requests.get(METRICS_URL)
        response.raise_for_status()
        st.session_state.metrics = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching metrics: {e}")
        st.session_state.metrics = None
    return st.session_state.metrics


def show_metrics():
    try:
        st.title("📈 Model Metrics")

        metrics = get_metrics()
        mae = metrics.get("mae", None)
        da = metrics.get("da", None)

        if mae is not None:
            mae_rounded = round(mae, 2)
            st.metric("Mean Absolute Error", mae_rounded)
            st.image(MAE_IMG_PATH, width=500)

        else:
            st.metric("Mean Absolute Error", "N/A")

        if da is not None:
            da_rounded = round(da, 2) * 100
            st.metric("DA(Directional Accuracy)%", da_rounded)
            st.image(DA_IMG_PATH, width=500)

        else:
            st.metric("DA(Directional Accuracy)%", "N/A")

    except Exception as e:
        st.error(f"An error occurred while displaying metrics: {e}")
        st.warning("Please try again later. If the problem persists, contact support.")
