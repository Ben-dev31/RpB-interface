import numpy as np

def pink_noise(length,sr=None):
    """
    Génère un bruit rose (pink noise) de longueur 'length'.
    """
    # Méthode du filtre IIR simple
    b = [0.02109238, 0.07113478, 0.68873558]
    a = [1, -1.73472577, 0.7660066]
    white = np.random.randn(length)
    pink = np.zeros(length)
    for i in range(2, length):
        pink[i] = b[0]*white[i] + b[1]*white[i-1] + b[2]*white[i-2] - a[1]*pink[i-1] - a[2]*pink[i-2]
    pink = pink / np.max(np.abs(pink))
    return pink

def brownian_noise(length,sr=None):
    """
    Génère un bruit brownien (brownian noise) de longueur 'length'.
    """
    # Bruit brownien = intégrale du bruit blanc
    white = np.random.randn(length)
    brown = np.cumsum(white)
    brown = brown / np.max(np.abs(brown))
    return brown

def velvet_noise(length, sr=None):
    """
    Génère un bruit velvet de longueur 'length'.
    """
    # Velvet noise est une forme de bruit rose
    pink = pink_noise(length)
    velvet = np.cumsum(pink)
    velvet = velvet / np.max(np.abs(velvet))
    return velvet
