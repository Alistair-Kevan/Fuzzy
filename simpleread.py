import serial
print("hello")
ser = serial.Serial('/dev/ttyUSB0',9600)
s = [0]
print("hell")
while True:
    print("he")
    s[0] = ser.readline()
    print (s)
    #print (cc[2:][:-5])
    print(s.decode("utf-8"))
