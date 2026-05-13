FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies
# Build context is now assumed to be the ml_pipeline directory
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pymongo

# Copy the ML pipeline code
COPY . .

# By default, run the main training script
CMD ["python", "main.py"]
