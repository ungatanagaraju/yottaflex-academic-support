
import sqlite3

DB_PATH = "data/academic_support.db"


def route_ticket(ticket_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Find ticket and its assigned support team
        cursor.execute("""
            SELECT t.ticket_id, t.status, c.assigned_team
            FROM Ticket t
            JOIN Category c
                ON t.category_id = c.category_id
            WHERE t.ticket_id = ?
        """, (ticket_id,))

        ticket = cursor.fetchone()

        if ticket is None:
            print(f"Ticket {ticket_id} not found.")
            return False

        _, current_status, assigned_team = ticket

        if current_status in ("resolved", "closed"):
            print(f"Cannot assign ticket {ticket_id}: it is {current_status}.")
            return False

        # Check for an existing active assignment
        cursor.execute("""
            SELECT assignment_id
            FROM Assignment
            WHERE ticket_id = ?
              AND assignment_status = 'active'
        """, (ticket_id,))

        if cursor.fetchone():
            print(f"Ticket {ticket_id} already has an active assignment.")
            return False

        # Use the first requester as the assignment actor.
        # This is a placeholder until a staff table is implemented.
        cursor.execute("""
            SELECT requester_id
            FROM Requester
            ORDER BY requester_id
            LIMIT 1
        """)

        actor = cursor.fetchone()

        if actor is None:
            print("No requester available for assignment.")
            return False

        cursor.execute("""
            INSERT INTO Assignment (
                ticket_id,
                assigned_team,
                assigned_by,
                assigned_at,
                assignment_status
            )
            VALUES (?, ?, ?, datetime('now'), 'active')
        """, (ticket_id, assigned_team, actor[0]))

        cursor.execute("""
            UPDATE Ticket
            SET status = 'assigned',
                updated_at = datetime('now')
            WHERE ticket_id = ?
        """, (ticket_id,))

        conn.commit()

        print(f"Ticket {ticket_id} assigned to {assigned_team}.")
        return True

    except sqlite3.Error as error:
        conn.rollback()
        print("Database error:", error)
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    ticket_id = input("Enter ticket ID (example: TKT-00001): ").strip()
    route_ticket(ticket_id)
