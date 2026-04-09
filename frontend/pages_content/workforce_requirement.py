import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from config import API_BASE_URL

WORKFORCE_URL = f"{API_BASE_URL}/forecast/workforce-requirement"


def workforce_estimation():
    st.subheader("Workforce Requirement Estimation")

    # Inputs for workforce estimation
    avg_call_time = st.number_input(
        "Enter average call time (minutes)", min_value=1, max_value=60, value=5
    )
    work_hours_per_agent = st.number_input(
        "Enter work hours per agent (hours)", min_value=1, max_value=12, value=8
    )

    # Initialize session state for workforce data if not exists
    if "workforce_data" not in st.session_state:
        st.session_state.workforce_data = None

    if st.button("Estimate Workforce"):
        try:
            response = requests.post(
                WORKFORCE_URL,
                json={
                    "avg_call_time": avg_call_time,
                    "work_hours_per_agent": work_hours_per_agent,
                },
            )
            if response.status_code == 400:
                st.error(
                    "⚠️ Please generate a forecast first before estimating workforce."
                )
                return

            response.raise_for_status()  # Raises an error for 4xx/5xx errors

            # Store data in session state
            st.session_state.workforce_data = response.json()["workforce"]

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error during workforce estimation: {e}")

    # Display stored workforce data if available
    if st.session_state.workforce_data:
        df_workforce = pd.DataFrame(st.session_state.workforce_data)

        st.subheader("Estimated Workforce Requirements")
        st.dataframe(df_workforce)

        # Bar Chart → Required Staffing Levels per Month
        fig = px.bar(
            df_workforce,
            x="month",
            y="agents_needed",
            title="Required Staffing Levels per Month",
            labels={"month": "Month", "agents_needed": "Number of Agents"},
            text_auto=True,
            color="month",  # Assigns different colors per month
            color_discrete_sequence=px.colors.qualitative.Set1,  # Categorical colors instead of gradient
        )

        st.plotly_chart(fig)


import base64

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from config import API_BASE_URL

WORKFORCE_URL = f"{API_BASE_URL}/forecast/workforce-requirement"


def workforce_estimation():
    st.subheader("Workforce Requirement Estimation")

    # Inputs for workforce estimation
    avg_call_time = st.number_input(
        "Enter average call time (minutes)", min_value=1, max_value=60, value=5
    )
    work_hours_per_agent = st.number_input(
        "Enter work hours per agent (hours)", min_value=1, max_value=12, value=8
    )

    # Initialize session state for workforce data if not exists
    if "workforce_data" not in st.session_state:
        st.session_state.workforce_data = None

    if st.button("Estimate Workforce"):
        try:
            response = requests.post(
                WORKFORCE_URL,
                json={
                    "avg_call_time": avg_call_time,
                    "work_hours_per_agent": work_hours_per_agent,
                },
            )
            if response.status_code == 400:
                st.error(
                    "⚠️ Please generate a forecast first before estimating workforce."
                )

            response.raise_for_status()  # Raises an error for 4xx/5xx errors

            # Store data in session state
            st.session_state.workforce_data = response.json()["workforce"]

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error during workforce estimation: {e}")

    # Display stored workforce data if available
    if st.session_state.workforce_data:
        df_workforce = pd.DataFrame(st.session_state.workforce_data)

        st.subheader("Estimated Workforce Requirements")
        st.dataframe(df_workforce)

        # Bar Chart → Required Staffing Levels per Month
        fig = px.bar(
            df_workforce,
            x="month",
            y="agents_needed",
            title="Required Staffing Levels per Month",
            labels={"month": "Month", "agents_needed": "Number of Agents"},
            text_auto=True,
            color="month",  # Assigns different colors per month
            color_discrete_sequence=px.colors.qualitative.Set1,  # Categorical colors instead of gradient
        )

        st.plotly_chart(fig)
