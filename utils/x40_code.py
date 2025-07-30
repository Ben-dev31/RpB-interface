import time
from gpiozero import Button

# Initialisation des broches du codeur rotatif
clk = Button(16, pull_up=True)
dt = Button(15, pull_up=True)
reset_button = Button(14, pull_up=True)  # Bouton de remise à zéro du compteur

last_clk_state = clk.is_pressed  # Sauvegarde le dernier état de CLK

# Initialiser le compteur
counter = 0
def get_state():
    global counter
    return counter 
    
def read_encoder():
    global last_clk_state, counter
    while True:
        current_clk_state = clk.is_pressed
        if current_clk_state != last_clk_state:  # Reconnaître un changement d'état
            if current_clk_state:
                if dt.is_pressed != current_clk_state:
                    counter += 1  # Rotation dans le sens des aiguilles d'une montre
                    direction = "Dans le sens des aiguilles d'une montre"
                else:
                    counter -= 1  # Rotation dans le sens inverse des aiguilles d'une montre
                    direction = "Dans le sens inverse des aiguilles d'une montre"
                #print(f"Sens de rotation: {direction}")
                print(f"Position actuelle: {counter}")
                print("------------------------------")
            last_clk_state = current_clk_state
        time.sleep(0.001)  # courte pause pour économiser le temps de l'unité centrale

def reset_counter():
    global counter
    counter = 0
    print("Contre-réinitialisation !")
    print("------------------------------")

# Ajouter un gestionnaire d'événement pour le bouton de réinitialisation
reset_button.when_pressed = reset_counter
'''
print("Test du capteur [appuyez sur CTRL+C pour terminer le test]")

try:
    read_encoder()  # Lancer la fonction de lecture du codeur
except KeyboardInterrupt:
    print("Le programme a été interrompu par l'utilisateur")
'''

