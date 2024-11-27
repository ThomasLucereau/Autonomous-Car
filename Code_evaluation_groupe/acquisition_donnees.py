import cv2
import numpy as np
import math as m
#import main
import time



#Permet de detecter des marqueurs Aruco (les reperer et obtenir leurs bords) sans pour l'instant en tirer des informations. Estime aussi la distance au qr code (si on en détecte un).

arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
FOCALE_CAM = 1259.4 # parametre sans unite
FOCALE_ORDI = 617
FOCALE = FOCALE_CAM
TAILLE_MARQUEUR = 0.05 # toutes les unites sont en m.
vitesse_virage = 25
vitesse_avance = 40

###Detection : Marqueurs, distance, angles, position, vitesse


def aruco_corners(image,arucoDict):
    parameters = cv2.aruco.DetectorParameters_create()
    corners,ids,rejected = cv2.aruco.detectMarkers(image, arucoDict, parameters=parameters)
    return corners,ids


def aruco_corners2(image,arucoDict):
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(arucoDict,parameters)
    corners,ids,rejected = detector.detectMarkers(image)
    return corners,ids



def estimation_distance_aruco(distance_focale,corners,taille_marqueur):
    """
    renvoie la distance en m avec la balise
    """
    y1,y2 = corners[3,0]-corners[0,0],corners[3,1]-corners[0,1] #prendre l'axe vertical car il devrait rester à peu près droit
    taille_image = m.sqrt(y1**2+y2**2) #en vrai y2 sert un peu à rien comme on est censé avoir y2=0 (camera droite)
    distance = (taille_marqueur*distance_focale)/taille_image
    return distance



def estimation_angle_aruco(corners):
    """
    renvoie l'angle en radian par rapport a la normale de la balise
    (utilisation: calculer le `a` pour la fonction `angle_ij`
    """
    x1,x2 = corners[1,0]-corners[0,0],corners[1,1]-corners[0,1]
    pcam = m.sqrt(x1**2+x2**2)
    y1,y2 = corners[3,0]-corners[0,0],corners[3,1]-corners[0,1]
    dcam = m.sqrt(y1**2+y2**2)
    y1d,y2d = corners[2,0]-corners[1,0],corners[2,1]-corners[1,1]
    dcam2 = m.sqrt(y1d**2+y2d**2)
    if pcam<=dcam:
        angle = m.acos(pcam/dcam)
        if dcam>dcam2: #À gauche du marqueur
            return -angle #renvoie un nombre en radians
        return angle
    return 0



def ecart_centre_qrcode_ecran(image,corners):
    #Renvoie l'ecart entre le centre de l'ecran et le qr code sur l'ecran
    LARG,LONG = image.shape[0:2] #oui abscisse et ordonnee sont inversés...
    Xqr,Yqr = (corners[0,0]+corners[2,0])/2, (corners[0,1]+corners[2,1])/2 #la position du centre du qr code
    Xc,Yc = LONG//2,LARG//2
    ecart_image = Xqr-Xc #encore une fois on n'a pas besoin de Yqr et Yc car la camera est censée etre droite
    return ecart_image #positif = vers la droite



#def estimation_correction_pour_centrer(image,d,distance_focale,corners):
#    deplacement_image = ecart_centre_qrcode_ecran(image,corners)
#    deplacement_correction = (d*deplacement_image)/distance_focale
#    return deplacement_correction #positif = vers la droite




#Fonctions de deplacement


def acquisition_donnees(cap):
    ret,img = cap.read()
    corners,ids = aruco_corners2(img,arucoDict)
    if len(corners)>0:
        corners = corners[0][0]
        ids = int(ids[0][0])
        d = estimation_distance_aruco(FOCALE,corners,TAILLE_MARQUEUR)
        ecart_centre = ecart_centre_qrcode_ecran(img,corners)
        LARG,LONG = img.shape[0:2]
        ecart_centre_norme = ecart_centre/LONG
        angle = estimation_angle_aruco(corners)
        return [corners,ids,d,ecart_centre,ecart_centre_norme,angle]
    return [-1,-1,-1,-1,0,0]


