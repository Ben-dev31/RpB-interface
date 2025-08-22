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

def multi_well_C1(x, N, Xb):
    """
    Potentiel multi-puits défini par morceaux :
    - C¹ continu entre puits internes,
    - Bords extrêmes gauche et droite divergents (pas tronqués).

    Paramètres :
        x   : vecteur numpy des abscisses
        N   : nombre de puits
        Xb  : demi-largeur de chaque puits
    """
    L = 2 * Xb
    x0_list = [ (i - (N - 1)/2) * L for i in range(N) ]
    U = np.zeros_like(x)

    for i, x0 in enumerate(x0_list):
        if i == 0:  # premier puits : prolongé à gauche
            mask = x <= x0 + Xb
        elif i == N - 1:  # dernier puits : prolongé à droite
            mask = x >= x0 - Xb
        else:  # puits internes
            mask = (x >= x0 - Xb) & (x <= x0 + Xb)

        U[mask] = -0.5 * (x[mask] - x0)**2 + (1 / (4 * Xb**2)) * (x[mask] - x0)**4

    return U

def multi_well_gradient(x, N:int = 1, Xb:float = 1):
    """
    Version scalaire du potentiel multi-puits défini par morceaux.
    Entrée : x (float)
    Retour : U(x) (float)

    - N : nombre de puits
    - Xb : demi-largeur du domaine d’un puits
    """
    L = 2 * Xb
    x0_list = [ (i - (N - 1)/2) * L for i in range(N) ]

    for i, x0 in enumerate(x0_list):
        if i == 0 and x <= x0 + Xb:
            return -(x - x0) + (1 / (Xb**2)) * (x - x0)**3
        elif i == N - 1 and x >= x0 - Xb:
            return -(x - x0) + (1 / (Xb**2)) * (x - x0)**3
        elif 0 < i < N - 1 and (x0 - Xb <= x <= x0 + Xb):
            return -(x - x0) + (1 / (Xb**2)) * (x - x0)**3

    return 0.0 # En dehors de tout puits (hors bords)


def bistable_filter(signal, **kwargs):
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
    tau = 1/ kwargs.get('tau', 0.5)
    Xb = kwargs.get('Xb', 1.0)
    weellNum = kwargs.get('weellNum', 1)
    dt = kwargs.get("dt",1./44100)  # Assuming a sample rate of 44100 Hz
    init = kwargs.get("initial_value",-Xb)

    print(f"Applying bistable filter with tau={tau}, Xb={Xb}, weellNum={weellNum}, dt={dt}")

    signal = np.asarray(signal).flatten()
    X = np.zeros_like(signal)
    X[0] = -init  # condition initiale

    for i in range(len(signal)-1):
        dU_dx = multi_well_gradient(X[i], weellNum, Xb)
        X[i+1] = X[i] + dt/tau * (-dU_dx + signal[i])

    return X
        