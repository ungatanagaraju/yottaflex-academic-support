
import random
from datetime import datetime, timedelta

from faker import Faker
from src.database import get_connection


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

fake = Faker()
Faker.seed(42)
random.seed(42)


# --------------------------------------------------
# 1. GENERATE ROLES
# --------------------------------------------------

def generate_roles(cursor):
    print("Generating roles...")

    roles = ["Student", "Faculty", "Support Agent"]

    for role in roles:
        cursor.execute(
            "INSERT INTO Role (role_name) VALUES (?)",
            (role,)
        )

    print("3 roles generated.")


# --------------------------------------------------
# 2. GENERATE REQUESTERS
# --------------------------------------------------

def generate_requesters(cursor, count=500):
    print(f"Generating {count} requesters...")

    roles = cursor.execute(
        "SELECT role_id FROM Role"
    ).fetchall()

    if not roles:
        raise ValueError("Roles must be generated first.")

    departments = [
        "Computer Science",
        "Engineering",
        "Business",
        "Arts",
        "Science"
    ]

    for _ in range(count):
        role_id = random.choice(roles)[0]

        cursor.execute("""
            INSERT INTO Requester (
                requester_name,
                email,
                role_id,
                department,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            fake.name(),
            fake.unique.email(),
            role_id,
            random.choice(departments),
            fake.date_time_this_year().isoformat()
        ))

    print(f"{count} requesters generated.")


# --------------------------------------------------
# 3. GENERATE TERMS
# --------------------------------------------------

def generate_terms(cursor):
    print("Generating academic terms...")

    terms = [
        ("Fall 2026", "2026-08-01", "2026-12-31"),
        ("Spring 2027", "2027-01-01", "2027-05-31"),
        ("Summer 2027", "2027-06-01", "2027-07-31")
    ]

    for term in terms:
        cursor.execute("""
            INSERT INTO Term (
                term_name,
                start_date,
                end_date
            )
            VALUES (?, ?, ?)
        """, term)

    print("3 academic terms generated.")


# --------------------------------------------------
# 4. GENERATE CATEGORIES
# --------------------------------------------------

def generate_categories(cursor):
    print("Generating categories...")

    categories = [
        ("Admissions", "Admission-related questions", "Admissions Team"),
        ("Financial Aid", "Scholarship and fee questions", "Finance Team"),
        ("Registration", "Course registration issues", "Academic Team"),
        ("Technical Support", "Technical problems", "IT Team"),
        ("Examinations", "Exam-related questions", "Exam Team"),
        ("Academic Records", "Academic records requests", "Records Team")
    ]

    for category in categories:
        cursor.execute("""
            INSERT INTO Category (
                category_name,
                description,
                assigned_team
            )
            VALUES (?, ?, ?)
        """, category)

    print("6 categories generated.")


# --------------------------------------------------
# 5. GENERATE TICKETS
# --------------------------------------------------

def generate_tickets(cursor, count=5000):
    print(f"Generating {count} tickets...")

    requesters = [
        row[0] for row in cursor.execute(
            "SELECT requester_id FROM Requester"
        ).fetchall()
    ]

    categories = [
        row[0] for row in cursor.execute(
            "SELECT category_id FROM Category"
        ).fetchall()
    ]

    terms = [
        row[0] for row in cursor.execute(
            "SELECT term_id FROM Term"
        ).fetchall()
    ]

    if not requesters or not categories or not terms:
        raise ValueError(
            "Requesters, categories and terms are required."
        )

    priorities = ["low", "medium", "high", "urgent"]

    statuses = [
        "open",
        "assigned",
        "in_progress",
        "escalated",
        "resolved",
        "closed"
    ]

    for i in range(count):

        created = fake.date_time_between(
            start_date="-180d",
            end_date="now"
        )

        updated = created + timedelta(
            minutes=random.randint(5, 1440)
        )

        status = random.choice(statuses)

        resolved_at = None

        if status in ["resolved", "closed"]:
            resolved_at = updated.isoformat()

        cursor.execute("""
            INSERT INTO Ticket (
                ticket_id,
                requester_id,
                category_id,
                term_id,
                subject,
                description,
                priority,
                status,
                created_at,
                updated_at,
                resolved_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"TKT-{i + 1:05d}",
            random.choice(requesters),
            random.choice(categories),
            random.choice(terms),
            fake.sentence(nb_words=6),
            fake.paragraph(nb_sentences=3),
            random.choice(priorities),
            status,
            created.isoformat(),
            updated.isoformat(),
            resolved_at
        ))

    print(f"{count} tickets generated.")


