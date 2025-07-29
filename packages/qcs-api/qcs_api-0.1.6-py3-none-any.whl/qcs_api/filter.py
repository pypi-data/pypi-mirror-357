import sqlite3
import os
import pandas as pd

FILENAME = "hbn_defects_structure.db"
DATA_PATH = os.path.join(os.getcwd(), FILENAME)

def get_filtered_data(properties: str, value=None):
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("Database not found. Run get_all_data first.")

    conn = sqlite3.connect(DATA_PATH)

    if value is not None:
        query = f"""
        SELECT "Defect", "Defect name", "{properties}"
        FROM your_table_name
        WHERE "{properties}" = ?
        """
        df = pd.read_sql_query(query, conn, params=(value,))
    else:
        query = f"""
        SELECT "Defect", "Defect name", "{properties}"
        FROM your_table_name
        """
        df = pd.read_sql_query(query, conn)

    conn.close()
    return df