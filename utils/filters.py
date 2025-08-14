
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

def bistable_filter(signal: np.ndarray, tau: float, Xb: float, weellNum: int) -> np.ndarray:
    """
    Filtre bistable

    Arguments:
    signal (numpy ndarray): signal d'entrée
    tau (float): temps de relaxation
    Xb (float): seuil de basculement
    weellNum (int): nombre de puits

    Returns:
    numpy ndarray: signal filtré
    """
    # Implémentation simplifiée du filtre bistable
    state = 0
    output = np.zeros_like(signal)
    
    for i, x in enumerate(signal):
        if x > Xb:
            state = 1
        elif x < -Xb:
            state = -1
        
        output[i] = state * tau
    
    return output