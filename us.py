# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_hcsr04
import RPi.GPIO
import board
import digitalio

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D5, echo_pin=board.D6)

def destroy():
    RPi.GPIO.cleanup()
    print("\nCleaned up GPIO resources.")

while True:
    try:
        print((sonar.distance,))
    except RuntimeError:
        print("Retrying!")
    except KeyboardInterrupt:
        destroy()
    time.sleep(0.1)




