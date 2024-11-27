import cv2
import numpy as np
import matplotlib.pyplot as plt
import math as m





#Permet de detecter des marqueurs Aruco (les reperer et obtenir leurs bords) sans pour l'instant en tirer des informations. Estime aussi la distance au qr code (si on en détecte un).

arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
FOCALE_CAM = 1259.4
FOCALE_ORDI = 617
FOCALE = FOCALE_ORDI
TAILLE_MARQUEUR = 5
cap = cv2.VideoCapture(0) #0 = cam ordi ; 2 = camera voiture


###Detection : Marqueurs, distance, angles, position, vitesse


def aruco_corners(image,arucoDict):
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(arucoDict,parameters)
    corners,ids,rejected = detector.detectMarkers(image)
    return corners,ids



def estimation_distance_aruco(distance_focale,corners,taille_marqueur):
    y1,y2 = corners[3,0]-corners[0,0],corners[3,1]-corners[0,1] #prendre l'axe vertical car il devrait rester à peu près droit
    taille_image = m.sqrt(y1**2+y2**2) #en vrai y2 sert un peu à rien comme on est censé avoir y2=0 (camera droite)
    distance = (taille_marqueur*distance_focale)/taille_image
    return distance



def estimation_angle_aruco(corners):
    x1,x2 = corners[1,0]-corners[0,0],corners[1,1]-corners[0,1]
    pcam = m.sqrt(x1**2+x2**2)
    y1,y2 = corners[3,0]-corners[0,0],corners[3,1]-corners[0,1]
    dcam = m.sqrt(y1**2+y2**2)
    if pcam<=dcam:
        return m.acos(pcam/dcam) #renvoie un nombre en radians
    return 0



def ecart_centre_qrcode_ecran(image,corners):
    #Renvoie l'ecart entre le centre de l'ecran et le qr code sur l'ecran
    LARG,LONG = image.shape[0:2] #oui abscisse et ordonnee sont inversés...
    Xqr,Yqr = (corners[0,0]+corners[2,0])/2, (corners[0,1]+corners[2,1])/2 #la position du centre du qr code
    Xc,Yc = LONG//2,LARG//2
    ecart_image = Xqr-Xc #encore une fois on n'a pas besoin de Yqr et Yc car la camera est censée etre droite
    return ecart_image #positif = vers la droite



def estimation_correction_pour_centrer(image,d,distance_focale,corners):
    deplacement_image = ecart_centre_qrcode_ecran(image,corners)
    deplacement_correction = (d*deplacement_image)/distance_focale
    return deplacement_correction #positif = vers la droite




def corriger_deplacement(deplacement):
    #tourner à droite de (deplacement/abs(deplacement))*90 degrés, petit subterfuge pour aller plus vite
    #avancer de abs(deplacement)
    #tourner à gauche de (deplacement/abs(deplacement))*90 degrés
    pass


def corriger_angle(angle):
    pass



while True:
    #Récupérer l'image contenant potentiellement un qr code
    ret, img = cap.read()
    #img = cv2.resize(img,(340,220)) #340,220
    #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    corners,ids = aruco_corners(img,arucoDict)
    if len(corners)>0:
        corners = corners[0][0]
        ids = int(ids[0][0])
        d = estimation_distance_aruco(FOCALE,corners,TAILLE_MARQUEUR)
        angle = estimation_angle_aruco(corners)
        correction = estimation_correction_pour_centrer(img,d,FOCALE,corners)
        print("Distance à l'objet :",d)
        print("Angle en degrés :",angle*180/m.pi)
        print("Identifiant du marqueur :",ids)
        print("Deplacement à effectuer :",correction)
        print("\n")

