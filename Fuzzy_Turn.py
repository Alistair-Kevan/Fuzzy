import time
from math import atan2, degrees, cos
import RPi.GPIO
import board
import digitalio
import pwmio
import adafruit_hcsr04
import adafruit_lsm303dlh_mag
import numpy as np
import skfuzzy as fuzz
#import matplotlib.pyplot as plt
RPi.GPIO.cleanup()#ensure gpios are clean
#create objects for each sesnor, f/b = front/back l/m/r = left/middle/right
sonarfl = adafruit_hcsr04.HCSR04(trigger_pin=board.D9, echo_pin=board.D11)  # 9, 11
sonarfm = adafruit_hcsr04.HCSR04(trigger_pin=board.D5, echo_pin=board.D6)
sonarfr = adafruit_hcsr04.HCSR04(trigger_pin=board.D22, echo_pin=board.D10)  # 22, 10
sonarbr = adafruit_hcsr04.HCSR04(trigger_pin=board.D17, echo_pin=board.D27)  # 17,27
sonarbm = adafruit_hcsr04.HCSR04(trigger_pin=board.D14, echo_pin=board.D15)  # 24,25
sonarbl = adafruit_hcsr04.HCSR04(trigger_pin=board.D25, echo_pin=board.D18)  # 18, 23
fl = 0
fm = 0
fr = 0
br = 0
bm = 0
bl = 0

i2c = board.I2C()  # uses board.SCL and board.SDA initates i2c communcation for lsm303dlhc
sensor = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
fr1 = pwmio.PWMOut(board.D20)  # front right motor pair
fr2 = pwmio.PWMOut(board.D21)

br1 = pwmio.PWMOut(board.D16)  # back right motor pair
br2 = pwmio.PWMOut(board.D12)

fl1 = pwmio.PWMOut(board.D7)  # front left motor pair
fl2 = pwmio.PWMOut(board.D8)

bl1 = pwmio.PWMOut(board.D19)  # back left motor pair
bl2 = pwmio.PWMOut(board.D26)


def destroy():
    fr1.deinit()  # stop the  PWM outputs
    fr2.deinit()
    fl1.deinit()
    fl2.deinit()
    br1.deinit()
    br2.deinit()
    bl1.deinit()
    bl2.deinit()
    i2c.deinit()
    RPi.GPIO.cleanup()
    print("\nCleaned up GPIO resources.")


def vector_2_degrees(x, y):
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle += 360
    return angle


def get_heading(_sensor):
    magnet_x, magnet_y, _ = _sensor.magnetic
    return vector_2_degrees(magnet_x, magnet_y)


def setup():#find robot's start up heading and make it negative
    roomdeg = get_heading(sensor)
    roomdeg = -1*roomdeg
    print("set up")
    return roomdeg

#
def headchange(head, change):
    head = (head + change) % 360
    return head  # return processed resultant heading


def motors(leftcycle, leftback, rightcycle, rightback):
    fr1.duty_cycle = rightcycle*65535  # right motors
    fr2.duty_cycle = rightback*65535
    br1.duty_cycle = rightcycle*65535
    br2.duty_cycle = rightback*65535

    fl1.duty_cycle = leftcycle*65535  # left motors
    fl2.duty_cycle = leftback*65535
    bl1.duty_cycle = leftcycle*65535
    bl2.duty_cycle = leftback*65535


