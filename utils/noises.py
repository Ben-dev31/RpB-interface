import numpy as np

def _ensure_1d(x):
    """Force x à être un tableau 1D (mono)."""
    x = np.asarray(x)
    if x.ndim == 2 and x.shape[1] == 1:
        return x[:, 0]
    return x

def pink_noise(length, sr=None, **kwargs):
    if isinstance(length, (tuple, list, np.ndarray)):
        if isinstance(length, (tuple, list)):
            length = length[0]
        else:
            length = length.shape[0]
    white = np.random.randn(length)
    b = [0.02109238, 0.07113478, 0.68873558]
    a = [1, -1.73472577, 0.7660066]
    pink = np.zeros(length)
    for i in range(2, length):
        pink[i] = b[0]*white[i] + b[1]*white[i-1] + b[2]*white[i-2] - a[1]*pink[i-1] - a[2]*pink[i-2]
    pink = pink / (np.max(np.abs(pink)) + 1e-8)
    return pink

def brownian_noise(length, sr=None, **kwargs):
    if isinstance(length, (tuple, list, np.ndarray)):
        if isinstance(length, (tuple, list)):
            length = length[0]
        else:
            length = length.shape[0]
    white = np.random.randn(length)
    brown = np.cumsum(white)
    brown = brown / (np.max(np.abs(brown)) + 1e-8)
    return brown

def velvet_noise(length, sr=None, **kwargs):
    pink = pink_noise(length)
    velvet = np.cumsum(pink)
    velvet = velvet / (np.max(np.abs(velvet)) + 1e-8)
    return velvet

def white_noise(length, sr=None, **kwargs):
    if isinstance(length, (tuple, list, np.ndarray)):
        if isinstance(length, (tuple, list)):
            length = length[0]
        else:
            length = length.shape[0]
    return np.random.normal(0, 1, length)


