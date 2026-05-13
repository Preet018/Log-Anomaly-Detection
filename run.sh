#!/bin/bash

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting FastAPI Prediction Service (port 8000)..."
cd prediction_service
python app.py &
BACKEND_PID=$!
cd ..

echo "Waiting for prediction service to start..."
sleep 3

echo "Starting Drift Detection Service (port 8001)..."
cd drift_service
python app.py &
DRIFT_PID=$!
cd ..

echo "Starting Streamlit Frontend (port 8501)..."
streamlit run frontend/app.py &
FRONTEND_PID=$!

echo ""
echo "All services are running!"
echo "  Prediction Service : http://localhost:8000  (PID: $BACKEND_PID)"
echo "  Drift Service      : http://localhost:8001  (PID: $DRIFT_PID)"
echo "  Dashboard          : http://localhost:8501  (PID: $FRONTEND_PID)"
echo ""
echo "Press Ctrl+C to stop all services."

# Stop all background services on Ctrl+C
trap "echo 'Stopping services...'; kill $BACKEND_PID $DRIFT_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT

wait
