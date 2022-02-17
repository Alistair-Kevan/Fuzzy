# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_hcsr04
import RPi.GPIO
import board
import digitalio

sonarfm = adafruit_hcsr04.HCSR04(trigger_pin=board.D5, echo_pin=board.D6)
sonarfl = adafruit_hcsr04.HCSR04(trigger_pin=board.D9, echo_pin=board.D11)#9, 11
sonarfr = adafruit_hcsr04.HCSR04(trigger_pin=board.D22, echo_pin=board.D10)#22, 10

def destroy():
    RPi.GPIO.cleanup()
    print("\nCleaned up GPIO resources.")

while True:
    try:
        print((sonarfl.distance,),(sonarfm.distance,),(sonarfr.distance,))
    except RuntimeError:
        print("Retrying!")
    except KeyboardInterrupt:
        destroy()
    time.sleep(0.1)




