import psycopg2
import psycopg2.extras
import logging

def check_db_connection():
  try:
    conn = psycopg2.connect(
      dbname="db-games",
      user="admin",
      password="qwerty",
      host="game-db",
      connect_timeout=1
    )
    conn.close()
    return True
  except psycopg2.OperationalError as e:
    logging.error(f"Database connection failed: {e}")
    return False
  except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
    return False  