"""Request/response models for the prediction API.

Field constraints reflect physiologically plausible ranges for the Pima
Indians Diabetes dataset so obviously bad input is rejected with a 422
before it ever reaches the model.
"""
from pydantic import BaseModel, Field


class DiabetesInput(BaseModel):
    Pregnancies: int = Field(..., ge=0, le=20, description="Number of times pregnant")
    Glucose: float = Field(..., gt=0, le=300, description="Plasma glucose concentration (mg/dL)")
    BloodPressure: float = Field(..., gt=0, le=200, description="Diastolic blood pressure (mm Hg)")
    BMI: float = Field(..., gt=0, le=80, description="Body mass index")
    Age: int = Field(..., ge=1, le=120, description="Age in years")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "Pregnancies": 2,
                    "Glucose": 130,
                    "BloodPressure": 70,
                    "BMI": 28.5,
                    "Age": 45,
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    diabetic: bool
    probability: float = Field(..., description="Predicted probability of the positive class")
    model_version: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str | None = None
