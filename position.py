# On va utiliser le module orbit, qui nous donne les positions de plusieurs objets célestes.
# Mais en pratique, on va uniquement utiliser le sous-module ISS. C'est ce qu'on dit ici :
from orbit import ISS

# Ca, c'est juste parce que c'est amusant : ce module nous donne la grande ville
# la plus proche de certaines coordonnées.
import reverse_geocoder

# Time, c'est le module qui s'occupe du temps. On va l'utiliser pour attendre un peu.
import time

# Datetime, c'est le module qui s'occupe des dates. On utilise son sous-module datetime (oui, le sous-module a le même nom que le module !)
from datetime import datetime

# On va faire 10 fois les opérations suivantes :
for i in range(0, 10):
    # On demande au module datetime quelle est l'heure actuelle, et on stocke dans la variable appellée maintenant.
    maintenant = datetime.now()
    # Pour afficher la date et l'heure, on dit qu'on va "formatter" l'image avec jour/mois/année heure/minute/seconde
    maintenant_texte = maintenant.strftime("%d/%m/%y %H:%M:%S")
    # On récupère la position de l'ISS dans une variable position_ISS.
    # On demande cette position avec le sous-module ISS du module orbit.
    position_ISS = ISS.coordinates()
    # position_ISS n'est pas juste une valeur. C'est un objet complexe,
    # avec des sous-objets.
    # Si on veut la latitude, on utilise position_ISS.latitude.
    # Mais la latitude elle-même est un objet complexe !
    # Si on veut la latitude en degrés, on utilise position_ISS.latitude.degrees
    # La fonction pour trouver la ville la plus proche veut une paire de
    # latitude et longitude en degrés.
    # C'est l'objet qu'on crée juste là :
    coordinate_pair = ( position_ISS.latitude.degrees, position_ISS.longitude.degrees)
    # Et maintenant, on demande à la fonction "search" du module reverse_geocoder
    # de nous retourner la ville la plus proche.
    # On met ca dans la variable info_ville.
    info_ville = reverse_geocoder.search(coordinate_pair)
    # Le problème, c'est que info_ville est aussi un objet complexe ! C'est une liste
    # d'infos, par ordre croissant de distance.
    # On veut la ville la plus proche, on prend celle d'indice 0 (0 = 1er, 1 = 2eme, etc.)
    info_ville_la_plus_proche = info_ville[0]
    # On a les infos de la ville la plus proche ! Maintenant, il faut extraire
    # le nom de la ville.
    # info_ville_la_plus_proche est un "dictionnaire". C'est-à-dire que c'est comme une liste,
    # sauf qu'on ne lui donne pas un numéro d'objet, mais un nom, en texte.
    # Ici, le nom de la ville est associé à "name".
    nom_ville = info_ville_la_plus_proche["name"]
    # On affiche ! On n'oublie pas de convertir les valeurs numériques en texte avec str()
    print(maintenant_texte + " - Latitude: "+ str(position_ISS.latitude.degrees) +
          " - Longitude: " + str(position_ISS.longitude.degrees) +
          " - Ville la plus proche: " + nom_ville)
    # On attend 30 secondes avant de recommencer
    time.sleep(30)

    