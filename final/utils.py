from image_processing import *
from picamera import PiCamera
from picamera.array import PiRGBArray

from orbit import ISS
from skyfield.api import load
from time import sleep

from datetime import datetime,timedelta
from pathlib import Path
import json
import math

from logzero import logger, logfile

# ASAP
start_time = datetime.now()
logger.info("Starting at " + start_time.strftime("%Y/%m/%d %H:%M:%S"))

camera = PiCamera()
ephemeris = load('de421.bsp')
timescale = load.timescale()

# Init: file naming
base_folder = Path(__file__).parent.resolve()

def configure(config):
    logger.info("Configuring...")
    #camera.resolution = (3280, 2464) # Full FOV
    #camera.resolution = (1664, 1232) # Binned, full FOV
    camera.resolution = config["camera_resolution"] # Binned, full FOV
    logger.info("* Resolution configured: " + str(camera.resolution))
    global rawCapture
    rawCapture = PiRGBArray(camera)
    global end_time
    end_time = start_time + timedelta(minutes=config["duration_minutes"])
    logger.info("* Duration configured: " + str(config["duration_minutes"]) + " minutes -> " + end_time.strftime("%Y/%m/%d %H:%M:%S"))
    global wait_time
    wait_time = config["acquisition_period_seconds"]
    global climates_map
    climates_map = cv2.imread(config["climates_file"])
    logger.info("* Climates map: " + config["climates_file"])
    global record_folder
    record_folder = config["record_folder"]
    logger.info("* Record folder " + record_folder)
    logger.info("... Configuring done")
    
#https://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification
def climate_code_to_text(climate_zone):
    # Rough classification, which is Precise_classification/10
    if climate_zone == 5:
        return "Tropical"
    elif climate_zone == 10:
        return "Dry"
    elif climate_zone == 15:
        return "Temperate"
    elif climate_zone == 20:
        return "Continental"
    # Precise classification
    elif climate_zone == 51:
        return "Tropical rainforest"
    elif climate_zone == 52:
        return "Tropical monsoon"
    elif climate_zone == 53:
        return "Savanna" # Tropical
    elif climate_zone == 101:
        return "Desert"
    elif climate_zone == 102:
        return "Semi arid" # Dry
    elif climate_zone == 151:
        return "Humid subtropical"
    elif climate_zone == 152:
        return "Oceanic"
    elif climate_zone == 153:
        return "Mediterranean" # Temperate
    elif climate_zone == 201:
        return "Humid continental"
    elif climate_zone == 202:
        return "Subarctic" # Continental
    else:
        return "Other"
    
def get_climate_code(iss_position):
    # Positive latitude: north
    # Negative latitude: south
    # Positive longitude: east of Greenwich
    # Negative longitude: west of Greenwich
    row = math.floor(-179.5/90 * iss_position.latitude.degrees + 179.5)
    col = math.floor(359.5/180 * iss_position.longitude.degrees + 359.5)
    row = min(max(0, row), 359)
    col = min(max(0, col), 719)
    return climates_map[row,col,0]

def experiment_done():
    return datetime.now() >= end_time

def get_current_time():
    current_time_dt = datetime.now()
    current_time_ts = timescale.now()
    return (current_time_dt, current_time_ts)

def wait_next_pass(tuple_temps):
    end_sleep_time = tuple_temps[0] + timedelta(seconds = wait_time)
    current_time_dt = datetime.now()
    if current_time_dt < end_sleep_time:
        sleep((end_sleep_time - current_time_dt).total_seconds())
        
def position_iss(tuple_temps):
    return ISS.at(tuple_temps[1]).subpoint()

def is_on_day_side(tuple_temps):
    return ISS.at(tuple_temps[1]).is_sunlit(ephemeris)

def capture_image():
    return cv2.imread("51845638376_d241c3f433_o.jpg")
    #camera.capture(rawCapture, format="bgr")
    #image = np.copy(rawCapture.array)
    #rawCapture.truncate(0)
    #return image

def generate_save_name(base, time, extension):
    time_str = time[0].strftime("%y%m%d_%H%M%S%f")
    return f"{record_folder}/{time_str}_{base}.{extension}"

def generate_base_capture_metadata(time, position,climate_code):
    data = {
        "time":
            {
            "year": time[0].strftime("%y"),
            "month": time[0].strftime("%m"),
            "day": time[0].strftime("%d"),
            "hour":time[0].strftime("%H"),
            "minute": time[0].strftime("%M"),
            "second": time[0].strftime("%S"),
            "micro": time[0].strftime("%f")
            },
        "coords":
            {
                "lat": position.latitude.degrees,
                "lon": position.longitude.degrees,
            },
        "climate":
            {
                "code": int(climate_code),
                "precise_zone": climate_code_to_text(climate_code),
                "rough_zone": climate_code_to_text(climate_code/10)
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

def compte_nombre_indices(image, indice):
    lower = np.array(indice, dtype = "uint8")
    upper = np.array(indice, dtype = "uint8")
    mask = cv2.inRange(image, lower, upper)
    pixel_count = np.count_nonzero(mask)
    return pixel_count

def compute_stats(ndvi_indexes):
    total = 0
    mean = 0
    stdev = 0
    for index in range(11):
        total += ndvi_indexes[index]
        mean += index * ndvi_indexes[index]
    if total > 0:
        mean = mean / total
        for index in range(11):
            stdev += (mean - index) * (mean - index) * ndvi_indexes[index]
        stdev /= total
        stdev = math.sqrt(stdev)
    return (mean, stdev)
