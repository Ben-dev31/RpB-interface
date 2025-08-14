

// static/js/controls.js
document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const filterSelect = document.getElementById('filterSelect');
    const noiseSelect = document.getElementById('noiseSelect');
    const thresholdSlider = document.getElementById('thresholdSlider');
    const frequencySlider = document.getElementById('noiseSlider');
    const thresholdValue = document.getElementById('thresholdValue');
    const noiseValue = document.getElementById('noiseAmpl');
    const systemTimeSlider = document.getElementById('systemTimeSlider');
    const systemTimeValue = document.getElementById('systemTimeValue');
    const wellPosSlider = document.getElementById('wellPosSlider');
    const wellPosValue = document.getElementById('wellPosValue');
    const wellNumSlider = document.getElementById('weellNumSlider');
    const wellNumValue = document.getElementById('weellNumValue');
    const audioVolumeSlider = document.getElementById('VolumeSlider');
    const audioVolumeValue = document.getElementById('VolumeValue');
    const microphoneRadio = document.getElementById('microphone');
    const fileRadio = document.getElementById('file');
    const jackRadio = document.getElementById('jack');
    const processedAudio = document.getElementById('processedAudio');


    thresholdSlider.addEventListener('input', () => {
        thresholdValue.textContent = thresholdSlider.value;
    });
    frequencySlider.addEventListener('input', () => {
        noiseValue.textContent = frequencySlider.value;
    });
    systemTimeSlider.addEventListener('input', () => {
        systemTimeValue.textContent = `${systemTimeSlider.value} Hz`;
    });
    wellPosSlider.addEventListener('input', () => {
        wellPosValue.textContent = wellPosSlider.value;
    });
    wellNumSlider.addEventListener('input', () => {
        wellNumValue.textContent = wellNumSlider.value;
    });
    audioVolumeSlider.addEventListener('input', () => {
        audioVolumeValue.textContent = audioVolumeSlider.value;
    });

    if(filterSelect.value === 'bistable') {
            document.querySelector('.dynamic-control-group').style.display = 'flex';
    }
    else {
        document.querySelector('.dynamic-control-group').style.display = 'none';
    }

    filterSelect.addEventListener('change', () => {
        if(filterSelect.value === 'bistable') {
            document.querySelector('.dynamic-control-group').style.display = 'flex';
        }
        else {
            document.querySelector('.dynamic-control-group').style.display = 'none';
        }
    });

    if(fileRadio.checked) {
        fileLabel.style.display = 'block';
    }
    else {
        fileLabel.style.display = 'none';
    }



});