# tapas API

tapas is basically a web implementation of [jayne](https://github.com/seanrife/jayne). It accepts file uploads while backend worker(s) process the uploaded files. It requires Postgres, which it uses as a job cue and to hold results.

Requirements:
 - flask
 - NLTK
 - psycopg2
 - BeautifulSoup

Modules:
 - api.py: main flask backend program
 - worker.py: runs in the background, checking the DB for new jobs and updating their progress until complete.

Endpoints:
 - /upload (POST): accepts one or more files; returns `status_url` which indicates where new status updates will be posted, and where results can be obtained once the job is complete.
 - /jobs/`jobid`: indicates the status of a given job id.
 - /downloads/`jobid`: returns a CSV of results for a give job id.
