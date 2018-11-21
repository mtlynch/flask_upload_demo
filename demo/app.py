import logging
import os

import flask
import werkzeug.utils

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = flask.Flask(__name__)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

logger = app.logger


def ensure_dir_exists(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def is_file_allowed(filename):
    extension = os.path.splitext(filename)[1]
    if not extension:
        return False
    return extension[1:].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return flask.send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if flask.request.method == 'POST':
        if 'file' not in flask.request.files:
            flask.flash('No file part')
            return flask.redirect(flask.request.url)
        uploaded_file = flask.request.files['file']
        if not uploaded_file.filename:
            flask.flash('No selected file')
            return flask.redirect(flask.request.url)
        if uploaded_file and is_file_allowed(uploaded_file.filename):
            filename = werkzeug.utils.secure_filename(uploaded_file.filename)
            ensure_dir_exists(UPLOAD_FOLDER)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            logger.info('Saving uploaded file "%s" to "%s"', filename,
                        save_path)
            uploaded_file.save(save_path)
            return flask.redirect(
                flask.url_for('serve_uploaded_file', filename=filename))
    return """
<!doctype html>
<html>
<title>Flask File Upload Demo</title>
<h1>Upload a File</h1>
<form method="post" enctype="multipart/form-data">
  <input type="file" name="file">
  <input type="submit" value="Upload File">
</form>
</html>
"""
