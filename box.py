import time
from math import atan2, degrees
import RPi.GPIO
import board
import digitalio
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
import adafruit_hcsr04
import adafruit_lsm303dlh_mag
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
fr1 = digitalio.DigitalInOut(board.D20)  # front right motor pair
fr1.direction = digitalio.Direction.OUTPUT
fr2 = digitalio.DigitalInOut(board.D21)
fr2.direction = digitalio.Direction.OUTPUT

br1 = digitalio.DigitalInOut(board.D16)  # 19 back right motor pair
br1.direction = digitalio.Direction.OUTPUT
br2 = digitalio.DigitalInOut(board.D12)  # 26
br2.direction = digitalio.Direction.OUTPUT

fl1 = digitalio.DigitalInOut(board.D7)  # front left motor pair
fl1.direction = digitalio.Direction.OUTPUT
fl2 = digitalio.DigitalInOut(board.D8)
fl2.direction = digitalio.Direction.OUTPUT

bl1 = digitalio.DigitalInOut(board.D19)  # 12 back left motor pair
bl1.direction = digitalio.Direction.OUTPUT
bl2 = digitalio.DigitalInOut(board.D26)  # 16
bl2.direction = digitalio.Direction.OUTPUT


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

def loop():
    global fl
    global fm
    global fr
    global br
    global bm
    global bl
    ygoal = 200
    headtolerance = 5
    roomofset = setup()#save room orienation
    count = 0
    print("roomofset", roomofset)
    while True:

        #get readings from US and Compas.
        head = get_heading(sensor)
        #print("heading: {:.2f} degrees".format(head))
        roomhead = headchange(head, roomofset)#alighnes heading to room
        print("roomhead: ", roomhead, "roomofset", roomofset, "heading:", head, "count:", count)
        #print(head)
        try:
            fail = "bm"
            bm = sonarbm.distance
            fail = "fm"
            fm = sonarfm.distance
            fail = "fl"
            fl = sonarfl.distance
            fail = "fr"
            fr = sonarfr.distance
            fail = "bl"
            bl = sonarbl.distance
            fail = "br"
            br = sonarbr.distance


            print("fl: ", fl, "fm: ", fm, "fr: ", fr, "bl: ", bl, "bm:", bm, "br:", br)
        except RuntimeError:
            print("Retrying failed:", fail, "fl: ", fl, "fm: ", fm, "fr: ", fr, "bl: ", bl, "bm:", bm, "br:", br)
        #logic starts here
        ymeasured = bm
        xmeasured = bl
        count = count + 1
        if fm < 10:
            print("stop!")
            fr1.value = 0
            fr2.value = 0
            br1.value = 0
            br2.value = 0

            fl1.value = 0
            fl2.value = 0
            bl1.value = 0
            bl2.value = 0
            headchange(roomofset, 90)
        elif(360-headtolerance) < roomhead or roomhead < headtolerance:
            if count >= 50:
                headchange(roomofset, 90)
                count = 0
                print("TURNING 90!")
            elif count < 100:
                print("go!")
                fr1.value = 1
                fr2.value = 0
                br1.value = 1
                br2.value = 0

                fl1.value = 1
                fl2.value = 0
                bl1.value = 1
                bl2.value = 0
        elif roomhead > 180:
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
            print("turn left")  # from high numbers towards north
            fr1.value = 1
            fr2.value = 0
            br1.value = 1
            br2.value = 0

            fl1.value = 0
            fl2.value = 1
            bl1.value = 0
            bl2.value = 1
        time.sleep(0.01)


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
