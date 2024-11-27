import main
import time
main.Motor.MotorRun(0,'forward',100)
main.Motor.MotorRun(1,'forward',100)
time.sleep(3)
main.Motor.MotorStop(0)
main.Motor.MotorStop(1)


#v = 50 => 40cm/s sans élastiques
#v = 70 => 55cm/s avec élastique
#vangulaire = 100 => 230°/S
