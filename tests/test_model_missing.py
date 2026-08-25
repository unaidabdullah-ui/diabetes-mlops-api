def test_health_and_predict_when_model_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("DIABETES_API_MODEL_PATH", str(tmp_path / "does-not-exist.pkl"))
    monkeypatch.setenv("DIABETES_API_METADATA_PATH", str(tmp_path / "does-not-exist.json"))

    from app.config import get_settings

    get_settings.cache_clear()

    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["model_loaded"] is False

        predict = client.post(
            "/predict",
            json={"Pregnancies": 1, "Glucose": 100, "BloodPressure": 70, "BMI": 25.0, "Age": 30},
        )
        assert predict.status_code == 503

    get_settings.cache_clear()
