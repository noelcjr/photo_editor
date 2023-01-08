import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from pillow import load_image, dupe_image
from pillow import get_image_size, rotate_image, resize_image, crop_image
from cleanup import remove_static_files

UPLOAD_FOLDER = os.getcwd() + '/static'
ALLOWED_EXTENSIONS = set(['png', 'jpeg', 'jpg'])
INPUT_FILENAME = ''

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

image = None
width, height = 0, 0
def refresh_parameters(image_path):
    global image, width, height
    image = load_image(image_path)
    width, height = get_image_size(image)

# So preview refreshes with any new change
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/', methods=['GET', 'POST'])
def home():
    global INPUT_FILENAME
    remove_static_files()
    if request.method == 'POST':
        submit_button = request.form.get('submit_button')
        if submit_button == 'upload_image':
            # check if the post request has the file part
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                return redirect(request.url)
            if file and allowed_file(file.filename):
                INPUT_FILENAME = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME))
                dupe_image(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME), 'copy')
                refresh_parameters(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME))
                return redirect(url_for('uploaded'))
    return render_template('home.html')

@app.route('/uploaded', methods=['GET', 'POST'])
def uploaded():
    global image

    if INPUT_FILENAME:
        if request.method == 'POST':
            # Nav
            original_button = request.form.get('original_button')
            download_button = request.form.get('download_button')
            # Rotate/resize/crop
            rotate_button = request.form.get('rotate_button')
            resize_button = request.form.get('resize_button')
            crop_button = request.form.get('crop_button')

            if original_button:
                dupe_image(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME), 'replace')
            if download_button:
                return send_file(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME), as_attachment=True)

            if rotate_button:
                angle = int(request.form.get('angle'))
                rotate_image(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME), angle)
            elif resize_button:
                n_width = int(request.form.get('width'))
                n_height = int(request.form.get('height'))
                resize_image(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME), n_width, n_height)
            elif crop_button:
                start_x = int(request.form.get('start_x'))
                start_y = int(request.form.get('start_y'))
                end_x = int(request.form.get('end_x'))
                end_y = int(request.form.get('end_y'))
                crop_image(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME), start_x, start_y, end_x, end_y)
            if any([original_button, rotate_button, resize_button, crop_button]):
                refresh_parameters(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME))
        return render_template('uploaded.html', width=width, height=height, filename=INPUT_FILENAME)
    else:
        return render_template('uploaded.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT'))
