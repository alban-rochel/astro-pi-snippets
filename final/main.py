from utils import *

config = {
    "climates_file": "climates_map.png",
    "camera_resolution": (4056, 3040),
    "duration_minutes": 178,
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
    
    position = position_iss(now)
    climate_code = get_climate_code(position)
    
    capture_metadata = generate_base_capture_metadata(now, position, climate_code)
    metadata_file_name = generate_save_name("info", now, "json")
    
    if has_daylight:
        # Capture image
        image = capture_image()
        cropped = crop_porthole(image)
        image_file_name = generate_save_name("image", now, "jpg")
        cv2.imwrite(image_file_name, cropped,  [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        
        # Compute where land is visible
        clouds = get_clouds_mask(cropped)
        land = get_land_mask(cropped)
        visible_land_mask = cv2.bitwise_and(porthole, land)
        visible_land_mask = cv2.bitwise_and(visible_land_mask, cv2.bitwise_not(clouds))
        land_mask_file_name = generate_save_name("mask", now, "png")
        cv2.imwrite(land_mask_file_name, visible_land_mask)
        
        # Compute NDVI indexes, ranging in [0, 10]
        ndvi = compute_ndvi(cropped)
        ndvi_file_name = generate_save_name("ndvi", now, "png")
        cv2.imwrite(ndvi_file_name, ndvi)
        
        # If on known climate zone, accumulate the number of points for each index
        rough_climate_code = int(climate_code/10)
        capture_metadata["ndvi"] = dict()
        for ndvi_index in range(11):
            lower = np.array(ndvi_index, dtype = "uint8")
            upper = np.array(ndvi_index, dtype = "uint8")
            count = np.count_nonzero(cv2.bitwise_and(cv2.inRange(ndvi, lower, upper), visible_land_mask))
            capture_metadata["ndvi"][ndvi_index] = count
            if rough_climate_code in data_store:
                data_store[rough_climate_code][ndvi_index] += count
            if climate_code in data_store:
                data_store[climate_code][ndvi_index] += count
        stats = compute_stats(capture_metadata["ndvi"])
        capture_metadata["ndvi"]["mean"] = stats[0]
        capture_metadata["ndvi"]["stdev"] = stats[1]

    with open(metadata_file_name, "w") as outfile:
        json.dump(capture_metadata, outfile)
        
    wait_next_pass(now)

# OK, we're done, but we have time to compute statistics
now = get_current_time()
final_stats = dict()
for climate_code in [0, 5, 10, 15, 20, 51, 52, 53, 101, 102, 151, 152, 153, 201, 202]:
    final_stats[climate_code] = dict()
    final_stats[climate_code]["zone"] = climate_code_to_text(climate_code)
    stats = compute_stats(data_store[climate_code])
    final_stats[climate_code]["mean"] = stats[0]
    final_stats[climate_code]["stdev"] = stats[1]

final_file_name = generate_save_name("final", now, "json")
with open(final_file_name, "w") as outfile:
    json.dump(final_stats, outfile)
