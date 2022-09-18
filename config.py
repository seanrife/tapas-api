import os
from dotenv import load_dotenv

load_dotenv()


DB_PASSWORD = os.environ['DB_PASSWORD']
UPLOAD_FOLDER = '/tapas/uploads/'
BASE_PORT = 2600
BASE_DOMAIN = 'http://tapas.murraystate.edu'
BASE_URL = f'{BASE_DOMAIN}:{BASE_PORT}'

db = {
    'host': 'localhost',
    'user': 'tapas',
    'passwd': DB_PASSWORD,
    'db': 'tapas'
    }

grobid = {
    'host': 'localhost',
    'path': 'grobid',
    'port': '8070'
    }

analysis = {
    'min_length': 100,
    'analysis_type': 'lev',
    'cutoff_score': .4,
    'qgram_val': 4,
    'ngram_val': 4,
    'level': 'paragraph'
}

system = {
    'process_count': 400
}

