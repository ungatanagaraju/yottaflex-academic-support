
import sqlite3


DB_PATH = "data/academic_support.db"


def validate_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    errors = []
    results = []

    # 1. Check foreign keys
    cursor.execute("PRAGMA foreign_key_check")
    foreign_errors = cursor.fetchall()

    if foreign_errors:
        errors.append(f"Foreign key violations: {foreign_errors[:10]}")
    else:
        results.append("Foreign key check passed")

    # 2. Check expected record counts
    expected_counts = {
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

    for table, expected in expected_counts.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        actual = cursor.fetchone()[0]

        if actual == expected:
            results.append(f"{table}: PASSED ({actual})")
        else:
            errors.append(
                f"{table}: Expected {expected}, found {actual}"
            )

    # 3. Check duplicate policy codes
    cursor.execute("""
        SELECT policy_code
        FROM PolicyDocument
        GROUP BY policy_code
        HAVING COUNT(*) > 1
    """)

    if cursor.fetchall():
        errors.append("Duplicate policy codes found")
    else:
        results.append("Policy code uniqueness passed")

    # 4. Check duplicate article codes
    cursor.execute("""
        SELECT article_code
        FROM KnowledgeArticle
        GROUP BY article_code
        HAVING COUNT(*) > 1
    """)

    if cursor.fetchall():
        errors.append("Duplicate article codes found")
    else:
        results.append("Article code uniqueness passed")

    # 5. Check ticket status values
    cursor.execute("""
        SELECT status, COUNT(*)
        FROM Ticket
        GROUP BY status
    """)

    status_counts = cursor.fetchall()
    total_status_records = sum(count for _, count in status_counts)

    if total_status_records == 5000:
        results.append("Ticket status distribution check passed")
    else:
        errors.append("Ticket status count does not equal 5000")

    conn.close()

    print("\nDATABASE VALIDATION RESULTS")
    print("=" * 40)

    for result in results:
        print("[PASS]", result)

    for error in errors:
        print("[FAIL]", error)

    print("=" * 40)

    if errors:
        print("VALIDATION FAILED")
        return False

    print("ALL VALIDATIONS PASSED")
    return True


if __name__ == "__main__":
    validate_database()
