let audioContext = new (window.AudioContext || window.webkitAudioContext)();
let analyser;
let biquadFilter;
let gainNode;
let audioElement;
let noiseBuffer;
let inputType = 'microphone';

const canvas = document.getElementById('audioCanvas');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusElement = document.getElementById('status');
const audioFile = document.getElementById('audioFile');
const fileLabel = document.getElementById('fileLabel');
const filterSelect = document.getElementById('filterSelect');
const noiseSelect = document.getElementById('noiseSelect');
const thresholdSlider = document.getElementById('thresholdSlider');
const noiseAmplSlider = document.getElementById('noiseSlider');
const thresholdValue = document.getElementById('thresholdValue');
const noiseValue = document.getElementById('noiseAmpl');
const systemTimeSlider = document.getElementById('systemTimeSlider');
const systemTimeValue = document.getElementById('systemTimeValue');
const wellPosSlider = document.getElementById('wellPosSlider');
const wellPosValue = document.getElementById('wellPosValue');
const wellNumSlider = document.getElementById('weellNumSlider');
const wellNumValue = document.getElementById('weellNumValue');
const signalAmplSlider = document.getElementById('signalAmplSlider');
const microphoneRadio = document.getElementById('microphone');
const fileRadio = document.getElementById('file');
const jackRadio = document.getElementById('jack');
const processedAudio = document.getElementById('processedAudio');
const downloadBtn = document.getElementById('downloadBtn');
const volumeSlider = document.getElementById('VolumeSlider');

// --- STREAMING SOCKET.IO ---
let socket = io();
let audioQueue = [];
let playing = false;

socket.on('audio_chunk', (data) => {
    // data est un ArrayBuffer (raw float32)
    audioQueue.push(data);
    if (!playing) playNextChunk();
});

socket.on('stream_end', () => {
    statusElement.textContent = "Streaming terminé.";
    playing = false;
});

let drawCounter = 0;
const DRAW_EVERY = 3; // N'affiche qu'un bloc sur 3

function playNextChunk() {
    if (audioQueue.length === 0) {
        playing = false;
        return;
    }
    playing = true;
    let chunk = audioQueue.shift();
    // Convertit le chunk en Float32Array
    let floatArray = new Float32Array(chunk.byteLength / 4);
    let view = new DataView(chunk);
    for (let i = 0; i < floatArray.length; i++) {
        floatArray[i] = view.getFloat32(i * 4, true);
    }
    let buffer = audioContext.createBuffer(1, floatArray.length, 44100);
    buffer.copyToChannel(floatArray, 0);

    // Dessin allégé
    drawCounter++;
    if (drawCounter % DRAW_EVERY === 0) {
        requestAnimationFrame(() => drawWaveformFromBuffer(buffer));
    }

    let source = audioContext.createBufferSource();
    source.buffer = buffer;
    source.connect(audioContext.destination);
    source.onended = playNextChunk;
    source.start();
}

// Démarre le streaming
function startStreaming() {
    audioQueue = [];
    playing = false;
    statusElement.textContent = "Streaming en cours...";
    startBtn.disabled = true;
    stopBtn.disabled = false;
    startBtn.style.display = 'none';
    stopBtn.style.display = 'inline-block';
    // Récupère les paramètres utilisateur
    const inputType = document.querySelector('input[name="input-type"]:checked').value;
    const filter = filterSelect.value;
    const noise = noiseSelect.value;
    const threshold = thresholdSlider.value;
    const amplitude = noiseAmplSlider.value;

    let params = {
        input_method: inputType,
        filter: filter,
        noise: noise,
        threshold: threshold,
        amplitude: amplitude
  
    };

    // Si entrée = fichier, inclure le fichier audio
    if (inputType === 'file') {
        const file = audioFile.files[0];
        if (!file) {
            statusElement.textContent = "Veuillez sélectionner un fichier audio.";
            return;
        }
        // Utilise FormData pour envoyer le fichier
        const formData = new FormData();
        for (const key in params) {
            formData.append(key, params[key]);
        }
        formData.append('audio_file', file);

        // Utilise fetch pour POST le fichier, puis démarre le streaming via socket
        fetch('/upload_stream_file', {
            method: 'POST',
            body: formData
        }).then(response => response.json())
          .then(result => {
              // On suppose que le serveur retourne un nom de fichier temporaire
              params.filename = result.filename;
              socket.emit('start_stream', params);
          }).catch(() => {
              statusElement.textContent = "Erreur lors de l'envoi du fichier.";
          });
    } else {
        socket.emit('start_stream', params);
    }
}

stopBtn.addEventListener('click', () => {
    socket.emit('stop_stream');
    statusElement.textContent = "Streaming arrêté.";
    startBtn.disabled = false;
    stopBtn.disabled = true;
    startBtn.style.display = 'inline-block';
    stopBtn.style.display = 'none';
    audioQueue = [];
    playing = false;
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Efface le canvas
    if (audioElement) {
        audioElement.pause();
        audioElement.currentTime = 0; // Réinitialise la position de lecture
    }   
});
// --- FIN STREAMING ---

// Resize canvas to fit container
function resizeCanvas() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Draw waveform from decoded audio buffer
function drawWaveformFromBuffer(audioBuffer) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const data = audioBuffer.getChannelData(0);
    const step = Math.ceil(data.length / canvas.width);
    const amp = canvas.height / 2;
    ctx.beginPath();
    ctx.moveTo(0, amp);
    for (let i = 0; i < canvas.width; i++) {
        let min = 1.0, max = -1.0;
        for (let j = 0; j < step; j++) {
            const datum = data[(i * step) + j] || 0;
            if (datum < min) min = datum;
            if (datum > max) max = datum;
        }
        ctx.lineTo(i, (1 + min) * amp);
    }
    ctx.strokeStyle = "#00ff99";
    ctx.lineWidth = 2;
    ctx.stroke();
}

