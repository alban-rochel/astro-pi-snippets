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
    print("min " + str(in_min) + " max " + str(in_max))
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
    
#for image in photos:
#    print("Processing "+ image)
#    original = cv2.imread(image+".jpg")
#    cropped = crop_porthole(original)
#    cv2.imwrite(image + "_cropped.jpg", cropped,  [int(cv2.IMWRITE_JPEG_QUALITY), 90])
#    clouds = get_clouds_mask(cropped)
#    cv2.imwrite(image + "_clouds.jpg", clouds)
#    land = get_land_mask(cropped)
#    cv2.imwrite(image + "_land.jpg", land)
#    land_mask = cv2.bitwise_and(porthole, land)
#    land_mask = cv2.bitwise_and(land_mask, cv2.bitwise_not(clouds))
#    #land_mask = cv2.cvtColor(land_mask, cv2.COLOR_GRAY2BGR)
#    #data = cv2.bitwise_and(cropped, land_mask)
#    #cv2.imwrite(image + "_test.jpg", data)
#    ndvi = calc_ndvi(cropped)
#    cv2.imwrite(image + "_ndvi.jpg", ndvi)
    
#    total = 0
#    mean = 0
#    pixel_count = dict()
#    for index in range(11):
#        lower = np.array(index, dtype = "uint8")
#        upper = np.array(index, dtype = "uint8")
#        pixel_count[index] = np.count_nonzero(cv2.bitwise_and(cv2.inRange(ndvi, lower, upper), land_mask))
#        mean += index * pixel_count[index]
#        #print("index " + str(index) + " count " + str(pixel_count))
#        total += pixel_count[index]
#    print("mean " + str(mean/total))
