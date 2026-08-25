# Diabetes Prediction API

![Jenkins](https://img.shields.io/badge/CI-Jenkins-D24939?logo=jenkins&logoColor=white)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![Docker](https://img.shields.io/badge/Docker-multi--stage-2496ED)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

A production-style ML service that predicts diabetes risk from a small set of
clinical features (Pregnancies, Glucose, Blood Pressure, BMI, Age), trained on
the Pima Indians Diabetes dataset and served via FastAPI.

This repo is intentionally small in scope but structured the way a real
service would be: separated concerns, config via environment variables,
health checks, input validation, tests, CI, and a hardened Docker image.

---

## Architecture

```
Client → FastAPI (app/main.py) → ModelService (app/model.py) → RandomForestClassifier
                │
                ├── /health    → reports whether the model is loaded + its version
                └── /predict   → validates input (app/schemas.py), returns prediction
```

- **`train.py`** trains the model, evaluates it on a held-out test split, and
  writes `models/diabetes_model.pkl` alongside `models/metadata.json`
  (version, metrics, hyperparameters, data source, library versions).
- **`app/`** is the serving layer only — it never touches training code or
  raw data, and imports the model as an opaque artifact + metadata.
- Model artifacts are **not** committed to git; they're produced by
  `train.py` (locally or in CI) and are `.gitignore`d / `.dockerignore`d.

---

## Project Structure

```
diabetes-mlops-api/
├── app/
│   ├── main.py             # FastAPI app, routes, lifespan model loading
│   ├── model.py             # Model load/predict wrapper
│   ├── schemas.py           # Request/response validation
│   ├── config.py            # Env-var driven settings
│   └── logging_config.py    # Structured logging setup
├── tests/
│   ├── conftest.py          # Trains a throwaway model for fast, offline tests
│   ├── test_api.py
│   └── test_model_missing.py
├── train.py                  # Training + evaluation + versioned metadata
├── models/                   # Generated: diabetes_model.pkl, metadata.json
├── Dockerfile                 # Multi-stage, non-root, healthcheck
├── Jenkinsfile                 # Lint → train → test → docker build
├── requirements.txt / requirements-dev.txt
└── pyproject.toml            # ruff + pytest config
```

---

## Getting Started

### 1. Clone & set up an environment

```bash
git clone https://github.com/unaidabdullah-ui/diabetes-mlops-api.git
cd diabetes-mlops-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

### 2. Train the model

```bash
python train.py
# -> models/diabetes_model.pkl, models/metadata.json
```

`train.py` prints accuracy, precision, recall, F1, and ROC-AUC on a held-out
test set, and stamps the saved model with a timestamped version.

### 3. Run the API locally

```bash
uvicorn app.main:app --reload
# Open http://127.0.0.1:8000/docs
```

### 4. Run tests / lint

```bash
pytest -v
ruff check .
```

Tests don't depend on the network or a real training run — `conftest.py`
fits a tiny model on synthetic data in a temp directory and points the app
at it via environment variables, so the suite runs in well under a second.

---

## API Reference

### `GET /health`

```json
{ "status": "ok", "model_loaded": true, "model_version": "20250101120000" }
```

Returns `status: "degraded"` and `model_loaded: false` if the model failed
to load at startup — useful as a container orchestrator readiness probe.

### `POST /predict`

Request:

```json
{
  "Pregnancies": 2,
  "Glucose": 130,
  "BloodPressure": 70,
  "BMI": 28.5,
  "Age": 45
}
```

Response:

```json
{ "diabetic": true, "probability": 0.695, "model_version": "20250101120000" }
```

Each field has physiologically sane bounds (e.g. `0 < Glucose <= 300`);
out-of-range or missing fields return `422` before reaching the model.

---

## Docker

The image is a multi-stage build: dependencies are installed in a `builder`
stage, and only the resulting virtualenv + app code are copied into a slim
runtime stage that runs as a **non-root user** and exposes a container
`HEALTHCHECK` against `/health`.

```bash
python train.py                                   # produce models/diabetes_model.pkl first
docker build -t diabetes-mlops-api .
docker run --rm -p 8000:8000 diabetes-mlops-api
# -> http://localhost:8000/docs
```

---

## CI/CD

The `Jenkinsfile` defines a declarative pipeline with these stages:

1. **Checkout** — pulls the repo
2. **Set up virtualenv** — creates `.venv`, installs `requirements-dev.txt`
3. **Lint** — `ruff check .`
4. **Train model** — runs `train.py` so the pipeline is exercised end-to-end
   and the model used by later stages is always freshly trained
5. **Test** — `pytest --junitxml=reports/junit.xml`, published via the
   `junit` step so results show up in the Jenkins UI
6. **Build Docker image** — tags the image with both `${BUILD_NUMBER}` and
   `latest`
7. **Post: archive artifacts** — `models/diabetes_model.pkl` and
   `models/metadata.json` are archived on the build so you can pull the
   exact model that was tested

### Setting it up

1. In Jenkins: **New Item → Pipeline** (or **Multibranch Pipeline** if you
   want a job per branch/PR automatically).
2. Point it at this repo; Jenkins will auto-detect the `Jenkinsfile`
3. The agent needs `python3` (with `venv`) and `docker` installed and on
   `PATH`. If your Jenkins agents run in containers, mount the Docker
   socket or use a Docker-capable agent label.
4. Image push is stubbed out in a commented `Push Docker image` stage —
   uncomment it and add a Jenkins credential (e.g. `dockerhub-creds`) to
   push to a registry.
5. For webhook-triggered builds, add a GitHub/GitLab webhook pointing at
   your Jenkins server, or enable **Poll SCM** on the job.

---

## Configuration

All runtime config is via environment variables (prefix `DIABETES_API_`),
see `app/config.py`:

| Variable | Default | Purpose |
|---|---|---|
| `DIABETES_API_MODEL_PATH` | `models/diabetes_model.pkl` | Path to the trained model |
| `DIABETES_API_METADATA_PATH` | `models/metadata.json` | Path to training metadata |
| `DIABETES_API_LOG_LEVEL` | `INFO` | Logging verbosity |
| `DIABETES_API_ENVIRONMENT` | `development` | Free-text environment tag |

---

## Roadmap

- [ ] Model registry / experiment tracking (MLflow) instead of a flat
      `metadata.json`
- [ ] Push built images to a container registry from CI
- [ ] Prometheus metrics endpoint + Grafana dashboard
- [ ] Cloud deployment manifests (ECS/Cloud Run/K8s)
- [ ] Data validation / drift monitoring on incoming requests

---

## Author

Unaid Abdullah — Aspiring MLOps Engineer | Full Stack Developer
