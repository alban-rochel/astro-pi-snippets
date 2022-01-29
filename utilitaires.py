from picamera import PiCamera
from picamera.array import PiRGBArray

from orbit import ISS
from skyfield.api import load
from time import sleep

from datetime import datetime,timedelta
from pathlib import Path
import json
import numpy as np
import math

from logzero import logger, logfile

import cv2

# ASAP
start_time = datetime.now()
logger.info("Démarrage à " + start_time.strftime("%Y/%m/%d %H:%M:%S"))

processed = cv2.imread("processed.png")

camera = PiCamera()
ephemeris = load('de421.bsp')
timescale = load.timescale()

# Init: file naming
base_folder = Path(__file__).parent.resolve()

def configure(config):
    logger.info("Configuration...")
    #camera.resolution = (3280, 2464) # Full FOV
    #camera.resolution = (1664, 1232) # Binned, full FOV
    camera.resolution = config["resolution_camera"] # Binned, full FOV
    logger.info("* Résolution configurée: " + str(camera.resolution))
    global rawCapture
    rawCapture = PiRGBArray(camera)
    global end_time
    end_time = start_time + timedelta(minutes=config["duree_minutes"])
    logger.info("* Durée configurée: " + str(config["duree_minutes"]) + " minutes -> " + end_time.strftime("%Y/%m/%d %H:%M:%S"))
    global wait_time
    wait_time = config["frequence_acquisition_secondes"]
    global climates_map
    climates_map = cv2.imread(config["fichier_climats"])
    logger.info("* Carte climats: " + config["fichier_climats"])
    global dossier_captures
    dossier_captures = config["dossier_enregistrement"]
    logger.info("* Dossier d'enregistrement: " + dossier_captures)
    logger.info("... Configuration terminée")
    
    
def convertir_code_climat_en_texte(climate_zone):
    if climate_zone == 51:
        return "Equatorial"
    elif climate_zone == 52:
        return "Mousson"
    elif climate_zone == 53:
        return "Savane"
    elif climate_zone == 101:
        return "Desertique"
    elif climate_zone == 102:
        return "Semi aride"
    elif climate_zone == 151:
        return "Subtropical humide"
    elif climate_zone == 152:
        return "Oceanique"
    elif climate_zone == 153:
        return "Mediterraneen"
    elif climate_zone == 201:
        return "Continental humide"
    elif climate_zone == 202:
        return "Subarctique"
    else:
        return "Autre"
    
def recuperer_code_climat(iss_position):
    # Positive latitude: north
    # Negative latitude: south
    # Positive longitude: east of Greenwich
    # Negative longitude: west of Greenwich
    row = math.floor(-179.5/90 * iss_position.latitude.degrees + 179.5)
    col = math.floor(359.5/180 * iss_position.longitude.degrees + 359.5)
    row = min(max(0, row), 359)
    col = min(max(0, col), 719)
    return climates_map[row,col,0]

def experience_terminee():
    return datetime.now() >= end_time

def recuperer_temps():
    current_time_dt = datetime.now()
    current_time_ts = timescale.now()
    return (current_time_dt, current_time_ts)

def attendre(tuple_temps):
    end_sleep_time = tuple_temps[0] + timedelta(seconds = wait_time)
    current_time_dt = datetime.now()
    if current_time_dt < end_sleep_time:
        sleep((end_sleep_time - current_time_dt).total_seconds())
        
def position_iss(tuple_temps):
    return ISS.at(tuple_temps[1]).subpoint()

def cote_jour(tuple_temps):
    return ISS.at(tuple_temps[1]).is_sunlit(ephemeris)

def capture_image():
    camera.capture(rawCapture, format="bgr")
    image = np.copy(rawCapture.array)
    rawCapture.truncate(0)
    return image

def genere_nom_sauvegarde(nom, temps, extension):
    temps_str = temps[0].strftime("%y%m%d_%H%M%S%f")
    return f"{dossier_captures}/{temps_str}_{nom}.{extension}"

def genere_infos_capture(temps, position, code_climat):
    data = {
        "time":
            {
            "year": temps[0].strftime("%y"),
            "month": temps[0].strftime("%m"),
            "day": temps[0].strftime("%d"),
            "hour":temps[0].strftime("%H"),
            "minute": temps[0].strftime("%M"),
            "second": temps[0].strftime("%S"),
            "micro": temps[0].strftime("%f")
            },
        "coords":
            {
                "lat": position.latitude.degrees,
                "lon": position.longitude.degrees,
            }
        }
    return data

def sauvegarde_image(image, nom):
    chemin_image = f"{base_folder}/{nom}"
    logger.debug("Enregistrement image {chemin_image}")
    cv2.imwrite(chemin_image, image)

def sauvegarde_infos_capture(donnees, nom):
    chemin_donnees = f"{base_folder}/{nom}"
    logger.debug("Enregistrement donnees {chemin_donnees}")
    with open(chemin_donnees, "w") as outfile:
        json.dump(donnees, outfile, indent=2)
        
def traitement_image(image):
    return processed

def compte_nombre_indices(image, indice):
    lower = np.array(indice, dtype = "uint8")
    upper = np.array(indice, dtype = "uint8")
    mask = cv2.inRange(image, lower, upper)
    pixel_count = np.count_nonzero(mask)
    return pixel_count