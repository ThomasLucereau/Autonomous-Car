import cv2
import matplotlib.pyplot as plt
import math as m


###Avec les informations rentrées par input, on en déduit une "focale". Ca ne correspond pas à une distance réeelle mais c'est utile pour les calculs dans detecter_aruco.py


cap = cv2.VideoCapture(0)



ret, img = cap.read()
img = cv2.resize(img,(340,220))
plt.imshow(img)
plt.show(block=False)
abscisse_gauche = float(input("Abscisse du point de gauche : "))
ordonnee_gauche = float(input("Ordonnée du point de gauche : "))
abscisse_droite = float(input("Abscisse du point de droite : "))
ordonnee_droite = float(input("Ordonnée du point de droite : "))
x1,x2 = abscisse_droite-abscisse_gauche,ordonnee_droite-ordonnee_gauche
taille_image = m.sqrt(x1**2+x2**2)
distance_im_objet = int(input("Distance à l'objet : "))
taille_objet = int(input("taille de l'objet : "))
focale = (taille_image*distance_im_objet)/taille_objet


print("\n -> Distance focale : focale")


#Il y aura juste à stocker focale dans un fichier pour s'en rappeler
