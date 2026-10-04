"""
RetailHub Database Layer (db.py)
CS4431: Human-Computer Interaction & E-Commerce Systems
Manages MySQL connection pooling and query execution helpers.
"""

import os
import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "RetailHub2026!")
DB_NAME = os.environ.get("DB_NAME", "retailhub_db")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", 5))

# Initialize MySQL Connection Pool
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="retailhub_pool",
        pool_size=POOL_SIZE,
        pool_reset_session=True,
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci"
    )
    print(f"[DB] Successfully initialized MySQL connection pool for '{DB_NAME}' on {DB_HOST}:{DB_PORT}")
except Exception as e:
    print(f"[DB WARNING] Could not connect to live MySQL instance ({e}). Running in fallback mode.")
    db_pool = None


@contextmanager
def get_db_connection():
    """Context manager for acquiring and releasing pooled MySQL connections."""
    if db_pool is None:
        raise ConnectionError("MySQL database pool is not initialized. Please verify DB credentials in .env")
    
    conn = db_pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()


def execute_query(query: str, params: tuple = None, fetch_one: bool = False, dictionary: bool = True):
    """Executes a SELECT query and returns records."""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            cursor.execute(query, params or ())
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
        finally:
            cursor.close()


def execute_mutation(query: str, params: tuple = None) -> int:
    """Executes an INSERT / UPDATE / DELETE query and commits transaction."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid or cursor.rowcount
        except Exception as err:
            conn.rollback()
            raise err
        finally:
            cursor.close()
