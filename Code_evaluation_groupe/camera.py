import cv2
import numpy as np
import math as m
import time
import Motor


#Permet de detecter des marqueurs Aruco (les reperer et obtenir leurs bords) sans pour l'instant en tirer des informations. Estime aussi la distance au qr code (si on en détecte un).

arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
FOCALE_CAM = 1259.4
FOCALE_ORDI = 617
FOCALE = FOCALE_CAM
TAILLE_MARQUEUR = 5
vitesse_virage = 35
vitesse_avance = 50


###Detection : Marqueurs, distance, angles, position, vitesse


def aruco_corners(image,arucoDict):
    parameters = cv2.aruco.DetectorParameters_create()
    corners,ids,rejected = cv2.aruco.detectMarkers(image, arucoDict, parameters=parameters)
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



#Deux fonctions plus compliquées qui serviront plus tard

def corriger_deplacement(deplacement):
    #tourner à droite de (deplacement/abs(deplacement))*90 degrés, petit subterfuge pour aller plus vite
    #avancer de abs(deplacement)
    #tourner à gauche de (deplacement/abs(deplacement))*90 degrés
    pass


def corriger_angle(angle):
    pass


#Fonctions de deplacement


def acquisition_donnees(cap,id_voulu):
    ret,img = cap.read()
    corners,ids = aruco_corners(img,arucoDict)
    if len(corners)>0 and (id_voulu in list(ids[0])):
        j = list(ids[0]).index(id_voulu)
        corners = corners[0][j]
        d = estimation_distance_aruco(FOCALE,corners,TAILLE_MARQUEUR)
        ecart_centre = ecart_centre_qrcode_ecran(img,corners)
        LARG,LONG = img.shape[0:2]
        ecart_centre_norme = ecart_centre/LONG
        return corners,ids,d,ecart_centre,ecart_centre_norme
    return [-1,-1,-1,-1,0]



def recentrer(crit_entree,crit_sortie,cap,id_voulu,v_virage=20):
    corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap,id_voulu)

    if abs(ecart_centre_norme)>crit_entree:
        if ecart_centre_norme>0:
            Motor.Motor.MotorRun(0,'forward',v_virage)
            Motor.Motor.MotorRun(1,'forward',v_virage)
        elif ecart_centre_norme<0: #cas 0 : soit erreur, soit parfaitement centré (en vrai impossible) et donc peut etre ignoré. De toute facon vu les codes après c'est pas la peine de prendre en compte ce cas.
            Motor.Motor.MotorRun(0,'backward',v_virage)
            Motor.Motor.MotorRun(1,'backward',v_virage)
        while abs(ecart_centre_norme)>crit_sortie:
                corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap,id_voulu)
    Motor.Motor.MotorStop(0)
    Motor.Motor.MotorStop(1)


def go_marqueur(dist,id,cap):
    dernier_ecart=0
    v = 70
    previous_d =float('inf')
    

    loop=0
    ZONE_TOLEREE = 0.25
    ZONE_BONNE = 0.10
    Motor.Motor.MotorRun(0,'forward',v)
    Motor.Motor.MotorRun(1,'backward',v)
    corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap,id)
    while previous_d>dist:
        print("distance jusqu'au marqueur : ", d)
        if d != -1:    
            Motor.Motor.MotorRun(0,'forward',v)
            Motor.Motor.MotorRun(1,'backward',v)
            loop=0
        
        if d == -1:
            Motor.Motor.MotorStop(0)
            Motor.Motor.MotorStop(1)
            time.sleep(0.1)
            loop+=1
            
        if loop>20:
            recherche_traditionnelle(id,cap,'backward')
            loop=0

        """"       
        if previous_d < 27 and loop>10:
            Motor.Motor.MotorStop(0)
            Motor.Motor.MotorStop(1)
            print('petit malin va')
            break
        if previous_d>120 and loop>7:
            Motor.Motor.MotorRun(0,'forward',v)
            Motor.Motor.MotorRun(1,'backward',v)
            print('petit coquin')
            time.sleep(0.9)
            Motor.Motor.MotorStop(0)
            Motor.Motor.MotorStop(1) 
            time.sleep(0.7)
            loop=0
            previous_d=35
            
        """                 

        corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap,id)
        print(d,ecart_centre_norme)
        if d > 0:
            previous_d=d
        

        if abs(ecart_centre_norme) > ZONE_TOLEREE:
            Motor.Motor.MotorStop(0)
            Motor.Motor.MotorStop(1)
            time.sleep(0.2)
            Motor.Motor.MotorRun(0,'forward',v)
            Motor.Motor.MotorRun(1,'backward',v)
            recentrer(ZONE_TOLEREE,ZONE_BONNE,cap,id)
            loop=0


        print("distance 2 jusqu'au marqueur : ", d)
    Motor.Motor.MotorStop(0)
    Motor.Motor.MotorStop(1)


def recherche_traditionnelle(id,cap,sens):
    """"
    sens : True = droite, False= gauche
    """
    tourner='salut :)'
    if sens=='backward':
        tourner='backward'
    else:
        tourner='forward'
    v = 40
    ZONE_TOLEREE = 0.25
    ZONE_BONNE = 0.10
    corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap,id)
    while type(corners)==int: #tant qu'on detecte rien ou que l'on detecte un mauvais marqueur
        Motor.Motor.MotorRun(0,tourner,v)
        Motor.Motor.MotorRun(1,tourner,v)
        time.sleep(0.15)
        Motor.Motor.MotorStop(0)
        Motor.Motor.MotorStop(1)
        time.sleep(0.5)
        corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap,id)

    if type(corners)!=int: #un marqueur impair a bien été détecté
        recentrer(ZONE_TOLEREE,ZONE_BONNE,cap,id)
    

