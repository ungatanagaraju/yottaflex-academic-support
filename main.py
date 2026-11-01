
from src.database import create_tables, get_connection

# Create database tables
create_tables()

# Connect to database
connection = get_connection()

cursor = connection.cursor()

# Get all database tables
cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    AND name NOT LIKE 'sqlite_%'
    ORDER BY name
""")

tables = cursor.fetchall()

print("\nDATABASE TABLES")

for table in tables:
    print("-", table[0])

connection.close()
