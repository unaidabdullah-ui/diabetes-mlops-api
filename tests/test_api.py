VALID_PAYLOAD = {
    "Pregnancies": 2,
    "Glucose": 130,
    "BloodPressure": 70,
    "BMI": 28.5,
    "Age": 45,
}


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.json()


def test_health_reports_model_loaded(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert body["model_version"] == "test-v1"


def test_predict_valid_payload(client):
    resp = client.post("/predict", json=VALID_PAYLOAD)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["diabetic"], bool)
    assert 0.0 <= body["probability"] <= 1.0
    assert body["model_version"] == "test-v1"


def test_predict_rejects_out_of_range_glucose(client):
    payload = {**VALID_PAYLOAD, "Glucose": -5}
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 422


def test_predict_rejects_missing_field(client):
    payload = {**VALID_PAYLOAD}
    del payload["BMI"]
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 422


def test_predict_rejects_wrong_type(client):
    payload = {**VALID_PAYLOAD, "Age": "not-a-number"}
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 422
