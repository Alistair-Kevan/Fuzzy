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

#
def headchange(head, change):
    return (head + change) % 360


def motors(leftforward,leftback, rightcycle,rightback):
    fr1.duty_cycle = rightcycle*65535  # right motors
    fr2.duty_cycle = rightback*65535
    br1.duty_cycle = rightcycle*65535
    br2.duty_cycle = rightback*65535

    fl1.duty_cycle = leftforward*65535  # left motors
    fl2.duty_cycle = leftback*65535
    bl1.duty_cycle = leftforward*65535
    bl2.duty_cycle = leftback*65535


def loop():
    print("loop")
    global fl, fm, fr, br, bm, bl
    roomofset = setup()#save room orienation
    gridheading = 0 #direction relative to start position
    headtolerance = 10
    fail = "bigfail" # variable for tracking US sensor failures
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
            """fail = "br" #back sensors are not used (extra time taken to fire each sensor)
            br = sonarbr.distance
            fail = "bl"
            bl = sonarbl.distance
            fail = "bm"
            bm = sonarbm.distance"""
            print("fl: ", fl, "fr: ", fr, "fm: ", fm,  "bl: ", bl, "bm:", bm, "br:", br)
        except RuntimeError:
            print("Retrying failed at sensor:", fail, "fl: ", fl, "fm: ", fm, "fr: ", fr, "bl: ", bl, "bm:", bm, "br:", br)
        # fuzzy override
        if (360 - headtolerance) < head or head < headtolerance:
            motors(1, 0, 1, 0)  # fuzzy defined motor speeds
        elif head > 180:
            print("turn right")  # from low numbers towards north
            motors(1, 0, 0, 1)  # turn on spot left
        else:
            print("turn left")  # from high numbers towards

            motors(0, 1, 1, 0)  # else turn on spot right
        """ AVOID OBSTICLE AS IN FUZZY.PY
        if fm > 17 and fr > 10 and fl > 10:  # if (no immidate obsticals)
            motors(1, 0, 1, 0)  # fuzzy defined motor speeds
        elif fl > fr:  # else if obsticals closest on right
            motors(1, 0, 0, 1)  # turn on spot left
        else:
            motors(0, 1, 1, 0)  # else turn on spot right
        """

if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
        print("destroyed!")

