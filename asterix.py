import cv2
from orbit import ISS
from skyfield.api import load
from time import sleep
from picamera import PiCamera
from picamera.array import PiRGBArray
from datetime import datetime,timedelta
from pathlib import Path
import json
import numpy as np
import math

def contrast_stretch(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)
    
    out_min = 0.0
    out_max = 255.0
    
    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min
    
    return out

def calc_ndvi(image):
    b, g, r = cv2.split(image)
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom==0] = 0.01
    ndvi = (b.astype(float) - r) / bottom
    return ndvi

# ASAP
start_time = datetime.now()
#end_time = heure_de_debut + timedelta(minutes=178)
end_time = start_time + timedelta(minutes=1)

"""
Init: camera
"""
camera = PiCamera()
#camera.resolution = (3280, 2464) # Full FOV
#camera.resolution = (1664, 1232) # Binned, full FOV
camera.resolution = (1376, 768) # Binned, full FOV
rawCapture = PiRGBArray(camera)

# Init: ephemeris
ephemeris = load('de421.bsp')
timescale = load.timescale()

# Init: file naming
base_folder = Path(__file__).parent.resolve()

"""
Init: climate map
"""
climates_map = cv2.imread("climats_nb.png")

def climate_type_to_string(climate_zone):
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

def get_climate_type(latitude_degrees, longitude_degrees):
    # Positive latitude: north
    # Negative latitude: south
    # Positive longitude: east of Greenwich
    # Negative longitude: west of Greenwich
    #line = round (180-2*(position_ISS.latitude.degrees))
    row = math.floor(-179.5/90 * latitude_degrees + 179.5)
    col = math.floor(359.5/180 * longitude_degrees + 359.5)
    row = min(max(0, row), 359)
    col = min(max(0, col), 719)
    #print("Row " + str(row) + " for " + str(latitude_degrees))
    return climates_map[row,col,0]
    
print("Paris: " + climate_type_to_string(get_climate_type(48.3, 2.3)))
print("Moscow: " + climate_type_to_string(get_climate_type(55.7, 37.6)))
print("Sydney: " + climate_type_to_string(get_climate_type(-33.8, 151.2)))
print("Rio de Janeiro: " + climate_type_to_string(get_climate_type(-22.9, -43.2)))
print("Caracas: " + climate_type_to_string(get_climate_type(10.4, -66.8)))

#exit(0)

while datetime.now() < end_time:
    # All the following must be as synchronized as possible (little to no processing between each)
    current_time_dt = datetime.now()
    current_time_ts = timescale.now()
    earth_location = ISS.at(current_time_ts).subpoint()
    camera.capture(rawCapture, format="bgr")
    
    # Now, process our data
    capture_time_txt = current_time_dt.strftime("%y%m%d_%H%M%S%f")
    
    is_on_day_side = True # ISS.at(current_time_ts).is_sunlit(ephemeris)
    
    data = {}
    data = {
        "time":
            {
            "year": current_time_dt.strftime("%y"),
            "month": current_time_dt.strftime("%m"),
            "day": current_time_dt.strftime("%d"),
            "hour":current_time_dt.strftime("%H"),
            "minute": current_time_dt.strftime("%M"),
            "second": current_time_dt.strftime("%S"),
            "micro": current_time_dt.strftime("%f")
            },
        "coords":
            {
                "lat": earth_location.latitude.degrees,
                "lon": earth_location.longitude.degrees,
            },
        "sunlit": is_on_day_side
        }
    
    
    if is_on_day_side:
        print(earth_location)
        base_image = rawCapture.array
        contrast1 = contrast_stretch(base_image)
        ndvi = calc_ndvi(contrast1)
        processed_image = contrast_stretch(ndvi)
        image_filename = f"{base_folder}/capture/{capture_time_txt}_image.jpg"
        contrast_filename = f"{base_folder}/capture/{capture_time_txt}_constrast.jpg"
        ndvi_filename = f"{base_folder}/capture/{capture_time_txt}_ndvi.jpg"
        processed_filename = f"{base_folder}/capture/{capture_time_txt}_processed.jpg"
        cv2.imwrite(image_filename, base_image)
        cv2.imwrite(contrast_filename, contrast1)
        cv2.imwrite(ndvi_filename, ndvi)
        cv2.imwrite(processed_filename, processed_image)
        data["base_image"] = image_filename
        data["processed_image"] = processed_filename
    
    json_filename = f"{base_folder}/capture/{capture_time_txt}_data.json"
    with open(json_filename, "w") as outfile:
        json.dump(data, outfile)
    
    rawCapture.truncate(0)
    
    end_sleep_time = current_time_dt + timedelta(seconds = 1)
    current_time_dt = datetime.now()
    
    if current_time_dt < end_sleep_time:
        sleep((end_sleep_time - current_time_dt).total_seconds())
        
print("DONE")
    

    