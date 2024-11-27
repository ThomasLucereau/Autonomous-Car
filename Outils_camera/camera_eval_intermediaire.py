import cv2
import numpy as np
import matplotlib.pyplot as plt
import math as m





#Permet de detecter des marqueurs Aruco (les reperer et obtenir leurs bords) sans pour l'instant en tirer des informations. Estime aussi la distance au qr code (si on en détecte un).

arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
FOCALE_CAM = 1259.4
FOCALE_ORDI = 617
FOCALE = FOCALE_CAM
TAILLE_MARQUEUR = 5
cap = cv2.VideoCapture(2) #0 = cam ordi ; 2 = camera voiture


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



#Deux fonctions plus compliquées qui serviront plus tard

def corriger_deplacement(deplacement):
    #tourner à droite de (deplacement/abs(deplacement))*90 degrés, petit subterfuge pour aller plus vite
    #avancer de abs(deplacement)
    #tourner à gauche de (deplacement/abs(deplacement))*90 degrés
    pass


def corriger_angle(angle):
    pass


#Fonctions de deplacement


def acquisition_donnees():
        ret,img = cap.read()
        corners,ids = aruco_corners(img,arucoDict)
        if len(corners)>0:
            corners = corners[0][0]
            ids = int(ids[0][0])
            d = estimation_distance_aruco(FOCALE,corners,TAILLE_MARQUEUR)
            ecart_centre = ecart_centre_qrcode_ecran(img,d,FOCALE,corners)
            LARG,LONG = img.shape[0:2]
            ecart_centre_norme = ecart_centre/LONG
            return corners,ids,d,ecart_centre,ecart_centre_norme
        return [-1,-1,-1,-1,0]



def recentrer(crit_entree,crit_sortie):
    corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees()

    if abs(ecart_centre_norme)>crit_entree:
        if ecart_centre_norme>0:
            pass
            #tourner à droite (lentement)
        elif ecart_centre_norme<0: #cas 0 : soit erreur, soit parfaitement centré (en vrai impossible) et donc peut etre ignoré. De toute facon vu les codes après c'est pas la peine de prendre en compte ce cas.
            pass
            #tourner à gauche (lentement)
        while abs(ecart_center_norme)>crit_sortie:
                corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees()
        #motor.stop



#############################################################################################################

### DEBUT DE COURSE !


marqueur_impair_trouve = False
marqueur_pair_trouve = False
ZONE_BONNE = 0.10 #sur les ecart_centre_norme
ZONE_TOLEREE = 0.25

#Phase 1 : Trouver un marqueur impair

while marqueur_impair_trouve == False:
    #tourner sur soi meme
    corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees()
    while corners==-1: #introduire un temps limite pour pas que ca cherche indefinimment
        corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees()
    #motor.stop
    if corners!=-1:
        if ids%2==1:
            marqueur_impair_trouve = True
            recentrer(ZONE_TOLEREE,ZONE_BONNE)

            
#Phase 2 : s'approcher à 20 cm


while d>21:
    #Avancer
    corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees()
    while ecart_centre_norme < ZONE_TOLEREE:
        corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees()        
    #motor.stop
    if corners!=-1: #en vrai pas necessaire car le cas d'erreur est géré par la fonction mais on sait jamais
        recentrer(ZONE_TOLEREE,ZONE_BONNE)

#Faire demi-tour


#Phase 3 : rechercher un marqueur pair


while marqueur_pair_trouve == False:
    #Avancer et peut etre tourner un peu si pas aligné ?
    corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees()
    while corners==-1:
        corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees()
    #motor.stop
    if corners!=-1:
        if ids%2==0:
            marqueur_pair_trouve = True
            recentrer(ZONE_TOLEREE,ZONE_BONNE)


#Phase 4 : s'avancer à 20 cm


while d>21:
    #Avancer tout droit
    corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees()
    while ecart_centre_norme > ZONE_TOLEREE:
        corners,ids,d,ecart_centre,ecart_centre_norme = acquisition_donnees()
    #motor.stop
    if corners!=-1:
        recentrer(ZONE_TOLEREE,ZONE_BONNE)



#### FIN DE COURSE




"""angle = estimation_angle_aruco(corners)
correction = estimation_correction_pour_centrer(img,d,FOCALE,corners)
print("Distance à l'objet :",d)
print("Angle en degrés :",angle*180/m.pi)
print("Identifiant du marqueur :",ids)
print("Deplacement à effectuer :",correction)
print("\n")"""

