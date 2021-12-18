import cv2
from orbit import ISS

image = cv2.imread("climats.png")

print(image.shape)
print(image[10, 10])

position_ISS = ISS.coordinates()