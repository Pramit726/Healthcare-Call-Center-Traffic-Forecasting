import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from config import API_BASE_URL
from pages_content import metrics, workforce_requirement

FORECAST_URL = f"{API_BASE_URL}/forecast/forecast"


def forecast():
    st.title("Call Volume Forecast and Workforce Estimation")

    st.subheader("Forecasted Call Volumes")

    # User input for forecast
    n_months = st.number_input(
        "Enter number of months to forecast", min_value=1, max_value=12, value=3
    )

    if "forecast_data" not in st.session_state:
        st.session_state.forecast_data = None  # Initialize if not exists

    if st.button("Get Forecast"):
        try:
            response = requests.post(FORECAST_URL, json={"n_months": n_months})
            response.raise_for_status()  # Raises an error for 4xx/5xx status codes

            forecast_data = response.json()["forecast"]

            # Store forecast in session state
            st.session_state.forecast_data = forecast_data

            # Convert to DataFrame
            df_forecast = pd.DataFrame(forecast_data)
            st.subheader("Forecasted Call Volumes")
            st.dataframe(df_forecast)

            # Line Chart
            fig = px.line(
                df_forecast,
                x="month",
                y="forecasted_calls",
                title="Forecasted Call Volume (Monthly)",
                markers=True,
            )
            st.plotly_chart(fig)

            model_metrics()

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error during forecasting: {e}")
        except KeyError:
            st.error("❌ Error: Call volumes missing from Forecasted result.")

    # Only show workforce estimation if forecast exists
    if st.session_state.forecast_data:
        workforce_requirement.workforce_estimation()


def model_metrics():
    metrics.show_metrics()


import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from config import API_BASE_URL
from pages_content import metrics, workforce_requirement

FORECAST_URL = f"{API_BASE_URL}/forecast/forecast"


def forecast():
    st.title("Call Volume Forecast and Workforce Estimation")

    st.subheader("Forecasted Call Volumes")

    # User input for forecast
    n_months = st.number_input(
        "Enter number of months to forecast", min_value=1, max_value=12, value=3
    )

    if "forecast_data" not in st.session_state:
        st.session_state.forecast_data = None  # Initialize if not exists

    if st.button("Get Forecast"):
        try:
            response = requests.post(FORECAST_URL, json={"n_months": n_months})
            response.raise_for_status()  # Raises an error for 4xx/5xx status codes

            forecast_data = response.json()["forecast"]

            # Store forecast in session state
            st.session_state.forecast_data = forecast_data

            # Convert to DataFrame
            df_forecast = pd.DataFrame(forecast_data)
            st.subheader("Forecasted Call Volumes")
            st.dataframe(df_forecast)

            # Line Chart
            fig = px.line(
                df_forecast,
                x="month",
                y="forecasted_calls",
                title="Forecasted Call Volume (Monthly)",
                markers=True,
            )
            st.plotly_chart(fig)

            model_metrics()

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error during forecasting: {e}")
        except KeyError:
            st.error("❌ Error: Call volumes missing from Forecasted result.")

    # Only show workforce estimation if forecast exists
    if st.session_state.forecast_data:
        workforce_requirement.workforce_estimation()


def model_metrics():
    metrics.show_metrics()
