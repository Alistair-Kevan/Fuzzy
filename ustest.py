# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import adafruit_hcsr04
# from adafruit_hcsr04 import HCSR04
import RPi.GPIO
import board
import digitalio

RPi.GPIO.cleanup()
sonarbr = adafruit_hcsr04.HCSR04(trigger_pin=board.D17, echo_pin=board.D27)  # 17,27
sonarbm = adafruit_hcsr04.HCSR04(trigger_pin=board.D24, echo_pin=board.D25)  # 24,25
sonarbl = adafruit_hcsr04.HCSR04(trigger_pin=board.D18, echo_pin=board.D23)  # 18, 23


def destroy():
    RPi.GPIO.cleanup()
    print("\nCleaned up GPIO resources.")


while True:
    try:
        bl = sonarbl.distance
        bm = sonarbm.distance
        br = sonarbr.distance
        print("bl: ", bl, "bm:", bm, "br:", br)
    except RuntimeError:
        print("Retrying!", "bl: ", bl, "bm:", bm, "br:", br)
    except KeyboardInterrupt:
        destroy()
    time.sleep(0.3)





