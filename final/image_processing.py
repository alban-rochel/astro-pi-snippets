import cv2
import numpy as np

clouds_threshold = 200 # Grayscale values over this are clouds
land_threshold = 60    # Blue values under this are water

# Crop area to remove porthole
crop_left = 800
crop_right = 3700
crop_top = 50
crop_bottom = 2900

porthole = cv2.imread("porthole_mask.png", cv2.IMREAD_GRAYSCALE)

def crop_porthole(image):
    """
    Crops the image to fit the porthole
    """
    return image[crop_top:crop_bottom, crop_left:crop_right]

def get_clouds_mask(image):
    """
    Returns the mask of clouds
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    (dummy, clouds) = cv2.threshold(gray,clouds_threshold,255,cv2.THRESH_BINARY)
    return clouds

def get_land_mask(image):
    """
    Returns the mask of land
    """
    (blue, green, red) = cv2.split(image)
    (dummy, land) = cv2.threshold(blue,land_threshold,255,cv2.THRESH_BINARY)
    return land

def compute_ndvi(image):
    """
    Computes NDVI indexes, scaled in the [0, 10] integer range. No contrast expansion, as this changes values from an image to another,
    making the comparison and stats less relevant.
    """
    b, g, r = cv2.split(image)
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom==0] = 0.01
    ndvi = (b.astype(float) - r) / bottom * 10.0
    ndvi = np.clip(ndvi, 0, 10).astype(np.uint8)
    return ndvi
