# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import adafruit_hcsr04
# from adafruit_hcsr04 import HCSR04
import RPi.GPIO
import board
import digitalio


RPi.GPIO.cleanup()
sonarfl = adafruit_hcsr04.HCSR04(trigger_pin=board.D9, echo_pin=board.D11)#9, 11
sonarbr = adafruit_hcsr04.HCSR04(trigger_pin=board.D17, echo_pin=board.D27)  # 17,27
sonarbm = adafruit_hcsr04.HCSR04(trigger_pin=board.D14, echo_pin=board.D15)  # 24,25
sonarbl = adafruit_hcsr04.HCSR04(trigger_pin=board.D25, echo_pin=board.D23)  # 18, 23
fl = 0
br = 0
bm = 0
bl = 0

def destroy():
    RPi.GPIO.cleanup()
    print("\nCleaned up GPIO resources.")


while True:
    try:

        fl = sonarfl.distance
        br = sonarbr.distance
        bm = sonarbm.distance
        bl = sonarbl.distance



        #br = sonarbr.distance
        print("fl:", fl, "bl: ", bl, "br:", br, "bm: ", bm)
    except RuntimeError:
        print("Retrying!", "fl:", fl, "bl: ", bl, "br:", br, "bm: ", bm) #bm, "br:", br)
    except KeyboardInterrupt:
        destroy()
    time.sleep(0.3)
