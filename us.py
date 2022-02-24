# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import adafruit_hcsr04
#from adafruit_hcsr04 import HCSR04
import RPi.GPIO
import board
import digitalio

RPi.GPIO.cleanup()
sonarfl = adafruit_hcsr04.HCSR04(trigger_pin=board.D9, echo_pin=board.D11)#9, 11
sonarfm = adafruit_hcsr04.HCSR04(trigger_pin=board.D5, echo_pin=board.D6)
sonarfr = adafruit_hcsr04.HCSR04(trigger_pin=board.D22, echo_pin=board.D10)#22, 10

sonarbr = adafruit_hcsr04.HCSR04(trigger_pin=board.D17, echo_pin=board.D27)#17,27
sonarbm = adafruit_hcsr04.HCSR04(trigger_pin=board.D24, echo_pin=board.D25)#24,25
sonarbl = adafruit_hcsr04.HCSR04(trigger_pin=board.D18, echo_pin=board.D23)#18, 23


def destroy():
    RPi.GPIO.cleanup()
    print("\nCleaned up GPIO resources.")


while True:
    try:
        print("fl: ", sonarfl.distance, "fm: ", sonarfm.distance, "fr: ", sonarfr.distance, "bl: ", sonarbl.distance, "bm:", sonarbm.distance, "br:", sonarbr.distance)
    except RuntimeError:print("Retrying!")
    except KeyboardInterrupt:destroy()
    time.sleep(0.3)


"""with HCSR04(trigger_pin=board.D5, echo_pin=board.D6) as sonar:
    try:
        while True:
            print(sonar.distance)
        except RuntimeError:
            print("Retrying!")
        time.sleep(2)
        
        print("fl: ", sonarfl.distance)
        print(sonarfm.distance)
        print(sonarfr.distance)
        print("bl: ", sonarbl.distance)
        print(sonarbm.distance)
        print(sonarbr.distance)
        print("")"""
    #except KeyboardInterrupt:
    #    pass




