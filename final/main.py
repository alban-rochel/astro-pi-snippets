from utils import *

"""
Our experiments aims at evaluating if the climate zone
as defined by Koppen (https://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification)
can be inferred by NDVI statistics.

When on dayside, we acquire an image, remove the porthole (mask),
remove the water (threshold on blue layer) and the clouds (threshold on grayscale),
compute NDVI, scaling it in the [0, 10] range of integers.

Thanks to a map of climates, we determine which climate we observe, and
we accumulate the measurements.

We are able to compute the mean and stdev of NDVI for every image AND every
climate zone.
We hope to be able to extract correlations, and maybe clusters of mean/stdev by zone.

Data is recorded so that we are able to replay the computations with other tunings
on the ground if needed.
"""

config = {
    "climates_file": "climates_map.png", # Map of climate zones, gray value = zone
    "camera_resolution": (4056, 3040),   # Acquisition size
    "duration_minutes": 178,             # Should be enough to stop before 3 hours
    "acquisition_period_seconds": 10,    # Check at least every 10 seconds
    "record_folder": ""                  # Captured data recorded in the current folder
}

configure(config)

# Prepare the structure for registering the data used to compute statistics
data_store = dict()
# These are all our climate zone values
for climate_code in [0, 5, 10, 15, 20, 51, 52, 53, 101, 102, 151, 152, 153, 201, 202]:
    data_store[climate_code] = dict()
    for ndvi_score in range(11): # NDVI indexes will be scaled in the [0, 10] range
        data_store[climate_code][ndvi_score] = 0

# While we still have time left
while not experiment_done():
    now = get_current_time()
    
    has_daylight = is_on_day_side(now)
    
    position = position_iss(now)
    climate_code = get_climate_code(position)
    
    # Prepare the base metadata info we will save for this sample
    capture_metadata = generate_base_capture_metadata(now, position, climate_code)
    # Generate a timestamped name for this metadata
    metadata_file_name = generate_save_name("info", now, "json")
    try:
        if has_daylight:
            logger.info("On daylight side, acquiring and evaluating image")
        
            # Capture image
            image = capture_image()
            # We save disk space and computation time by removing everything around the porthole
            cropped = crop_porthole(image)
            # Generate a timestamped name for this image (saved for later analysis or replay)
            image_file_name = generate_save_name("image", now, "jpg")
            cv2.imwrite(image_file_name, cropped,  [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        
            # Compute where land is visible, on the cropped image
            # Get the clouds mask
            clouds = get_clouds_mask(cropped)
            # Get the land mask (= not water)
            land = get_land_mask(cropped)
            # Combine with the porthole mask
            visible_land_mask = cv2.bitwise_and(porthole, land)
            visible_land_mask = cv2.bitwise_and(visible_land_mask, cv2.bitwise_not(clouds))
            # Generate a timestamped name for the mask, and save it
            land_mask_file_name = generate_save_name("mask", now, "png")
            cv2.imwrite(land_mask_file_name, visible_land_mask)
        
            # Compute NDVI indexes, ranging in [0, 10]
            ndvi = compute_ndvi(cropped)
            # Generate a timestamped name for the ndvi values, and save it
            ndvi_file_name = generate_save_name("ndvi", now, "png")
            cv2.imwrite(ndvi_file_name, ndvi)
        
            # If on known climate zone, accumulate the number of points for each index
            rough_climate_code = int(climate_code/10) # int(climate_code/10) is the "rough-grain climate zone" (temperate, tropical...). If results are not exploitable in fine-grain zones, this may be better.
            capture_metadata["ndvi"] = dict() # The scores will be saved with the image metadata (companion) json file
            for ndvi_index in range(11):
                # For each NDVI value, count the number of pixels on the visible land
                lower = np.array(ndvi_index, dtype = "uint8")
                upper = np.array(ndvi_index, dtype = "uint8")
                count = np.count_nonzero(cv2.bitwise_and(cv2.inRange(ndvi, lower, upper), visible_land_mask))
                capture_metadata["ndvi"][ndvi_index] = count
                # Accumulate for the global computations
                if rough_climate_code in data_store:
                    data_store[rough_climate_code][ndvi_index] += count
                if climate_code in data_store:
                    data_store[climate_code][ndvi_index] += count
            # Compute stats for the image
            stats = compute_stats(capture_metadata["ndvi"])
            capture_metadata["ndvi"]["mean"] = stats[0]
            capture_metadata["ndvi"]["stdev"] = stats[1]
        else:
            logger.info("On night side, ignoring")
        
        # Save json companion file (metadata)
        with open(metadata_file_name, "w") as outfile:
            json.dump(capture_metadata, outfile, indent=2)
            
    except Exception as e:
        logger.error(f"Caught: {e}")
    
    wait_next_pass(now)

logger.info("Writing session statistics")
# OK, we're done, but we have time to compute statistics for the whole run
now = get_current_time()
final_stats = dict()
for climate_code in [0, 5, 10, 15, 20, 51, 52, 53, 101, 102, 151, 152, 153, 201, 202]:
    final_stats[climate_code] = dict()
    final_stats[climate_code]["zone"] = climate_code_to_text(climate_code)
    stats = compute_stats(data_store[climate_code])
    final_stats[climate_code]["mean"] = stats[0]
    final_stats[climate_code]["stdev"] = stats[1]

# Save global results json file
final_file_name = generate_save_name("final", now, "json")
with open(final_file_name, "w") as outfile:
    json.dump(final_stats, outfile, indent=2)
    
logger.info("Experiment done, thanks to the ESA and the Raspberry Pi Foundation!")
