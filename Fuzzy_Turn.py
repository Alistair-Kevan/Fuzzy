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

br1 = pwmio.PWMOut(board.D16)  # 19 back right motor pair
br2 = pwmio.PWMOut(board.D12)  # 26

fl1 = pwmio.PWMOut(board.D7)  # front left motor pair
fl2 = pwmio.PWMOut(board.D8)

bl1 = pwmio.PWMOut(board.D19)  # 12 back left motor pair
bl2 = pwmio.PWMOut(board.D26)  # 16


def destroy():
    fr1.stop()  # stop the  PWM output
    fr2.stop()
    fl1.stop()
    fl2.stop()
    br1.stop()
    br2.stop()
    bl1.stop()
    bl2.stop()
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


def setup():
    roomdeg = get_heading(sensor)
    roomdeg = -1*roomdeg
    print("set up")
    return roomdeg


def headchange(goalhead, change):
    goalhead = goalhead + change
    if 360 <= goalhead:
        goalhead = goalhead - 360
    if goalhead < 0:
        goalhead = goalhead + 360
    return goalhead


def motors(leftcycle,leftback, rightcycle,rightback):
    fr1.duty_cycle = rightcycle
    fr2.duty_cycle = rightback
    br1.duty_cycle = rightcycle
    br2.duty_cycle = rightback

    fl1.duty_cycle = leftcycle
    fl2.duty_cycle = leftback
    bl1.duty_cycle = leftcycle
    bl2.duty_cycle = leftback


def loop():
    print("loop")
    global fl
    global fm
    global fr
    global br
    global bm
    global bl
    #silly variable
    ygoal = 200
    headtolerance = 10
    roomofset = setup()#save room orienation
    gridheading = 0 #direction relative to start position
    count = 0
    chill =0
    fail = "bigfail"
    #fuzzy
    # Generate universe variables
    #   * Quality and leftice on subjective ranges [0, 10]
    #   * Tip has a range of [0, 25] in units of percentage points
    frontobstical = np.arange(0, 200, 1)  # 0,11,1
    leftobstical = np.arange(0, 200, 1)
    rightobstical = np.arange(0, 200, 1)
    leftmotorspeed = np.arange(0, 1, 0.01)
    rightmotorspeed = np.arange(0, 1, 0.01)

    front_lo = fuzz.trapmf(frontobstical, [0, 0, 20, 100])
    front_md = fuzz.trimf(frontobstical, [50, 100, 150])
    front_hi = fuzz.trimf(frontobstical, [100, 200, 200])
    left_lo = fuzz.trapmf(leftobstical, [0, 0, 20, 100])
    left_md = fuzz.trimf(leftobstical, [50, 100, 150])
    left_hi = fuzz.trimf(leftobstical, [100, 200, 200])
    right_lo = fuzz.trapmf(rightobstical, [0, 0, 20, 100])
    right_md = fuzz.trimf(rightobstical, [50, 100, 150])
    right_hi = fuzz.trimf(rightobstical, [100, 200, 200])

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
        print("roomhead: ", roomhead, "roomofset", roomofset, "heading:", head, "count:", count)
        #print(head)
        try:

            fail = "fm"
            fm = sonarfm.distance
            fail = "fl"
            fr = sonarfl.distance
            fail = "fr"
            fl = sonarfr.distance
            """
            fail = "br"
            br = sonarbr.distance
            fail = "bl"
            bl = sonarbl.distance
            fail = "bm"
            bm = sonarbm.distance
            """
            print("fl: ", fl, "fr: ", fr, "fm: ", fm,  "bl: ", bl, "bm:", bm, "br:", br)
        except RuntimeError:
            print("Retrying failed:", fail, "fl: ", fl, "fm: ", fm, "fr: ", fr, "bl: ", bl, "bm:", bm, "br:", br)
        if fm > 199:
            fm = 199
        if fl > 199:
            fl = 199
        if fr > 199:
            fr = 199
        #ymeasured = bm * cos(roomhead)
        #xmeasured = bl*cos(roomhead)

        #print("membership")
        leftobsticalclose = fuzz.interp_membership(leftobstical, left_lo, fl)
        leftobsticalmid = fuzz.interp_membership(leftobstical, left_md, fl)
        leftobsticalfar = fuzz.interp_membership(leftobstical, left_hi, fl)

        rightobsticalclose = fuzz.interp_membership(rightobstical, right_lo, fr)
        rightobsticalmid = fuzz.interp_membership(rightobstical, right_md, fr)
        rightobsticalfar = fuzz.interp_membership(rightobstical, right_hi, fr)

        frontobsticalclose = fuzz.interp_membership(frontobstical, front_lo, fm)
        frontobsticalmid = fuzz.interp_membership(frontobstical, front_md, fm)
        frontobsticalfar = fuzz.interp_membership(frontobstical, front_hi, fm)
        #print("rules")
        # The OR operator means we take the maximum of these two.
        active_rule1 = np.fmax(leftobsticalclose, frontobsticalclose)
        # Now we apply this by clipping the top off the corresponding output
        # membership function with `np.fmin`
        # map left obsticals to right speeds
        right_activation_close = np.fmin(active_rule1,right_slow)  # if left or middle obstcial close, righ motor slow

        active_rule2 = np.fmax(leftobsticalmid, frontobsticalmid)# if left obstical or front obstical close
        right_activation_md = np.fmin(active_rule2, right_trundle)  # right motor slow

        active_rule3 = np.fmin(leftobsticalfar, frontobsticalfar)# if left and front obstical far, right motor fast
        right_activation_far = np.fmin(active_rule3, right_fast)

        # map right obsticals to left speeds
        left_activation_close = np.fmin(rightobsticalclose, left_slow)
        left_activation_md = np.fmin(rightobsticalmid, left_trundle)
        left_activation_far = np.fmin(rightobsticalfar, left_fast)

        right0 = np.zeros_like(rightmotorspeed)
        left0 = np.zeros_like(leftmotorspeed)
        #print("defuzzy")
        #defuzzy
        aggregatedleft =np.fmax(left_activation_close, np.fmax(left_activation_md, left_activation_far))
        leftcrispspeed = (fuzz.defuzz(leftmotorspeed, aggregatedleft, 'centroid')*65535)

        aggregatedright =np.fmax(right_activation_close, np.fmax(right_activation_md, right_activation_far))
        rightcrispspeed = (fuzz.defuzz(rightmotorspeed, aggregatedright, 'centroid')*65535)

        print("left,right:", rightcrispspeed, leftcrispspeed)
        if fm > 17 and fr > 5 and fl > 5: #if (no immidate obsticals
            motors(rightcrispspeed, 0, leftcrispspeed, 0) # fuzzy defined motor speeds
        elif fl > fr:#else if obsticals closest on right
            motors(65535, 0, 0, 65535) #turn on spot left
        else:
            motors(0, 65535, 65535, 0)#else turn on spot right




if __name__ == '__main__':
    #print("go!")
    #setup()
    #print("setup")
    try:
        #print("try loop!")
        loop()
        #print("exit loop?")
    except KeyboardInterrupt:
       # print("destroy")
        destroy()
        print("destroyed!")

