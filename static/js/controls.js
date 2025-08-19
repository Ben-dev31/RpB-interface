

// static/js/controls.js
document.addEventListener('DOMContentLoaded', () => {
    const filterSelect = document.getElementById('filterSelect');
    const thresholdSlider = document.getElementById('thresholdSlider');
    const noiseSlider = document.getElementById('noiseSlider');
    const thresholdValue = document.getElementById('thresholdValue');
    const noiseValue = document.getElementById('noiseAmpl');
    const systemTimeSlider = document.getElementById('systemTimeSlider');
    const systemTimeValue = document.getElementById('systemTimeValue');
    const wellPosSlider = document.getElementById('wellPosSlider');
    const wellPosValue = document.getElementById('wellPosValue');
    const wellNumSlider = document.getElementById('weellNumSlider');
    const wellNumValue = document.getElementById('weellNumValue');
    const signalAmplSlider = document.getElementById('signalAmplSlider');
    const signalAmplValue = document.getElementById('signalAmplValue');
    const volumeSlider = document.getElementById('VolumeSlider');
    const volumeValue = document.getElementById('volume');

    const fileRadio = document.getElementById('file');
    

    thresholdValue.textContent = thresholdSlider.value;
    noiseValue.textContent = noiseSlider.value;
    systemTimeValue.textContent = `${systemTimeSlider.value} Hz`;
    wellPosValue.textContent = wellPosSlider.value;
    wellNumValue.textContent = wellNumSlider.value;
    signalAmplValue.textContent = signalAmplSlider.value;
    volumeValue.textContent = `${volumeSlider.value} %`;


    thresholdSlider.addEventListener('input', () => {
        thresholdValue.textContent = thresholdSlider.value;
    });
    noiseSlider.addEventListener('input', () => {
        noiseValue.textContent = noiseSlider.value;
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
    signalAmplSlider.addEventListener('input', () => {
        signalAmplValue.textContent = signalAmplSlider.value;
    });
    volumeSlider.addEventListener('input', () => {
        volumeValue.textContent = `${volumeSlider.value} %`;
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