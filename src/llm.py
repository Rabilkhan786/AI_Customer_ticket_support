
"""Generate SQL queries from natural-language questions."""

import json
import logging

from groq import Groq

from src.config import GROQ_API_KEY, GROQ_MODEL, settings


logger = logging.getLogger(__name__)


def generate_sql(question: str) -> dict:
    """Convert a natural-language question into SQL."""

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured.")

    if not GROQ_MODEL:
        raise ValueError("GROQ_MODEL is not configured.")

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You convert user questions into SQLite queries.

Database table:
support_tickets

Columns:
- ticket_id
- created_at
- category
- priority
- status
- response_time_hrs
- resolution_time_hrs
- agent_id
- customer_rating
- issue_summary

Allowed category values:
Billing, Technical, General

Allowed priority values:
Low, Medium, High, Critical

Allowed status values:
Open, Resolved, Escalated

Rules:
1. Generate only SELECT queries.
2. Use only the support_tickets table.
3. Do not modify the database.
4. Use SQLite syntax.
5. Limit row-returning queries to {settings["query"]["max_rows"]} rows.
6. If the question cannot be answered using these columns,
   return null for sql.
7. Respond only as JSON.

Return this format:
{{
    "sql": "SQL query or null",
    "explanation": "Short explanation"
}}

User question:
{question}
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=settings["llm"]["temperature"],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("LLM returned an empty response.")

    result = json.loads(content)

    logger.info("SQL generated successfully for user question.")

    return result