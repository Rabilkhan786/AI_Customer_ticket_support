"""Handle natural-language database queries."""

import logging

import sqlglot
from sqlglot import exp

from src.database import TABLE_NAME, execute_query
from src.anomaly_service import detect_resolution_anomalies
from src.llm import generate_sql


logger = logging.getLogger(__name__)


def validate_sql(sql: str) -> None:
    """Validate LLM-generated SQL before execution."""

    statements = sqlglot.parse(sql, read="sqlite")

    if len(statements) != 1:
        raise ValueError("Only one SQL statement is allowed.")

    statement = statements[0]

    if not isinstance(statement, exp.Select):
        raise ValueError("Only SELECT queries are allowed.")

    for table in statement.find_all(exp.Table):
        if table.name != TABLE_NAME:
            raise ValueError(
                f"Invalid table: {table.name}"
            )

def is_resolution_anomaly_question(question: str) -> bool:
    """Check whether the question asks about resolution-time anomalies."""

    text = question.lower()

    return "anomal" in text and "resolution" in text


def answer_question(question: str) -> dict:
    """Answer a natural-language question."""

    if is_resolution_anomaly_question(question):
        anomalies = detect_resolution_anomalies()

        return {
            "question": question,
            "sql": None,
            "explanation": (
                "Resolution-time anomalies were detected "
                "using the IQR method."
            ),
            "data": anomalies.to_dict(orient="records"),
        }

    llm_result = generate_sql(question)

    sql = llm_result.get("sql")
    explanation = llm_result.get("explanation", "")

    if not sql:
        return {
            "question": question,
            "sql": None,
            "explanation": explanation,
            "data": [],
        }

    validate_sql(sql)

    data = execute_query(sql)

    logger.info(
        "Query executed successfully. Returned %d rows.",
        len(data),
    )

    return {
        "question": question,
        "sql": sql,
        "explanation": explanation,
        "data": data,
    }