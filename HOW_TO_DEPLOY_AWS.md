# How to Deploy Fraud Detection to AWS — Step by Step

**Author: Suresh D R | AI Product Developer & Technology Mentor**
*MLOps Syllabus — Deploy and Retrain ML Models on AWS*

---

## What You Will Do

```
PART 1 — Local Setup
  Step 1  → Create virtual environment and run locally
  Step 2  → Push code to GitHub
  Step 3  → CI/CD pipeline runs automatically

PART 2 — AWS Setup (one time only)
  Step 4  → Create AWS account
  Step 5  → Create IAM user with permissions
  Step 6  → Install and configure AWS CLI
  Step 7  → Create Amazon ECR repository
  Step 8  → Build Docker image and push to ECR
  Step 9  → Install kubectl and eksctl
  Step 10 → Create EKS cluster

PART 3 — Deploy to AWS
  Step 11 → Add GitHub Secrets
  Step 12 → Update Kubernetes YAML with your account ID
  Step 13 → Deploy to EKS and get live URL

PART 4 — Auto Deploy on Every Code Change
  Step 14 → Make a code change
  Step 15 → git push — auto deploys to AWS
  Step 16 → See change live immediately

PART 5 — Delete Everything (Save Cost)
  Step 17 → Delete EKS cluster
  Step 18 → Delete ECR images
  Step 19 → Delete ECR repository
  Step 20 → Stop EC2 instances
```

---

# PART 1 — LOCAL SETUP

---

## STEP 1 — Create Virtual Environment and Run Locally

Open project in VS Code → open Git Bash terminal.

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/Scripts/activate
```

You will see `(venv)` appear. ✅

```bash
# Install libraries
pip install -r requirements.txt

# Generate data and train model
cd src
python generate_data.py
python train.py
cd ..

# Run all 8 tests
pytest tests/test_model.py -v
```

All 8 tests pass. ✅

```bash
# Run Streamlit app locally
streamlit run src/app.py
```

Open browser → `http://localhost:8501` → app works ✅

Stop app → press `Ctrl+C`

---

## STEP 2 — Push Code to GitHub

```bash
git init
git config --global user.name "Suresh D R"
git config --global user.email "your-email@gmail.com"

git add .
git commit -m "Initial commit — fraud detection with CI/CD and AWS deployment"
git branch -M main
git remote add origin https://github.com/your-username/fraud-detection-aws.git
git push -u origin main
```

Enter username and Personal Access Token when asked. ✅

---

## STEP 3 — CI/CD Pipeline Runs Automatically

Go to GitHub → **Actions** tab.

You will see:
```
✅ Install, Train and Test    — 32 seconds
⏳ Build Docker Image and Push — waiting for AWS setup
⏳ Deploy to AWS EKS          — waiting for AWS setup
```

Job 1 passes immediately. Jobs 2 and 3 need AWS setup — do that next.

---

# PART 2 — AWS SETUP (ONE TIME ONLY)

---

## STEP 4 — Create AWS Account

1. Go to `https://aws.amazon.com/free`
2. Click **Create a Free Account**
3. Enter email → set password → account name: `mlops-account`
4. Select **Personal** account type
5. Enter contact details
6. Enter credit/debit card details
7. Phone verification → OTP → verify
8. Choose **Basic Support — Free**
9. Click **Complete Sign Up** ✅

**Login:**
```
https://console.aws.amazon.com
```

**Set Region — top right corner:**
```
Asia Pacific (Mumbai) — ap-south-1
```

---

## STEP 5 — Create IAM User with Permissions

### 5a — Create IAM User

1. Search **IAM** in AWS Console → click IAM
2. Click **Users** → **Create user**
3. Username: `mlops-user`
4. Click **Next**
5. Select **Attach policies directly**
6. Search and tick these policies one by one:
   - Search `AmazonECRFullAccess` → tick ✅
   - Search `AmazonEKSFullAccess` → tick ✅
   - Search `AmazonEKSClusterPolicy` → tick ✅
   - Search `AmazonS3FullAccess` → tick ✅

> ⚠️ If you cannot find these policies — just search `AdministratorAccess` and tick that. It gives full access to everything — perfectly fine for learning.

7. Click **Next** → **Create user** ✅

### 5b — Create Access Keys

1. Click on `mlops-user`
2. Click **Security credentials** tab
3. Scroll to **Access keys** → click **Create access key**
4. Select **Command Line Interface (CLI)**
5. Tick confirmation → click **Next** → **Create access key**
6. **DOWNLOAD CSV FILE immediately!**

```
AWS_ACCESS_KEY_ID     = AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY = wJalrXUtnFEMI/K7MDENG
```

> ⚠️ You cannot see secret key again after closing this page. Save in Notepad.

---

