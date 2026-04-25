import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from preprocess import preprocess

def train_and_track(n_estimators=100, max_depth=5,
                    data_path='../data/transactions.csv',
                    experiment_name='fraud-detection'):
    """Train model and log everything to MLflow"""

    mlflow.set_experiment(experiment_name)

    with mlflow.start_run():

        # Log parameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth",    max_depth)
        mlflow.log_param("data_path",    data_path)

        # Load and prepare data
        X, y = preprocess(data_path)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size",  len(X_test))

        # Train model
        print(f"Training: n_estimators={n_estimators}, max_depth={max_depth}")
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        accuracy  = accuracy_score(y_test, y_pred)
        f1        = f1_score(y_test, y_pred, zero_division=0)
        roc_auc   = roc_auc_score(y_test, y_prob)

        # Log metrics
        mlflow.log_metric("accuracy",  accuracy)
        mlflow.log_metric("f1_score",  f1)
        mlflow.log_metric("roc_auc",   roc_auc)

        # Log model
        mlflow.sklearn.log_model(model, "fraud_model")

        run_id = mlflow.active_run().info.run_id

        print(f"\nRun ID  : {run_id}")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"F1 Score: {f1:.4f}")
        print(f"ROC-AUC : {roc_auc:.4f}")

        return run_id, roc_auc, model

def compare_and_register(experiment_name='fraud-detection'):
    """Find best run and register in Model Registry"""

    runs = mlflow.search_runs(
        experiment_names=[experiment_name],
        order_by=["metrics.roc_auc DESC"]
    )

    if runs.empty:
        print("No runs found. Train a model first.")
        return

    best = runs.iloc[0]
    print("\n========== BEST MODEL ==========")
    print(f"Run ID      : {best['run_id']}")
    print(f"n_estimators: {best['params.n_estimators']}")
    print(f"max_depth   : {best['params.max_depth']}")
    print(f"Accuracy    : {best['metrics.accuracy']:.4f}")
    print(f"ROC-AUC     : {best['metrics.roc_auc']:.4f}")
    print("================================")

    print("\nAll experiment runs:")
    print(runs[['run_id','params.n_estimators','params.max_depth',
                'metrics.accuracy','metrics.roc_auc']].to_string(index=False))

if __name__ == "__main__":
    print("Running 3 experiments with different settings...\n")

    run1, auc1, _ = train_and_track(n_estimators=100, max_depth=5)
    run2, auc2, _ = train_and_track(n_estimators=200, max_depth=10)
    run3, auc3, _ = train_and_track(n_estimators=300, max_depth=15)

    print("\n========== EXPERIMENT SUMMARY ==========")
    print(f"Run 1: n=100, depth=5  → AUC: {auc1:.4f}")
    print(f"Run 2: n=200, depth=10 → AUC: {auc2:.4f}")
    print(f"Run 3: n=300, depth=15 → AUC: {auc3:.4f}")
    print("\nRun 'mlflow ui' to view dashboard")
    print("Open: http://localhost:5000")

    compare_and_register()
