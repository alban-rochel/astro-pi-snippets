from utils import *

config = {
    "climates_file": "climates_map.png",
    "camera_resolution": (4056, 3040),
    "duration_minutes": 1,
    "acquisition_period_seconds": 10,
    "record_folder": "captures"
}

configure(config)

# Prepare the structure for registering the data used to compute statistics
data_store = dict()
for climate_code in [0, 5, 10, 15, 20, 51, 52, 53, 101, 102, 151, 152, 153, 201, 202]:
    data_store[climate_code] = dict()
    for ndvi_score in range(11):
        data_store[climate_code][ndvi_score] = 0

while not experiment_done():
    now = get_current_time()
    
    has_daylight = is_on_day_side(now)
    has_daylight = True # TODO REMOVE
    
    position = position_iss(now)
    climate_code = get_climate_code(position)
    
    data_to = genere_infos_capture(now, position, climate_code)
    
    if has_daylight:
        # Capture image
        image = capture_image()
        cropped = crop_porthole(image)
        
        # Compute where land is visible
        clouds = get_clouds_mask(cropped)
        land = get_land_mask(cropped)
        visible_land_mask = cv2.bitwise_and(porthole, land)
        visible_land_mask = cv2.bitwise_and(visible_land_mask, cv2.bitwise_not(clouds))
        
        # Compute NDVI indexes, ranging in [0, 10]
        ndvi = compute_ndvi(cropped)
        
        # If on known climate zone, accumulate the number of points for each index
        if climate_code > 0:
            rough_climate_zone = climate_code/10
            for ndvi_index in range(11):
                lower = np.array(ndvi_index, dtype = "uint8")
                upper = np.array(ndvi_index, dtype = "uint8")
                count = np.count_nonzero(cv2.bitwise_and(cv2.inRange(ndvi, lower, upper), visible_land_mask))
                data_store[rough_climate_zone][ndvi_index] += count
                data_store[climate_zone][ndvi_index] += count
        
    wait_next_pass(now)

# OK, we're done, but we have time to compute statistics

for climate_code in [0, 5, 10, 15, 20, 51, 52, 53, 101, 102, 151, 152, 153, 201, 202]:
    total = 0
    mean = 0
    stdev = 0
    for ndvi_index in range(11):
        total += data_store[climate_code][ndvi_index]
        mean += ndvi_index * data_store[climate_code][ndvi_index]
    if total > 0:
        mean /= total
        # compute standard deviation
        for ndvi_index in range(11):
            stdev += (mean - ndvi_index) * (mean - ndvi_index) * data_store[climate_code][ndvi_index]
        stdev /= total
        stdev = sqrt(stdev)
    data_store[climate_code]["total"] = total
    data_store[climate_code]["mean"] = mean
    data_store[climate_code]["stdev"] = stdev

        
