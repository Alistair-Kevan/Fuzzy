import RPi.GPIO as GPIO
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

""" Display compass heading data five times per second """
import time
from math import atan2, degrees
import board.I2C
import adafruit_lsm303dlh_mag

i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)


def vector_2_degrees(x, y):
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle += 360
    return angle


def get_heading(_sensor):
    magnet_x, magnet_y, _ = _sensor.magnetic
    return vector_2_degrees(magnet_x, magnet_y)





def setup():
    # Use GPIO numbers not pin numbers

    GPIO.setmode(GPIO.BOARD)

    # set up the GPIO channels - one input and one output
    GPIO.setup(40, GPIO.OUT)
    GPIO.setup(38, GPIO.OUT)
    GPIO.setup(36, GPIO.OUT)
    GPIO.setup(32, GPIO.OUT)

    GPIO.setup(26, GPIO.OUT)
    GPIO.setup(24, GPIO.OUT)
    GPIO.setup(35, GPIO.OUT)
    GPIO.setup(37, GPIO.OUT)


def loop():
    while True:

        head = get_heading(sensor)
        print("heading: {:.2f} degrees".format(head))
        print(head)
        if head > 20.0 and head < 340.0:
            print("turn")
            GPIO.output(35, 0)  # back left fw
            GPIO.output(37, 1)

            GPIO.output(40, 1)  # front right fw
            GPIO.output(38, 0)

            # leftfw
            GPIO.output(26, 1)
            GPIO.output(24, 0)
            GPIO.output(36, 1)
            GPIO.output(32, 0)
        else:
            print("go!")
            GPIO.output(35, 1)  # back left fw
            GPIO.output(37, 0)

            GPIO.output(40, 0)  # front right fw
            GPIO.output(38, 1)

            # leftfw
            GPIO.output(26, 1)
            GPIO.output(24, 0)
            GPIO.output(36, 1)
            GPIO.output(32, 0)
        time.sleep(0.01)

        # output to GPIO8
        # rightfw




def destroy():
    # pwm.stop()
    # rightfw
    GPIO.output(35, 0)
    GPIO.output(37, 0)

    GPIO.output(40, 0)
    GPIO.output(38, 0)
    # leftfw
    GPIO.output(26, 0)
    GPIO.output(24, 0)
    GPIO.output(36, 0)
    GPIO.output(32, 0)
    GPIO.cleanup()


if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
