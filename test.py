import RPi.GPIO as ahmed
import time 

ahmed.setwarnings(False)
ahmed.setmode(ahmed.BOARD)

TRIG = 11
ECHO = 23

ahmed.setup(TRIG,ahmed.OUT)
ahmed.setup(ECHO,ahmed.IN)
t=1
#g=31 # capteur gauche
r=33 # capteur droite
m=7 # capteur milieu

#====================================================================================================#
#ahmed.setup(g,ahmed.IN) #GPIO 2 -> capteur gauche
ahmed.setup(m,ahmed.IN) #GPIO 7 -> capteur milieu
ahmed.setup(r,ahmed.IN) #GPIO 3 -> capteur droite
ahmed.setup(29,ahmed.OUT) #GPIO 4 -> Moteur 1 +
ahmed.setup(31,ahmed.OUT) #GPIO 14 -> Moteur 1 -
ahmed.setup(12,ahmed.OUT)
my_pwm=ahmed.PWM(12,50)
my_pwm.start(0)
ahmed.setup(21,ahmed.OUT) #GPIO 17 -> Moteur 2 +
ahmed.setup(19,ahmed.OUT) #GPIO 18 -> Moteur 2 -
#====================================================================================================#
def avance(t):
    ahmed.output(29,True) #1A+
    ahmed.output(31,False) #1B-
    
    ahmed.output(21,True) #2A+
    ahmed.output(19,False) #2B-
    time.sleep(t)
    #ahmed.cleanup()
#=====================================================================================================#
def arriere(t):
    ahmed.output(29,False) #1A+
    ahmed.output(31,True) #1B-
    
    ahmed.output(21,False) #2A+
    ahmed.output(19,True) #2B-
    time.sleep(t)
    #ahmed.cleanup()
#=====================================================================================================#
def stop():
    ahmed.output(29,False) #1A+
    ahmed.output(31,False) #1B-

    ahmed.output(21,False) #2A+
    ahmed.output(19,False) #2B-
#=====================================================================================================#
def loop():
    my_pwm.ChangeDutyCycle(100)
    while 1:
        avance(1)
        stop()
        arriere(1)

#=====================================================================================================#
def destroy():
    stop()
    ahmed.cleanup()
    print("interruption par clavier CTRL+C")
#=====================================================================================================#
try:
    loop()
except KeyboardInterrupt:
    destroy()
