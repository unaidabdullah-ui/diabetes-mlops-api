"""FastAPI application for the Diabetes Prediction API."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app import model as model_module
from app.config import get_settings
from app.logging_config import configure_logging
from app.model import ModelNotLoadedError, ModelService
from app.schemas import DiabetesInput, HealthResponse, PredictionResponse

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Re-read settings here (rather than relying on the module-level
    # `settings`) so tests that patch env vars and clear the settings
    # cache pick up a fresh model_path/metadata_path per TestClient.
    current_settings = get_settings()
    service = ModelService(current_settings.model_path, current_settings.metadata_path)
    try:
        service.load()
    except FileNotFoundError as exc:
        # Fail loudly in logs but let the app start so /health can report
        # the problem instead of the container crash-looping silently.
        logger.error("Startup model load failed: %s", exc)
    model_module.model_service = service
    yield
    model_module.model_service = None


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


@app.get("/", tags=["meta"])
def read_root():
    return {"message": f"{settings.app_name} is live", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health():
    service = model_module.model_service
    loaded = bool(service and service.is_loaded)
    return HealthResponse(
        status="ok" if loaded else "degraded",
        model_loaded=loaded,
        model_version=service.version if loaded else None,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(data: DiabetesInput):
    service = model_module.model_service
    if service is None or not service.is_loaded:
        raise HTTPException(status_code=503, detail="Model is not loaded. Check /health.")

    try:
        diabetic, probability = service.predict(data.model_dump())
    except ModelNotLoadedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        logger.exception("Prediction failed for input=%s", data.model_dump())
        raise HTTPException(status_code=500, detail="Prediction failed.") from None

    logger.info("Prediction served: diabetic=%s probability=%.4f", diabetic, probability)
    return PredictionResponse(diabetic=diabetic, probability=probability, model_version=service.version)
