import serial
# Try this port. If I get nothing printing out, try '/dev/ttyAMA0'
#ser = serial.Serial('/dev/ttyACM0', 9600)
#ser = serial.Serial('/dev/ttyACM0', 9600)#
#new comment

ser = serial.Serial('/dev/ttyUSB0', 9600)
if __name__ == '__main__':
    ser.reset_input_buffer()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            compas = float(line)
            print(compas+10)
