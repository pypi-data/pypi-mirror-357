import sqlite3
import os
import pandas as pd

FILENAME = "hbn_defects_structure.db"
DATA_PATH = os.path.join(os.path.dirname(__file__), FILENAME)

def get_filtered_data(properties: str, value):
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("Database not found. Run download_db() first.")

    conn = sqlite3.connect(DATA_PATH)

    query = f"""
    SELECT "Defect", "Defect name", "{properties}"
    FROM your_table_name
    WHERE "{properties}" = ?
    """
    df = pd.read_sql_query(query, conn, params=(value,))
    conn.close()

    return df
