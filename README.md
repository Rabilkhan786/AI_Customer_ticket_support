# AI Support Ticket Intelligence

AI-powered customer support ticket analysis system built for the AI Engineer assessment.

The system can:

- Answer natural-language questions about support ticket data.
- Convert user questions into SQL using an LLM.
- Validate generated SQL before execution.
- Detect abnormal resolution times.
- Detect unresolved High/Critical tickets older than 24 hours.
- Expose the functionality through FastAPI and Streamlit.

## Architecture

```text
User
  ↓
Streamlit UI
  ↓
FastAPI
  ↓
┌─────────────────────┬─────────────────────┐
│                     │                     │
Query Service         Anomaly Service
│                     │
↓                     │
Groq LLM              │
│                     │
↓                     │
SQL Generation        │
│                     │
↓                     │
SQL Validation        │
│                     │
└──────────┬──────────┘
           ↓
         SQLite
           ↓
   support_tickets.csv
```

### Query Flow

```text
Natural-language question
        ↓
LLM generates SQL
        ↓
SQL is validated
        ↓
SQLite executes query
        ↓
Result returned to user
```

The LLM does not calculate the final answer itself. It generates SQL, while SQLite produces the actual result.

## Anomaly Detection

The system detects two anomaly types.

### Long Resolution Time

Resolved tickets are checked using the IQR method:

```text
IQR = Q3 - Q1

Upper Limit = Q3 + 1.5 × IQR
```

Tickets above the upper limit are flagged.

### Unresolved Priority Tickets

A ticket is flagged when:

```text
Priority = High or Critical
Status != Resolved
Ticket age > 24 hours
```

Because the dataset is historical, ticket age is calculated relative to the latest timestamp in the dataset.

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| Data Processing | Pandas |
| Database | SQLite |
| LLM | Groq |
| SQL Validation | SQLGlot |
| API | FastAPI |
| UI | Streamlit |
| Testing | Pytest |
| Logging | Python Logging |
| Containerization | Docker Compose |

## API Endpoints

```text
GET  /health
POST /query
GET  /anomalies
```

FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

## Example Query

Question:

```text
How many tickets are currently open?
```

Generated SQL:

```sql
SELECT COUNT(*) AS open_ticket_count
FROM support_tickets
WHERE status = 'Open';
```

Result:

```json
{
  "open_ticket_count": 111
}
```

Example complex question:

```text
Among High and Critical priority tickets,
which agent resolved the most tickets,
and what was that agent's average resolution time
and average customer rating?
```

## Running the Project

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_model_name
```

Start the complete application:

```bash
docker compose up --build
```

Open:

```text
Streamlit UI:
http://localhost:8501

Swagger API:
http://localhost:8000/docs
```

## Project Structure

```text
AI_Customer_ticket_support/
│
├── src/
│   ├── config.py
│   ├── logging_config.py
│   ├── database.py
│   ├── llm.py
│   ├── query_service.py
│   └── anomaly_service.py
│
├── config/
│   └── config.yaml
│
├── data/
│   └── support_tickets.csv
│
├── tests/
├── main.py
├── ui.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Known Limitations

The system only answers questions supported by the provided dataset schema.

For example:

```text
Which city has the most tickets?
```

cannot be answered because the dataset does not contain location information.

LLM-generated SQL may also be incorrect for highly ambiguous questions, so generated queries are validated before execution.

## Summary

This project focuses on four main requirements:

```text
CSV → Queryable Database
          ↓
Natural Language → SQL
          ↓
Anomaly Detection
          ↓
FastAPI + Streamlit
```

The architecture is intentionally simple so the system remains easy to run, test, and explain.