# --------------------------------------------------
# 6. GENERATE ASSIGNMENTS
# --------------------------------------------------

def generate_assignments(cursor):
    print("Generating assignments...")

    tickets = cursor.execute("""
        SELECT
            t.ticket_id,
            c.assigned_team,
            t.status,
            t.created_at
        FROM Ticket t
        JOIN Category c
            ON t.category_id = c.category_id
    """).fetchall()

    agents = [
        row[0] for row in cursor.execute("""
            SELECT r.requester_id
            FROM Requester r
            JOIN Role ro
                ON r.role_id = ro.role_id
            WHERE ro.role_name = 'Support Agent'
        """).fetchall()
    ]

    for ticket_id, team, status, created_at in tickets:

        assignment_status = (
            "completed"
            if status in ["resolved", "closed"]
            else "active"
        )

        assigned_by = (
            random.choice(agents) if agents else None
        )

        cursor.execute("""
            INSERT INTO Assignment (
                ticket_id,
                assigned_team,
                assigned_by,
                assigned_at,
                assignment_status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            ticket_id,
            team,
            assigned_by,
            created_at,
            assignment_status
        ))

    print(f"{len(tickets)} assignments generated.")


# --------------------------------------------------
# 7. GENERATE SLA RECORDS
# --------------------------------------------------

def generate_slas(cursor):
    print("Generating SLA records...")

    tickets = cursor.execute("""
        SELECT
            ticket_id,
            priority,
            created_at,
            resolved_at
        FROM Ticket
    """).fetchall()

    # These are synthetic demonstration values,
    # not official institutional SLA policies.

    response_hours = {
        "low": 48,
        "medium": 24,
        "high": 8,
        "urgent": 2
    }

    resolution_hours = {
        "low": 120,
        "medium": 72,
        "high": 24,
        "urgent": 8
    }

    for ticket_id, priority, created_at, resolved_at in tickets:

        created = datetime.fromisoformat(created_at)

        response_due = created + timedelta(
            hours=response_hours[priority]
        )

        resolution_due = created + timedelta(
            hours=resolution_hours[priority]
        )

        response_at = created + timedelta(
            minutes=random.randint(5, 180)
        )

        if resolved_at:
            resolved = datetime.fromisoformat(resolved_at)

            sla_status = (
                "met"
                if resolved <= resolution_due
                else "breached"
            )
        else:
            sla_status = (
                "breached"
                if datetime.now() > resolution_due
                else "pending"
            )

        cursor.execute("""
            INSERT INTO SLA (
                ticket_id,
                response_due,
                resolution_due,
                response_at,
                resolved_at,
                sla_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ticket_id,
            response_due.isoformat(),
            resolution_due.isoformat(),
            response_at.isoformat(),
            resolved_at,
            sla_status
        ))

    print(f"{len(tickets)} SLA records generated.")


# --------------------------------------------------
# 8. GENERATE MESSAGES
# --------------------------------------------------

