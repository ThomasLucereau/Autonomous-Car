import protocol as pr
import Fonctions_communes as fc
import websockets
import Motor
import time
import asyncio
import camera
import cv2


cap = cv2.VideoCapture(0)
ordre = [5,1,3]

def motor_go_distance(distance,vitesse=0.4):
    t=distance/vitesse
    Motor.Motor.MotorRun(0,'forward',70)
    Motor.Motor.MotorRun(1,'backward',70)
    time.sleep(t)
    Motor.Motor.MotorStop(0)
    Motor.Motor.MotorStop(1)
    return




def rotate(sens_rota, angle):
    v = 50
    t = angle/230
    if sens_rota=="left":
        Motor.Motor.MotorRun(0,'forward',v)
        Motor.Motor.MotorRun(1,'forward',v)
        time.sleep(t)
        Motor.Motor.MotorStop(0)
        Motor.Motor.MotorStop(1)
    elif sens_rota=="right":
        Motor.Motor.MotorRun(0,'backward',v)
        Motor.Motor.MotorRun(1,'backward',v)
        time.sleep(t)
        Motor.Motor.MotorStop(0)
        Motor.Motor.MotorStop(1)



async def run():
    # ETAPES POUR TOUTES LES VOITURES (sauf la première):*
    #   - Ouvrir la connexion
    ws = await pr.open_connection(14)
    balises = await pr.get_ordre_balise(ws)
    print(balises)
    position = [balises[str(b)] for b in ordre]

    #   - Attendre le go
    print("On atd de pouvoir partir")
    while not await pr.can_go(ws,0,0):
        time.sleep(0.5)

    #   - Aller au milieu
    print("On avance au milieu")
    motor_go_distance(1.75)

    #   - Chercher notre balise grace a l'information donnée
    if position[0]<0 : 
        sens_rota = "right" 
    else: 
        sens_rota = "left"
    print("On s'oriente vers la première balise")
    rotate(sens_rota, angle = abs(45*position[0]))
    
    corners,ids,d,ecart_centre,ecart_centre_norme = camera.acquisition_donnees(cap,ordre[0])
    #       - Si problème de balise non trouvée chercher normalement
    if type(corners)==int or (type(corners)!=int and ids!=ordre[0]):
        camera.recherche_traditionnelle(ordre[0],cap,not(sens_rota))
    
    #   - Aller à la balise
    
    
    await pr.send_signal(ws,1,ordre[0])
    # avancer de x metre
    print("On part vers la première balise")
    camera.go_marqueur(26,ordre[0],cap)
    #   - Envoyer un signal quand on est arrivé
    await pr.send_signal(ws,2,ordre[0])

    #   - Attendre le go
    while not await pr.can_go(ws,2,ordre[0]):
        print("On attend de pouvoir partir")
        time.sleep(0.5)

    Motor.Motor.MotorRun(0,'backward',70)
    Motor.Motor.MotorRun(1,'forward',70)
    time.sleep(0.5)
    Motor.Motor.MotorStop(0)
    Motor.Motor.MotorStop(1)


    #   - Calculer l'angle avec un decalage pour arriver en face
    angle = fc.angle_ij(position[0], position[1], 0.3,0)    
    # On peut prendre en compte le fait qu'on connait l'angle d'arrivé donc ne pas se placer a 0.3m (y a la fontion sur le git)
    if angle<0 : sens_rota = "left" 
    else: sens_rota = "right"
    print("On s'oriente vers la deuxième balise")
    rotate(sens_rota, abs(angle)-5+3.14/180)





    corners,ids,d,ecart_centre,ecart_centre_norme = camera.acquisition_donnees(cap, ordre[1])
    if type(corners)==int or (type(corners)!=int and ids!=ordre[1]):
        camera.recherche_traditionnelle(ordre[1],cap,sens_rota)

    await pr.send_signal(ws,3,ordre[0])
    print("On part vers la deuxième balise")
    Motor.Motor.MotorRun(0,'forward',70)
    Motor.Motor.MotorRun(1,'backward',70)
    time.sleep(0.5)
    Motor.Motor.MotorStop(0)
    Motor.Motor.MotorStop(1)
    #   - Aller à la balise

    camera.go_marqueur(26,ordre[1],cap)

    #   - Envoyer un signal quand on est arrivé
    await pr.send_signal(ws, 4, ordre[1])


    #   - Attendre le go
    while not await pr.can_go(ws,4,ordre[1]):
        print("On attend de pouvoir partir")
        time.sleep(0.5)

    Motor.Motor.MotorRun(0,'backward',70)
    Motor.Motor.MotorRun(1,'forward',70)
    time.sleep(0.75)
    Motor.Motor.MotorStop(0)
    Motor.Motor.MotorStop(1)


    #   - Calculer l'angle avec un decalage pour arriver en face
    angle = fc.angle_ij(position[1], position[2], 0.3,0)
    if angle<0 : sens_rota = "left" 
    else: sens_rota = "right"
    print("On s'oriente vers la troisième balise")
    rotate(sens_rota, abs(angle-20*3.14/180))



    corners,ids,d,ecart_centre,ecart_centre_norme = camera.acquisition_donnees(cap,ordre[2])
    if type(corners)==int or (type(corners)!=int and ids!=ordre[2]):
        camera.recherche_traditionnelle(ordre[2],cap,sens_rota)
    await pr.send_signal(ws, 5, ordre[1])
    print("On part vers la troisième balise")
    Motor.Motor.MotorRun(0,'forward',70)
    Motor.Motor.MotorRun(1,'backward',70)
    time.sleep(0.5)
    Motor.Motor.MotorStop(0)
    Motor.Motor.MotorStop(1)

    camera.go_marqueur(26,ordre[2],cap)

    #   - Envoyer un signal quand on est arrivé
    await pr.send_signal(ws, 6, ordre[2])

    #   - Attendre le go
    while not await pr.can_go(ws,6,ordre[2]):
        print("On attend de pouvoir partir")
        time.sleep(0.5)

    Motor.Motor.MotorRun(0,'backward',70)
    Motor.Motor.MotorRun(1,'forward',70)
    time.sleep(0.5)
    Motor.Motor.MotorStop(0)
    Motor.Motor.MotorStop(1)


    #   - S'orienter vers l'arrivée
    angle = fc.angle_ij(position[0], position[1], 0.3,0)
    if angle<0 : sens_rota = "left" 
    else: sens_rota = "right"
    print("On s'oriente vers l'arrivé*")
    rotate(sens_rota, abs(angle))



    corners,ids,d,ecart_centre,ecart_centre_norme = camera.acquisition_donnees(cap,9)
    if type(corners)==int or (type(corners)!=int and ids!=9):
        camera.recherche_traditionnelle(9,cap,sens_rota)
    #   - Aller à l'arrivé
    await pr.send_signal(ws, 7, ordre[2])
    print("On part vers l'arrivé")
    camera.go_marqueur(26,9,cap)

    #   - Envoyer un signal quand on est arrivé
    await pr.send_signal(ws, 8, 9)
    print("On est arrivé à la fin.")


    #   - Se décaler pour laisser les autres voitures passer
    rotate('right',45)
    motor_go_distance(1)

    # POUR TOUTES LES VOITURES ENVOYER DES SIGNAUX DE VIES

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
