import json

import joblib
import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier


@pytest.fixture()
def trained_model_dir(tmp_path):
    """Create a tiny, fast-to-train model + metadata for tests."""
    rng = np.random.default_rng(0)
    X = rng.integers(0, 100, size=(50, 5))
    y = rng.integers(0, 2, size=50)

    model = RandomForestClassifier(n_estimators=5, random_state=0)
    model.fit(X, y)

    model_path = tmp_path / "model.pkl"
    metadata_path = tmp_path / "metadata.json"
    joblib.dump(model, model_path)
    metadata_path.write_text(json.dumps({"version": "test-v1", "metrics": {"accuracy": 1.0}}))

    return model_path, metadata_path


@pytest.fixture()
def client(trained_model_dir, monkeypatch):
    model_path, metadata_path = trained_model_dir
    monkeypatch.setenv("DIABETES_API_MODEL_PATH", str(model_path))
    monkeypatch.setenv("DIABETES_API_METADATA_PATH", str(metadata_path))

    # Ensure settings + app are freshly built against the patched env vars.
    from app.config import get_settings

    get_settings.cache_clear()

    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()
