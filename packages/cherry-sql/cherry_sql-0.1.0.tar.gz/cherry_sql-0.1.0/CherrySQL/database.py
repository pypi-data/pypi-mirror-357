import pyodbc
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.connection_string = (
            f"Driver={{ODBC Driver 17 for SQL Server}};"
            f"Server={DB_CONFIG['server']};"
            f"Database={DB_CONFIG['database']};"
            f"Trusted_Connection=Yes;"
        )
    
    def connect(self):
        return pyodbc.connect(self.connection_string)

    def execute_query(self, query, params=None):
        with self.connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            try:
                return cursor.fetchall()
            except pyodbc.ProgrammingError:
                return None
            finally:
                conn.commit()
                conn.commit()
