from flask import Flask, render_template, request, redirect, url_for,send_from_directory
import os
import librosa as lb
from flask import jsonify
import numpy as np

from utils import*


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'm4a', 'aac'}

FILTERS = {
    "diode": diode_filter,
    "diode_clipper": rubber_zener_filter
}





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
        data,samplerate = lb.load(filepath, duration=2, sr=None, mono=True)
        # Si stéréo, on garde le canal gauche
        if len(data.shape) > 1:
            data = data[:, 0]

       

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



@app.route('/get_filter_data', methods=['GET'])
def get_filter_data():
    filter_type = request.args.get("filtre")
    threshold = float(request.args.get("threshold", 0))


    if filter_type not in FILTERS:
        return jsonify({"error": "Invalid filter type"}), 400

    # Générer les données du filtre
    x = np.linspace(-threshold - 1, threshold +1, 100)
    y = FILTERS[filter_type](x, threshold)
    y = np.clip(y, -threshold-1, threshold+1)  # Limiter les valeurs de y pour éviter les erreurs de graphique

    x = np.round(x, 2).tolist()  # Arrondir les valeurs de x
    y = np.round(y, 2).tolist()  # Arrondir les valeurs de y
    return jsonify({
        "x": x,
        "y": y
    })


@app.route('/get_filtered_signal', methods=['GET'])
def get_filtered_signal():
    filename = request.args.get("filename")
    filter_type = request.args.get("filtre")
    threshold = float(request.args.get("threshold", 0))
    noise = request.args.get("noise", "none")
    amplitude = float(request.args.get("amplitude", 0))

    if not filename or not filter_type:
        return jsonify({"error": "Missing parameters"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(filepath):
        return jsonify({"error": "File not found"}), 404

    try:
        data, samplerate = lb.load(filepath, sr=None, mono=True)

        # Appliquer le filtre
        filtered_data = FILTERS[filter_type](data, threshold)

        return jsonify({
            "x": np.linspace(0, len(filtered_data) / samplerate, num=len(filtered_data)).tolist(),
            "y": filtered_data.tolist()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
