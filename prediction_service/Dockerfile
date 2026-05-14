FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY prediction_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pymongo

COPY prediction_service/app.py \
    prediction_service/model_loader.py \
    prediction_service/model_class.py \
    prediction_service/preprocess.py \
    prediction_service/feature_engineering.py \
    prediction_service/utils.py ./

COPY models/ ./models/

EXPOSE 8000

CMD ["python", "app.py"]
