from zipfile import ZipFile
from pathlib import Path
import os
from db import get_cursor
import config
from pdf2xml import process
from common import update_status
from jayne import run
from time import sleep

from psycopg2.extras import execute_batch

UPLOAD_FOLDER = config.UPLOAD_FOLDER

while True:

    with get_cursor(commit=True) as cursor:
        query = """
                SELECT job_id FROM jobs
                WHERE status = 'READY'
                LIMIT 1;
                """
        cursor.execute(query)
        job_id = cursor.fetchone()
        
        if job_id:
            job_id = job_id[0]
        else:
            sleep(5)
            pass

        working_dir = os.path.join(UPLOAD_FOLDER, job_id)

    paths = Path(working_dir).rglob('*.zip')
    for path in paths:
        with ZipFile(path) as zf:
            zf.extractall(working_dir)

    update_status(job_id, "EXTRACTED")

    pdfs = Path(working_dir).rglob('*.pdf')
    file_count = 0

    for pdf in pdfs:
        if process(pdf, job_id):
            file_count = file_count + 1
            
    update_status(job_id, "CONVERTED")

    percent_complete = 0

    results = run(working_dir)

    for item in results:
        item.update({'slug':job_id})

    update_status(job_id, "ANALYZED")

    with get_cursor(commit=True) as cursor:
        query = """
                INSERT INTO public.results(
                    slug,
                    file1,
                    file2,
                    text1,
                    text2,
                    score
                )
                VALUES(
                    %(slug)s,
                    %(file1)s,
                    %(file2)s,
                    %(text1)s,
                    %(text2)s,
                    %(score)s
                );
                """
        execute_batch(cursor, query, results)

    update_status(job_id, "FINISHED")
