# Complete MLOps Pipeline — End to End How to Run

**Author: Suresh D R | AI Product Developer & Technology Mentor**
*MLOps Syllabus — Deploy and Retrain ML Models on AWS*

---

## What You Will Build

```
PHASE 1 — Local Setup and Run
  Step 1  → Unzip project and open in VS Code
  Step 2  → Create virtual environment
  Step 3  → Install all libraries
  Step 4  → Generate data and train model
  Step 5  → Run all tests
  Step 6  → Run Streamlit app locally
  Step 7  → Run REST API locally
  Step 8  → Demo drift detection locally

PHASE 2 — Push to GitHub with CI/CD
  Step 9  → Create GitHub repository
  Step 10 → Push code — CI/CD pipeline triggers automatically
  Step 11 → Watch pipeline run on GitHub Actions

PHASE 3 — Docker and ECR
  Step 12 → Build Docker image locally
  Step 13 → Push to Docker Hub (for sharing)
  Step 14 → Create ECR and push image

PHASE 4 — Deploy to AWS EKS
  Step 15 → Create EKS cluster
  Step 16 → Add GitHub Secrets
  Step 17 → Deploy to EKS — get live URL
  Step 18 → Test live app

PHASE 5 — MLflow Experiment Tracking
  Step 19 → Run multiple experiments
  Step 20 → Open MLflow dashboard
  Step 21 → Compare runs and pick best model

PHASE 6 — Data Drift Demo
  Step 22 → Run drift check on normal data — no drift
  Step 23 → Run drift check on drifted data — drift detected
  Step 24 → Understand what the results mean

PHASE 7 — Cleanup
  Step 25 → Delete EKS cluster (save cost)
  Step 26 → Delete ECR images
```

---

# PHASE 1 — LOCAL SETUP AND RUN

---

## STEP 1 — Unzip and Open in VS Code

1. Download `fraud-mlops-complete.zip`
2. Right click → **Extract All** → choose **Desktop** → **Extract**
3. Open **VS Code**
4. **File** → **Open Folder** → select `fraud-mlops-complete` → **Select Folder**

**Project structure you will see:**
```
fraud-mlops-complete/
├── src/
│   ├── generate_data.py     → creates sample data
│   ├── preprocess.py        → feature engineering
│   ├── train.py             → trains fraud model
│   ├── predict.py           → makes predictions
│   ├── app.py               → Streamlit frontend
│   └── api.py               → FastAPI REST API
├── monitoring/
│   ├── detect_drift.py      → data drift detection
│   └── track_experiment.py  → MLflow experiment tracking
├── pipeline/
│   └── sagemaker_trigger.py → trigger SageMaker retraining
├── tests/
│   └── test_model.py        → 8 pytest tests
├── k8s/
│   ├── deployment-uat.yml   → UAT Kubernetes config
│   └── deployment-prod.yml  → Production Kubernetes config
├── .github/workflows/
│   └── mlops_pipeline.yml   → CI/CD automation
├── data/
│   ├── reference/           → training data for drift baseline
│   └── demo_drift/          → demo datasets for drift detection
├── models/                  → trained model saved here
├── Dockerfile
├── requirements.txt
└── .gitignore
```

---

## STEP 2 — Open Git Bash and Create Virtual Environment

1. VS Code → **Terminal** → **New Terminal**
2. Dropdown **(▾)** → **Select Default Profile** → **Git Bash** → **New Terminal**

```bash
# Check you are in right folder
pwd
# Should show: /c/Users/Suresh D R/Desktop/fraud-mlops-complete

# Create virtual environment
python -m venv venv

# Activate it
source venv/Scripts/activate
```

You will see `(venv)` appear. ✅

> ⚠️ Every time you open a new terminal — run `source venv/Scripts/activate` first.

---

## STEP 3 — Install All Libraries

```bash
pip install -r requirements.txt
```

This installs:
```
pandas, numpy, scikit-learn  → ML libraries
streamlit                    → web app
fastapi, uvicorn             → REST API
evidently                    → drift detection
mlflow                       → experiment tracking
boto3                        → AWS SDK
scipy                        → statistical tests
pytest                       → testing
```

Wait 3-5 minutes. ✅

---

## STEP 4 — Generate Data and Train Model

```bash
cd src
python generate_data.py
```
```
Created 1000 transactions
Fraud cases: 100 (10.0%) ✅
```

```bash
python train.py
cd ..
```
```
Accuracy  : 0.92
ROC-AUC   : 0.95
Model saved to: ../models/fraud_model.pkl ✅
```

