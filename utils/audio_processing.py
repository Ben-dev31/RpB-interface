import numpy as np
import sounddevice as sd

#from x40_code import *

from .noises import *
from .filters import *
import os 
import librosa as lb




class AudioStream:
    def __init__(self, fs=44100, block_size=1024):
        self.fs = fs
        self.block_size = block_size
        self.stream = None
        self.stream_state = 'stopped'  # 'stopped', 'running', 'paused'

        #self.encoder_thread = threading.Thread(target=read_encoder)
        #self.encoder_thread.daemon = True

        self.input_methode = 'file'  # Default stream method ['file', 'live', 'jack]
        self.input_file_path = None

        self.data_pos = 0

        self.noise_id = 'none'  # Default noise type
        self.filter_id = 'diode'  # Default filter type

        self.noise_amplitude = 0.1  # Default noise amplitude
        self.threshold = 1.0  # Default threshold value
        self.signal_amplitude = 0.1  # Default signal amplitude

        self.tau = 0.5  # Default tau value
        self.Xb = 1.0  # Default Xb value
        self.weellNum = 1  # Default well number

        self.input_data = None  # Data for file input
        self.volume = 0.1  # Default volume level


        self.FILTERS = {
            "diode": diode_filter,
            "diode_clipper": rubber_zener_filter,
        }
        self.NOISES = {
            "none": lambda length, sr: np.zeros(length),
            "white": lambda length, sr: np.random.normal(0, 1, length),
            "pink": pink_noise,
            "brown": brownian_noise,
            "velvet": velvet_noise
        }
    
    def set_input_method(self, method):
        if method in ['file', 'live', 'jack']:
            self.input_methode = method
        else:
            raise ValueError(f"Input method '{method}' not recognized.")
    
    def set_input_file(self, file_path):
        if os.path.isfile(file_path):
            self.input_file_path = file_path
            self.input_data, self.fs = lb.load(file_path, sr=self.fs, mono=True)
            self.data_pos = 0
        else:
            raise FileNotFoundError(f"File '{file_path}' not found.")
    
    def set_parameters(self, threshold=None, signal_amplitude=None, noise_amplitude=None, tau=None, Xb=None, weellNum=None):
        if threshold is not None:
            self.threshold = threshold
        if signal_amplitude is not None:
            self.signal_amplitude = signal_amplitude
        if noise_amplitude is not None:
            self.noise_amplitude = noise_amplitude
        if tau is not None:
            self.tau = tau
        if Xb is not None:
            self.Xb = Xb
        if weellNum is not None:
            self.weellNum = weellNum    
    
    def set_noise(self, noise_id):
        if noise_id in self.NOISES:
            self.noise_id = noise_id
        else:
            raise ValueError(f"Noise type '{noise_id}' not recognized.")
    
    def set_filter(self, filter_id):
        if filter_id in self.FILTERS:
            self.filter_id = filter_id
        elif filter_id == 'none':
            self.filter_id = 'none'
        else:
            raise ValueError(f"Filter type '{filter_id}' not recognized.")
    

    def apply_filter(self,data,thr,filtre_id='diode', **kwargs) -> np.ndarray:
        """
        Applique un filtre au signal d'entrée.
        Arguments:
            data (numpy ndarray): Signal d'entrée à filtrer.
            thr (float): Seuil pour le filtre.
            filtre_id (str): Identifiant du filtre à appliquer.
            kwargs: Autres paramètres spécifiques au filtre.
        Returns:
            numpy ndarray: Signal filtré.
        """
        try:
            y = self.FILTERS[filtre_id](data, thr=thr, **kwargs)
        except KeyError or ValueError :
            return data  # Si le filtre n'est pas reconnu, retourne les données d'origine
        else:
            return y 

    def apply_noise(self,size, ampl, noise_id='none', **kwargs) -> np.ndarray:
        y = self.NOISES[noise_id](size,ampl, **kwargs)
        return y 


    def start(self):
        if self.stream is None:
            
            #self.encoder_thread.start()

            with sd.Stream(samplerate=self.fs, channels=1, dtype='float32', callback=self.callback,blocksize=self.block_size) as self.stream:
                print(f"Streaming live at {self.fs} Hz. Press Ctrl+C to stop.")
                self.stream_state = 'running'
                try:
                    while True:
                        if self.stream_state == 'running':
                            sd.sleep(1)
                        else:
                            print("Stream is stopped. Waiting for start command...")
                            self.stream_state = 'stopped'
                            #self.encoder_thread.close()  # Close the encoder thread if needed
                            break
               
                except KeyboardInterrupt:
                    print("\nStopped.")
                    #self.encoder_thread.close()
    
    def set_noise_amplitude(self, amplitude):
        self.noise_amplitude = amplitude
            
    
    def callback(self, indata, outdata, frames, time, status):
        global counter
        #b = np.abs(get_state())*0.3
        
        inputdata = indata if self.input_methode != 'file' else self.input_data[self.data_pos:self.data_pos + self.block_size]
        inputdata = np.resize(inputdata, (self.block_size,))  # Ensure inputdata is the correct size

        inputdata *= self.signal_amplitude  # Apply signal amplitude
        # Application du bruit 
        noise = self.apply_noise(inputdata.shape[0],ampl=self.noise_amplitude,noise_id=self.noise_id,frames=frames,fs=self.fs,base_freq=200, octaves = 3,persistence = 0.5,lacunarity=1.0)

        '''
        Les parametres de cette fonction son general pour tout types de bruit, certaines sont ignore en fonction du type de bruit 
        voire la fonction apply_noise pour les parametres passe a cette fonction
        '''
        # Creation du signal bruite'
        signal = inputdata + noise
        
        # Filtrage 
        signal = self.apply_filter(signal,thr=self.threshold, filtre_id=self.filter_id, tau=self.tau, Xb=self.Xb, weellNum=self.weellNum)
        '''
        Les parametre de cette fonction sont comune a tous les filtres.
        Vour le module filters
        '''
    
        audio = np.reshape(signal, (self.block_size, 1))

        if self.input_methode == 'file':
            if self.data_pos + self.block_size >= len(self.input_data):
                self.data_pos = 0
            else:
                # Avance la position des données pour le prochain bloc
                self.data_pos += self.block_size

        outdata[:] = audio/np.max(np.abs(audio))*self.volume
        

    def stop(self):
        
        if self.stream is not None:
            self.stream_state = 'stopped'
            self.stream.stop()
            self.stream.close()
            self.stream = None
            #self.encoder_thread.close()


    def is_active(self):
        return self.stream is not None and self.stream.active

    def set_volume(self, volume):
        """
        Set the volume of the audio stream.
        Arguments:
            volume (float): Volume level between 0.0 and 1.0.
        """
        self.volume = volume
    
    def get_query_devices(self):
        return sd.query_devices()

