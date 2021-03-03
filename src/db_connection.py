import mysql.connector
from .config import DB_USER, DB_PWD, DB_URL, DB_NAME, ALLOWED_COLUMNS


def get_db_connection():
    # Optimization: connection pool
    return mysql.connector.connect(user=DB_USER, password=DB_PWD, host=DB_URL, database=DB_NAME)


def release_db_connection(connection):
    connection.close()


def allowed_column_name(table, column_name):
    if table in ALLOWED_COLUMNS and column_name in ALLOWED_COLUMNS[table]:
        return True
    return False
