import board
import adafruit_lsm303_accel
import adafruit_lis2mdl

i2c = board.I2C()
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
mag = adafruit_lis2mdl.LIS2MDL(i2c)