from math import cos, acos, sin, pi, degrees
import numpy as np


def angle_ij(i, j, d, a, ecart=0.2, r=2.5):
    '''
    Le robot est à une distance d de la balise i, à un angle a
    il vise le point en face de la balise j à un écart de 20cm (voir dessin)
    Paramètres :
    -----------
    i : angle de la balise sur laquelle le robot est
    j : angle de la balise que le robot vise
    d : distance robot balise (en m)
    a : angle axe robot, balise .
        utiliser acquisition_donnees.py -> estimation_angle_aruco pour le connaitre
    ecart : distance entre balise j et point visé sur l'axe centre-balise j (en m)
    r : le rayon du terrain (en m)
    Résultat :
    -----------
    Calcule l'angle dont il doit tourner (en degré)
    Si l'angle est negatif, on tourne vers la gauche
    '''

    rprime = r - ecart

    bi = -i*pi/4+pi/2
    bj = -j*pi/4+pi/2

    # vecteur entre le robot et la balise de départ
    RBi = np.array([d*cos(a+bi), d*sin(a+bi)])
    normeRBi = d

    # Vecteur vers la 2eme balise
    OBi = np.array([r*cos(bi), r*sin(bi)])
    OCj = np.array([rprime*cos(bj), rprime*sin(bj)])

    RCj = RBi-OBi+OCj
    normeRCj = np.linalg.norm(RCj)

    cosi = np.dot(RBi, RCj)/(normeRBi*normeRCj)
    theta = degrees(acos(cosi))
    if -np.cross(RBi, RCj) >= 0:
        return theta
    return -theta


# assert angle_ij(-2, 2, 2.5, 0) == 180.0
#assert angle_ij(0, -1, 2.5, 0) == -45
# assert abs(angle_ij(0, 1, 2.5, 0) - 45) < 0.0001
# assert angle_ij(-1, -3, 2.5, 0) == -90
# assert angle_ij(3, 1, 2.5, 0) == -90
# assert angle_ij(1, 3, 2.5, 0) == 90

def distance_ij(i,j,d,a,ecart = 0.2,r = 2.5):
    '''
    Renvoie la distance (m) que le robot devra parcourir à partir de sa position pour aller vers la prochaine balise (en ligne droite)
    '''
    rprime = r - ecart
    bi = -i*pi/4+pi/2
    bj = -j*pi/4+pi/2

    BiCj = np.array([rprime*cos(bj)-(r-d)*cos(bi),rprime*sin(bj)-(r-d)*sin(bi)])
    normeBiCj = np.linalg.norm(BiCj)
    return normeBiCj


def iscrossing(Triangle, BA, posbalise):
    '''
    Parametre :
    ----------
    Triangle : liste [B1,B2,B3] : balises de l'autre triangle
    BA : balise actuelle
    posbalise : le dictionnaire associant les balises à leur position selon la convention
    Résultat :
    ----------
    Renvoie True si pour aller a ZA, le robot placé a BA croise le triangle opposé
    Renvoie False s'il ne croise pas
    '''
    Triangle_pos = [posbalise[b] for b in Triangle]
    BA_pos = posbalise[BA]
    Croise = False
    for b in Triangle_pos:
        if b*BA_pos > 0:
            if abs(BA_pos) < abs(b):
                Croise = True
    return Croise


assert iscrossing(
    [1, 3, 5], 4, {1: 1, 2: 2, 3: 3, 4: -3, 5: -2, 6: -1}) == False
assert iscrossing(
    [1, 3, 4], 5, {1: 1, 2: 2, 3: 3, 4: -3, 5: -2, 6: -1}) == True