def generate_messages(cursor, count=20000):
    print(f"Generating {count} messages...")

    existing_count = cursor.execute(
        "SELECT COUNT(*) FROM Message"
    ).fetchone()[0]

    if existing_count > 0:
        print(f"Messages already exist: {existing_count}. Skipping.")
        return

    ticket_ids = [
        row[0] for row in cursor.execute(
            "SELECT ticket_id FROM Ticket"
        ).fetchall()
    ]

    requester_ids = [
        row[0] for row in cursor.execute(
            "SELECT requester_id FROM Requester"
        ).fetchall()
    ]

    if not ticket_ids or not requester_ids:
        raise ValueError("Tickets or requesters are missing.")

    message_templates = [
        "I need help with my academic support request.",
        "Could you please provide an update on my request?",
        "I have attached the required information.",
        "Thank you for your assistance.",
        "I need clarification about the applicable policy.",
        "Please let me know what steps I should follow.",
        "I am still waiting for a resolution.",
        "The issue has been resolved. Thank you.",
        "Could you review my request again?",
        "Please explain the next steps in this process.",
        "I have a question about the application deadline.",
        "My student portal is not working correctly.",
        "Could you check the status of my registration?",
        "I need assistance with my financial aid application.",
        "Please confirm whether my documents were received."
    ]

    messages = []

    for _ in range(count):

        ticket_id = random.choice(ticket_ids)
        sender_id = random.choice(requester_ids)
        message_text = random.choice(message_templates)

        sent_at = fake.date_time_between(
            start_date="-1y",
            end_date="now"
        ).strftime("%Y-%m-%d %H:%M:%S")

        messages.append((
            ticket_id,
            sender_id,
            message_text,
            sent_at
        ))

    cursor.executemany("""
        INSERT INTO Message (
            ticket_id,
            sender_id,
            message_text,
            sent_at
        )
        VALUES (?, ?, ?, ?)
    """, messages)

    print(f"{len(messages)} messages generated.")


# --------------------------------------------------
# 9. GENERATE POLICY DOCUMENTS
# --------------------------------------------------

def generate_policy_documents(cursor, count=200):
    print(f"Generating {count} policy documents...")

    existing_count = cursor.execute(
        "SELECT COUNT(*) FROM PolicyDocument"
    ).fetchone()[0]

    if existing_count > 0:
        print(
            f"Policy documents already exist: {existing_count}. Skipping."
        )
        return

    policy_topics = [
        (
            "Admissions Eligibility",
            "Admission requirements and eligibility criteria."
        ),
        (
            "Financial Aid",
            "Scholarship eligibility and financial assistance procedures."
        ),
        (
            "Course Registration",
            "Course registration rules and deadlines."
        ),
        (
            "Examination Guidelines",
            "Examination procedures and student responsibilities."
        ),
        (
            "Academic Records",
            "Rules for transcripts and academic records."
        ),
        (
            "Student Attendance",
            "Attendance requirements and attendance exemptions."
        ),
        (
            "Fee Payment",
            "Tuition fees, payment schedules and late payment rules."
        ),
        (
            "Technical Support",
            "Student portal and technical support procedures."
        ),
        (
            "Grading Policy",
            "Grading methods and academic performance requirements."
        ),
        (
            "Student Conduct",
            "Student responsibilities and conduct expectations."
        )
    ]

    for i in range(count):

        topic, description = random.choice(policy_topics)

        policy_code = f"POL-{i + 1:04d}"

        cursor.execute("""
            INSERT INTO PolicyDocument (
                policy_code,
                title,
                version,
                effective_from,
                effective_to,
                policy_content,
                status,
                source_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            policy_code,
            topic,
            1,
            "2026-01-01",
            None,
            (
                f"{description} "
                "Students should review the applicable requirements "
                "and contact the relevant academic support team "
                "if they need clarification."
            ),
            "draft",
            None
        ))

    print(f"{count} policy documents generated.")


# --------------------------------------------------
# 10. GENERATE KNOWLEDGE ARTICLES
# --------------------------------------------------

def generate_knowledge_articles(cursor, count=200):
    print(f"Generating {count} knowledge articles...")

    existing_count = cursor.execute(
        "SELECT COUNT(*) FROM KnowledgeArticle"
    ).fetchone()[0]

    if existing_count > 0:
        print(
            f"Knowledge articles already exist: {existing_count}. Skipping."
        )
        return

    policies = cursor.execute("""
        SELECT
            policy_id,
            title,
            policy_content
        FROM PolicyDocument
        ORDER BY policy_id
    """).fetchall()

    if not policies:
        raise ValueError(
            "Policy documents are missing. Generate them first."
        )

    for i in range(count):

        policy_id, policy_title, policy_content = (
            policies[i % len(policies)]
        )

        cursor.execute("""
            INSERT INTO KnowledgeArticle (
                policy_id,
                article_code,
                title,
                content,
                version,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            policy_id,
            f"KB-{i + 1:04d}",
            f"Student Guide: {policy_title}",
            (
                f"Overview: {policy_content} "
                "Steps: Review the requirements, prepare the necessary "
                "information, and submit your request to the appropriate "
                "support team. Contact academic support if further "
                "assistance is required."
            ),
            1,
            datetime.now().isoformat()
        ))

    print(f"{count} knowledge articles generated.")


