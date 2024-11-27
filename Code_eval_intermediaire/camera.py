import cv2
import numpy as np
import math as m
import main
import time



#Permet de detecter des marqueurs Aruco (les reperer et obtenir leurs bords) sans pour l'instant en tirer des informations. Estime aussi la distance au qr code (si on en détecte un).

arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
FOCALE_CAM = 1259.4
FOCALE_ORDI = 617
FOCALE = FOCALE_CAM
TAILLE_MARQUEUR = 5
vitesse_virage = 25
vitesse_avance = 40

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


def acquisition_donnees(cap):
    ret,img = cap.read()
    corners,ids = aruco_corners(img,arucoDict)
    if len(corners)>0:
        corners = corners[0][0]
        ids = int(ids[0][0])
        d = estimation_distance_aruco(FOCALE,corners,TAILLE_MARQUEUR)
        ecart_centre = ecart_centre_qrcode_ecran(img,corners)
        LARG,LONG = img.shape[0:2]
        ecart_centre_norme = ecart_centre/LONG
        return corners,ids,d,ecart_centre,ecart_centre_norme
    return [-1,-1,-1,-1,0]



def recentrer(crit_entree,crit_sortie,cap):
    corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap)

    if abs(ecart_centre_norme)>crit_entree:
        if ecart_centre_norme>0:
            main.Motor.MotorRun(0,'forward',vitesse_virage)
            main.Motor.MotorRun(1,'forward',vitesse_virage)
        elif ecart_centre_norme<0: #cas 0 : soit erreur, soit parfaitement centré (en vrai impossible) et donc peut etre ignoré. De toute facon vu les codes après c'est pas la peine de prendre en compte ce cas.
            main.Motor.MotorRun(0,'backward',vitesse_virage)
            main.Motor.MotorRun(1,'backward',vitesse_virage)
        while abs(ecart_centre_norme)>crit_sortie:
                corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap)
    main.Motor.MotorStop(0)
    main.Motor.MotorStop(1)

#############################################################################################################

### DEBUT DE COURSE !




def mode_auto_eval():

    cap = cv2.VideoCapture(0) #0 = cam ordi ; 2 = camera voiture

    ZONE_BONNE = 0.10 #sur les ecart_centre_norme
    ZONE_TOLEREE = 0.25

    #Phase 1 : Trouver un marqueur impair

    print("Etape 1 : trouver un marqueur impair")

    main.Motor.MotorRun(0,'forward',vitesse_avance)
    main.Motor.MotorRun(1,'backward',vitesse_avance)
    time.sleep(4)
    main.Motor.MotorStop(0)
    main.Motor.MotorStop(1)
    corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap)
    while type(corners)==int or (type(corners)!=int and ids%2==0): #introduire un temps limite pour pas que ca cherche indefinimment. Si corners est de type int c'est qu'aucun marqueur n'a été détécté
        main.Motor.MotorRun(0,'backward',vitesse_virage)
        main.Motor.MotorRun(1,'backward',vitesse_virage)
        time.sleep(0.2)
        main.Motor.MotorStop(0)
        main.Motor.MotorStop(1)
        time.sleep(0.5)
        corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap)

    if type(corners)!=int and ids%2==1: #un marqueur impair a bien été détecté
        recentrer(ZONE_TOLEREE,ZONE_BONNE,cap)

                
    #Phase 2 : s'approcher à 20 cm

    print("Etape 2 : s'approcher à 20 cm")
    
    main.Motor.MotorRun(0,'forward',vitesse_avance)
    main.Motor.MotorRun(1,'backward',vitesse_avance)
    while d>22 or d==-1:
        print("distance jusqu'au marqueur : ", d)
        if d == -1:
            main.Motor.MotorStop(0)
            main.Motor.MotorStop(1)
            time.sleep(0.7)
            main.Motor.MotorRun(0,'forward',vitesse_avance)
            main.Motor.MotorRun(1,'backward',vitesse_avance)
        corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap)
        if abs(ecart_centre_norme) > ZONE_TOLEREE:
            main.Motor.MotorStop(0)
            main.Motor.MotorStop(1)
            recentrer(ZONE_TOLEREE,ZONE_BONNE,cap)
            main.Motor.MotorRun(0,'forward',vitesse_avance)
            main.Motor.MotorRun(1,'backward',vitesse_avance)
        print("distance 2 jusqu'au marqueur : ", d)
    main.Motor.MotorStop(0)
    main.Motor.MotorStop(1)
         
    main.Motor.MotorRun(0,'backward',vitesse_avance)
    main.Motor.MotorRun(1,'forward',vitesse_avance)
    time.sleep(5)
    main.Motor.MotorStop(0)
    main.Motor.MotorStop(1)


    #Phase 3 : rechercher un marqueur pair
    
    print("Etape 3 : recherche du marqueur pair")
    
    corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap)
    while type(corners)==int or (type(corners)!=int and ids%2==1): #introduire un temps limite pour pas que ca cherche indefinimment. Si corners est de type int c'est qu'aucun marqueur n'a été détécté
        main.Motor.MotorRun(0,'backward',vitesse_virage)
        main.Motor.MotorRun(1,'backward',vitesse_virage)
        time.sleep(0.2)
        main.Motor.MotorStop(0)
        main.Motor.MotorStop(1)
        time.sleep(0.5)
        corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap)

    if type(corners)!=int and ids%2==0: #un marqueur pair a bien été détecté
        recentrer(ZONE_TOLEREE,ZONE_BONNE,cap)


    #Phase 4 : s'avancer à 20 cm

    print("Etape 4 : s'avancer à 20 cm")
    main.Motor.MotorRun(0,'forward',vitesse_avance)
    main.Motor.MotorRun(1,'backward',vitesse_avance)
    while d>22 or d==-1:
        print("distance jusqu'au marqueur : ", d)
        if d == -1:
            main.Motor.MotorStop(0)
            main.Motor.MotorStop(1)
            time.sleep(0.7)
            main.Motor.MotorRun(0,'forward',vitesse_avance)
            main.Motor.MotorRun(1,'backward',vitesse_avance)
        corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees(cap)
        if abs(ecart_centre_norme) > ZONE_TOLEREE:
            main.Motor.MotorStop(0)
            main.Motor.MotorStop(1)
            recentrer(ZONE_TOLEREE,ZONE_BONNE,cap)
            main.Motor.MotorRun(0,'forward',vitesse_avance)
            main.Motor.MotorRun(1,'backward',vitesse_avance)
    main.Motor.MotorStop(0)
    main.Motor.MotorStop(1)
    
# mode_auto_eval()

#### FIN DE COURSE