```bash
# Verify
ls models/
```
```
fraud_model.pkl ✅
```

---

## STEP 5 — Run All Tests

```bash
pytest tests/test_model.py -v
```

```
tests/test_model.py::test_model_file_exists          PASSED
tests/test_model.py::test_model_loads                PASSED
tests/test_model.py::test_prediction_keys            PASSED
tests/test_model.py::test_prediction_is_binary       PASSED
tests/test_model.py::test_confidence_range           PASSED
tests/test_model.py::test_risk_level_valid           PASSED
tests/test_model.py::test_legitimate_prediction      PASSED
tests/test_model.py::test_fraud_prediction           PASSED

8 passed ✅
```

---

## STEP 6 — Run Streamlit App (Type 2 Deployment — Web App)

```bash
streamlit run src/app.py
```

Open browser → `http://localhost:8501`

Test these combinations:

| Amount | Hour | Merchant | Expected |
|--------|------|----------|----------|
| 500 | 14 | Grocery | ✅ LEGITIMATE |
| 95000 | 3 | Electronics | 🚨 FRAUD |
| 1200 | 13 | Restaurant | ✅ LEGITIMATE |
| 120000 | 1 | Jewellery | 🚨 FRAUD |

Stop → `Ctrl+C`

---

## STEP 7 — Run REST API (Type 1 Deployment — API for Other Apps)

```bash
python src/api.py
```

```
INFO: Uvicorn running on http://0.0.0.0:8000 ✅
```

Open browser → `http://localhost:8000/docs`

You see the interactive API documentation. Test the `/predict` endpoint directly from the browser.

**Or test from terminal:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 45000,
    "hour": 3,
    "day_of_week": 6,
    "merchant_type": "electronics",
    "customer_age": 22,
    "num_prev_txns": 1,
    "avg_txn_amount": 300
  }'
```

```json
{
  "prediction": "FRAUD",
  "confidence": 88.5,
  "risk_level": "HIGH"
}
```

Stop → `Ctrl+C`

---

## STEP 8 — Demo Data Drift Detection Locally

```bash
python monitoring/detect_drift.py
```

**You will see TWO scenarios:**

**Scenario 1 — Normal data (no drift expected):**
```
======== SCENARIO 1: Normal Data ========

  [+] amount          Training mean: 520  Current mean: 535  (2.9% change)
                      P-value: 0.6234 → OK ✅

  [+] hour            Training mean: 14.8 Current mean: 14.5
                      P-value: 0.5821 → OK ✅

  [+] customer_age    Training mean: 41.2 Current mean: 40.8
                      P-value: 0.7102 → OK ✅

  Dataset drift: NO — Model still good ✅
```

**Scenario 2 — Drifted data (drift detected):**
```
======== SCENARIO 2: Drifted Data ========

  [X] amount          Training mean: 520   Current mean: 85400  (16323% change!)
                      P-value: 0.000001 → DRIFT DETECTED ❌

  [X] hour            Training mean: 14.8  Current mean: 2.1
                      P-value: 0.000003 → DRIFT DETECTED ❌

  [X] num_prev_txns   Training mean: 110   Current mean: 2.3
                      P-value: 0.000002 → DRIFT DETECTED ❌

  Dataset drift: YES — RETRAIN NEEDED ❌
```

This demonstrates clearly what drift looks like vs no drift.

---

# PHASE 2 — PUSH TO GITHUB WITH CI/CD

---

## STEP 9 — Create GitHub Repository

1. Go to `https://github.com`
2. Click **+** → **New repository**
3. Name: `fraud-detection-mlops`
4. Set to **Public**
5. Do NOT tick README or .gitignore
6. Click **Create repository**
7. Copy the URL

---

## STEP 10 — Push Code to GitHub

```bash
git init
git config --global user.name "Suresh D R"
git config --global user.email "your-email@gmail.com"

git add .
git status
```

Check that `models/` and `data/` are NOT listed — .gitignore is working. ✅

```bash
git commit -m "Initial commit — complete MLOps fraud detection project"
git branch -M main
git remote add origin https://github.com/your-username/fraud-detection-mlops.git
git push -u origin main
```

Enter username and Personal Access Token when asked.

---

## STEP 11 — Watch CI/CD Pipeline Run

Go to GitHub → **Actions** tab.

You will see pipeline running:
```
✅ Install, Train and Test    — 32 seconds
✅ Build Docker Image         — 3 minutes
```

Every future `git push` triggers this automatically. ✅