# --------------------------------------------------
# 11. MAIN DATA GENERATION FUNCTION
# --------------------------------------------------

def generate_data():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Roles
        count = cursor.execute(
            "SELECT COUNT(*) FROM Role"
        ).fetchone()[0]

        if count == 0:
            generate_roles(cursor)
        else:
            print(f"Roles already exist: {count}")

        # Requesters
        count = cursor.execute(
            "SELECT COUNT(*) FROM Requester"
        ).fetchone()[0]

        if count == 0:
            generate_requesters(cursor, 500)
        else:
            print(f"Requesters already exist: {count}")

        # Terms
        count = cursor.execute(
            "SELECT COUNT(*) FROM Term"
        ).fetchone()[0]

        if count == 0:
            generate_terms(cursor)
        else:
            print(f"Terms already exist: {count}")

        # Categories
        count = cursor.execute(
            "SELECT COUNT(*) FROM Category"
        ).fetchone()[0]

        if count == 0:
            generate_categories(cursor)
        else:
            print(f"Categories already exist: {count}")

        # Tickets
        count = cursor.execute(
            "SELECT COUNT(*) FROM Ticket"
        ).fetchone()[0]

        if count == 0:
            generate_tickets(cursor, 5000)
        else:
            print(f"Tickets already exist: {count}")

        # Assignments
        count = cursor.execute(
            "SELECT COUNT(*) FROM Assignment"
        ).fetchone()[0]

        if count == 0:
            generate_assignments(cursor)
        else:
            print(f"Assignments already exist: {count}")

        # SLA records
        count = cursor.execute(
            "SELECT COUNT(*) FROM SLA"
        ).fetchone()[0]

        if count == 0:
            generate_slas(cursor)
        else:
            print(f"SLA records already exist: {count}")

        # Messages
        count = cursor.execute(
            "SELECT COUNT(*) FROM Message"
        ).fetchone()[0]

        if count == 0:
            generate_messages(cursor, 20000)
        else:
            print(f"Messages already exist: {count}")

        # Policy documents
        count = cursor.execute(
            "SELECT COUNT(*) FROM PolicyDocument"
        ).fetchone()[0]

        if count == 0:
            generate_policy_documents(cursor, 200)
        else:
            print(f"Policy documents already exist: {count}")

        # Knowledge articles
        count = cursor.execute(
            "SELECT COUNT(*) FROM KnowledgeArticle"
        ).fetchone()[0]

        if count == 0:
            generate_knowledge_articles(cursor, 200)
        else:
            print(f"Knowledge articles already exist: {count}")

        # Save all generated records
        connection.commit()

        print("\nDATA GENERATION COMPLETED!")

        # Display final counts
        tables = [
            "Role",
            "Requester",
            "Term",
            "Category",
            "Ticket",
            "Assignment",
            "SLA",
            "Message",
            "PolicyDocument",
            "KnowledgeArticle"
        ]

        print("\nFINAL RECORD COUNTS")

        total_records = 0

        for table in tables:

            count = cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            total_records += count

            print(f"{table}: {count}")

        print("-" * 35)
        print(f"TOTAL RECORDS: {total_records}")

    except Exception as error:

        connection.rollback()

        print("\nDATA GENERATION FAILED!")
        print("Error:", error)

        raise

    finally:
        connection.close()


# --------------------------------------------------
# 12. PROGRAM ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    print("Starting data generator...")
    generate_data()
