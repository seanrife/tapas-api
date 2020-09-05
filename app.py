import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request
from coolname import generate_slug
from zipfile import ZipFile
from db import get_cursor
import socket

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = '/home/sean/tapas/uploads'


def send_file(filename):
    s = socket.socket()
    host = '54.186.172.17'
    port = 10069
    s.connect((host, port))
    with open(filename, 'rb') as f:
        data = f.read(1024)
        while (data):
            s.send(data)
            data = f.read(1024)
        s.close


@app.route('/')
def table_upload():
    return render_template('index.html', file_list=['File 1', 'File 2'])


@app.route('/upload', methods=['POST'])
def upload():
    slug = generate_slug()
    try:
        os.mkdir(os.path.join(UPLOAD_FOLDER, slug))
    except OSError:
        print("Failed to create directory" % slug)

    # Using multiple uploads in a loop so we can easily expand >2 uploads
    for file in request.files.getlist('file'):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, slug, filename))

    # Write metadata file
    with open(os.path.join(UPLOAD_FOLDER, slug, 'meta.dat'), 'a') as f:
        f.write(slug)

    slug_tuple = (slug,)
    with get_cursor(commit=True) as cursor:
        query = """
                INSERT INTO jobs (job_id)
                VALUES (%s);
                """
        cursor.execute(query, slug_tuple)

    arcfilename = os.path.join(UPLOAD_FOLDER, slug) + '.pack'

    with ZipFile(arcfilename, 'w') as newzip:
        for file in os.listdir(os.path.join(UPLOAD_FOLDER, slug)):
            newzip.write(os.path.join(UPLOAD_FOLDER, slug, file), arcname=file)

    send_file(arcfilename)

    link = 'https://tapas.ai/{}'.format(slug)
    return render_template('upload_complete.html', link=link)


if __name__ == '__main__':
    app.run()
