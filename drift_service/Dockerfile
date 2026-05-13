# ── Stage: runtime ────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Metadata
LABEL maintainer="NetSentinel" \
      description="Drift Detection Service – FastAPI microservice (port 8001)"

# Prevents Python from writing .pyc files and enables unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Working directory inside the container.
# The service references ../data_storage and ../ml_pipeline so we mirror
# the repository layout: /app/drift_service  (service code)
#                        /app/data_storage   (mounted at runtime)
#                        /app/ml_pipeline    (mounted at runtime)
WORKDIR /app

# Install dependencies first (layer cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pymongo

# Copy service source files
COPY app.py detector.py ./

# Expose the port the service listens on
EXPOSE 8001

# Run the FastAPI app via uvicorn
CMD ["python", "app.py"]
