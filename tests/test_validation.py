
import sqlite3
import os
import pytest

DB_PATH = "data/academic_support.db"


@pytest.fixture
def connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()


def test_database_exists():
    assert os.path.exists(DB_PATH)


def test_expected_record_counts(connection):
    expected = {
        "Role": 3,
        "Requester": 500,
        "Term": 3,
        "Category": 6,
        "Ticket": 5000,
        "Assignment": 5000,
        "SLA": 5000,
        "Message": 20000,
        "PolicyDocument": 200,
        "KnowledgeArticle": 200,
    }

    cursor = connection.cursor()

    for table, count in expected.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        actual = cursor.fetchone()[0]
        assert actual == count, (
            f"{table}: expected {count}, found {actual}"
        )


def test_foreign_key_integrity(connection):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_key_check")
    assert cursor.fetchall() == []


def test_ticket_status_values(connection):
    allowed = {
        "open",
        "assigned",
        "in_progress",
        "escalated",
        "resolved",
        "closed",
    }

    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT status FROM Ticket")
    actual = {row[0] for row in cursor.fetchall()}

    assert actual.issubset(allowed)


def test_ticket_priority_values(connection):
    allowed = {"low", "medium", "high", "urgent"}

    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT priority FROM Ticket")
    actual = {row[0] for row in cursor.fetchall()}

    assert actual.issubset(allowed)


def test_policy_codes_are_unique(connection):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT policy_code, COUNT(*)
        FROM PolicyDocument
        GROUP BY policy_code
        HAVING COUNT(*) > 1
    """)

    assert cursor.fetchall() == []


def test_article_codes_are_unique(connection):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT article_code, COUNT(*)
        FROM KnowledgeArticle
        GROUP BY article_code
        HAVING COUNT(*) > 1
    """)

    assert cursor.fetchall() == []


def test_ticket_required_fields(connection):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM Ticket
        WHERE subject IS NULL
           OR description IS NULL
           OR created_at IS NULL
           OR priority IS NULL
           OR status IS NULL
    """)

    assert cursor.fetchone()[0] == 0


def test_message_required_fields(connection):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM Message
        WHERE message_text IS NULL
           OR sent_at IS NULL
    """)

    assert cursor.fetchone()[0] == 0
