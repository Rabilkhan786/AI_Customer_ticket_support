
import pytest

from src.query_service import validate_sql


def test_valid_select_query():
    sql = "SELECT * FROM support_tickets LIMIT 5;"

    validate_sql(sql)


def test_reject_delete_query():
    sql = "DELETE FROM support_tickets;"

    with pytest.raises(ValueError):
        validate_sql(sql)


def test_reject_unknown_table():
    sql = "SELECT * FROM users;"

    with pytest.raises(ValueError):
        validate_sql(sql)