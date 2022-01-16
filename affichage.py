from sense_hat import SenseHat
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import numpy as np

sense = SenseHat()

camera = PiCamera()
#camera.resolution = (3280, 2464) # Full FOV
#camera.resolution = (1664, 1232) # Binned, full FOV
camera.resolution = (1376, 768) # Binned, full FOV
rawCapture = PiRGBArray(camera)

def contrast_stretch2(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)
    
    out_min = 0.0
    out_max = 255.0
    
    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min
    
    out[out > 255] = 255
    out[out < 0] = 0
    
    return out

def process_image(image):
    plop = cv2.resize(image, (8,8))
    plop = contrast_stretch2(plop)
    return plop

def display_image(image):
    for row in range(8):
        for col in range(8):
            sense.set_pixel(row, col, image[row, col].astype(int))

counter = 0

while counter < 1:
    camera.capture(rawCapture, format="rgb")
    image = rawCapture.array
    processed = process_image(image)
    print(processed.shape)
    display_image(processed)
    #cv2.imwrite("processed.jpg", processed)
    #cv2.imwrite("original.jpg", image)
    rawCapture.truncate(0)
    counter = counter + 1