## STEP 6 — Install and Configure AWS CLI

### 6a — Check if installed

```bash
aws --version
```

If not installed:
1. Go to `https://aws.amazon.com/cli/`
2. Download → Windows 64-bit
3. Install → restart Git Bash

### 6b — Configure

```bash
aws configure
```

```
AWS Access Key ID: your-access-key
AWS Secret Access Key: your-secret-key
Default region name: ap-south-1
Default output format: json
```

**Verify:**
```bash
aws sts get-caller-identity
```

```json
{
    "Account": "968603941077",
    "Arn": "arn:aws:iam::968603941077:user/mlops-user"
}
```

AWS CLI connected. ✅

---

## STEP 7 — Create Amazon ECR Repository

```bash
aws ecr create-repository \
    --repository-name fraud-detection \
    --region ap-south-1
```

**You will see:**
```json
{
    "repository": {
        "repositoryUri": "968603941077.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection"
    }
}
```

**Save these:**
```
Account ID    : 968603941077
ECR Registry  : 968603941077.dkr.ecr.ap-south-1.amazonaws.com
ECR Repository: fraud-detection
```

---

## STEP 8 — Build Docker Image and Push to ECR

> ⚠️ Switch to **mobile hotspot** before all Docker commands — WiFi blocks Docker.

### 8a — Make sure model exists

```bash
ls models/
```
```
fraud_model.pkl ✅
```

If not there — train first:
```bash
cd src && python generate_data.py && python train.py && cd ..
```

### 8b — Build Docker image

```bash
docker build -t fraud-detection:v1.0 .
```

Wait 5-10 minutes first time. You will see:
```
[+] Building 65.3s (8/8) FINISHED
=> naming to fraud-detection:v1.0 ✅
```

### 8c — Login to ECR

```bash
aws ecr get-login-password --region ap-south-1 | \
docker login --username AWS --password-stdin \
968603941077.dkr.ecr.ap-south-1.amazonaws.com
```
```
Login Succeeded ✅
```

### 8d — Tag the image

```bash
docker tag fraud-detection:v1.0 \
968603941077.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:latest

docker tag fraud-detection:v1.0 \
968603941077.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:v1.0
```

### 8e — Push to ECR

```bash
docker push \
968603941077.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:latest

docker push \
968603941077.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:v1.0
```

```
latest: digest: sha256:abc123... size: 892MB
Pushed ✅
```

**Verify on AWS Console:**
Go to ECR → Repositories → fraud-detection → image appears ✅

---

## STEP 9 — Install kubectl and eksctl

### Install kubectl

```bash
curl -LO "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"
mkdir -p ~/bin
mv kubectl.exe ~/bin/kubectl
kubectl version --client
```
```
Client Version: v1.28.0 ✅
```

### Install eksctl

```bash
curl -sLO "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_Windows_amd64.zip"
unzip eksctl_Windows_amd64.zip -d ~/bin/
eksctl version
```
```
0.157.0 ✅
```

---

## STEP 10 — Create EKS Cluster

> ⚠️ Costs ₹600-800/day. Delete after practice.

```bash
eksctl create cluster \
  --name fraud-detection-cluster \
  --region ap-south-1 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed
```

Takes 15-20 minutes. You will see:
```
[✔] EKS cluster fraud-detection-cluster is ready ✅
```

**Verify:**
```bash
kubectl get nodes
```
```
NAME                  STATUS   AGE
ip-10-0-1-100.ap      Ready    2m ✅
ip-10-0-2-200.ap      Ready    2m ✅
```

---

## STEP 10b — If Cluster Creation Fails — Fixes

### Fix 1 — EC2 Quota Not Approved Yet

If you see:
```
error: failed to create cluster
waiter state transitioned to Failure
```

**Solution — Request EC2 quota increase:**
1. Go to `https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas`
2. Search `Running On-Demand Standard`
3. Click **Request increase at account level**
4. Enter `8` → **Request**
5. Wait for approval email (15 mins to 2 hours)
6. Then try again

---

### Fix 2 — Try with Fewer Nodes

If cluster still fails — try with just 1 node:

```bash
eksctl create cluster \
  --name fraud-detection-cluster \
  --region ap-south-1 \
  --node-type t3.micro \
  --nodes 1
```

---

### Fix 3 — Delete Failed Cluster and Retry

If cluster creation failed halfway:

```bash
# Delete the failed cluster first
eksctl delete cluster \
  --region ap-south-1 \
  --name fraud-detection-cluster
```

Wait 5-10 minutes for full cleanup. Then retry.

---

### Fix 4 — Check What Went Wrong in CloudFormation

1. Go to AWS Console → search **CloudFormation**
2. Click on the failed stack
3. Click **Events** tab
4. Look for red **FAILED** entries
5. Read the error message — it tells you exactly what failed

