DB_CONFIG = {
   'driver': '{ODBC Driver 17 for SQL Server}',
   'server': 'MYLAPTOP',
   'database': 'Var4',
   'trusted_connection': 'yes',
}


server = '192.168.1.233'
db = 'demo_wibe'
usname = 'admin'
uspsw = '123456'


# Если нужно использовать логин/пароль, раскомментируйте этот блок:
#DB_CONFIG = {
#     'driver': '{ODBC Driver 17 for SQL Server}',
#     'server': server,
#     'database': db,
#     'username': usname,
#     'password': uspsw
#}










# Для Trusted_Connection раскомментируйте и заполните строки ниже:
# trusted_connection = 'yes'
# server = 'MYLAPTOP'
# db = 'Var4'

# --- Автоматическая сборка конфигурации ---
#DB_CONFIG = {}

# --- Использовать подключение по логину/паролю ---





# --- Использовать Trusted_Connection ---
# Если нужно использовать Trusted_Connection, раскомментируйте этот блок:
#DB_CONFIG = {
#    'driver': '{ODBC Driver 17 for SQL Server}',
 #   'server': 'MYLAPTOP',
 #   'database': 'Var4',
#   'trusted_connection': 'yes',
#}



###'trusted_connection': 'no'###