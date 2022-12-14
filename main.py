import numpy as np
from math import *
# allows to control lidar
from rplidar import RPLidar
import time
import os
# allows to process config.json
import json
import curses # For key pressing
# allows to control & monitor input devices (mouse & keyboard)
from pynput import keyboard

from evitement import *
from filtrage import *

# Centre initial
# from Phidget22.Phidget import *
# from Phidget22.Devices.Gyroscope import *
# from Phidget22.Devices.Accelerometer import *

# General Purpose Input Output Library : allows interactions between RasPi & external electronic components
import RPi.GPIO as GPIO

# Files in which show_result.py is going to stock datas for post analysis
filename = "output.txt"
filename_map = "output_map.txt"

#############  CONFIGURATION  ##############

# Opening and parsing the json file
with open("config.json", "r") as config_file:
    config_string = config_file.read()
config = json.loads(config_string)

# When we want a constant speed :
v_cste = config['v_cste']
# When we want an exponential law of command :
coeff = config['coeff']
vmin  = config['vmin'] * coeff
vmax  = config['vmax'] * coeff
d     = config['d'] # Is used in the speed computation
#The angle of opening of the detection code :
cone_detect = config['cone_detect'] # might have a dynamic strategy about it
largeur_convolution = config['largeur_convolution']

# Connection pins
servo_pin  = config['servo_pin']
moteur_pin = config['moteur_pin']

# ??
# Calibration de servo moteur
deg_0_pulse   = config['deg_0_pulse'] 
deg_180_pulse = config['deg_180_pulse']

# Frequency needed for the PWM command
f = config['f']
period = 1000/f

# ??
# Calibration de servo moteur
deg_0_duty = deg_0_pulse * f/10
pulse_range = deg_180_pulse - deg_0_pulse
duty_range = pulse_range * f/10
duty = deg_0_duty + (90/180.0) * duty_range

# Max Iter
tours_init = config['tours_init']
limit_tour = config['limit_tour']

# Centre initial
# ch_acl = Accelerometer()
# ch_yaw = Gyroscope()
# ch_yaw.openWaitForAttachment(200)
# ch_acl.openWaitForAttachment(200)

angle_cible=0
angle_consigne=0
dmax=0

################  END OF CONFIGURATION  ###############

################  Motors initialization ###############

# Option GPIO.BCM means that we refer to pins by number "Broadcom SOC channel" : it is number then "GPIO"
GPIO.setmode(GPIO.BCM)
# Define the pin "servo_pin" (=17) as an output
GPIO.setup(servo_pin,GPIO.OUT)
# Define the pin "moteur_pin" (=18) as an output
GPIO.setup(moteur_pin,GPIO.OUT)

# Define the PMW command by the frequency f (=50 Hz) for the servomotor
pwm_servo = GPIO.PWM(servo_pin,f)
# Define the cycle rate of the PMW command for the servomotor
cyclerate_servo = 0
# Launch the PMW command
pwm_servo.start(cyclerate_servo)


# Define PMW command by the frequency f (=50 Hz) for the DC motor
pwm_moteur = GPIO.PWM(moteur_pin,f)
# Define the cycle rate of the PMW command for the DC motor
cyclerate_motor = 2.5
# Launch the PMW command
pwm_moteur.start(cyclerate_motor)

# Change the cycle rate of the PMW command for the servo motor, depending on its initial calibration
pwm_servo.ChangeDutyCycle(duty)
# Change the cycle rate of the PMW command for the motor to 0
pwm_moteur.ChangeDutyCycle(0)

##############  LIDAR Initialization  #################

LIDAR_DEVICE = '/dev/ttyUSB0'
# Connect to Lidar unit
lidar = RPLidar(LIDAR_DEVICE)

# note :  SLAM (Simultaneous Localization and Mapping)

#info = lidar.get_info()
#print(info)

#health = lidar.get_health()
#print(health)

# Starts sensor motor
lidar.start_motor()
# Connects to the serial port with the name self.port. If it was connected to another serial port disconnects from it first.
lidar.connect()

# Pause
time.sleep(2)

############# PYNPUT INITIALIZATION ###################

# When equal to 1, the car starts
go = 0

# Press 'g' to start, Press 's' to stop
def on_press(key):
    try:
         # Display the key pressed
            print('Alphanumeric key pressed: {0} '.format(
            key.char))
        global go
        if key.char=='g':
            go = 1
        elif key.char=='s':
            go = 0
            # Stop listener
            return False
    except AttributeError:
        # Display the special key pressed
        print('special key pressed: {0}'.format(
            key))
        pass

