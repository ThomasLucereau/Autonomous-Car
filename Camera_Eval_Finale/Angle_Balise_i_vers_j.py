from math import cos,acos,sin,pi,degrees
import numpy as np

def angle_ij(i,j,d,a,ecart = 0.2,r = 2.5):
    '''
    Le robot est à une distance d de la balise i, à un angle a
    il vise le point en face de la balise j à un écart de 20cm (voir dessin)
    Paramètres :
    -----------
    i : id de la balise sur laquelle le robot est
    j : id de la balise que le robot vise
    d : distance robot balise (en m)
    a : angle axe robot, balise calculé par la fonction Etienne (en radians)
    ecart : distance entre balise j et point visé sur l'axe centre-balise j (en m)
    r : le rayon du terrain (en m)
    Résultat :
    -----------
    Calcule l'angle dont il doit tourner (en degré)
    '''


    rprime = r - ecart

    bi = -i*pi/4+pi/2
    bj = -j*pi/4+pi/2

    RBi = np.array([d*cos(a+bi),+d*sin(a+bi)])
    normeRBi = d
    BiCj = np.array([rprime*cos(bj)-(r-d)*cos(bi),rprime*sin(bj)-(r-d)*sin(bi)])
    normeBiCj = np.linalg.norm(BiCj)

    cosi = np.dot(RBi, BiCj)/(normeRBi*normeBiCj)
    theta = degrees(acos(cosi))
    if -np.cross(RBi, BiCj) >= 0:
        return theta
    return -theta


assert angle_ij(-2,2,2.5,0) == 180.0
#assert angle_ij(0,1,2.5,-pi/4) == 0
#assert angle_ij(0,1,2.5, pi/4) == 90
#assert angle_ij(0,0,2.5,pi/4) == 45
#assert angle_ij(-1,1,2.5,pi/4) == 90+45

assert angle_ij(0,-1,2.5,0) == -45
assert angle_ij(-1,-3,2.5,0) == -90
assert angle_ij(3,1,2.5,0) == -90