---

### Fix 5 — Command That Actually Worked

This is the exact command that worked:

```bash
eksctl create cluster \
  --name fraud-detection-cluster \
  --region ap-south-1 \
  --node-type t3.medium \
  --nodes 2
```

> Note: Remove `--nodegroup-name`, `--nodes-min`, `--nodes-max`, `--managed` flags if you get errors. Simple command works best.

---

## STEP 10c — Create EKS Cluster from AWS Console (Alternative)

> If CLI commands keep failing — you can create the cluster from AWS Console website directly.

### Step 1 — Go to EKS

1. AWS Console → search **EKS**
2. Click **Elastic Kubernetes Service**
3. Click **Create cluster**

### Step 2 — Configure Cluster

```
Name            → fraud-detection-cluster
Kubernetes version → 1.28 (or latest)
Cluster IAM role   → Create new role (AWS creates automatically)
```

Click **Next**

### Step 3 — Networking

```
VPC             → select default VPC
Subnets         → select all available subnets
Security groups → leave default
Cluster endpoint access → Public
```

Click **Next** → **Next** → **Create**

Wait 10-15 minutes until status shows **Active** ✅

### Step 4 — Add Node Group

1. Click on your cluster `fraud-detection-cluster`
2. Click **Compute** tab
3. Click **Add node group**
4. Fill in:
```
Name          → workers
Node IAM role → Create new role
```
Click **Next**

5. Instance type: `t3.medium`
6. Scaling:
```
Minimum size  → 1
Maximum size  → 3
Desired size  → 2
```
Click **Next** → **Next** → **Create**

Wait 5-10 minutes until nodes show **Ready** ✅

### Step 5 — Connect kubectl to Console Cluster

```bash
aws eks update-kubeconfig \
  --region ap-south-1 \
  --name fraud-detection-cluster
```

**Verify:**
```bash
kubectl get nodes
```
```
NAME                  STATUS   AGE
ip-192-168-2-42.ap    Ready    2m ✅
ip-192-168-45-185.ap  Ready    2m ✅
```

Now continue with Step 11 — same as before. ✅

---

# PART 3 — DEPLOY TO AWS

---

## STEP 11 — Add GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** — add these:

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Your IAM access key |
| `AWS_SECRET_ACCESS_KEY` | Your IAM secret key |
| `AWS_REGION` | `ap-south-1` |
| `ECR_REGISTRY` | `968603941077.dkr.ecr.ap-south-1.amazonaws.com` |
| `ECR_REPOSITORY` | `fraud-detection` |
| `EKS_CLUSTER_NAME` | `fraud-detection-cluster` |

All 6 secrets added ✅

---

## STEP 12 — Update Kubernetes YAML with Your Account ID

Open `k8s/deployment.yml` in VS Code.

Find:
```yaml
image: ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:latest
```

Replace with your actual account ID:
```yaml
image: 968603941077.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:latest
```

Save — `Ctrl+S`

Push this change:
```bash
git add k8s/deployment.yml
git commit -m "Update deployment with ECR account ID"
git push
```

---

## STEP 13 — Deploy to EKS and Get Live URL

```bash
# Connect to EKS cluster
aws eks update-kubeconfig \
  --region ap-south-1 \
  --name fraud-detection-cluster

# Deploy
kubectl apply -f k8s/deployment.yml
```

```
deployment.apps/fraud-detection created
service/fraud-detection-service created
```

**Check pods:**
```bash
kubectl get pods
```
```
NAME                               READY   STATUS    AGE
fraud-detection-7d9f8b-abc12       1/1     Running   2m ✅
fraud-detection-7d9f8b-def34       1/1     Running   2m ✅
```

**Get public URL:**
```bash
kubectl get service fraud-detection-service
```
```
NAME                       TYPE           EXTERNAL-IP
fraud-detection-service    LoadBalancer   abc123.ap-south-1.elb.amazonaws.com
```

Open browser:
```
http://abc123.ap-south-1.elb.amazonaws.com:8501
```

**Fraud detection app is LIVE on AWS!** 🎉

---

# PART 4 — AUTO DEPLOY ON EVERY CODE CHANGE

---

## STEP 14 — Make a Code Change

Open `src/train.py` → find:
```python
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, n_jobs=-1)
```

Change to:
```python
model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
```

Save — `Ctrl+S`

---

## STEP 15 — Push to GitHub

```bash
git add src/train.py
git commit -m "Improve model — 200 trees, depth 10"
git push
```

---

## STEP 16 — Watch Auto Deploy to AWS

Go to GitHub → **Actions** tab → new pipeline runs automatically:

```
✅ Install, Train and Test       — 32 seconds
✅ Build Docker Image and Push   — 4 minutes
✅ Deploy to AWS EKS             — 2 minutes (rolling update, zero downtime)
```

