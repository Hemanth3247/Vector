from machine import I2C, Pin
import time
from mpu6500 import MPU6500

# SAME wiring as you requested
# GP4 = SDA
# GP5 = SCL
i2c = I2C(
    0,
    sda=Pin(4),
    scl=Pin(5),
    freq=100_000
)

print("Scanning I2C bus...")
print([hex(a) for a in i2c.scan()])

mpu = MPU6500(i2c)

while True:
    ax, ay, az = mpu.accel()
    gx, gy, gz = mpu.gyro()

    print("ACCEL:", ax, ay, az)
    print("GYRO :", gx, gy, gz)
    print("-" * 30)

    time.sleep(0.5)

