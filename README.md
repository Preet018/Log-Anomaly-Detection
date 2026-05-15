<p align="left">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Build-Docker-blue?style=flat-square&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/CI-Jenkins-orange?style=flat-square&logo=jenkins&logoColor=white" alt="Jenkins">
  <img src="https://img.shields.io/badge/Deployment-Ansible-red?style=flat-square&logo=ansible&logoColor=white" alt="Ansible">
  <img src="https://img.shields.io/badge/Orchestration-Kubernetes-blue?style=flat-square&logo=kubernetes&logoColor=white" alt="Kubernetes">
  <img src="https://img.shields.io/badge/Monitoring-ELK%20Stack-005571?style=flat-square&logo=elastic-stack&logoColor=white" alt="ELK Stack">
</p>

---

# Cyber Security Log Anomaly Detection & MLOps Pipeline

## Project Overview

This project is developed as part of the **SPE Project** and demonstrates a complete, production-grade **MLOps (Machine Learning Operations)** and **DevOps CI/CD pipeline** for a CyberSecurity Log Anomaly Detection system.

The core application is implemented in **Python** using **FastAPI** and **Scikit-Learn**. It detects both known network attacks (using Random Forest) and novel Zero-Day threats (using Autoencoders). The project integrates multiple industry-standard DevOps tools to automate the entire lifecycle—from training and testing to containerization, orchestration, and continuous monitoring.

The main objective of this project is to implement a **Self-Healing MLOps Pipeline** that not only automates deployment but also monitors model performance (Drift Detection) and triggers automated retraining when data patterns change.

---

## DevOps & MLOps Pipeline Overview

The automated pipeline performs the following critical stages:

### 1. Source Code Management & CI
*   **Version Control:** Managed via Git/GitHub with branch protection.
*   **Continuous Integration:** A **Jenkins** pipeline is triggered on every commit to validate code, run linting, and prepare for containerization.

### 2. Automated ML Pipeline
*   **Baseline Generation:** A Kubernetes Job handles the initial data download (NSL-KDD dataset) and generates baseline statistics.
*   **Model Training:** Automated training of the Random Forest and Autoencoder models.
*   **Artifact Versioning:** Trained models (`.pkl`) and preprocessors are saved to **Persistent Volumes (PVC)** to ensure persistence across pod restarts.

### 3. Containerization & Registry
*   **Docker:** Every microservice (Frontend, Prediction, Drift Detection) is containerized using optimized Dockerfiles.
*   **Image Versioning:** Jenkins automatically builds and tags images with short Git SHAs, pushing them to a registry for deployment.

### 4. Infrastructure as Code & Orchestration
*   **Kubernetes (K8s):** The system is orchestrated on Kubernetes, utilizing **Deployments**, **Services**, **PVCs**, and **Ingress Controllers** for traffic routing.
*   **Ansible:** Deployment is handled via **Ansible Playbooks** that template Kubernetes manifests dynamically based on Jenkins build parameters.

### 5. Drift Detection & Self-Healing
*   **Continuous Monitoring:** A dedicated **Drift Detection Service** monitors the Kolmogorov-Smirnov (KS) statistics of incoming traffic.
*   **Auto-Retraining:** If model drift is detected (e.g., a change in network traffic patterns), the service automatically triggers the ML Pipeline job to retrain the model and signals the Prediction Service to hot-reload the new artifacts without downtime.

### 6. Centralized Logging (ELK Stack)
*   **Elasticsearch & Kibana:** All system logs are indexed for high-speed searching and visualization.
*   **Fluent Bit:** Acts as a lightweight log processor and forwarder, collecting container logs and shipping them to the EFK stack.

---

## Technical Stack

*   **Languages:** Python (3.11)
*   **Backend:** FastAPI, Uvicorn
*   **Frontend:** Streamlit (Cyberpunk/Neon Aesthetic)
*   **Machine Learning:** Scikit-Learn, PyTorch (Autoencoders), Pandas, NumPy
*   **DevOps:** Jenkins (Groovy Pipelines), Ansible, Docker
*   **Orchestration:** Kubernetes (Minikube), Ingress-NGINX
*   **Monitoring:** ELK Stack (Elasticsearch, Fluent Bit, Kibana)
*   **Database:** MongoDB (for raw log archival)

---

## Project Structure

```bash
├── Ansible/                # IaC: Deployment playbooks and inventory
├── Kubernetes/             # Orchestration: K8s manifests (Deployments, Services, Ingress)
│   └── logging/            # Centralized Logging: ELK Stack configurations (Elasticsearch, Fluent Bit, Kibana)
├── ml_pipeline/            # ML Engineering: Data loading, training, and retraining logic
├── prediction_service/     # Core Service: FastAPI inference microservice
├── drift_service/          # Monitoring: Drift detection and retraining trigger
├── frontend/               # UI: Cyber-themed Streamlit dashboard
├── data_storage/           # Shared Volume: Persistent storage for logs and baseline stats
├── models/                 # Artifacts: Pre-trained models and preprocessors
├── Jenkinsfile             # CI/CD: Automated build and deployment pipeline
├── docker-compose.yml      # Local Dev: Container orchestration for local testing
└── requirements.txt        # Dependencies: Global project requirements
```

