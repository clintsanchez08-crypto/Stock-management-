# ============================================================
# database.py - connection and ONE central query runner
# ------------------------------------------------------------
# NOTE: Change the MySQL password in DB_CONFIG below to your
#       OWN MySQL root password before running!
# ============================================================

import mysql.connector
from mysql.connector import Error

# All connection settings live here (change password only)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",          # <--- CHANGE THIS to your MySQL password
    "database": "stocks_db",
}


def open_database():
    """Opens a connection to the database, or prints why it failed."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("[SUCCESS] Connected to the MySQL database 'stocks_db'.")
        return conn
    except Error as err:
        print(f"[ERROR] Could not connect to MySQL: {err}")
        return None


def run_sql(connection, query, params=(), fetch=False):
    """Runs ONE parameterized SQL statement safely.

    - params must be a tuple (always use %s placeholders, never strings!)
    - set fetch=True for SELECT statements to get the rows back
    - commits automatically for INSERT / UPDATE / DELETE
    - on a MySQL error: rolls back and re-raises the error so the caller
      can print its own [ERROR] message
    - the finally block ALWAYS closes the cursor

    Returns: (rows, lastrowid, affected_rows)
    """
    cursor = None
    rows, new_id, affected = None, None, 0
    try:
        # dictionary=True so rows come back like {'stock_id': 1, ...}
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        new_id = cursor.lastrowid
        affected = cursor.rowcount
        if fetch:
            rows = cursor.fetchall()
        if not query.strip().upper().startswith("SELECT"):
            connection.commit()
        return rows, new_id, affected
    except Error:
        connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()


def close_database(connection):
    """Closes the connection on the way out."""
    if connection is not None and connection.is_connected():
        connection.close()
        print("[SUCCESS] Connection closed. Goodbye!")
