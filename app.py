import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = '/home/sean/tapas/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/')
def table_upload():
    return render_template('index.html', file_list=['File 1', 'File 2'])


@app.route('/upload', methods=['POST'])
def upload():
    for file in request.files.getlist('file'):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('upload-complete.html')


if __name__ == '__main__':
    app.run()
