import RPi.GPIO as GPIO
# Use GPIO numbers not pin numbers
GPIO.setmode(GPIO.BOARD)
 
# set up the GPIO channels - one input and one output
GPIO.setup(40, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)

GPIO.setup(36, GPIO.OUT)
GPIO.setup(32, GPIO.OUT)

GPIO.setup(26, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)


import serial
ser = serial.Serial('/dev/ttyUSB0',9600)

if __name__ == '__main__':
    ser.reset_input_buffer()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            compas= float(line)
            #int.from_bytes(line,byteorder='big')
            if (compas > 20 and compas < 300):
                #rightbw
                GPIO.output(22, 0)
                GPIO.output(15, 1)
                GPIO.output(40, 1)
                GPIO.output(38, 0)
                #leftfw
                GPIO.output(26, 1)
                GPIO.output(24, 0)
                GPIO.output(36, 0)
                GPIO.output(32, 1) 
            else:
                # output to GPIO8
                GPIO.output(26, 1)
                GPIO.output(24, 0)
                GPIO.output(22, 1)
                GPIO.output(15, 0)

                GPIO.output(40, 0)
                GPIO.output(38, 1)
                GPIO.output(36, 0)
                GPIO.output(32, 1)  
                
        
