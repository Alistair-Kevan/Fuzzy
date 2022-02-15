import board
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag

i2c = board.I2C()
mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)