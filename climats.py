import cv2
from orbit import ISS

image = cv2.imread("climats.png")

#print(image.shape)
#print(image[50, 150])

position_ISS = ISS.coordinates()
print (position_ISS)
ligne = round (180-2*(position_ISS.latitude.degrees))
colonne = round (360-2*(position_ISS.longitude.degrees))
zone_climatique = image[ligne,colonne]
print (zone_climatique)
print (zone_climatique[0])
if zone_climatique[0] == 51:
    print ("equatorial")
elif zone_climatique[0] == 52:
    print ("Mousson")
elif zone_climatique[0] == 53:
    print ("Savane")
elif zone_climatique[0] == 101:
    print ("Desertique")
elif zone_climatique[0] == 102:
    print ("Semi aride")
elif zone_climatique[0] == 151:
    print ("Subtropical humide")
elif zone_climatique[0] == 152:
    print ("Oceanique")
elif zone_climatique[0] == 153:
    print ("Mediterraneen")
elif zone_climatique[0] == 201:
    print ("Continental humide")
elif zone_climatique[0] == 202:
    print ("Subarctique")
else:
     print("Autre")
print ("colonne = "+str(colonne))
print ("ligne = " +str(ligne))

 