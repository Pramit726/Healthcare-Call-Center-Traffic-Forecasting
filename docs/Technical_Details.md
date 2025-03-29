# Technical Documentation: 

## 1. Requirements Gathering

### A. Scope Clarification

1. **What is the system supposed to do?**
   - Predict call volumes for the healthcare domain in a call center on a monthly basis.

2. **Who are the primary users?**
   - Healthcare call center managers and operation heads responsible for resource planning and workforce management.

3. **What are the boundaries of the system?**
   - The system focuses only on forecasting healthcare call volumes, not handling actual call operations or customer interactions.
   - It relies on historical call data.

4. **What problem are we solving for the stakeholders?**
   - Helping call center managers optimize staffing and resources based on forecasted call volume.
   - Reducing operational inefficiencies by providing accurate demand predictions.
   - Preventing service delays and ensuring customer satisfaction by anticipating high-traffic periods.

### B. Functional Requirements

1. **Prediction Functionality:**
   - Forecast the number of calls received in the healthcare domain for future months using a time series model.

2. **Data Handling:**
   - Ingest and preprocess monthly healthcare call data.
   - Handle missing values, normalize numerical features, and encode categorical ones.

3. **Model Evaluation:**
   - Evaluate forecast accuracy using metrics like Mean Absolute Error (MAE) and Mean Absolute Percentage Error (MAPE).
  
4. **Web Application Integration:**
   - Develop an interactive dashboard where stakeholders can:
     - View historical call trends.



### C. Non-functional Requirements

1. **Performance:**
   - Forecasts should be generated in under 2 seconds for seamless interaction within the web application.

2. **Reliability:**
   - The system should produce consistent forecasts across multiple runs with minimal variance.

3. **Maintainability:**
   - Use modular and well-documented code to enable easy updates and debugging.

4. **Usability:**
   - Provide an intuitive and visually engaging interface that simplifies forecasting for call center managers.






