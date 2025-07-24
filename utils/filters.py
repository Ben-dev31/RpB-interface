
import numpy as np

def rubber_zener_filter(x:np.ndarray,a :float = 2) -> np.ndarray:
    """
    Filtre rubber zener

    Arguments:
    x (numpy ndarry) : données à filtrer
    a (float) : coefficient de non linéarité

    Returns:
    y (numpy ndarry) : données filtrées
    """
    y = np.zeros_like(x)
    y[x > a] = x[x > a] - a    # cas ou le signal x > a
    y[x < -a] = x[x < -a] + a  # cas ou le signal x < a
    return y

def diode_filter(u:np.ndarray, v_th : float =1.5) -> np.ndarray:
    '''
    Fonction qui retourne la tension de sortie d'un diode en fonction de la tension d'entrée.

    u (numpy ndarray): tension de sortie
    v_th (float) : tension de seuil

    return (numpy ndarray) : tension de sortie
    '''
    return np.where(u < v_th, 0, u - v_th)