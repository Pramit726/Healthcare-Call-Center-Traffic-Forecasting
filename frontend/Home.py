import requests
import streamlit as st
from config import API_BASE_URL


def main():
    st.set_page_config(page_title="Home", layout="wide")

    # Check API availability
    try:
        response = requests.get(f"{API_BASE_URL}/home")
        response.raise_for_status()
        st.session_state.api_available = True
        data = response.json()
    except requests.exceptions.RequestException as e:
        st.session_state.api_available = False
        st.error(
            "Oops! It seems our app is temporarily unavailable. Please try again later."
        )
        st.warning("Technical details: " + str(e))
        st.stop()
    except Exception as e:
        st.session_state.api_available = False
        st.error("Uh oh! Something unexpected went wrong. We're looking into it!")
        st.warning("Technical details: " + str(e))
        st.stop()

    # Hero Section
    st.title("📞 Call Volume Forecasting & Workforce Planning")
    st.subheader("Optimize workforce allocation with accurate call volume predictions!")

    st.write(
        """
        This platform helps businesses optimize their call center staffing by predicting future call volumes
        and estimating the required workforce. Make data-driven decisions and ensure efficiency while reducing costs.
        """
    )

    # Call-to-Action (CTA) Button
    if st.session_state.api_available:
        if st.button("🚀 Get Started"):
            st.switch_page("pages/Forecast_Workforce.py")

    st.markdown("---")

    # Benefits Section from API
    if st.session_state.api_available:
        st.header("📈 Why Use This Tool?")
        for point in data["points"]:
            st.write(f"✅ **{point}**")

        st.info(f"💡 {data['info_message']}")

    st.markdown("---")

    # Navigation Panel
    st.subheader("📌 Explore the Features")
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.api_available:
            if st.button("📊 View Forecast & Workforce Analysis"):
                st.switch_page("pages/Forecast_Workforce.py")

    with col2:
        st.button("📌 Additional Insights (Coming Soon 🚀)", disabled=True)


if __name__ == "__main__":
    main()