# Release 'esc' to stop
def on_release(key):
    # Display the key released
    print('Key released: {0}'.format(
        key))
    if key==keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)

#####  Utility variables  #####

# This data is going to stock successive scans
data=[]
#data_yaw = []
#data_acl = [] # 0:a_x, 1:a_y
map=[1000 for i in range(360)]

angle_cible=0
angle_consigne=0
dmax=0

compteur=0
init=0

# Launch the keyboard listener
listener.start() # starting 

flag = False
try:
        ############  Data acquisition ##############
        
        # Check if the file path exists
        if os.path.exists(filename):
            # Remove or delete the file path
            os.remove(filename)
        # Open the file 
        file_obj = open(filename, 'a')
        # Check if the file path exists
        if os.path.exists(filename_map):
            # Remove or delete the file path
            os.remove(filename_map)
        # Open the file
        file_obj_map = open(filename_map, 'a')
        
        # Write in the file -"TimeStamp", "Average Distance", "Motor Speed", "Raw Direction", "Calculated Direction", "Suggest Direction"-
        file_obj.writelines("%s %s %s %s %s %s\n"
                            %("TimeStamp","Average Distance", "Motor Speed",
                              "Raw Direction", "Calculated Direction", "Suggest Direction"))
        # Write in the file -"TimeStamp", "Lidar Data"-
        file_obj_map.writelines("%s %s\n"%("TimeStamp", "Lidar Data"))
            

        ################  MAIN LOOP  #################
        
        # Stock lidar scans over time
        # Scan is a list of tuples (quality, angle, distance)
        for scan in lidar.iter_scans(500,10):
            # Stocks scan in data
            data.append(np.array(scan))

            # Extremal tuple of data (ie last made scan)
            X = data[-1]
            for j in range(len(X)):
                map[min(int(X[j][1])-1,359)]=X[j][2]
            
            # Put a convolution filter on the map to lift the map
            mapt=filtrage(map, largeur_convolution)


            # Centrale inertielle
#             for mes in ch_yaw.getAngularRate():
#                 data_yaw.append(np.array(mes))
#                 Mes_yaw = np.round(data_yaw[-1], 1)
#         
#             for mes in ch_acl.getAcceleration():
#                 data_acl.append(np.array(mes))
#                 Mes_ax = np.round(data_acl[-1], 1)
            
            
            if go==1:
                flag = True
                

                ##################  LOI DE DIRECTION  ####################
                dmax=0
                # Sets the maximal distance
                for i in range(-cone_detect, cone_detect):
                    if mapt[i]>dmax:
                        dmax=mapt[i]
                        angle_cible=i
                        
                # Sets the angle aimed by the car
                angle_raw = angle_cible # pour acquisition
                
                # Direction law which refers to the README file
                if abs(angle_cible)<15:
                        angle_consigne=0
                elif abs(angle_cible)<50:
                        angle_consigne=min(10,max(-10,angle_cible))
                else:
                        angle_consigne=min(22,max(-22,angle_cible))
                
                # Changes steering angle of the car, aiming the farthest point
                consigne_servo=60*((angle_consigne+22)/44+1)
                
                duty = deg_0_duty + (consigne_servo/180.0)* duty_range
                pwm_servo.ChangeDutyCycle(duty)
                
                ###################  LOI DE VITESSE  #####################
                alpha_max = 30
                #d_frontcar = mapt[0]
                # Different law from the README file
                v=vmin+(vmax-vmin)*(1-exp(-mapt[0]*3/d))*(1-abs(consigne_servo-90)/alpha_max)
                # v = v_cste              
                consigne_moteur=v
                pwm_moteur.ChangeDutyCycle(consigne_moteur)
                ################## FIN CONSIGNE VITESSE ##################
                

                #################### DATA ACQUISITION, WRITING ##################
                file_obj.write("%f %f %f %f %f %f\n"%(time.time(),mapt[0],v,angle_raw, angle_cible, consigne_servo))
                
                file_obj_map.write("%f "%(time.time()))
                file_obj_map.writelines(str(map))
                file_obj_map.write("\n")
                
                data=[]

            
            if go==0 and flag:
                pwm_moteur.ChangeDutyCycle(0)
                pwm_moteur.stop()
            ####################  END OF MAIN LOOP  ########################

    
except Exception as err:
        print(type(err).__name__)
        print(err)
        lidar.stop_motor()
        lidar.reset()
        lidar.disconnect()
        file_obj.close()
        
try:
    lidar.stop_motor()
    lidar.reset()
    lidar.disconnect()
    file_obj.close()
except Exception as err:
    print(type(err).__name__)
