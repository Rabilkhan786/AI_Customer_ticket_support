
"""Anomaly detection for support tickets."""

import logging
import sqlite3

import pandas as pd

from src.config import settings
from src.database import DATABASE_PATH


logger = logging.getLogger(__name__)

IQR_MULTIPLIER = settings["anomaly"]["iqr_multiplier"]
UNRESOLVED_HOURS = settings["anomaly"]["unresolved_hours"]


def detect_resolution_anomalies() -> pd.DataFrame:
    """Detect tickets with unusually long resolution times."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        df = pd.read_sql_query(
            """
            SELECT
                ticket_id,
                priority,
                status,
                resolution_time_hrs,
                agent_id
            FROM support_tickets
            WHERE resolution_time_hrs IS NOT NULL
            """,
            connection,
        )

    q1 = df["resolution_time_hrs"].quantile(0.25)
    q3 = df["resolution_time_hrs"].quantile(0.75)

    iqr = q3 - q1
    upper_limit = q3 + (IQR_MULTIPLIER * iqr)

    anomalies = df[
        df["resolution_time_hrs"] > upper_limit
    ].copy()

    anomalies["anomaly_type"] = "long_resolution_time"

    logger.info(
        "Detected %d long resolution-time anomalies.",
        len(anomalies),
    )

    return anomalies


def detect_priority_anomalies() -> pd.DataFrame:
    """Detect old unresolved High and Critical tickets."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        df = pd.read_sql_query(
            """
            SELECT
                ticket_id,
                created_at,
                priority,
                status,
                agent_id
            FROM support_tickets
            """,
            connection,
        )

    df["created_at"] = pd.to_datetime(df["created_at"])

    snapshot_time = df["created_at"].max()

    df["ticket_age_hours"] = (
        snapshot_time - df["created_at"]
    ).dt.total_seconds() / 3600

    anomalies = df[
        (df["status"] != "Resolved")
        & (df["priority"].isin(["High", "Critical"]))
        & (df["ticket_age_hours"] > UNRESOLVED_HOURS)
    ].copy()

    anomalies["anomaly_type"] = "unresolved_priority_ticket"

    logger.info(
        "Detected %d unresolved priority anomalies.",
        len(anomalies),
    )

    return anomalies