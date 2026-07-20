"""
schemas.py — Pydantic request/response models for the prediction API.

The default schema matches the Iris dataset used in the demo pipeline.
Adapt these models when switching to a different dataset or task.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Input features for a single prediction."""
    sepal_length: float = Field(..., ge=0, description="Sepal length in cm")
    sepal_width: float = Field(..., ge=0, description="Sepal width in cm")
    petal_length: float = Field(..., ge=0, description="Petal length in cm")
    petal_width: float = Field(..., ge=0, description="Petal width in cm")


class PredictResponse(BaseModel):
    """Prediction result."""
    prediction: int = Field(..., description="Predicted class index")
    label: str = Field(..., description="Human-readable class label")
    confidence: float | None = Field(None, description="Prediction probability (if available)")
    model_version: str = Field(..., description="Currently loaded model file name")


class BatchPredictRequest(BaseModel):
    """Multiple prediction inputs."""
    instances: list[PredictRequest]


class BatchPredictResponse(BaseModel):
    """Multiple prediction results."""
    predictions: list[PredictResponse]


class HealthResponse(BaseModel):
    service: str
    status: str
    model_loaded: bool
    model_version: str | None
