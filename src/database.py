
import sqlite3
from pathlib import Path

# Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "academic_support.db"


def get_connection():
    """Create a database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables():
    """Create all required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    schema = [

        # 1. Role table
        """
        CREATE TABLE IF NOT EXISTS Role (
            role_id INTEGER PRIMARY KEY,
            role_name TEXT NOT NULL UNIQUE
        )
        """,

        # 2. Requester table
        """
        CREATE TABLE IF NOT EXISTS Requester (
            requester_id INTEGER PRIMARY KEY,
            requester_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role_id INTEGER NOT NULL,
            department TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (role_id) REFERENCES Role(role_id)
        )
        """,

        # 3. Term table
        """
        CREATE TABLE IF NOT EXISTS Term (
            term_id INTEGER PRIMARY KEY,
            term_name TEXT NOT NULL UNIQUE,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            CHECK (end_date >= start_date)
        )
        """,

        # 4. PolicyDocument table
        """
        CREATE TABLE IF NOT EXISTS PolicyDocument (
            policy_id INTEGER PRIMARY KEY,
            policy_code TEXT NOT NULL,
            title TEXT NOT NULL,
            version INTEGER NOT NULL,
            effective_from TEXT NOT NULL,
            effective_to TEXT,
            policy_content TEXT NOT NULL,
            status TEXT NOT NULL
                CHECK (status IN ('active', 'expired', 'draft')),
            source_url TEXT,
            UNIQUE(policy_code, version),
            CHECK (
                effective_to IS NULL
                OR effective_to >= effective_from
            )
        )
        """,

        # 5. Category table
        """
        CREATE TABLE IF NOT EXISTS Category (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT NOT NULL UNIQUE,
            description TEXT,
            assigned_team TEXT NOT NULL
        )
        """,

        # 6. KnowledgeArticle table
        """
        CREATE TABLE IF NOT EXISTS KnowledgeArticle (
            article_id INTEGER PRIMARY KEY,
            policy_id INTEGER,
            article_code TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            version INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (policy_id)
                REFERENCES PolicyDocument(policy_id)
        )
        """,

        # 7. Ticket table
        """
        CREATE TABLE IF NOT EXISTS Ticket (
            ticket_id TEXT PRIMARY KEY,
            requester_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            term_id INTEGER,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL
                CHECK (priority IN (
                    'low', 'medium', 'high', 'urgent'
                )),
            status TEXT NOT NULL
                CHECK (status IN (
                    'open', 'assigned', 'in_progress',
                    'escalated', 'resolved', 'closed'
                )),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            resolved_at TEXT,
            FOREIGN KEY (requester_id)
                REFERENCES Requester(requester_id),
            FOREIGN KEY (category_id)
                REFERENCES Category(category_id),
            FOREIGN KEY (term_id)
                REFERENCES Term(term_id)
        )
        """,

        # 8. Message table
        """
        CREATE TABLE IF NOT EXISTS Message (
            message_id TEXT PRIMARY KEY,
            ticket_id TEXT NOT NULL,
            sender_id INTEGER,
            message_text TEXT NOT NULL,
            sent_at TEXT NOT NULL,
            FOREIGN KEY (ticket_id)
                REFERENCES Ticket(ticket_id),
            FOREIGN KEY (sender_id)
                REFERENCES Requester(requester_id)
        )
        """,

        # 9. Assignment table
        """
        CREATE TABLE IF NOT EXISTS Assignment (
            assignment_id INTEGER PRIMARY KEY,
            ticket_id TEXT NOT NULL,
            assigned_team TEXT NOT NULL,
            assigned_by INTEGER,
            assigned_at TEXT NOT NULL,
            assignment_status TEXT NOT NULL
                CHECK (assignment_status IN (
                    'active', 'completed', 'reassigned'
                )),
            FOREIGN KEY (ticket_id)
                REFERENCES Ticket(ticket_id),
            FOREIGN KEY (assigned_by)
                REFERENCES Requester(requester_id)
        )
        """,

        # 10. SLA table
        """
        CREATE TABLE IF NOT EXISTS SLA (
            sla_id INTEGER PRIMARY KEY,
            ticket_id TEXT NOT NULL,
            response_due TEXT NOT NULL,
            resolution_due TEXT NOT NULL,
            response_at TEXT,
            resolved_at TEXT,
            sla_status TEXT NOT NULL
                CHECK (sla_status IN (
                    'within_sla', 'breached', 'met', 'pending'
                )),
            FOREIGN KEY (ticket_id)
                REFERENCES Ticket(ticket_id)
        )
        """,

        # 11. ResolutionFeedback table
        """
        CREATE TABLE IF NOT EXISTS ResolutionFeedback (
            feedback_id INTEGER PRIMARY KEY,
            ticket_id TEXT NOT NULL UNIQUE,
            resolution_notes TEXT NOT NULL,
            rating INTEGER CHECK (
                rating IS NULL OR rating BETWEEN 1 AND 5
            ),
            feedback_comment TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (ticket_id)
                REFERENCES Ticket(ticket_id)
        )
        """
    ]

    try:
        for statement in schema:
            cursor.execute(statement)

        # Useful database indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticket_requester
            ON Ticket(requester_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticket_category
            ON Ticket(category_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_message_ticket
            ON Message(ticket_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_policy_code
            ON PolicyDocument(policy_code)
        """)

        connection.commit()
        print("Database and tables created successfully!")

    except sqlite3.Error as error:
        connection.rollback()
        print("Database error:", error)
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()

    connection = get_connection()
    cursor = connection.cursor()

    tables = cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    for (table_name,) in tables:
        print(f"\n{table_name}:")
        columns = cursor.execute(
            f"PRAGMA table_info([{table_name}])"
        ).fetchall()

        for column in columns:
            print(" -", column[1])

    connection.close()