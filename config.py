import os


DB_PASSWORD = os.environ['DB_PASSWORD']


db = {
    'host': 'localhost',
    'user': 'tapas',
    'passwd': DB_PASSWORD,
    'db': 'tapas'
    }
