from flask import Flask, render_template, request, jsonify
import main
import time
from math import ceil
#import camera_nouveau
vlin = 55
vang = 8

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('site_web_nouveau.html')

@app.route('/traiter_donnees/<vitesse>+<direction>+<arret>+<auto>', methods=['GET'])
def traiter_donnees(vitesse,direction,arret,auto="false") :
    def avancer_d(dist):
        temps = dist / vlin
        main.Motor.MotorRun(0,'forward',vlin)
        main.Motor.MotorRun(1,'backward',vlin)
        time.sleep(temps)
        main.Motor.MotorStop(0)
        main.Motor.MotorStop(1)
    def tourner(ang) :
        nb_accoup = ceil(abs(ang)/vang)
        if ang < 0 : 
            for i in range(nb_accoup):
                main.Motor.MotorRun(0,'forward',50)
                main.Motor.MotorRun(1,'forward',50)
                time.sleep(0.1)
                main.Motor.MotorStop(0)
                main.Motor.MotorStop(1)
        else:
            for i in range(nb_accoup):
                main.Motor.MotorRun(0,'backward',50)
                main.Motor.MotorRun(1,'backward',50)
                time.sleep(0.1)
                main.Motor.MotorStop(0)
                main.Motor.MotorStop(1)




    v1 = 100
    v2 = 50
    d = int(direction)
    # stop= bool(arret)
    stop = False if arret == "false" else True
    # mode_auto = bool(auto)
    mode_auto = False if auto == "false" else True
    print(d)
    print(mode_auto)
    print(stop)
    if (stop == True ) : 
        main.Motor.MotorStop(0)
        main.Motor.MotorStop(1)

    else : 
        if (d > 0) : 
            if (int(vitesse) < 0):
                main.Motor.MotorRun(0,'forward',v2)
                main.Motor.MotorRun(1,'forward',v2)
                time.sleep(0.08)
            else : 
                main.Motor.MotorRun(0,'forward',v2)
                main.Motor.MotorRun(1,'forward',v2)
                time.sleep(0.08)

        if (d < 0 ) :
            if(int(vitesse)<0):
                main.Motor.MotorRun(0,'backward',v2)
                main.Motor.MotorRun(1,'backward',v2)
                time.sleep(0.08)
            else : 
                main.Motor.MotorRun(0,'backward',v2)
                main.Motor.MotorRun(1,'backward',v2)
                time.sleep(0.08)
        elif (d == 0 ) :
            if (int(vitesse)>0) :
                main.Motor.MotorRun(0,'forward',v1)
                main.Motor.MotorRun(1,'backward',v1)
                time.sleep(0.4)  
            elif (int(vitesse)<0) :
                main.Motor.MotorRun(0,'backward',v1)
                main.Motor.MotorRun(1,'forward',v1)
                time.sleep(0.4)
        #if mode_auto:
        #    camera_nouveau.mode_auto_eval()
        
        main.Motor.MotorStop(0)
        main.Motor.MotorStop(1)

    return jsonify({'message': 'Valeurs reçues et traitées avec succès'})

if __name__ == '__main__':
    app.run(debug = True,host='137.194.173.14',port=8000)