---

# PHASE 3 — DOCKER AND ECR

---

## STEP 12 — Build Docker Image Locally

> ⚠️ Docker Desktop must be running. Switch to mobile hotspot.

```bash
# Check model exists
ls models/
# fraud_model.pkl ✅

# Build image
docker build -t fraud-detection-app:v1.0 .
```

Wait 5-10 minutes first time.

```
[+] Building 65.3s (8/8) FINISHED
=> naming to fraud-detection-app:v1.0 ✅
```

```bash
# Run locally
docker run -p 8501:8501 fraud-detection-app:v1.0
```

Open browser → `http://localhost:8501` — app runs inside Docker! ✅

Stop → `Ctrl+C`

---

## STEP 13 — Push to Docker Hub (Share with Anyone)

```bash
# Login
docker login -u your-dockerhub-username
# Enter your Docker Hub Personal Access Token as password

# Tag
docker tag fraud-detection-app:v1.0 \
    your-username/fraud-detection-app:v1.0

# Push
docker push your-username/fraud-detection-app:v1.0
```

**Anyone can now run your app with one command:**
```bash
docker run -p 8501:8501 your-username/fraud-detection-app:v1.0
```

---

## STEP 14 — Create ECR and Push Image

```bash
# Create ECR repo
aws ecr create-repository \
    --repository-name fraud-detection \
    --region ap-south-1

# Login to ECR
aws ecr get-login-password --region ap-south-1 | \
docker login --username AWS --password-stdin \
968603941077.dkr.ecr.ap-south-1.amazonaws.com

# Tag and push
docker tag fraud-detection-app:v1.0 \
    968603941077.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:latest

docker push \
    968603941077.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:latest
```

```
Pushed ✅
```

---

# PHASE 4 — DEPLOY TO AWS EKS

---

## STEP 15 — Create EKS Cluster

> ⚠️ Costs ₹600-800/day. Delete after practice.

```bash
eksctl create cluster \
  --name fraud-detection-cluster \
  --region ap-south-1 \
  --node-type t3.medium \
  --nodes 2
```

Wait 15-20 minutes.

```
EKS cluster fraud-detection-cluster is ready ✅
```

```bash
kubectl get nodes
```
```
NAME                  STATUS   AGE
ip-192-168-2-42.ap    Ready    2m ✅
ip-192-168-45-185.ap  Ready    2m ✅
```

---

## STEP 16 — Add GitHub Secrets

Go to GitHub repo → **Settings** → **Secrets and variables** → **Actions** → add:

| Secret | Value |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | your IAM key |
| `AWS_SECRET_ACCESS_KEY` | your IAM secret |
| `AWS_REGION` | `ap-south-1` |
| `ECR_REGISTRY` | `968603941077.dkr.ecr.ap-south-1.amazonaws.com` |
| `ECR_REPOSITORY` | `fraud-detection` |
| `EKS_CLUSTER_NAME` | `fraud-detection-cluster` |

---

## STEP 17 — Deploy to EKS

```bash
# Update k8s/deployment.yml — replace ACCOUNT_ID with 968603941077
# Then apply

aws eks update-kubeconfig \
  --region ap-south-1 \
  --name fraud-detection-cluster

kubectl apply -f k8s/deployment.yml
```

```
deployment.apps/fraud-detection created
service/fraud-detection-service created
```

```bash
kubectl get pods
```
```
fraud-detection-abc12   1/1   Running   2m ✅
fraud-detection-def34   1/1   Running   2m ✅
```

```bash
kubectl get service fraud-detection-service
```
```
EXTERNAL-IP: abc123.ap-south-1.elb.amazonaws.com
```

---

## STEP 18 — Test Live App

Open browser:
```
http://abc123.ap-south-1.elb.amazonaws.com:8501
```

**Fraud detection app is LIVE on AWS!** 🎉

---

# PHASE 5 — MLFLOW EXPERIMENT TRACKING

---

## STEP 19 — Run Multiple Experiments

First make sure you are in project root with venv active.
Also make sure data and model exist from Phase 1.

```bash
python monitoring/track_experiment.py
```

You will see 3 experiments run with different settings:
```
Run 1: n_estimators=100, max_depth=5  → AUC: 0.9521
Run 2: n_estimators=200, max_depth=10 → AUC: 0.9687
Run 3: n_estimators=300, max_depth=15 → AUC: 0.9701
```

---

## STEP 20 — Open MLflow Dashboard

```bash
mlflow ui
```

Open browser → `http://localhost:5000`

