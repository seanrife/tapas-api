from pathlib import Path
import os
from lib.db import get_cursor
import config
from lib.grobid import process
from lib.common import update_status, logger
from lib.jayne import run
from time import sleep

from psycopg2.extras import execute_batch

"""
Runs in the background looking for unprocessed jobs.
When it find one, locates and extracts the archive,
then converts the PDFs to TEI, extracts the text, and
looks for similarity (basically everything else).
"""

UPLOAD_FOLDER = config.UPLOAD_FOLDER

def process_job(job_id):
    working_dir = os.path.join(UPLOAD_FOLDER, job_id)

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
        logger(f"Processing job id {job_id[0]}.")
        process_job(job_id[0])
    else:
        sleep(5)


