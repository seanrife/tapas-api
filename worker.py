from pathlib import Path
import os
from lib.db import get_cursor
import config
from lib.grobid import process
from lib.common import update_status, logger
from lib.jayne import run
from time import sleep, time

from psycopg2.extras import execute_batch

"""
Runs in the background looking for unprocessed jobs.
When it find one, locates and extracts the archive,
then converts the PDFs to TEI, extracts the text, and
looks for similarity (basically everything else).
"""

UPLOAD_FOLDER = config.UPLOAD_FOLDER

def process_job(job):

    start_time = time()
    
    job_id = job[0]
    job_cutoff = job[1]
    
    working_dir = os.path.join(UPLOAD_FOLDER, job_id)

    pdfs = Path(working_dir).rglob('*.pdf')
    file_count = 0

    for pdf in pdfs:
        if process(pdf, job_id):
            file_count = file_count + 1
            
    update_status(job_id, "CONVERTED")

    percent_complete = 0

    results = run(working_dir, job_cutoff)

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
    
    end_time = time()
    
    compute_time = end_time-start_time
    
    logger(f"Job completed in {compute_time} seconds.")


min_length = config.analysis['min_length']
cutoff_score = config.analysis['cutoff_score']
analysis_type = config.analysis["analysis_type"]
process_count = config.system["process_count"]

logger(f"Started master worker process.")
logger(f"Minimum length: {min_length}")
logger(f"Analysis type: {analysis_type}")
logger(f"Process count: {process_count}")

while True:

    with get_cursor(commit=True) as cursor:
        query = """
                SELECT job_id, cutoff FROM jobs
                WHERE status = 'READY'
                LIMIT 1;
                """
        cursor.execute(query)
        job = cursor.fetchone()
        
    if job:
        logger("  ====================  GOT NEW JOB  ====================  ")
        logger(f"Processing job id {job[0]}.")
        process_job(job)
    else:
        sleep(5)
