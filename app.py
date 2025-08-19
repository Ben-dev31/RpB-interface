from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import numpy as np
import soundfile as sf
import io
import time,os

import threading
from utils import *
from utils.noises import pink_noise, brownian_noise, velvet_noise

from utils.audio_processing import AudioStream

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

FILTERS = {
    
    "bistable": bistable_filter,
    "diode": diode_filter,
    "diode_clipper": rubber_zener_filter,
    
}

NOISES = {
    "none": lambda length, sr, **kwargs: np.zeros(length),
    "white":white_noise,
    "pink": pink_noise,
    "brown": brownian_noise,
    "perlin": perlin_stream,
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

stream = AudioStream(fs=44100, block_size=1024)
stream.FILTERS = FILTERS
stream.NOISES = NOISES

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
    global threshold, signalAmplitude, tau, Xb, weellNum, noiseAmplitude, AUDIO, AUDIO_FILE, stream

    input_method = data.get('input_method', 'jack')
    print(f"Input method: {input_method}")
    if input_method == 'file':
        stream.set_input_method('file')
        filename = data.get('filename')
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        stream.set_input_file(filepath)

    else:
        stream.set_input_method('jack')
   
        
    # Applique le bruit si spécifié
    noise_type = data.get('noise')
    noiseAmplitude= float(data.get('amplitude', 0.1))
    threshold = float(data.get('threshold', 1.0))

    filter_type = data.get('filter')

    stream.set_filter(filter_type)
    stream.set_noise(noise_type)
    stream.set_parameters(
        threshold=threshold,
        signal_amplitude=signalAmplitude,
        noise_amplitude=noiseAmplitude,
        tau=tau,
        Xb=Xb,
        weellNum=weellNum
    )

   

    stream_thread = threading.Thread(target=stream.start)
    stream_thread.daemon = True  # Allow thread to exit when main program exits
    stream_thread.start()
  



@socketio.on('stop_stream')
def handle_stop_stream():
    global stream

    stream.stop()
    print("Stream stopped by user")
    

@socketio.on('update_parameters')
def handle_update_params(data):
    global threshold, signalAmplitude, tau, Xb, weellNum, noiseAmplitude
    threshold = float(data.get('threshold', 1.0))
    signalAmplitude = float(data.get('signalAmplitude', 0.1))
    tau = float(data.get('tau', 0.5))
    Xb = float(data.get('Xb', 1.0))
    weellNum = int(data.get('weellNum', 1))
    noiseAmplitude = float(data.get('noiseAmplitude', 0.1))
    print(f"Updated parameters: threshold={threshold}, signalAmplitude={signalAmplitude}, noiseAmplitude = {noiseAmplitude} tau={tau}, Xb={Xb}, weellNum={weellNum}")
    # Met à jour les paramètres du flux audio
    stream.set_parameters(
        threshold=threshold,
        signal_amplitude=signalAmplitude,
        noise_amplitude=noiseAmplitude,
        tau=tau,
        Xb=Xb,
        weellNum=weellNum   
    )

@socketio.on('update_filter')
def handle_update_filter(data):
    global stream
    filter_type = data.get('filter')
   
    stream.set_filter(filter_type)
    threshold = float(data.get('threshold', 1.0))
    tau = float(data.get('tau', 0.5))
    Xb = float(data.get('Xb', 1.0))
    weellNum = int(data.get('weellNum', 1)) 
    stream.set_parameters(
        threshold=threshold,
        tau=tau,
        Xb=Xb,
        weellNum=weellNum
    )
    print(f"Filter updated to: {filter_type}")

@socketio.on('update_noise')
def handle_update_noise(data):
    global stream
    noise_type = data.get('noise')
    noiseAmplitude = float(data.get('amplitude', 0.1))
    
    stream.set_noise(noise_type)
    stream.set_parameters(noise_amplitude=noiseAmplitude)
    print(f"Noise updated to: {noise_type} with amplitude {noiseAmplitude}")
    


@socketio.on('update_volume')
def handle_update_volume(data):
    global stream
    volume = float(data.get('volume', 100)) / 100.0
    stream.set_volume(volume)
    print(f"Volume updated to: {volume * 100}%")

if __name__ == '__main__':
    socketio.run(app, debug=True)