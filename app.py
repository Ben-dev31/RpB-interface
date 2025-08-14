from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import numpy as np
import soundfile as sf
import io
import time,os

from utils import *
from utils.noises import pink_noise, brownian_noise, velvet_noise

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

FILTERS = {
    "diode": diode_filter,
    "diode_clipper": rubber_zener_filter,
    
}

NOISES = {
    "none": lambda length, sr: np.zeros(length),
    "white": lambda length, sr: np.random.normal(0, 1, length),
    "pink": pink_noise,
    "brown": brownian_noise,
    "perlin": perlin_noise,
    "velvet": velvet_noise
}

threshold = 1.0  # Valeur par défaut du seuil
signalAmplitude = 0.1  # Amplitude par défaut du signal
noiseAmplitude = 0.1  # Amplitude par défaut du bruit
tau = 0.5  # Valeur par défaut de tau
Xb = 1.0  # Valeur par défaut de Xb
weellNum = 1  # Valeur par défaut du nombre de puits

AUDIO = None  # Variable pour stocker l'audio en cours de traitement
AUDIO_FILE = ''  # Variable pour stocker le fichier audio en cours de traitement

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_stream_file', methods=['POST'])
def upload_stream_file():
    file = request.files.get('audio_file')
    if not file:
        return jsonify({"error": "No file"}), 400
    filename = f"stream_{int(time.time())}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return jsonify({"filename": filename})

@socketio.on('start_stream')
def handle_stream(data):
    global threshold, signalAmplitude, tau, Xb, weellNum, noiseAmplitude, AUDIO, AUDIO_FILE

    sr = 44100
    chunk_size = 1024  # Taille du chunk en échantillons

    filename = data.get('filename')
    if not filename:
        emit('stream_end')
        return

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(filepath):
        emit('stream_end')
        return

    # Lis le fichier audio
    if AUDIO is None or AUDIO_FILE != filepath:
        AUDIO, sr = sf.read(filepath)
        if AUDIO.ndim > 1:
            AUDIO = AUDIO[:, 0]  # mono
        
        AUDIO = AUDIO.astype(np.float32)
        AUDIO_FILE = filepath
    
    audio = AUDIO.copy()


    # Applique le bruit si spécifié
    noise_type = data.get('noise')
    noiseAmplitude= float(data.get('amplitude', 0.1))
    threshold = float(data.get('threshold', 1.0))

    filter_type = data.get('filter')

    audio = audio /np.max(np.abs(audio)) * signalAmplitude
    

    # Découpe et envoie par blocs
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i+chunk_size]

        sg = signalAmplitude * chunk + noiseAmplitude * NOISES[noise_type](len(chunk), sr)

        new_chunk = FILTERS[filter_type](sg,threshold) if filter_type != 'bistable' else bistable_filter(sg, tau, Xb, weellNum)

        buf = io.BytesIO()
        sf.write(buf, new_chunk, sr, format='RAW', subtype='FLOAT')
        emit('audio_chunk', buf.getvalue())
        time.sleep(chunk_size / sr)

    emit('stream_end')

@socketio.on('stop_stream')
def handle_stop_stream():
    print("Stream stopped by user")
    emit('stream_stopped')

@socketio.on('update_parameters')
def handle_update_params(data):
    global threshold, signalAmplitude, tau, Xb, weellNum, noiseAmplitude
    threshold = float(data.get('threshold', 1.0))
    signalAmplitude = float(data.get('signalAmplitude', 0.1))
    tau = float(data.get('tau', 0.5))
    Xb = float(data.get('Xb', 1.0))
    weellNum = int(data.get('weellNum', 1))
    noiseAmplitude = float(data.get('noiseAmplitude', 0.1))
    print(f"Updated parameters: threshold={threshold}, signalAmplitude={signalAmplitude}, tau={tau}, Xb={Xb}, weellNum={weellNum}")

if __name__ == '__main__':
    socketio.run(app, debug=True)