# Running Guide — NetSentinel Hybrid Threat Detection System

Complete step-by-step guide from initial training to drift-triggered retraining.

---

## Prerequisites

```bash
cd "Microservices-Based Drift-Aware MLOps for Cybersecurity Log Anomaly Detection"
source venv/bin/activate
```

---

## Phase 1 — Initial Training (Run Once)

```bash
cd ml_pipeline
python main.py
cd ..
```

**What happens:**
- Downloads `KDDTrain+.txt` from GitHub (NSL-KDD dataset)
- Splits it into:
  - `data_storage/KDDTrain_initial.txt` — 70% (used for initial training)
  - `data_storage/KDDRetrain_reserve.txt` — 30% (held back for drift retraining)
- Trains `HybridAnomalyDetector` (Random Forest + Autoencoder) on 70% data
- Saves `models/model_v1.pkl` and `models/preprocessor.pkl`
- Saves `data_storage/baseline_stats.json` for drift comparison

**Expected output:**
```
Splitting KDDTrain+.txt → KDDTrain_initial.txt (70%) + KDDRetrain_reserve.txt (30%)...
  Initial set : 88,181 rows
  Reserve set : 37,792 rows
Training Random Forest (known attack detector)...
Training Autoencoder on normal traffic only (Zero-Day detector)...
Accuracy: 0.9718
Baseline stats saved to data_storage/baseline_stats.json
ML Pipeline completed successfully.
```

---

## Phase 2 — Start the 3 Services (Each in a Separate Terminal)

### Terminal 1 — Prediction Service (Backend)
```bash
source venv/bin/activate
cd prediction_service
python app.py
# Runs at http://localhost:8000
```

### Terminal 2 — Drift Detection Service
```bash
source venv/bin/activate
cd drift_service
python app.py
# Runs at http://localhost:8001
```

### Terminal 3 — Dashboard (Frontend)
```bash
source venv/bin/activate
streamlit run frontend/app.py
# Runs at http://localhost:8501
```

> **Alternatively**, start all 3 services at once with:
> ```bash
> ./run.sh
> ```

---

## Phase 3 — Make Predictions

Open the dashboard: [http://localhost:8501](http://localhost:8501)

- **Batch Prediction** — upload a `.txt` or `.csv` file with 41 features per row
- **Single Prediction** — enter 41 comma-separated values manually

Every prediction is automatically logged to `data_storage/logs.csv`.

---

## Phase 4 — Check for Drift (Terminal 4)

```bash
# Quick status
curl http://localhost:8001/drift/status

# Full detailed report (KS-test per feature)
curl http://localhost:8001/drift/report | python3 -m json.tool
```

**Possible responses:**

| Status | Meaning |
|---|---|
| `insufficient_data` | Need at least 50 predictions in logs.csv |
| `stable` | Model distribution matches training baseline |
| `drift_detected` | Anomaly rate or feature distributions have shifted |

---

## Phase 5 — Retrain When Drift is Detected

### Option A — Via API (recommended, zero downtime)
```bash
curl -X POST http://localhost:8001/drift/retrain
```

What happens automatically:
1. `ml_pipeline/retrain.py` runs using **initial 70% + reserve 30%** data
2. New `model_v1.pkl` and `preprocessor.pkl` are saved
3. Drift service calls `POST /reload` on the prediction service
4. Prediction service hot-swaps model in memory — no restart needed
5. `baseline_stats.json` is updated with new baseline

### Option B — Manual retraining
```bash
# Stop prediction service (Ctrl+C in Terminal 1)
source venv/bin/activate
cd ml_pipeline
python retrain.py
cd ..

# Restart prediction service
cd prediction_service && python app.py
```

---

## All API Endpoints

### Prediction Service — `http://localhost:8000`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/docs` | Swagger interactive API docs |
| `POST` | `/predict` | Single log prediction |
| `POST` | `/predict_batch` | Batch CSV file prediction |
| `POST` | `/reload` | Hot-swap model without restart |

### Drift Detection Service — `http://localhost:8001`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `GET` | `/drift/status` | Quick drift flag (stable / drift_detected) |
| `GET` | `/drift/report` | Full KS-test report per feature |
| `POST` | `/drift/retrain` | Trigger retraining + auto hot-reload |

---

## Prediction Labels

| Code | Label | Detected By |
|---|---|---|
| `0` | `normal` | Both RF and Autoencoder agree it is safe |
| `1` | `confirmed threat` | Random Forest matched a known attack pattern |
| `2` | `novel threat` | Autoencoder flagged a potential Zero-Day |

---

## Data Files Reference

```
data_storage/
├── KDDTrain+.txt              — raw downloaded dataset (never modified)
├── KDDTrain_initial.txt       — 70% split, used for initial training
├── KDDRetrain_reserve.txt     — 30% split, used for drift retraining
├── baseline_stats.json        — anomaly rate + feature means/stds from training
└── logs.csv                   — every prediction logged here (input to drift check)

models/
├── model_v1.pkl               — trained HybridAnomalyDetector
└── preprocessor.pkl           — sklearn Pipeline (FeatureEngineer + Scaler/OHE)
```

---

## Quick Summary Table

| Step | Command | Where to run |
|---|---|---|
| 1. Initial train | `cd ml_pipeline && python main.py` | Project root |
| 2. Prediction API | `cd prediction_service && python app.py` | Terminal 1 |
| 3. Drift API | `cd drift_service && python app.py` | Terminal 2 |
| 4. Dashboard | `streamlit run frontend/app.py` | Terminal 3 |
| 5. Check drift | `curl localhost:8001/drift/status` | Terminal 4 |
| 6. Retrain | `curl -X POST localhost:8001/drift/retrain` | Terminal 4 |
