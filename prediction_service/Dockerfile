FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Build context is the project root (set in docker-compose.yml)
# Install dependencies
COPY prediction_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pymongo

# Copy service source files
COPY prediction_service/app.py \
    prediction_service/model_loader.py \
    prediction_service/model_class.py \
    prediction_service/preprocess.py \
    prediction_service/feature_engineering.py \
    prediction_service/utils.py ./

# Copy pre-trained model artifacts from project root
COPY models/ ./models/

EXPOSE 8000

CMD ["python", "app.py"]
