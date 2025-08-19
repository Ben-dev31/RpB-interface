import numpy as np

def rubber_zener_filter(x, a=2, **kwargs):
    """
    Filtre rubber zener

    Arguments:
    x (numpy ndarry) : données à filtrer
    a (float) : coefficient de non linéarité

    Returns:
    y (numpy ndarry) : données filtrées
    """
    x = np.asarray(x).flatten()
    y = np.zeros_like(x)
    y[x > a] = x[x > a] - a
    y[x < -a] = x[x < -a] + a
    return y

def diode_filter(u, v_th=1.5, **kwargs):
    '''
    Fonction qui retourne la tension de sortie d'un diode en fonction de la tension d'entrée.

    u (numpy ndarray): tension de sortie
    v_th (float) : tension de seuil

    return (numpy ndarray) : tension de sortie
    '''
    u = np.asarray(u).flatten()
    return np.where(u < v_th, 0, u - v_th)

def bistable_filter(signal, tau=None, Xb=None, weellNum=None, **kwargs):
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
    signal = np.asarray(signal).flatten()
    if tau is None:
        tau = kwargs.get('tau', 0.5)
    if Xb is None:
        Xb = kwargs.get('Xb', 1.0)
    if weellNum is None:
        weellNum = kwargs.get('weellNum', 1)
    state = 0
    output = np.zeros_like(signal)
    for i, x in enumerate(signal):
        if x > Xb:
            state = 1
        elif x < -Xb:
            state = -1
        output[i] = state * tau
    return output