# M1 test 1: BME280 on I2C0 (SDA = GP8, SCL = GP9).
# Run on the Pico: mpremote run m1/bme280_test.py
import time
from machine import I2C, Pin
from bme280 import BME280, CHIP_BME280, CHIP_BMP280

i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
print("I2C scan:", [hex(a) for a in i2c.scan()])

sensor = BME280(i2c)
name = {CHIP_BME280: "BME280", CHIP_BMP280: "BMP280 (NO humidity!)"}[sensor.chip_id]
print("Found %s at 0x%02X (chip id 0x%02X)" % (name, sensor.addr, sensor.chip_id))

print("20 readings, 1 per second. Breathe on the sensor to see humidity rise.")
for i in range(20):
    t, p, h = sensor.read()
    print("%2d  T=%6.2f C   P=%8.2f hPa   RH=%5.1f %%" % (i + 1, t, p, h))
    time.sleep(1)
