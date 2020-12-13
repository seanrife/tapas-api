import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, send_from_directory
from coolname import generate_slug
from zipfile import ZipFile
from db import get_cursor
import config
import csv

app = Flask(__name__, static_folder="static", template_folder="templates")

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


@app.route('/downloads/<job_id>')
def download(job_id):
    results = get_data(job_id)
    generate_csv(job_id, results)
    downloads = '/tapas/tapas/downloads'
    return send_from_directory(directory=downloads, filename=f"{job_id}.csv", as_attachment=True)


@app.route('/')
def table_upload():
    return render_template('index.html', file_list=['File'])


@app.route('/jobs/<name>')
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
    
    if status == "READY":
        msg = "Your files have been uploaded but we haven't gotten to them yet. Please check back in a few minutes."
        return render_template('job.html', msg=msg)
    elif status == "EXTRACTED":
        msg = "Your files have been extracted and are being converted to text! Check back in a few minutes."
        return render_template('job.html', msg=msg)
    elif status == "CONVERTED":
        msg = "Your files have been converted to text and are being analyzed. This can take anywhere between under a minute to many hours depending on how many files you uploaded and how busy we are."
        return render_template('job.html', msg=msg)
    elif status == "FINISHED":
        url = f"{config.BASE_URL}/downloads/{name}"
        return render_template('results.html', url=url)
    


@app.route('/upload', methods=['POST'])
def upload():
    slug = generate_slug()
    try:
        os.mkdir(os.path.join(UPLOAD_FOLDER, slug))
    except OSError:
        print("Failed to create directory" % slug)

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
    return render_template('upload_complete.html', link=link)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
