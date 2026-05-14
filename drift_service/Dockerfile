FROM python:3.11-slim

LABEL maintainer="NetSentinel" \
    description="Drift Detection Service – FastAPI microservice (port 8001)"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pymongo

COPY app.py detector.py ./

EXPOSE 8001

CMD ["python", "app.py"]