Open your live URL — new model is live! ✅

---

# PART 5 — DELETE EVERYTHING (SAVE COST)

> ⚠️ Always delete after practice. Cost is ₹600-800/day.

---

## STEP 17 — Delete EKS Cluster (Most Important — Stops Charges)

```bash
eksctl delete cluster \
  --name fraud-detection-cluster \
  --region ap-south-1
```

Takes 10-15 minutes. You will see:
```
All cluster resources were deleted ✅
```

---

## STEP 18 — Delete ECR Images (from AWS Console)

1. Go to AWS Console → search **ECR**
2. Click **Repositories**
3. Click **fraud-detection**
4. Tick all images (select all checkboxes)
5. Click **Delete** → type `delete` to confirm ✅

---

## STEP 19 — Delete ECR Repository

**From terminal:**
```bash
aws ecr delete-repository \
    --repository-name fraud-detection \
    --region ap-south-1 \
    --force
```

**Or from Console:**
1. ECR → Repositories
2. Select `fraud-detection`
3. Click **Delete** → type `delete` to confirm ✅

---

## STEP 20 — Verify Nothing is Running (Check Billing)

**Check EC2 — make sure no instances running:**
```bash
aws ec2 describe-instances \
    --region ap-south-1 \
    --query 'Reservations[].Instances[].{ID:InstanceId,State:State.Name}'
```

Should show empty or `terminated`. ✅

**Check from Console:**
1. Go to **EC2** → **Instances**
2. All should show **Terminated** or none ✅

**Check billing:**
1. Search **Billing** in AWS Console
2. Click **Bills**
3. Verify no unexpected charges ✅

---

## Quick Delete Commands — All in One

```bash
# Delete EKS cluster (most important)
eksctl delete cluster --name fraud-detection-cluster --region ap-south-1

# Delete ECR repository and all images
aws ecr delete-repository --repository-name fraud-detection --region ap-south-1 --force

# Verify no EC2 running
aws ec2 describe-instances --region ap-south-1 \
    --query 'Reservations[].Instances[].State.Name'
```

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `docker daemon not running` | Docker Desktop closed | Open Docker Desktop |
| `TLS handshake timeout` | WiFi blocking Docker | Switch to mobile hotspot |
| `aws: command not found` | AWS CLI not installed | Install from aws.amazon.com/cli |
| `Unable to connect to cluster` | Wrong kubeconfig | Run `aws eks update-kubeconfig` again |
| `ImagePullBackOff` | EKS cannot pull from ECR | Check IAM permissions |
| `CrashLoopBackOff` | Container crashing | `kubectl logs pod-name` |
| `Pending` pods | Not enough EC2 | Wait or increase nodes |
| Pipeline Job 2 fails | GitHub Secrets missing | Add all 6 secrets |
| Policy not found in IAM | Search differently | Use `AdministratorAccess` instead |

---

## All Commands — Quick Reference

```bash
# Local setup
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
cd src && python generate_data.py && python train.py && cd ..
pytest tests/test_model.py -v
streamlit run src/app.py

# Git
git add . && git commit -m "message" && git push

# AWS CLI
aws configure
aws sts get-caller-identity

# ECR
aws ecr create-repository --repository-name fraud-detection --region ap-south-1
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <ECR_URL>

# Docker
docker build -t fraud-detection:v1.0 .
docker tag fraud-detection:v1.0 <ECR_URL>/fraud-detection:latest
docker push <ECR_URL>/fraud-detection:latest

# EKS — Create
eksctl create cluster --name fraud-detection-cluster --region ap-south-1 --node-type t3.medium --nodes 2 --managed

# Kubernetes — Deploy
aws eks update-kubeconfig --region ap-south-1 --name fraud-detection-cluster
kubectl apply -f k8s/deployment.yml
kubectl get pods
kubectl get service fraud-detection-service
kubectl get nodes
kubectl logs <pod-name>
kubectl rollout status deployment/fraud-detection

# DELETE EVERYTHING
eksctl delete cluster --name fraud-detection-cluster --region ap-south-1
aws ecr delete-repository --repository-name fraud-detection --region ap-south-1 --force
```

---

## Cost Warning

```
EKS Control Plane  → $0.10/hour = ₹8/hour  = ₹200/day
EC2 t3.medium x2   → $0.10/hour = ₹8/hour  = ₹400/day
ECR storage        → free up to 500MB/month

Total per day      → ₹600-800/day ⚠️

Always delete after practice:
eksctl delete cluster --name fraud-detection-cluster --region ap-south-1
```

---

*MLOps Syllabus — Deploy and Retrain ML Models on AWS*
*Author: Suresh D R | AI Product Developer & Technology Mentor*
