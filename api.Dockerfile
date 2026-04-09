# Use a minimal base image for Python
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends tini && rm -rf /var/lib/apt/lists/*

# Copy only API-related files
COPY api ./api
COPY ml ./ml
COPY data/raw ./data/raw
COPY artifacts ./artifacts
COPY setup.py pyproject.toml requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Expose API port
EXPOSE 8000

# Set tini as entrypoint
ENTRYPOINT ["/usr/bin/tini", "--"]

# Start FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
