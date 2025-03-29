# Project Summary Documentation

## Project Goal

The goal of this project is to develop a time-series forecasting model to predict monthly call volumes in the healthcare domain. This will help call center managers optimize staffing, reduce patient wait times, and improve service quality by ensuring adequate phone lines and channels are available.

Higher forecast accuracy enables better resource planning, reducing overstaffing costs and minimizing agent burnout, ultimately improving patient satisfaction.


## Stakeholder

- Michael – Call Center Supervisor: Uses predictions to optimize agent scheduling and reduce burnout.


## Proposed Solution

### Key Features:

1.  **Predict Monthly Call Volume:**
    -   Forecast call traffic to prevent bottlenecks and ensure resource availability.
2.  **Analyze Seasonal Trends:**
    -   Identify peak call periods (e.g., flu season, COVID waves) to prepare in advance.
3.  **Optimize Staffing Levels:**
    -   Reduce agent underutilization and prevent service disruptions by ensuring appropriate staffing.
4.  **Monitor Phone Lines and Channels:**
    -   Ensure adequate phone infrastructure based on predicted call demand.
5.  **Interactive Dashboard for Real-Time Insights:**
    -   Develop a web application where managers can explore past trends and future forecasts.

## Deliverables

-   **Web Application for Interactive Forecasting**
-   **Project Documentation (in markdown format)**

## Key Metrics

### Mean Absolute Error (MAE): "Accurate Staffing = Reduced Wait Times & Burnout"

- Technical Meaning:

Measures the average error between predicted and actual call volumes.

- Why It Matters to Michael:

A low MAE (e.g., within ±10 calls) ensures Michael can trust forecasts for daily staffing decisions.
* Example: "If we predict 1,000 calls next month, the actual volume is typically between 990-1,010."
* Ensures confident decision-making in daily staff scheduling, minimizing both understaffing (leading to long wait times) and overstaffing (leading to agent burnout).

- Business Metric Tied To It:

* **Average Patient Wait Time:** Lower MAE directly translates to more accurate staffing, reducing patient wait times.
* **Agent Burnout Rate:** Accurate staffing prevents overwork, reducing agent burnout.

### Directional Accuracy (DA): "Right Trend = Proactive Scheduling"

- Technical Meaning:

Measures the percentage of times the model correctly predicts the direction of change (increase or decrease) in call volumes.

- Why It Matters to Michael:

Knowing whether call volumes will increase or decrease allows Michael to proactively adjust staffing levels.
* Example: "If the model predicts an increase in calls, we can schedule more agents in advance."
* Enables proactive scheduling adjustments to meet anticipated demand, ensuring smooth operations.

### Business Metric Tied To It:

* **Percentage of Days with Staffing Aligned with Demand Trend:** Higher DA means Michael is more often correctly predicting the direction of change and staffing accordingly.

## Scope and Limitations

### Scope

-   **Focus Areas:**
    -   Forecast **monthly** call volumes for healthcare call centers.
    -   Enable stakeholders to interact with forecasts through a **web application**.

### Limitations

-   **Excluded Factors:**
    -   Does not account for **external disruptions** such as policy changes, healthcare crises, or economic factors.
    -   Forecasting accuracy depends on **historical data quality and external regressor reliability.**
-   **Scalability:**
    -   The web application is currently a **proof-of-concept (PoC)**, hosted on **Render Cloud**, and may require optimization for production-scale deployment.



