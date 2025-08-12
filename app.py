from flask import Flask, render_template
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

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_stream')
def handle_stream(data):
    # data peut contenir les paramètres utilisateur
    sr = 44100
    duration = 5  # secondes
    chunk_size = 2048  # échantillons par bloc

    # Exemple : génère un sinus
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    signal = 0.5 * np.sin(2 * np.pi * 440 * t)

    # Découpe et envoie par blocs
    for i in range(0, len(signal), chunk_size):
        chunk = signal[i:i+chunk_size]
        buf = io.BytesIO()
        sf.write(buf, chunk, sr, format='RAW', subtype='FLOAT')
        emit('audio_chunk', buf.getvalue())
        time.sleep(chunk_size / sr)  # Simule le temps réel

    emit('stream_end')


if __name__ == '__main__':
    socketio.run(app, debug=True)