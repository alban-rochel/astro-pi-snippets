### CHARGEMENT DES MODULES ###
# Module pour vérifier si l'ISS est du côté illuminé
from skyfield.api import load
# Module pour calculer la position de l'ISS à toute heure
from orbit import ISS
# Module pour pouvoir faire attendre le programme
from time import sleep
# Module pour récupérer des images de la caméra
from picamera import PiCamera
# Modules pour gérer le temps
from datetime import datetime,timedelta
### FIN CHARGEMENT DES MODULES ###


### INITIALISATIONS ###

# On récupère l'heure de début (maintenant !)
heure_de_debut = datetime.now()
# On calcule l'heure après laquelle on veut s'arrêter : heure de début + 178 minutes (un peu moins de 3 heures)
heure_de_fin = heure_de_debut+timedelta(minutes=178)

# On initialise ce dont on aura besoin pour les calculs d'illumination de l'ISS
ephemeris = load('de421.bsp')
timescale = load.timescale()

# On initialise la caméra
camera = PiCamera()
camera.resolution = (2400,1200)

### FIN INITIALISATIONS ###

### BOUCLE PRINCIPALE ###
# Tant que l'heure actuelle est avant l'heure de fin (qu'on a calculée plus haut)
while datetime.now()<heure_de_fin:
    # On met dans la variable lumiere_du_jour une valeur True si on est illuminé, ou False sinon.
    lumiere_du_jour = ISS.at (timescale.now()).is_sunlit(ephemeris)
    
    # Si lumiere_du_jour est vrai/True, alors...
    if lumiere_du_jour:
        print ("on fait une photo")
        camera.capture("rien.jpg")
        sleep(1.5)
        print ("fini")
        sleep (3)
    else:
        print ("pas de photo!!!")
### FIN BOUCLE PRINCIPALE
        
### TRAITEMENTS DE FIN DE PROGRAMME ###
### FIN TRAITEMENTS DE FIN DE PROGRAMME ###