import pyodbc

# Substitua pelos dados de conexão corretos do seu banco SQL Server
server = 'servidor origem'
database = 'nome banco'
username = 'usuário banco'
password = 'senha banco'
connection = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(connection)