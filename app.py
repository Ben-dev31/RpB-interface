from flask import Flask, render_template, request, redirect, url_for,send_from_directory
import os
import librosa as lb
from flask import jsonify

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg','m4a'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return render_template('index.html', filename=file.filename)

    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/get_audio_data", methods=["GET"])
def get_audio_data():
    import numpy as np

    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Missing filename"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(filepath):
        return jsonify({"error": "File not found"}), 404

    try:
        data,samplerate = lb.load(filepath, duration=2, sr=None, mono=True)

        # Si stéréo, on garde le canal gauche
        if len(data.shape) > 1:
            data = data[:, 0]

        # Normalisation (valeurs entre -1 et 1 si int16)
        if data.dtype == np.int16:
            data = data / 32768.0
        elif data.dtype == np.int32:
            data = data / 2147483648.0
        elif data.dtype == np.uint8:
            data = (data - 128) / 128.0

        # Prendre une fenêtre de 2 secondes max
        duration = 2  # secondes
        max_samples = int(samplerate * duration)
        data = data[:max_samples]

        time = np.linspace(0, len(data) / samplerate, num=len(data))

        return jsonify({
            "x": time.tolist(),
            "y": data.tolist()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
