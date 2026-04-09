# Use a minimal base image for Python
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends tini && rm -rf /var/lib/apt/lists/*

# Copy only frontend-related files
COPY frontend ./frontend

# Set working directory to frontend before installing dependencies
WORKDIR /app/frontend

# Install frontend dependencies
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Set tini as entrypoint
ENTRYPOINT ["/usr/bin/tini", "--"]

# Start Streamlit server
CMD ["streamlit", "run", "Home.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
