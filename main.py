"""FastAPI application for the support ticket system."""

import json
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.anomaly_service import (
    detect_priority_anomalies,
    detect_resolution_anomalies,
)
from src.database import initialize_database
from src.logging_config import setup_logging
from src.query_service import answer_question


setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Support Ticket Intelligence",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    """Natural-language query request."""

    question: str


@app.on_event("startup")
def startup_event() -> None:
    """Initialize the database when the application starts."""

    initialize_database()
    logger.info("Application started successfully.")


@app.get("/health")
def health_check() -> dict:
    """Check whether the API is running."""

    return {"status": "healthy"}


@app.post("/query")
def query_tickets(request: QueryRequest) -> dict:
    """Answer a natural-language question about support tickets."""

    try:
        return answer_question(request.question)

    except Exception as error:
        logger.exception("Failed to process query.")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@app.get("/anomalies")
def get_anomalies() -> dict:
    """Return detected support ticket anomalies."""

    try:
        resolution_df = detect_resolution_anomalies()
        priority_df = detect_priority_anomalies()

        resolution_anomalies = json.loads(
            resolution_df.to_json(
                orient="records",
                date_format="iso",
            )
        )

        priority_anomalies = json.loads(
            priority_df.to_json(
                orient="records",
                date_format="iso",
            )
        )

        return {
            "resolution_time_anomalies": resolution_anomalies,
            "priority_anomalies": priority_anomalies,
        }

    except Exception as error:
        logger.exception("Failed to detect anomalies.")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error