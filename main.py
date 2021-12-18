#module pour régler l'attente
from skyfield.api import load
from orbit import ISS
from time import sleep
from picamera import PiCamera
from datetime import datetime,timedelta
heure_de_debut = datetime.now()
heure_de_fin = heure_de_debut+timedelta(minutes=178)
ephemeris = load('de421.bsp')
timescale = load.timescale()
camera = PiCamera()
camera.resolution = (2400,1200)
while datetime.now()<heure_de_fin:
    lumiere_du_jour = ISS.at (timescale.now()).is_sunlit(ephemeris)
    if lumiere_du_jour:
        print ("on fait une photo")
        camera.capture("rien.jpg")
        sleep(1.5)
        print ("fini")
        sleep (3)
    else:
        print ("pas de photo!!!")
    