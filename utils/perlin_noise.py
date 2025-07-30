import ctypes
import numpy as np
import soundfile as sf
import pathlib


libs_path = pathlib.Path(__file__).parent.parent.joinpath('libs/noises')   # Chemin vers le dossier libs
if not libs_path.exists():
    raise FileNotFoundError(f"Le dossier {libs_path} n'existe pas. Assurez-vous que les bibliothèques C sont compilées et placées dans ce dossier.")
# Charger la librairie
lib = ctypes.CDLL(f"{libs_path}/PerlinLibs/libperlin.so")  # .dll si Windows

# Signature de la fonction
lib.generate_samples.argtypes = [
    ctypes.POINTER(ctypes.c_float),  # out array
    ctypes.c_int,                    # count
    ctypes.c_float,                  # base_freq
    ctypes.c_int,                    # octaves
    ctypes.c_float,                  # persistence
    ctypes.c_float,                  # lacunarity
    ctypes.c_int                     # sample_rate
]
lib.generate_samples.restype = None

lib_stream = ctypes.CDLL(f'{libs_path}/PerlinLibs/libperlin_stream.so')
lib_stream.init_perlin()
lib_stream.generate_stream_block.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_int,
    ctypes.c_float,
    ctypes.c_int,
    ctypes.c_float,
    ctypes.c_float,
    ctypes.c_int
]
lib_stream.generate_stream_block.restype = None


def perlin_noise(size, fs = 44100, base_freq = 20.0, octaves = 5,persistence = 0.5,lacunarity=2.0, ampl = 1.0):

    # Allouer un tableau en numpy (float32)
    samples = np.zeros(size[0], dtype=np.float32)

    # Appel de la fonction C
    lib.generate_samples(
        samples.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        size[0],
        base_freq,        # base_freq
        octaves,          # octaves
        persistence,        # persistence
        lacunarity,        # lacunarity
        fs          # sample_rate
    )

    # Normaliser et sauvegarder
    samples /= np.max(np.abs(samples))

    
    return np.array([samples])*ampl


def perlin_stream(size, ampl = 1,frames=None, fs = 44100, base_freq = 20.0, octaves = 5,persistence = 0.5,lacunarity=2.0,**kwargs) -> np.ndarray:

    if frames is None:
        try:
            frames = kwargs['frames']

        except KeyError:
            raise KeyError
        except Exception as e:
            raise e.with_traceback()

    try:
        fs = kwargs['fs']
        base_freq = kwargs['base_freq']
        octaves = kwargs['octaves']
        persistence = kwargs['persistence']
        lacunarity = kwargs['lacunarity']
    except:
        pass


    data = np.zeros(size)
    buffer = np.zeros(frames, dtype=np.float32)
    lib_stream.generate_stream_block(
        buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        frames,
        base_freq,
        octaves,
        persistence,
        lacunarity,
        fs
    )
    buffer /= np.max(np.abs(buffer)) + 1e-8  # évite division par zéro
    buffer = buffer*ampl 
    data[:] = buffer.reshape(-1, 1)

    return data

if __name__ == "__main__":

        # Paramètres audio
    duration = 5  # secondes
    sr = 44100
    count = duration * sr

    samples = perlin_noise((count,1))

    sf.write("perlin_array2.wav", samples, sr)
    print("Fichier 'perlin_array.wav' généré.")
