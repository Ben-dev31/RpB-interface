// Variables globales
let isPlaying = false;
let currentTime = 0;
const totalTime = 8; // 8 secondes

// Contrôles de lecture
const playBtn = document.getElementById('playBtn');
const progressFill = document.getElementById('progressFill');

playBtn.addEventListener('click', togglePlay);

function togglePlay() {
    isPlaying = !isPlaying;
    playBtn.textContent = isPlaying ? '⏸' : '▶';
    
    if (isPlaying) {
        startPlayback();
    } else {
        stopPlayback();
    }
}

let playbackInterval;
function startPlayback() {
    playbackInterval = setInterval(() => {
        currentTime += 0.1;
        if (currentTime >= totalTime) {
            currentTime = totalTime;
            stopPlayback();
        }
        updateProgress();
    }, 100);
}

function stopPlayback() {
    clearInterval(playbackInterval);
    isPlaying = false;
    playBtn.textContent = '▶';
}

function updateProgress() {
    const percentage = (currentTime / totalTime) * 100;
    progressFill.style.width = percentage + '%';
}

// Contrôles des sliders
const thresholdSlider = document.getElementById('thresholdSlider');
const thresholdValue = document.getElementById('thresholdValue');
const amplitudeSlider = document.getElementById('amplitudeSlider');
const amplitudeValue = document.getElementById('amplitudeValue');

thresholdSlider.addEventListener('input', function() {
    thresholdValue.textContent = parseFloat(this.value).toFixed(2);
    updateCharts();
});

amplitudeSlider.addEventListener('input', function() {
    amplitudeValue.textContent = parseFloat(this.value).toFixed(2);
    updateCharts();
});

// Configuration des graphiques
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false
        }
    },
    scales: {
        x: {
            grid: {
                color: '#e0e0e0'
            }
        },
        y: {
            grid: {
                color: '#e0e0e0'
            }
        }
    }
};

// Profil du filtre
const filterCtx = document.getElementById('filterChart').getContext('2d');
const filterChart = new Chart(filterCtx, {
    type: 'line',
    data: {
        labels: Array.from({length: 100}, (_, i) => (i - 50) / 10),
        datasets: [{
            data: Array.from({length: 100}, (_, i) => {
                const x = (i - 50) / 10;
                if (x < 0) return x;
                if (x < 2) return 0;
                return x - 2;
            }),
            borderColor: '#ffa500',
            backgroundColor: 'transparent',
            tension: 0
        }, {
            data: Array.from({length: 100}, (_, i) => {
                const x = (i - 50) / 10;
                return x === 2 ? 4 : null;
            }),
            borderColor: '#0066cc',
            backgroundColor: 'transparent',
            pointRadius: 0,
            showLine: false
        }]
    },
    options: chartOptions
});

// Signal pur

async function loadAudioChart(filename) {
    const pureSignalCtx = document.getElementById('pureSignalChart').getContext('2d');
    try {
        const response = await fetch(`/get_audio_data?filename=${filename}`);
        const data = await response.json();

        // Détruit l'ancien graphe s’il existe

        if (window.waveformChart) {
        window.waveformChart.destroy();
        }

        // Crée le nouveau graphique
        window.waveformChart = new Chart(pureSignalCtx, {
        type: 'line',
        data: {
        labels: data.x, // Axe X = temps
        datasets: [{
            label: 'Signal Audio',
            data: data.y,
            borderColor: 'blue',
            borderWidth: 1,
            pointRadius: 0, // pas de points
        }]
        },
        options: {
        scales: {
            x: {
            type: 'linear',
            title: { display: true, text: 'Temps (s)' }
            },
            y: {
            title: { display: true, text: 'Amplitude' }
            }
        },
        responsive: true,
        plugins: {
            legend: { display: false },
            title: { display: true, text: 'Signal audio brut' }
        },
        elements: {
            line: {
            tension: 0.1 // lissage léger
            }
        }
        }
        });
    } catch (err) {
        console.error("Erreur chargement audio :", err);
    }
}


// Signal après filtre
const filteredSignalCtx = document.getElementById('filteredSignalChart').getContext('2d');
const filteredSignalChart = new Chart(filteredSignalCtx, {
    type: 'line',
    data: {
        labels: Array.from({length: 1000}, (_, i) => i * 300),
        datasets: [{
            data: pureSignalData.map(val => Math.max(-0.05, Math.min(0.05, val * 0.8))),
            borderColor: '#00aa00',
            backgroundColor: 'rgba(0, 170, 0, 0.3)',
            pointRadius: 0,
            borderWidth: 1,
            fill: true
        }]
    },
    options: {
        ...chartOptions,
        scales: {
            ...chartOptions.scales,
            x: {
                ...chartOptions.scales.x,
                title: {
                    display: true,
                    text: 'Temps (s)'
                }
            }
        }
    }
});

function updateCharts() {
    // Mise à jour des graphiques basée sur les contrôles
    const threshold = parseFloat(thresholdSlider.value);
    const amplitude = parseFloat(amplitudeSlider.value);
    
    // Mise à jour du signal filtré
    const newFilteredData = pureSignalData.map(val => {
        const processed = val * amplitude;
        return Math.max(-threshold/10, Math.min(threshold/10, processed * 0.8));
    });
    
    filteredSignalChart.data.datasets[0].data = newFilteredData;
    filteredSignalChart.update('none');
}

// Gestion des filtres radio
document.querySelectorAll('input[name="filter"]').forEach(radio => {
    radio.addEventListener('change', updateCharts);
});

document.querySelectorAll('input[name="noise"]').forEach(radio => {
    radio.addEventListener('change', updateCharts);
});