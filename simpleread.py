import serial
ser = serial.Serial('/dev/ttyACM0',9600)

if __name__ == '__main__':
    ser.reset_input_buffer()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            compas = float(line)