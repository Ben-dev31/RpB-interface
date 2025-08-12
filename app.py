from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import librosa as lb
import numpy as np

from utils import *
from utils.noises import pink_noise, brownian_noise

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'm4a', 'aac'}

FILTERS = {
    "diode": diode_filter,
    "diode_clipper": rubber_zener_filter
}

NOISES = {
    "none": lambda length, sr: np.zeros(length),
    "white": lambda length, sr: np.random.normal(0, 1, length),
    "pink": pink_noise,
    "brownian": brownian_noise
}

SIGNAL_CACHE = None

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
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Missing filename"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(filepath):
        return jsonify({"error": "File not found"}), 404

    try:
        data, samplerate = lb.load(filepath, duration=2, sr=None, mono=True)
        if len(data.shape) > 1:
            data = data[:, 0]
        duration = 2  # secondes
        max_samples = int(samplerate * duration)
        data = data[:max_samples]
        time = np.linspace(0, len(data) / samplerate, num=len(data))
        return jsonify({
            "x": np.round(time, 2).tolist(),
            "y": np.round(data, 2).tolist()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_filter_profil_data(threshold, filter_type):
    if filter_type not in FILTERS:
        return {"error": "Invalid filter type"}
    x = np.linspace(-threshold - 1, threshold + 1, 100)
    y = FILTERS[filter_type](x, threshold)
    y = np.clip(y, -threshold - 1, threshold + 1)
    x = np.round(x, 2).tolist()
    y = np.round(y, 2).tolist()
    return x, y

def load_signal(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(filepath):
        return {"error": "File not found"}
    
    try:
        data, samplerate = lb.load(filepath, sr=None, mono=True)
        data = data / np.max(np.abs(data)) if np.max(np.abs(data)) != 0 else data
        return data, samplerate
    except Exception as e:
        return {"error": str(e)}

def get_filtered_signal(filename=None, filter_type=None, threshold=0, noise="none", amplitude=0):
    global SIGNAL_CACHE
   
    if SIGNAL_CACHE is not None and not isinstance(SIGNAL_CACHE, dict):
        data, samplerate = SIGNAL_CACHE
    else:
        SIGNAL_CACHE = load_signal(filename) 
        if isinstance(SIGNAL_CACHE, dict) and "error" in SIGNAL_CACHE:
            return SIGNAL_CACHE
        data, samplerate = SIGNAL_CACHE


    try:
        if noise in NOISES:
            noise_signal = NOISES[noise](len(data), samplerate)
        else:
            noise_signal = data
        filtered_data = FILTERS[filter_type](noise_signal * amplitude, threshold)
        x = np.linspace(0, len(filtered_data) / samplerate, num=len(filtered_data))
        y = filtered_data
        return x.tolist(), y.tolist()
    except Exception as e:
        return {"error": str(e)}

@app.route("/get_graph_data", methods=["GET"])
def get_graph_data():
    filter_type = request.args.get("filtre")
    threshold = float(request.args.get("threshold", 0))
    noise = request.args.get("noise", "none")
    amplitude = float(request.args.get("amplitude", 0))
    filename = request.args.get("filename")

    xf, yf = get_filtered_signal(filename, filter_type, threshold, noise, amplitude)
    if isinstance(xf, dict) and "error" in xf:
        return jsonify(xf), 400
    xp, yp = get_filter_profil_data(threshold, filter_type)
    if isinstance(xp, dict) and "error" in xp:
        return jsonify(xp), 400

    return jsonify({
        "xp": xp,
        "yp": yp,
        "xf": xf,
        "yf": yf
    })

if __name__ == '__main__':
    app.run(debug=True)
