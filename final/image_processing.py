import cv2
import numpy as np

#photos = ["51844705092_c5911aab09_o", "51844740352_16e5a1d9e7_o", "51845638376_d241c3f433_o", "51845638376_d241c3f433_o", "51846029134_70ee19bd98_o", "51846031879_1b2e3d1f69_o"]

clouds_threshold = 200
land_threshold = 60

crop_left = 800
crop_right = 3700
crop_top = 50
crop_bottom = 2900

porthole = cv2.imread("porthole_mask.png", cv2.IMREAD_GRAYSCALE)

def crop_porthole(image):
    in_min = np.percentile(image, 5)
    in_max = np.percentile(image, 95)
    #print("min " + str(in_min) + " max " + str(in_max))
    return image[crop_top:crop_bottom, crop_left:crop_right]

def get_clouds_mask(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    (dummy, clouds) = cv2.threshold(gray,clouds_threshold,255,cv2.THRESH_BINARY)
    return clouds

def get_land_mask(image):
    (blue, green, red) = cv2.split(image)
    (dummy, land) = cv2.threshold(blue,land_threshold,255,cv2.THRESH_BINARY)
    return land

def compute_ndvi(image):
    b, g, r = cv2.split(image)
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom==0] = 0.01
    ndvi = (b.astype(float) - r) / bottom * 10.0
    ndvi = np.clip(ndvi, 0, 10).astype(np.uint8)
    return ndvi
