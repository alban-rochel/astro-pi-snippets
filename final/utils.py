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

# ASAP, this is the reference startup time, so that we don't get interrupted after 3 hours
start_time = datetime.now()
logfile("events.log", maxBytes=10000000)
logger.info("Starting at " + start_time.strftime("%Y/%m/%d %H:%M:%S"))

camera = PiCamera()
ephemeris = load('de421.bsp')
timescale = load.timescale()

# Init: file naming
base_folder = Path(__file__).parent.resolve()

def configure(config):
    """
    Configures the global variables used everywhere.
    """
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
    if not record_folder:
        record_folder = f"{base_folder}"
    logger.info("* Record folder " + record_folder)
    logger.info("... Configuring done")
    
def climate_code_to_text(climate_zone):
    """
    Converts our climate zone codes into human-readable text.
    https://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification
    """
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
    """
    Converts the ISS ground coordinates into coordinates in our climates map, and returns the corresponding climate code.
    """
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
    """
    Tells if it is time to stop the main loop (according to the run time configured)
    """
    return datetime.now() >= end_time

def get_current_time():
    """
    Returns a structure containing "now" as both time formats needed in the program.
    Every function needing time will take the returned structure as its input, and choose the proper entry.
    """
    current_time_dt = datetime.now()
    current_time_ts = timescale.now()
    return (current_time_dt, current_time_ts)

def wait_next_pass(time_tuple):
    """
    Waits until the configured duration has been elapsed since time_tuple
    """
    end_sleep_time = time_tuple[0] + timedelta(seconds = wait_time)
    current_time_dt = datetime.now()
    if current_time_dt < end_sleep_time:
        sleep((end_sleep_time - current_time_dt).total_seconds())
        
def position_iss(time_tuple):
    """
    Returns the ground position of the ISS at time_tuple.
    """
    return ISS.at(time_tuple[1]).subpoint()

def is_on_day_side(time_tuple):
    """
    Returns whether the ISS is on day side at time_tuple. Otherwise we see nothing.
    """
    return ISS.at(time_tuple[1]).is_sunlit(ephemeris)

def capture_image():
    """
    Gets an image from the camera.
    """
    camera.capture(rawCapture, format="bgr")
    image = np.copy(rawCapture.array)
    rawCapture.truncate(0)
    return image

def generate_save_name(base, time, extension):
    """
    Generates a timestamped file name. The timestamp is such that sorting in alphabetic order is also the chronological order.
    """
    time_str = time[0].strftime("%y%m%d_%H%M%S%f")
    return f"{record_folder}/{time_str}_{base}.{extension}"

def generate_base_capture_metadata(time, position,climate_code):
    """
    Generates the base metadata attached to any capture.
    """
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

def compute_stats(ndvi_indexes):
    """
    With a dictionary of counts of points for each NDVI index as the entry ([0, 10]), computes mean and standard deviation of indexes.
    """
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
