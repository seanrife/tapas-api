# tapas API

tapas is basically a web implementation of [jayne](https://github.com/seanrife/jayne). It accepts file uploads while backend worker(s) process the uploaded files. It requires Postgres, which it uses as a job cue and to hold results.

The production version runs on a PowerEdge R7525 with two AMD EPYC 7552 48-Core Processors at [Murray State University](https://murraystate.edu). It's a beast. As such, your mileage may vary when testing locally.

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
 - /jobs/`jobid` (GET): indicates the status of a given job id.
 - /downloads/`jobid` (GET): returns a CSV of results for a give job id.

TODO:
 - Tests
 - A preconfigured Docker container for Postgres

This project is made possible by the generous support of the [Fetzer Franklin Fund](https://www.fetzer-franklin-fund.org/) and [Center for Open Science](https://cos.io).
