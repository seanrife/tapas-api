import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, send_from_directory, jsonify
from coolname import generate_slug
from zipfile import ZipFile
from db import get_cursor
import config
import csv
from common import logger

api = Flask(__name__)

UPLOAD_FOLDER = config.UPLOAD_FOLDER


def generate_csv(job_id, data):
    with open(f"/tapas/tapas/downloads/{job_id}.csv", "w") as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['file1', 'file2', 'text1', 'text2', 'score'])
        for row in data:
            csv_out.writerow(row)


def get_data(job_id):
    with get_cursor(commit=True) as cursor:
        try:
            query = """
                SELECT file1, file2, text1, text2, score
                FROM results
                WHERE
                slug = %s;
                """
            cursor.execute(query, (job_id,))
            results = cursor.fetchall()
            return results
        except Exception:
            return None


@api.route('/downloads/<job_id>')
def download(job_id):
    results = get_data(job_id)
    downloads = '/tapas/tapas/downloads'
    if not os.path.exists(f"{downloads}/{job_id}.csv"):
        generate_csv(job_id, results)
    return send_from_directory(directory=downloads, filename=f"{job_id}.csv", as_attachment=True)


@api.route('/jobs/<name>')
def job(name):
    with get_cursor(commit=True) as cursor:
        query = """
                SELECT status
                FROM jobs
                WHERE
                job_id = %s;
                """
        cursor.execute(query, (name,))
        status = cursor.fetchone()[0]
    
    return jsonify({'status': status})


@api.route('/')
def index():
    return jsonify({'message': 'API is running. Shiny!'})


@api.route("/upload", methods=["POST"])
def upload():
    """Upload a file."""
    slug = generate_slug()
    try:
        os.mkdir(os.path.join(UPLOAD_FOLDER, slug))
    except OSError:
        logger("Failed to create directory" % slug)

    # Using multiple uploads in a loop so we can easily expand number of uploads
    
    for file in request.files.getlist('file'):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, slug, filename))
        
    with get_cursor(commit=True) as cursor:
        query = """
                INSERT INTO jobs (job_id, status)
                VALUES (%s, %s);
                """
        cursor.execute(query, (slug, "READY"))

    link = f"{config.BASE_URL}/jobs/{slug}"
    return jsonify({'status_url': link})


if __name__ == '__main__':
    api.run(host='0.0.0.0', port=2600)
