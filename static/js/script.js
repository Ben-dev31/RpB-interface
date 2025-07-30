// Variables globales
let pureSignalData = [];
let gfilename = null;

// Récupération des éléments DOM
const thresholdSlider = document.getElementById('thresholdSlider');
const thresholdValue = document.getElementById('thresholdValue');
const amplitudeSlider = document.getElementById('amplitudeSlider');
const amplitudeValue = document.getElementById('amplitudeValue');
const volumeSignal = document.getElementById('amplitudeSignalValue');
const volumeSlider = document.getElementById('VolumeSlider');
const filterRadios = document.querySelectorAll('input[name="filter"]');
const noiseSelector = document.getElementById('noiseDropdown');

// Options de base pour Chart.js
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
        x: { grid: { color: '#e0e0e0' }, title: { display: true, text: 'Temps (s)' } },
        y: { grid: { color: '#e0e0e0' }, title: { display: true, text: 'Amplitude' } }
    },
    elements: { line: { tension: 0.1 } }
};

// Initialisation des graphiques
const filterChart = new Chart(
    document.getElementById('filterChart').getContext('2d'),
    {
        type: 'line',
        data: { labels: [], datasets: [{ data: [], borderColor: '#ffa500', backgroundColor: 'transparent', borderWidth: 2, pointRadius: 0 }] },
        options: chartOptions
    }
);

const pureSignalChart = new Chart(
    document.getElementById('pureSignalChart').getContext('2d'),
    {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Signal Audio', data: [], borderColor: 'blue', borderWidth: 1, pointRadius: 0 }] },
        options: { ...chartOptions, plugins: { ...chartOptions.plugins, title: { display: true, text: 'Signal audio brut' } } }
    }
);

const filteredSignalChart = new Chart(
    document.getElementById('filteredSignalChart').getContext('2d'),
    {
        type: 'line',
        data: { labels: [], datasets: [{ data: [], borderColor: '#00aa00', backgroundColor: 'rgba(0,170,0,0.3)', pointRadius: 0, borderWidth: 1, fill: false }] },
        options: chartOptions
    }
);

// Fonctions utilitaires
function updateSliderValue(slider, valueElem) {
    valueElem.textContent = parseFloat(slider.value).toFixed(2);
}

// Chargement et affichage du signal audio
async function loadAudioChart(filename) {
    gfilename = filename;
    try {
        const response = await fetch(`/get_audio_data?filename=${filename}`);
        const data = await response.json();
        if (!data || !data.x || !data.y) throw new Error("Données audio invalides");
        pureSignalData = data.y;
        pureSignalChart.data.labels = data.x;
        pureSignalChart.data.datasets[0].data = data.y;
        pureSignalChart.update('none');
        updateCharts();
    } catch (err) {
        console.error("Erreur chargement audio :", err);
    }
}

// Mise à jour du graphique du filtre
async function updateProfileChart() {
    const filterType = document.querySelector('input[name="filter"]:checked').value;
    const threshold = parseFloat(thresholdSlider.value);
    try {
        const response = await fetch(`/get_filter_data?filtre=${filterType}&threshold=${threshold}`);
        const data = await response.json();
        if (!data || !data.x || !data.y) throw new Error("Données de filtre invalides");
        filterChart.data.labels = data.x;
        filterChart.data.datasets[0].data = data.y;
        filterChart.update('none');
    } catch (err) {
        console.error("Erreur chargement filtre :", err);
    }
}

// Mise à jour du signal filtré (serveur)
async function updateFilteredSignal() {
    const filterType = document.querySelector('input[name="filter"]:checked').value;
    const threshold = parseFloat(thresholdSlider.value);
    const amplitude = parseFloat(amplitudeSlider.value);
    const noise = document.querySelector('input[name="noise"]:checked').value;
    try {
        const response = await fetch(`/get_filtered_signal?filtre=${filterType}&threshold=${threshold}&amplitude=${amplitude}&noise=${noise}&filename=${gfilename}`);
        const data = await response.json();
        if (!data || !data.x || !data.y) throw new Error("Données de signal filtré invalides");
        filteredSignalChart.data.labels = data.x;
        filteredSignalChart.data.datasets[0].data = data.y;
        filteredSignalChart.update('none');
    } catch (err) {
        console.error("Erreur chargement signal filtré :", err);
    }
}

// Mise à jour locale du signal filtré (si besoin)
function updateCharts() {
    const threshold = parseFloat(thresholdSlider.value);
    const amplitude = parseFloat(amplitudeSlider.value);
    // Mise à jour locale (optionnelle, dépend de ton usage)
    const newFilteredData = pureSignalData.map(val => Math.max(-threshold/10, Math.min(threshold/10, val * amplitude * 0.8)));
    filteredSignalChart.data.datasets[0].data = newFilteredData;
    filteredSignalChart.update('none');
    //updateProfileChart();
}

// Fonction unique pour mettre à jour tous les graphiques depuis le serveur
async function updateAllCharts() {
    const filterType = document.querySelector('input[name="filter"]:checked').value;
    const threshold = parseFloat(thresholdSlider.value);
    const amplitude = parseFloat(amplitudeSlider.value);
    const noise = document.getElementById("noiseDropdown").value;
    if (!gfilename) return;

    try {
        const audioRes = await fetch(`/get_graph_data?filename=${gfilename}&filtre=${filterType}&threshold=${threshold}&amplitude=${amplitude}&noise=${noise}&filename=${gfilename}`);
        const Data = await audioRes.json();
        if (!Data || !Data.xp || !Data.yf) throw new Error("Données audio invalides");
       
        // 2. Profil du filtre
        filterChart.data.labels = Data.xp;
        filterChart.data.datasets[0].data = Data.yp;
        filterChart.update('none');

        // 3. Signal filtré
        filteredSignalChart.data.labels = Data.xf;
        filteredSignalChart.data.datasets[0].data = Data.yf;
        filteredSignalChart.update('none');
    } catch (err) {
        console.error("Erreur lors de la mise à jour des graphiques :", err);
    }
}

// Événements sliders et radios
thresholdSlider.addEventListener('input', () => {
    updateSliderValue(thresholdSlider, thresholdValue);
    updateAllCharts();
});
amplitudeSlider.addEventListener('input', () => {
    updateSliderValue(amplitudeSlider, amplitudeValue);
    updateAllCharts();
});
volumeSlider.addEventListener('input', () => {
    updateSliderValue(volumeSlider, volumeSignal);
    updateAllCharts();
});

filterRadios.forEach(radio => radio.addEventListener('change', updateAllCharts));
noiseSelector.addEventListener('change', updateAllCharts);

// Exporte la fonction pour l'appel initial

document.addEventListener('DOMContentLoaded', () => {// Récupération du nom de fichier depuis le template

    updateAllCharts();
    
});