You will see:
- All 3 runs listed
- Parameters comparison side by side
- Metrics comparison — accuracy, F1, AUC
- Which run performed best

---

## STEP 21 — Compare and Pick Best Model

In MLflow UI:
1. Tick all 3 runs
2. Click **Compare**
3. See charts showing which settings gave best AUC
4. Run 3 (n=300, depth=15) → highest AUC 0.9701

This is the model you would register in Model Registry and deploy.

---

# PHASE 6 — DATA DRIFT DEMO

---

## STEP 22 — Run Drift Check on Normal Data

```bash
python monitoring/detect_drift.py
```

Watch Scenario 1 output — all features show p-value > 0.05 → no drift.

**What this means:**
The current transactions look similar to what the model was trained on. Model is still reliable. No retraining needed.

---

## STEP 23 — Run Drift Check on Drifted Data

Watch Scenario 2 output — features show p-value < 0.05 → drift detected.

**What this means:**
```
amount went from avg ₹520 → avg ₹85,400
hour went from avg 2pm → avg 2am
num_prev_txns went from avg 110 → avg 2
```

The real world changed. Fraudsters changed their behaviour. Model trained on old patterns will miss new fraud patterns.

**In production — this would automatically trigger SageMaker retraining.**

---

## STEP 24 — Understand the Statistics

**KS Test p-value:**
```
p-value < 0.05  → distributions are significantly different → DRIFT ❌
p-value ≥ 0.05  → distributions are similar → NO drift ✅
```

**Why p-value = 0.000001 means drift:**

If the two datasets came from the same distribution — seeing such a large difference would happen by chance only 1 in a million times. So we conclude — the distributions are different. The data has drifted.

---

# PHASE 7 — CLEANUP (SAVE COST)

---

## STEP 25 — Delete EKS Cluster

```bash
eksctl delete cluster \
  --name fraud-detection-cluster \
  --region ap-south-1
```

Wait 10-15 minutes.
```
All cluster resources were deleted ✅
```

---

## STEP 26 — Delete ECR Images and Repository

```bash
# Delete all images and repository
aws ecr delete-repository \
    --repository-name fraud-detection \
    --region ap-south-1 \
    --force
```

```
Repository deleted ✅
```

---

## All Commands Quick Reference

```bash
# ── Local setup ──────────────────────────────────
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

# ── Train and test ───────────────────────────────
cd src && python generate_data.py && python train.py && cd ..
pytest tests/test_model.py -v

# ── Run apps ─────────────────────────────────────
streamlit run src/app.py          # Type 2 — web app
python src/api.py                  # Type 1 — REST API

# ── Drift detection ──────────────────────────────
python monitoring/detect_drift.py

# ── MLflow ───────────────────────────────────────
python monitoring/track_experiment.py
mlflow ui                          # open http://localhost:5000

# ── Git ──────────────────────────────────────────
git add . && git commit -m "msg" && git push

# ── Docker ───────────────────────────────────────
docker build -t fraud-detection-app:v1.0 .
docker run -p 8501:8501 fraud-detection-app:v1.0

# ── ECR ──────────────────────────────────────────
aws ecr create-repository --repository-name fraud-detection --region ap-south-1
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <ECR_URL>
docker tag fraud-detection-app:v1.0 <ECR_URL>/fraud-detection:latest
docker push <ECR_URL>/fraud-detection:latest

# ── EKS ──────────────────────────────────────────
eksctl create cluster --name fraud-detection-cluster --region ap-south-1 --node-type t3.medium --nodes 2
aws eks update-kubeconfig --region ap-south-1 --name fraud-detection-cluster
kubectl apply -f k8s/deployment.yml
kubectl get pods
kubectl get service fraud-detection-service

# ── Cleanup ──────────────────────────────────────
eksctl delete cluster --name fraud-detection-cluster --region ap-south-1
aws ecr delete-repository --repository-name fraud-detection --region ap-south-1 --force
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `(venv)` not showing | `source venv/Scripts/activate` |
| Model not found | `cd src && python generate_data.py && python train.py && cd ..` |
| Docker daemon error | Open Docker Desktop first |
| Docker pull hangs | Switch to mobile hotspot |
| EKS cluster fails | Check EC2 quota in Service Quotas |
| GitHub Actions fails | Check all 6 secrets are added |
| ECR login fails | Run `aws ecr get-login-password...` again |

---

*MLOps Syllabus — Deploy and Retrain ML Models on AWS*
*Author: Suresh D R | AI Product Developer & Technology Mentor*
