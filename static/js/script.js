let audioContext;
let analyser;
let microphone;
let dataArray;
let animationId;
let isRecording = false;
let audioElement;
let biquadFilter;
let gainNode;
let noiseBuffer;
let inputType = 'microphone'; // Default input type

const canvas = document.getElementById('audioCanvas');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const status = document.getElementById('status');
const audioFile = document.getElementById('audioFile');
const fileLabel = document.getElementById('fileLabel');

// Controls

const filterSelect = document.getElementById('filterSelect');
const noiseSelect = document.getElementById('noiseSelect');
const gainSlider = document.getElementById('gainSlider');
const frequencySlider = document.getElementById('frequencySlider');
const gainValue = document.getElementById('gainValue');
const frequencyValue = document.getElementById('frequencyValue');

// Input type
const microphoneRadio = document.getElementById('microphone');
const fileRadio = document.getElementById('file');
const jackRadio = document.getElementById('jack');

// Set canvas size
function resizeCanvas() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}

resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Update slider values
gainSlider.addEventListener('input', () => {
    gainValue.textContent = gainSlider.value;
    if (gainNode) {
        gainNode.gain.value = gainSlider.value / 50; // Scale 0-100 to 0-2
    }
});

frequencySlider.addEventListener('input', () => {
    const freq = frequencySlider.value;
    frequencyValue.textContent = freq + ' Hz';
    if (biquadFilter) {
        biquadFilter.frequency.value = freq;
    }
});

// Filter type change
filterSelect.addEventListener('change', () => {
    if (biquadFilter) {
        const filterType = filterSelect.value;
        switch(filterType) {
            case 'lowpass':
                biquadFilter.type = 'lowpass';
                break;
            case 'highpass':
                biquadFilter.type = 'highpass';
                break;
            case 'passband':
                biquadFilter.type = 'bandpass';
                break;
        }
    }
});

// Input type changes


// Radio button sync with select
microphoneRadio.addEventListener('change', () => {
    if (microphoneRadio.checked) {
        inputType = 'microphone';
        fileLabel.style.display = 'none';
    }
});

fileRadio.addEventListener('change', () => {
    if (fileRadio.checked) {
        inputType = 'file';
        status.textContent = 'Fichier audio sélectionné';
        fileLabel.style.display = 'inline-block';
    }
});

jackRadio.addEventListener('change', () => {
    if (jackRadio.checked) {
        inputType = 'jack';
        fileLabel.style.display = 'none';
        status.textContent = 'Jack: Connectez votre périphérique Jack';
    }
});

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

function setupAudioContext() {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    dataArray = new Uint8Array(analyser.frequencyBinCount);
    
    // Create audio processing nodes
    biquadFilter = audioContext.createBiquadFilter();
    gainNode = audioContext.createGain();
    
    // Set initial filter settings
    biquadFilter.type = filterSelect.value === 'passband' ? 'bandpass' : filterSelect.value;
    biquadFilter.frequency.value = frequencySlider.value;
    biquadFilter.Q.value = 1;
    
    // Set initial gain
    gainNode.gain.value = gainSlider.value / 50;
}

