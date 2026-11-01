
import sqlite3
from datetime import date

DB_PATH = "data/academic_support.db"


def get_active_policies():
    """Display policies that are currently active and effective."""

    with sqlite3.connect(DB_PATH) as conn:
        today = date.today().isoformat()

        policies = conn.execute("""
            SELECT policy_id, policy_code, title, version,
                   effective_from, effective_to
            FROM PolicyDocument
            WHERE status = 'active'
              AND effective_from <= ?
              AND (effective_to IS NULL OR effective_to >= ?)
            ORDER BY policy_code
        """, (today, today)).fetchall()

    print(f"\nActive policies found: {len(policies)}")

    for policy in policies:
        print(f"{policy[1]} - {policy[2]} (Version {policy[3]})")

    return policies


def get_policy_by_code(policy_code):
    """Find a policy and clearly show its current status."""

    with sqlite3.connect(DB_PATH) as conn:
        policy = conn.execute("""
            SELECT policy_code, title, version, effective_from,
                   effective_to, policy_content, status
            FROM PolicyDocument
            WHERE policy_code = ?
            ORDER BY version DESC
            LIMIT 1
        """, (policy_code,)).fetchone()

    if policy is None:
        print(f"\nPolicy not found: {policy_code}")
        return None

    code, title, version, start, end, content, status = policy

    print(f"\nPolicy: {title}")
    print(f"Code: {code}")
    print(f"Version: {version}")
    print(f"Status: {status}")
    print(f"Effective from: {start}")
    print(f"Effective to: {end or 'Not specified'}")

    if status == "draft":
        print("Notice: This is a draft policy, not an active policy.")
    elif status != "active":
        print("Notice: This policy is not active.")
    else:
        today = date.today().isoformat()
        if start <= today and (end is None or end >= today):
            print("Policy is currently effective.")
        else:
            print("Policy is active but outside its effective date range.")

    print(f"\nContent:\n{content}")

    return policy


if __name__ == "__main__":
    get_active_policies()

    code = input("\nEnter policy code (example: POL-0001): ").strip()
    get_policy_by_code(code)
