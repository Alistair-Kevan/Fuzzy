import RPi.GPIO as GPIO


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
        # output to GPIO8
        # rightfw

        GPIO.output(35, 1) #back left fw
        GPIO.output(37, 0)

        GPIO.output(40, 0)#front right fw
        GPIO.output(38, 1)



        # leftfw
        GPIO.output(26, 1)
        GPIO.output(24, 0)
        GPIO.output(36, 1)
        GPIO.output(32, 0)


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
