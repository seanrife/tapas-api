from db import get_cursor
import time
import os

def update_status(job_id, status):
    with get_cursor(commit=True) as cursor:
        query = """
                UPDATE jobs
                SET status = %s
                WHERE job_id = %s;
                """
        cursor.execute(query, (status, job_id))


def logger(text):
    mkdirp('logs')
    logfile_name = 'logs/jayne.log'
    with open(logfile_name, mode='a') as logfile:
        logfile.write(text + '\n')


def mkdirp(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
