"""Thin wrapper around the trained model.

Keeping this separate from `main.py` means the FastAPI layer never talks
to joblib/numpy directly, and it gives tests a single seam to mock.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np

logger = logging.getLogger(__name__)

FEATURE_ORDER = ["Pregnancies", "Glucose", "BloodPressure", "BMI", "Age"]


class ModelNotLoadedError(RuntimeError):
    """Raised when a prediction is requested before/without a loaded model."""


class ModelService:
    """Loads the model (and optional metadata) once and serves predictions."""

    def __init__(self, model_path: str, metadata_path: str | None = None) -> None:
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path) if metadata_path else None
        self._model: Any = None
        self._metadata: dict = {}

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def version(self) -> str:
        return str(self._metadata.get("version", "unknown"))

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at '{self.model_path}'. "
                "Run train.py to produce it before starting the API."
            )
        logger.info("Loading model from %s", self.model_path)
        self._model = joblib.load(self.model_path)

        if self.metadata_path and self.metadata_path.exists():
            with open(self.metadata_path) as f:
                self._metadata = json.load(f)
            logger.info("Loaded model metadata: version=%s", self.version)
        else:
            logger.warning("No metadata file found at %s; version will report 'unknown'", self.metadata_path)

    def predict(self, features: dict) -> tuple[bool, float]:
        if not self.is_loaded:
            raise ModelNotLoadedError("Model has not been loaded yet.")

        ordered = np.array([[features[name] for name in FEATURE_ORDER]])

        prediction = bool(self._model.predict(ordered)[0])
        if hasattr(self._model, "predict_proba"):
            # Probability of the positive (diabetic) class.
            probability = float(self._model.predict_proba(ordered)[0][1])
        else:
            probability = float(prediction)

        return prediction, probability


# Module-level singleton used by the FastAPI app.
model_service: ModelService | None = None
