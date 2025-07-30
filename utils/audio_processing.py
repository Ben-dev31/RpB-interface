import numpy as np
import sounddevice as sd

from x40_code import *

import time
import threading

from noises import *
from filters import diode_filter,rubber_zener_filter


FILTERS = [
    diode_filter,
    rubber_zener_filter
]

NOISES = [
    white_noise,
    gaussian_noise,
    perlin_stream
]

def apply_filter(data,thr,filtre_id=1) -> np.ndarray:
    y = FILTERS[filtre_id](data, thr=thr)
    return y 

def apply_noise(size, ampl,noise_id=0,**kwargs):
    y = NOISES[noise_id](size,ampl, **kwargs)
    return y 

# Filter settings
fs = 44100  # Change to 48000/192000 if supported
block_size = 1024

# Audio streaming
def callback(indata, outdata, frames, time, status):

    global counter
    b = np.abs(get_state())*0.3
    
    inputdata = indata
    # Application du bruit 
    noise = apply_noise(inputdata.shape,ampl=b,noise_id=2,frames=frames,fs=fs,base_freq=200, octaves = 3,persistence = 0.5,lacunarity=1.0)
    '''
    Les parametres de cette fonction son general pour tout types de bruit, certaines sont ignore en fonction du type de bruit 
    voire la fonction apply_noise pour les parametres passe a cette fonction
    '''
    # Creation du signal bruite'
    signal = inputdata + noise
    
    # Filtrage 
    #signal = apply_filter(signal,thr=1.5, filtre_id=0)
    '''
    Les parametre de cette fonction sont comune a tous les filtres.
    Vour le module filters
    '''
 
    outdata[:] = signal*0.1
    
 
# Get device indexes if needed
print(sd.query_devices())

def run_streaming():
    with sd.Stream(samplerate=fs, channels=2, dtype='float32', callback=callback,blocksize=block_size):
        print(f"Streaming live at {fs} Hz. Press Ctrl+C to stop.")
        try:
            while True:
                sd.sleep(100)
        except KeyboardInterrupt:
            print("\nStopped.")
            encoder_thread.close()
        
encoder_thread = threading.Thread(target = read_encoder)
encoder_thread.daemon = True
encoder_thread.start()

run_streaming()
