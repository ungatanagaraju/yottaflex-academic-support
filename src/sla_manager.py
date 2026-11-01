import sqlite3
from datetime import datetime

from src.database import DB_PATH


def check_sla(ticket_id):
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                response_due,
                resolution_due,
                response_at,
                resolved_at,
                sla_status
            FROM SLA
            WHERE ticket_id = ?
        """, (ticket_id,))

        sla = cursor.fetchone()
        connection.close()

        if sla is None:
            print(f"No SLA record found for {ticket_id}.")
            return

        response_due, resolution_due, response_at, resolved_at, sla_status = sla

        now = datetime.now()

        print(f"\nSLA Report for {ticket_id}")
        print("-" * 40)

        if response_at:
            print("Response: Completed")
        elif datetime.fromisoformat(response_due) < now:
            print("Response: BREACHED")
        else:
            print("Response: Within deadline")

        if resolved_at:
            print("Resolution: Completed")
        elif datetime.fromisoformat(resolution_due) < now:
            print("Resolution: BREACHED")
        else:
            print("Resolution: Within deadline")

        print(f"Stored SLA Status: {sla_status}")

    except (sqlite3.Error, ValueError, TypeError) as error:
        print(f"Error checking SLA: {error}")


if __name__ == "__main__":
    ticket_id = input("Enter Ticket ID (example: TKT-00001): ").strip()
    check_sla(ticket_id)