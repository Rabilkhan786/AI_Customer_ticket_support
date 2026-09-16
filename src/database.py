"""Database setup and query functions."""

import logging
import sqlite3

import pandas as pd

from src.config import PROJECT_ROOT, settings


logger = logging.getLogger(__name__)

## Define the path 

CSV_PATH = PROJECT_ROOT / settings["data"]["csv_path"]
DATABASE_PATH = PROJECT_ROOT / settings["data"]["database_path"]

TABLE_NAME = "support_tickets"


REQUIRED_COLUMNS = [
    "ticket_id",
    "created_at",
    "category",
    "priority",
    "status",
    "response_time_hrs",
    "resolution_time_hrs",
    "agent_id",
    "customer_rating",
    "issue_summary",
]


## Load the dataset into pandas 

def load_dataset() -> pd.DataFrame:
    """Load and validate the support ticket dataset."""

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df["ticket_id"].duplicated().any():
        raise ValueError("Duplicate ticket IDs found.")

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="raise",
    )

    logger.info(
        "Dataset loaded successfully with %d rows.",
        len(df),
    )

    return df

## Take the data and store into sqllite

def initialize_database() -> None:
    """Load the dataset into the SQLite database."""

    df = load_dataset()

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        df.to_sql(
            TABLE_NAME,
            connection,
            if_exists="replace",
            index=False,
        )

    logger.info(
        "Loaded %d tickets into the database.",
        len(df),
    )


def execute_query(sql: str) -> list[dict]:
    """Execute a SQL query and return the results."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        cursor = connection.execute(sql)
        rows = cursor.fetchall()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    from src.logging_config import setup_logging

    setup_logging()
    initialize_database()