// Handle input type selection
microphoneRadio.addEventListener('change', () => {
    if (microphoneRadio.checked) {
        inputType = 'microphone';
        statusElement.textContent = 'Microphone activé';
        fileLabel.style.display = 'none';
    }
});
fileRadio.addEventListener('change', () => {
    if (fileRadio.checked) {
        inputType = 'file';
        statusElement.textContent = 'Fichier audio sélectionné';
        fileLabel.style.display = 'inline-block';
    }
});
jackRadio.addEventListener('change', () => {
    if (jackRadio.checked) {
        inputType = 'jack';
        fileLabel.style.display = 'none';
        statusElement.textContent = 'Jack: Connectez votre périphérique Jack';
    }
});

// Handle file selection
audioFile.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const url = URL.createObjectURL(file);
        if (audioElement) {
            audioElement.src = url;
        } else {
            audioElement = new Audio(url);
            audioElement.loop = true;
        }
        
    }
});

// Main: send parameters to server, receive and play processed audio, draw waveform
startBtn.addEventListener('click', async () => {
    // Si tu veux le mode streaming, utilise startStreaming()
    
    startStreaming();
});

// Download processed audio (non utilisé en streaming, mais conservé si besoin)
downloadBtn.onclick = () => {
    if (processedAudio.src) {
        const a = document.createElement('a');
        a.href = processedAudio.src;
        a.download = 'processed_audio.wav';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
};

thresholdSlider.addEventListener('input', () => {
    thValue = thresholdSlider.value;
    amplitude = noiseAmplSlider.value;
    audioVolume = signalAmplSlider.value;
    tau = systemTimeSlider.value;
    Xb = wellPosSlider.value;
    weellNum = wellNumSlider.value;


    socket.emit('update_parameters', {
        threshold: thValue,
        signalAmplitude: audioVolume,
        tau: tau,
        Xb: Xb, 
        noiseAmplitude: amplitude,
        weellNum: weellNum})
});

noiseAmplSlider.addEventListener('input', () => {
    thValue = thresholdSlider.value;
    amplitude = noiseAmplSlider.value;
    audioVolume = signalAmplSlider.value;
    tau = systemTimeSlider.value;
    Xb = wellPosSlider.value;
    weellNum = wellNumSlider.value;


    socket.emit('update_parameters', {
        threshold: thValue,
        signalAmplitude: audioVolume,
        tau: tau,
        Xb: Xb, 
        noiseAmplitude: amplitude,
        weellNum: weellNum})
});
systemTimeSlider.addEventListener('input', () => {
    thValue = thresholdSlider.value;
    amplitude = noiseAmplSlider.value;
    audioVolume = signalAmplSlider.value;
    tau = systemTimeSlider.value;
    Xb = wellPosSlider.value;
    weellNum = wellNumSlider.value;


    socket.emit('update_parameters', {
        threshold: thValue,
        signalAmplitude: audioVolume,
        tau: tau,
        Xb: Xb, 
        noiseAmplitude: amplitude,
        weellNum: weellNum})
});

wellPosSlider.addEventListener('input', () => {
    thValue = thresholdSlider.value;
    amplitude = noiseAmplSlider.value;
    audioVolume = signalAmplSlider.value;
    tau = systemTimeSlider.value;
    Xb = wellPosSlider.value;
    weellNum = wellNumSlider.value;
    socket.emit('update_parameters', {
        threshold: thValue,
        signalAmplitude: audioVolume,
        tau: tau,
        Xb: Xb, 
        noiseAmplitude: amplitude,
        weellNum: weellNum})
});
wellNumSlider.addEventListener('input', () => {
    thValue = thresholdSlider.value;
    amplitude = noiseAmplSlider.value;
    audioVolume = signalAmplSlider.value;
    tau = systemTimeSlider.value;
    Xb = wellPosSlider.value;
    weellNum = wellNumSlider.value;
    socket.emit('update_parameters', {
        threshold: thValue,
        signalAmplitude: audioVolume,
        tau: tau,
        Xb: Xb, 
        noiseAmplitude: amplitude,
        weellNum: weellNum})
});
signalAmplSlider.addEventListener('input', () => {
    thValue = thresholdSlider.value;
    amplitude = noiseAmplSlider.value;
    audioVolume = signalAmplSlider.value;
    tau = systemTimeSlider.value;
    Xb = wellPosSlider.value;
    weellNum = wellNumSlider.value;

    socket.emit('update_parameters', {
        threshold: thValue,
        signalAmplitude: audioVolume,
        tau: tau,
        Xb: Xb, 
        noiseAmplitude: amplitude,
        weellNum: weellNum})
});
volumeSlider.addEventListener('input', () => {
    const volume = volumeSlider.value;
    socket.emit('update_volume', { volume: volume });
});

filterSelect.addEventListener('change', () => {
    const filter = filterSelect.value;
    socket.emit('update_filter', { filter: filter , threshold: thresholdSlider.value, tau: systemTimeSlider.value, Xb: wellPosSlider.value, weellNum: wellNumSlider.value });
});

noiseSelect.addEventListener('change', () => {
    const noise = noiseSelect.value;
    socket.emit('update_noise', { noise: noise, amplitude: noiseAmplSlider.value});
});

