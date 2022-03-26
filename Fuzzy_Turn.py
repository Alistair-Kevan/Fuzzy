import time
from math import atan2, degrees, cos
import RPi.GPIO
import board
import digitalio
import pwmio
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
import adafruit_hcsr04
import adafruit_lsm303dlh_mag
import numpy as np
import skfuzzy as fuzz
#import matplotlib.pyplot as plt
#ensure gpios are clean
RPi.GPIO.cleanup()
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

# head = (head + change) % 360
def headchange(head, change):
    head = head + change  # add change to head
    if 360 <= head: #if new head is too large
        head = head - 360 # reduce head by 360
    if head < 0:# if head is now neative
        head = head + 360  # increase head by 360
    return head  # return processed resultant heading


def motors(leftcycle,leftback, rightcycle,rightback):
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
    #obstical ranges are from 0 to 200 cm,
    #motor speeds are multipliers, 0 to 1 is 0% to 100% speed
    frontobstical = np.arange(0, 200, 1)  # 0,11,1
    leftobstical = np.arange(0, 200, 1)
    rightobstical = np.arange(0, 200, 1)
    leftmotorspeed = np.arange(0, 1, 0.01)
    rightmotorspeed = np.arange(0, 1, 0.01)
    #define input membership funtions
    front_lo = fuzz.trapmf(frontobstical, [0, 0, 20, 100])
    front_md = fuzz.trimf(frontobstical, [50, 100, 150])
    front_hi = fuzz.trimf(frontobstical, [100, 200, 200])
    left_lo = fuzz.trapmf(leftobstical, [0, 0, 20, 100])
    left_md = fuzz.trimf(leftobstical, [50, 100, 150])
    left_hi = fuzz.trimf(leftobstical, [100, 200, 200])
    right_lo = fuzz.trapmf(rightobstical, [0, 0, 20, 100])
    right_md = fuzz.trimf(rightobstical, [50, 100, 150])
    right_hi = fuzz.trimf(rightobstical, [100, 200, 200])
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
        leftobsticalclose = fuzz.interp_membership(leftobstical, left_lo, fl)
        leftobsticalmid = fuzz.interp_membership(leftobstical, left_md, fl)
        leftobsticalfar = fuzz.interp_membership(leftobstical, left_hi, fl)
        rightobsticalclose = fuzz.interp_membership(rightobstical, right_lo, fr)
        rightobsticalmid = fuzz.interp_membership(rightobstical, right_md, fr)
        rightobsticalfar = fuzz.interp_membership(rightobstical, right_hi, fr)
        frontobsticalclose = fuzz.interp_membership(frontobstical, front_lo, fm)
        frontobsticalmid = fuzz.interp_membership(frontobstical, front_md, fm)
        frontobsticalfar = fuzz.interp_membership(frontobstical, front_hi, fm)

        # The OR operator means we take the maximum of these two. (Fmax = OR)
        # map left obsticals to right speeds
        active_rule1 = np.fmax(leftobsticalclose, frontobsticalclose)
        right_activation_close = np.fmin(active_rule1,right_slow)  # if left or middle obsticle close, right motor slow
        active_rule2 = np.fmax(leftobsticalmid, frontobsticalmid)# if left obstical or front obstical close
        right_activation_md = np.fmin(active_rule2, right_trundle)  # right motor slow
        active_rule3 = np.fmin(leftobsticalfar, frontobsticalfar)# if left and front obstical far, right motor fast
        right_activation_far = np.fmin(active_rule3, right_fast)
        # map right obsticals to left speeds
        left_activation_close = np.fmin(rightobsticalclose, left_slow)#If right obstical close, left motor slow
        left_activation_md = np.fmin(rightobsticalmid, left_trundle)
        left_activation_far = np.fmin(rightobsticalfar, left_fast)
        #defuzzyfy left and right motor speeds
        aggregatedleft =np.fmax(left_activation_close, np.fmax(left_activation_md, left_activation_far))
        leftcrispspeed = (fuzz.defuzz(leftmotorspeed, aggregatedleft, 'centroid'))
        aggregatedright =np.fmax(right_activation_close, np.fmax(right_activation_md, right_activation_far))
        rightcrispspeed = (fuzz.defuzz(rightmotorspeed, aggregatedright, 'centroid'))
        print("left,right:", rightcrispspeed, leftcrispspeed)  #  print crisp motor speeds
        # fuzzy override
        if fm > 17 and fr > 10 and fl > 10: #if (no immidate obsticals)
            motors(rightcrispspeed, 0, leftcrispspeed, 0) # fuzzy defined motor speeds
        elif fl > fr:#else if obsticals closest on right
            motors(1, 0, 0, 1) #turn on spot left
        else:
            motors(0, 1, 1, 0)#else turn on spot right


if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
        print("destroyed!")