function generateNoise() {
    const noiseType = noiseSelect.value;
    if (noiseType === 'none') return null;
    
    const bufferSize = audioContext.sampleRate * 2;
    noiseBuffer = audioContext.createBuffer(1, bufferSize, audioContext.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    
    switch(noiseType) {
        case 'white':
            for (let i = 0; i < bufferSize; i++) {
                output[i] = Math.random() * 2 - 1;
            }
            break;
        case 'pink':
            let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
            for (let i = 0; i < bufferSize; i++) {
                const white = Math.random() * 2 - 1;
                b0 = 0.99886 * b0 + white * 0.0555179;
                b1 = 0.99332 * b1 + white * 0.0750759;
                b2 = 0.96900 * b2 + white * 0.1538520;
                b3 = 0.86650 * b3 + white * 0.3104856;
                b4 = 0.55000 * b4 + white * 0.5329522;
                b5 = -0.7616 * b5 - white * 0.0168980;
                output[i] = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362;
                output[i] *= 0.11;
                b6 = white * 0.115926;
            }
            break;
        case 'brown':
            let lastOut = 0;
            for (let i = 0; i < bufferSize; i++) {
                const white = Math.random() * 2 - 1;
                output[i] = (lastOut + (0.02 * white)) / 1.02;
                lastOut = output[i];
                output[i] *= 3.5;
            }
            break;
        case 'blue':
            let lastValue = 0;
            for (let i = 0; i < bufferSize; i++) {
                const white = Math.random() * 2 - 1;
                output[i] = white - lastValue;
                lastValue = white;
                output[i] *= 0.1;
            }
            break;
    }
    
    const noiseSource = audioContext.createBufferSource();
    noiseSource.buffer = noiseBuffer;
    noiseSource.loop = true;
    return noiseSource;
}

async function startMicrophone() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        microphone = audioContext.createMediaStreamSource(stream);
        
        // Connect audio chain: microphone -> filter -> gain -> analyser
        microphone.connect(biquadFilter);
        biquadFilter.connect(gainNode);
        gainNode.connect(analyser);
        
        // Add noise if selected
        const noiseSource = generateNoise();
        if (noiseSource) {
            const noiseGain = audioContext.createGain();
            noiseGain.gain.value = 0.1;
            noiseSource.connect(noiseGain);
            noiseGain.connect(analyser);
            noiseSource.start();
        }
        
        return true;
    } catch (err) {
        console.error('Erreur d\'accès au microphone:', err);
        status.textContent = 'Erreur: Impossible d\'accéder au microphone';
        return false;
    }
}

function startAudioFile() {
    if (!audioElement) {
        status.textContent = 'Veuillez sélectionner un fichier audio';
        return false;
    }
    
    const source = audioContext.createMediaElementSource(audioElement);
    
    // Connect audio chain: source -> filter -> gain -> analyser -> destination
    source.connect(biquadFilter);
    biquadFilter.connect(gainNode);
    gainNode.connect(analyser);
    analyser.connect(audioContext.destination);
    
    // Add noise if selected
    const noiseSource = generateNoise();
    if (noiseSource) {
        const noiseGain = audioContext.createGain();
        noiseGain.gain.value = 0.1;
        noiseSource.connect(noiseGain);
        noiseGain.connect(analyser);
        noiseSource.start();
    }
    
    audioElement.play();
    return true;
}

function startJack() {
    // Jack simulation - in a real implementation, this would connect to Jack Audio Connection Kit
    status.textContent = 'Jack: Simulation - connecté virtuellement';
    
    // Create a simple oscillator for demonstration
    const oscillator = audioContext.createOscillator();
    oscillator.frequency.setValueAtTime(440, audioContext.currentTime);
    oscillator.type = 'sine';
    
    // Connect through the same audio chain
    oscillator.connect(biquadFilter);
    biquadFilter.connect(gainNode);
    gainNode.connect(analyser);
    
    oscillator.start();
    return true;
}

function drawVisualization() {
    analyser.getByteFrequencyData(dataArray);
    
    ctx.fillStyle = 'rgba(0, 4, 40, 0.2)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const barWidth = canvas.width / dataArray.length;
    let x = 0;

    for (let i = 0; i < dataArray.length; i++) {
        let barHeight = dataArray[i];
        barHeight = (barHeight / 255) * canvas.height;

        const hue = (i / dataArray.length) * 360 + (Date.now() * 0.1) % 360;
        ctx.fillStyle = `hsl(${hue}, 80%, 60%)`;
        
        ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
        x += barWidth;
    }

    animationId = requestAnimationFrame(drawVisualization);
}

startBtn.addEventListener('click', async () => {
    if (!isRecording) {
        setupAudioContext();
        
        let success = false;
        
        if (inputType === 'microphone') {
            success = await startMicrophone();
        } else if (inputType === 'file') {
            success = startAudioFile();
        } else if (inputType === 'jack') {
            success = startJack();
        }
        
        if (success) {
            isRecording = true;
            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
            status.textContent = `Enregistrement en cours (${inputType})...`;
            status.classList.add('active');
            drawVisualization();
        }
    }
});

stopBtn.addEventListener('click', () => {
    if (isRecording) {
        isRecording = false;
        startBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        status.textContent = 'Arrêté';
        status.classList.remove('active');
        
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        
        if (audioContext) {
            audioContext.close();
        }
        
        if (audioElement) {
            audioElement.pause();
        }
        
        // Clear canvas
        ctx.fillStyle = 'rgba(0, 4, 40, 1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
});