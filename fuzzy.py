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


def motors(leftcycle, rightcycle):
    fr1.duty_cycle = rightcycle
    fr2.value = 0
    br1.duty_cycle = rightcycle
    br2.value = 0

    fl1.duty_cycle = leftcycle
    fl2.value = 0
    bl1.duty_cycle = leftcycle
    bl2.value = 0


def loop():
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
    leftmotorspeed = np.arange(0, 20, 1)
    front_lo = fuzz.trimf(frontobstical , [0, 0, 20])
    front_md = fuzz.trimf(frontobstical , [10, 30, 50])
    front_hi = fuzz.trimf(frontobstical , [30, 200, 200])
    left_lo = fuzz.trimf(leftobstical , [0, 0, 20])
    left_md = fuzz.trimf(leftobstical , [10, 30, 50])
    left_hi = fuzz.trimf(leftobstical , [30, 200, 200])
    right_lo = fuzz.trimf(rightobstical , [0, 0, 20])
    right_md = fuzz.trimf(rightobstical , [10, 30, 50])
    right_hi = fuzz.trimf(rightobstical , [30, 200, 200])
    print("roomofset", roomofset)
    while True:

        #get readings from US and Compas.
        head = get_heading(sensor)
        #print("heading: {:.2f} degrees".format(head))
        roomhead = headchange(head, (roomofset+gridheading))#alighnes heading to room
        print("roomhead: ", roomhead, "roomofset", roomofset, "heading:", head, "count:", count)
        #print(head)
        try:
            fail = "bl"
            bl = sonarbl.distance
            fail = "bm"
            bm = sonarbm.distance
            fail = "fm"
            fm = sonarfm.distance
            fail = "fl"
            fl = sonarfl.distance
            fail = "fr"
            fr = sonarfr.distance

            fail = "br"
            br = sonarbr.distance
            print("fl: ", fl, "fm: ", fm, "fr: ", fr, "bl: ", bl, "bm:", bm, "br:", br)
        except RuntimeError:
            print("Retrying failed:", fail, "fl: ", fl, "fm: ", fm, "fr: ", fr, "bl: ", bl, "bm:", bm, "br:", br)
        ymeasured = bm * cos(roomhead)
        xmeasured = bl*cos(roomhead)


        leftobsticalclose = fuzz.interp_membership(leftobstical  , left_hi, fl)
        leftobsticalmid = fuzz.interp_membership(leftobstical  , left_mid, fl)
        leftobsticalfar = fuzz.interp_membership(leftobstical  , left_lo, fl)

        rightobsticalclose = fuzz.interp_membership(rightobstical  , right_hi, fm)
        rightobsticalmid = fuzz.interp_membership(rightobstical  , right_mid, fm)
        rightobsticalfar = fuzz.interp_membership(rightobstical  , right_lo, fm)

        frontobsticalclose = fuzz.interp_membership(frontobstical, front_hi, fr)
        frontobsticalmid = fuzz.interp_membership(frontobstical, front_mid, fr)
        frontobsticalfar = fuzz.interp_membership(frontobstical, front_lo, fr)

        leftmotorspeed = fuzz.interp_membership(frontobstical, front_hi, fr)


        #logic starts here

        count = count + 1

        for i in range(0, 101, 1):
            motors(i,i)
        """
        
         print("x = ", xmeasured, "y = ", ymeasured )
        close = x_close(xmeasured)
        mid = x_mid(xmeasured)
        far = x_far(xmeasured)
        
        if(360-headtolerance) < roomhead or roomhead < headtolerance:
                if chill == 0:
                    fr1.value = 0
                    fr2.value = 0
                    br1.value = 0
                    br2.value = 0

                    fl1.value = 0
                    fl2.value = 0
                    bl1.value = 0
                    bl2.value = 0
                    time.sleep(0.2)
                    chill = 1
                print("go!")
                fr1.value = 1
                fr2.value = 0
                br1.value = 1
                br2.value = 0

                fl1.value = 1
                fl2.value = 0
                bl1.value = 1
                bl2.value = 0
                if fm < 10:
                    #roomofset = headchange(roomofset, 30)
                    fr1.value = 0
                    fr2.value = 0
                    br1.value = 0
                    br2.value = 0

                    fl1.value = 0
                    fl2.value = 0
                    bl1.value = 0
                    bl2.value = 0
                    time.sleep(0.5)

        elif roomhead > 180:
            chill = 0
            print("turn right")  # from low numbers towards north
            fr1.value = 0
            fr2.value = 1
            br1.value = 0
            br2.value = 1

            fl1.value = 1
            fl2.value = 0
            bl1.value = 1
            bl2.value = 0
        else:
            chill = 1
            print("turn left")  # from high numbers towards north
            fr1.value, fr2.value = 1, 0
            br1.value, br2.value = 1, 0
            fl1.value, fl2.value = 0, 1
            bl1.value, bl2.value = 0, 1
        """
        #time.sleep(0.1)


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

"""
def trapmf(x, points):
    pointA = points[0]
    pointB = points[1]
    pointC = points[2]
    pointD = points[3]
    slopeAB = getSlope(pointA, 0, pointB, 1)
    slopeCD = getSlope(pointC, 1, pointD, 0)
    yInterceptAB = getYIntercept(pointA, 0, pointB, 1)
    yInterceptCD = getYIntercept(pointC, 1, pointD, 0)
    result = 0
    if x > pointA and x < pointB:
        result = slopeAB * x + yInterceptAB
    elif x >= pointB and x <= pointC:
        result = 1
    elif x > pointC and x < pointD:
        result = slopeCD * x + yInterceptCD
    return result
    
    def x_far(x): #  T\ left edge shape
    fallstart = 30
    fallend = 40
    if x <= fallstart:
        return 1
    elif x >= fallend:
        return 0
    elif fallstart < x < fallend:
        return (fallend - x) / (fallend - fallstart)#falling edge


def x_mid(x): # /T\ shape in middel
    leftend =10
    fullleft = 20
    fullright = 25
    rightend = 35
    if x <= leftend:
        return 0
    elif x >= rightend:
        return 0
    elif leftend < x < fullleft:
        return (x - leftend) / (fullleft - leftend)#rising edge
    elif fullleft >= x >= fullright:
        return 1
    elif fullright < x < rightend:
        return (rightend - x) / (rightend - fullright)# falling edge


def x_close(x): # /T shape right end
    fallstart = 5
    fallend = 15
    if x >= fallstart:
        return 1
    elif x <= fallend:
        return 0
    elif fallend < x < fallstart:
        return (fallend - x) / (fallend - fallstart)#falling edge

    
    """