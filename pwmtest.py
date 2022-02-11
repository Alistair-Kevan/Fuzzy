import RPi.GPIO as GPIO
import time

BLPWM = 33
BL = 36



def setup():
    global pwm
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BLPWM, GPIO.OUT)
    GPIO.output(BLPWM, GPIO.LOW)
    GPIO.setup(BL, GPIO.OUT)
    GPIO.output(BL, GPIO.LOW)
    pwm = GPIO.PWM(BLPWM, 1000)  # Set Frequency to 1 KHz
    pwm.start(0)  # Set the starting Duty Cycle


def loop():
    while True:
        GPIO.output(BL, GPIO.LOW)
        for dc in range(0, 101, 1):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.01)
        time.sleep(1)
        GPIO.output(BL, GPIO.HIGH)
        for dc in range(100, -1, -1):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.01)
        time.sleep(1)


def destroy():
    pwm.stop()
    GPIO.output(BLPWM, GPIO.LOW)
    GPIO.output(BL, GPIO.LOW)
    GPIO.cleanup()


if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
