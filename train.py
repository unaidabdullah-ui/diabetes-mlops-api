"""Train the diabetes classifier and save the model + metadata.

Usage:
    python train.py
    python train.py --data-url <csv-url> --output models/diabetes_model.pkl
"""
from __future__ import annotations

import argparse
import json
import logging
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

from app.logging_config import configure_logging

configure_logging("INFO")
logger = logging.getLogger(__name__)

DEFAULT_DATA_URL = "https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv"
FEATURES = ["Pregnancies", "Glucose", "BloodPressure", "BMI", "Age"]
TARGET = "Outcome"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-url", default=DEFAULT_DATA_URL, help="CSV source for training data")
    parser.add_argument("--output", default="models/diabetes_model.pkl", help="Where to save the model")
    parser.add_argument(
        "--metadata-output", default="models/metadata.json", help="Where to save training metadata/metrics"
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--n-estimators", type=int, default=200)
    return parser.parse_args()


def load_data(data_url: str) -> pd.DataFrame:
    logger.info("Loading dataset from %s", data_url)
    df = pd.read_csv(data_url)
    missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {missing}")
    logger.info("Loaded %d rows, %d columns", *df.shape)
    return df


def train(args: argparse.Namespace) -> None:
    df = load_data(args.data_url)
    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )

    model = RandomForestClassifier(n_estimators=args.n_estimators, random_state=args.random_state)
    logger.info("Training RandomForestClassifier (n_estimators=%d)", args.n_estimators)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }
    logger.info("Evaluation metrics: %s", {k: round(v, 4) for k, v in metrics.items()})

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    logger.info("Model saved to %s", output_path)

    metadata = {
        "version": datetime.now(UTC).strftime("%Y%m%d%H%M%S"),
        "trained_at": datetime.now(UTC).isoformat(),
        "features": FEATURES,
        "target": TARGET,
        "algorithm": "RandomForestClassifier",
        "hyperparameters": {"n_estimators": args.n_estimators, "random_state": args.random_state},
        "metrics": metrics,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "data_source": args.data_url,
        "sklearn_version": sklearn.__version__,
        "python_version": platform.python_version(),
    }
    metadata_path = Path(args.metadata_output)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Metadata saved to %s", metadata_path)


if __name__ == "__main__":
    try:
        train(parse_args())
    except Exception:
        logger.exception("Training failed")
        sys.exit(1)
