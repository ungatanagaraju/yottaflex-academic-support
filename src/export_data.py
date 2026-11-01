
import sqlite3
import pandas as pd
import json
import os

DB_PATH = "data/academic_support.db"
CSV_DIR = "outputs/csv"
JSON_DIR = "outputs/json"

TABLES = [
    "Role",
    "Requester",
    "Term",
    "Category",
    "Ticket",
    "Assignment",
    "SLA",
    "Message",
    "PolicyDocument",
    "KnowledgeArticle",
]


def export_data():
    os.makedirs(CSV_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    for table in TABLES:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)

        # Export CSV
        csv_path = os.path.join(CSV_DIR, f"{table.lower()}.csv")
        df.to_csv(csv_path, index=False)

        # Export JSON
        json_path = os.path.join(JSON_DIR, f"{table.lower()}.json")
        df.to_json(
            json_path,
            orient="records",
            indent=4,
            force_ascii=False
        )

        print(
            f"{table}: {len(df)} records exported successfully"
        )

    conn.close()

    print("\nCSV and JSON exports completed!")
    print("CSV folder:", CSV_DIR)
    print("JSON folder:", JSON_DIR)


if __name__ == "__main__":
    export_data()
