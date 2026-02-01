from machine import I2C
import time

class MPU6500:
    WHO_AM_I = 0x75
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43

    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr

        who = self._read8(self.WHO_AM_I)
        if who not in (0x70, 0x71):  # MPU6500 / MPU9250
            raise OSError("MPU6500 not found, WHO_AM_I =", hex(who))

        # Wake up device
        self._write8(self.PWR_MGMT_1, 0x00)
        time.sleep_ms(100)

    def _write8(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val]))

    def _read8(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def _read16(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        val = (data[0] << 8) | data[1]
        return val - 65536 if val > 32767 else val

    def accel(self):
        ax = self._read16(self.ACCEL_XOUT_H)
        ay = self._read16(self.ACCEL_XOUT_H + 2)
        az = self._read16(self.ACCEL_XOUT_H + 4)
        return ax, ay, az

    def gyro(self):
        gx = self._read16(self.GYRO_XOUT_H)
        gy = self._read16(self.GYRO_XOUT_H + 2)
        gz = self._read16(self.GYRO_XOUT_H + 4)
        return gx, gy, gz

