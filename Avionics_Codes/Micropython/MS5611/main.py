from machine import I2C, Pin
import time
from ms5611 import MS5611

# Your wiring:
# GP5 = SCL
# GP4 = SDA
i2c = I2C(
    0,
    scl=Pin(5),
    sda=Pin(4),
    freq=100_000
)

print("Scanning I2C bus...")
print([hex(a) for a in i2c.scan()])

sensor = MS5611(i2c, debug=True)

while True:
    temp, pressure = sensor.read()
    print("Temperature:", temp, "°C")
    print("Pressure:", pressure, "mbar")
    print("-" * 30)
    time.sleep(1)

