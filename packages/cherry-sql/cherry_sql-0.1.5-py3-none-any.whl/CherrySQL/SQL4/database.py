import pyodbc
from config import DB_CONFIG

class Database:
    def __init__(self):
        # Универсальное подключение: по паролю или Trusted_Connection
        if DB_CONFIG.get('trusted_connection', '').lower() in ('yes', 'true', '1'):
            self.connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={DB_CONFIG['server']};"
                f"DATABASE={DB_CONFIG['database']};"
                f"Trusted_Connection=Yes;"
            )
        else:
            self.connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={DB_CONFIG['server']};"
                f"DATABASE={DB_CONFIG['database']};"
                f"UID={DB_CONFIG.get('username','')};"
                f"PWD={DB_CONFIG.get('password','')};"
            )

    def connect(self):
        try:
            return pyodbc.connect(self.connection_string)
        except Exception:
            from tkinter.messagebox import showerror
            showerror(title='Ошибка', message='Нет соединения с базой данных. Работа приложения будет завершена.')
            exit(1)

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