def loop():
    print("loop")
    global fl, fm, fr, br, bm, bl
    roomofset = setup()#save room orienation
    gridheading = 0 #direction relative to start position
    fail = "bigfail" # variable for tracking US sensor failures
    # Fuzzy Control: Generate universe variables
    #Obstacle ranges are from 0 to 200 cm,
    #motor speeds are multipliers, 0 to 1 is 0% to 100% speed
    frontObstacle = np.arange(0, 200, 1)  # 0,11,1
    leftObstacle = np.arange(0, 200, 1)
    rightObstacle = np.arange(0, 200, 1)
    leftmotorspeed = np.arange(0, 1, 0.01)
    rightmotorspeed = np.arange(0, 1, 0.01)
    #define input membership funtions
    front_lo = fuzz.trapmf(frontObstacle, [0, 0, 20, 100])
    front_md = fuzz.trimf(frontObstacle, [50, 100, 150])
    front_hi = fuzz.trimf(frontObstacle, [100, 200, 200])
    left_lo = fuzz.trapmf(leftObstacle, [0, 0, 20, 100])
    left_md = fuzz.trimf(leftObstacle, [50, 100, 150])
    left_hi = fuzz.trimf(leftObstacle, [100, 200, 200])
    right_lo = fuzz.trapmf(rightObstacle, [0, 0, 20, 100])
    right_md = fuzz.trimf(rightObstacle, [50, 100, 150])
    right_hi = fuzz.trimf(rightObstacle, [100, 200, 200])
    #define output mebership functions
    left_slow = fuzz.trimf(leftmotorspeed, [0, 0, 0.3])
    left_trundle = fuzz.trimf(leftmotorspeed, [0.2, .5, 0.8])
    left_fast = fuzz.trimf(leftmotorspeed, [0.7, 1, 1])
    right_slow = fuzz.trimf(rightmotorspeed, [0, 0, 0.3])
    right_trundle = fuzz.trimf(leftmotorspeed, [0.2, .5, 0.8])
    right_fast = fuzz.trimf(rightmotorspeed, [0.7, 1, 1])
    #print("roomofset", roomofset)
    while True:
        #get readings from US and Compas.
        head = get_heading(sensor)
        #print("heading: {:.2f} degrees".format(head))
        roomhead = headchange(head, (roomofset+gridheading))#alighnes heading to room
        print("roomhead: ", roomhead, "roomofset", roomofset, "heading:", head)
        try:
            fail = "fm"
            fm = sonarfm.distance
            fail = "fl"
            fr = sonarfl.distance
            fail = "fr"
            fl = sonarfr.distance
            """fail = "br" #back sensors are not used
            br = sonarbr.distance
            fail = "bl"
            bl = sonarbl.distance
            fail = "bm"
            bm = sonarbm.distance"""
            print("fl: ", fl, "fr: ", fr, "fm: ", fm,  "bl: ", bl, "bm:", bm, "br:", br)
        except RuntimeError:
            print("Retrying failed at sensor:", fail, "fl: ", fl, "fm: ", fm, "fr: ", fr, "bl: ", bl, "bm:", bm, "br:", br)
        if fm > 199:#cap us sensor range to 200.
            fm = 199
        if fl > 199:
            fl = 199
        if fr > 199:
            fr = 199
        leftObstacleclose = fuzz.interp_membership(leftObstacle, left_lo, fl)
        leftObstaclemid = fuzz.interp_membership(leftObstacle, left_md, fl)
        leftObstaclefar = fuzz.interp_membership(leftObstacle, left_hi, fl)
        rightObstacleclose = fuzz.interp_membership(rightObstacle, right_lo, fr)
        rightObstaclemid = fuzz.interp_membership(rightObstacle, right_md, fr)
        rightObstaclefar = fuzz.interp_membership(rightObstacle, right_hi, fr)
        frontObstacleclose = fuzz.interp_membership(frontObstacle, front_lo, fm)
        frontObstaclemid = fuzz.interp_membership(frontObstacle, front_md, fm)
        frontObstaclefar = fuzz.interp_membership(frontObstacle, front_hi, fm)

        # The OR operator means we take the maximum of these two. (Fmax = OR)
        # map left obstacles to right speeds
        active_rule1 = np.fmax(leftObstacleclose, frontObstacleclose)
        right_activation_close = np.fmin(active_rule1,right_slow)  # if left or middle Obstacleclose, right motor slow

        active_rule2 = np.fmax(leftObstaclemid, frontObstaclemid)# if left Obstacle or front Obstacle close
        right_activation_md = np.fmin(active_rule2, right_trundle)  # right motor slow
        active_rule3 = np.fmin(leftObstaclefar, frontObstaclefar)# if left and front Obstacle far, right motor fast
        right_activation_far = np.fmin(active_rule3, right_fast)
        # map right Obstacles to left speeds
        left_activation_close = np.fmin(rightObstacleclose, left_slow)#If right Obstacle close, left motor slow
        left_activation_md = np.fmin(rightObstaclemid, left_trundle)
        left_activation_far = np.fmin(rightObstaclefar, left_fast)
        #defuzzyfy left and right motor speeds
        aggregatedleft =np.fmax(left_activation_close, np.fmax(left_activation_md, left_activation_far))
        leftcrispspeed = (fuzz.defuzz(leftmotorspeed, aggregatedleft, 'centroid'))
        aggregatedright =np.fmax(right_activation_close, np.fmax(right_activation_md, right_activation_far))
        rightcrispspeed = (fuzz.defuzz(rightmotorspeed, aggregatedright, 'centroid'))
        print("left,right:", rightcrispspeed, leftcrispspeed)  #  print crisp motor speeds
        # fuzzy override
        if fm > 17 and fr > 10 and fl > 10:  # if (no immediate obstacles)
            motors(rightcrispspeed, 0, leftcrispspeed, 0)  # fuzzy defined motor speeds
        elif fl > fr:  # else if obstacles are the closest on right
            motors(1, 0, 0, 1)  # turn on spot left
        else:
            motors(0, 1, 1, 0)  # else turn on spot right


if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
        print("destroyed!")

