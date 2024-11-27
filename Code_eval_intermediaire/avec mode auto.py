from flask import Flask, render_template, request, jsonify
import main
import time
import camera



app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('site_web.html')

@app.route('/traiter_donnees/<vitesse>+<direction>+<arret>+<auto>', methods=['GET'])
def traiter_donnees(vitesse,direction,arret,auto) :
    v = int(vitesse)
    v=abs(v)
    d = int(direction)
    # stop= bool(arret)
    stop = False if arret == "false" else True
    # mode_auto = bool(auto)
    mode_auto = False if auto == "false" else True
    print(v)
    v=abs(v)
    print(d)
    print(mode_auto)
    print(stop)
    if (stop == True ) : 
        main.Motor.MotorStop(0)
        main.Motor.MotorStop(1)

    else : 
        if (d < 0) : 
            main.Motor.MotorRun(0,'forward',v)
            main.Motor.MotorRun(1,'forward',v)


        if (d > 0 ) :
            main.Motor.MotorRun(0,'backward',v)
            main.Motor.MotorRun(1,'backward',v)

        if (d == 0 ) : 
            main.Motor.MotorRun(0,'backward',v)
            main.Motor.MotorRun(1,'forward',v)

        if mode_auto :
            camera.mode_auto_eval()


        time.sleep(10)
        main.Motor.MotorStop(0)
        main.Motor.MotorStop(1)
    return jsonify({'message': 'Valeurs reçues et traitées avec succès'})

if __name__ == '__main__':
    app.run(debug = True,host='137.194.173.14',port=8000)






