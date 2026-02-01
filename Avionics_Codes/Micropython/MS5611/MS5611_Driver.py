from machine import I2C
import time

class MS5611:
    CMD_RESET = 0x1E
    CMD_CONVERT_D1 = 0x48  # pressure, OSR=4096
    CMD_CONVERT_D2 = 0x58  # temperature, OSR=4096
    PROM_BASE = 0xA0
    ADDR_CANDIDATES = (0x77, 0x76)

    def __init__(self, i2c, address=None, debug=False):
        self.i2c = i2c
        self.debug = debug

        addrs = [address] if address else self.ADDR_CANDIDATES
        last_err = None

        for a in addrs:
            try:
                if self.debug:
                    print("Trying address", hex(a))

                self.i2c.writeto(a, b'\x1E')   # RESET
                time.sleep_ms(20)

                C = self._read_prom(a)

                # Validate C1–C6 only (C0 may be zero)
                for i in range(1, 7):
                    if C[i] == 0 or C[i] == 0xFFFF:
                        raise OSError("Invalid PROM C{}".format(i))

                self.address = a
                self.C = C

                if self.debug:
                    print("Init OK", hex(a), C)

                return

            except Exception as e:
                last_err = e
                if self.debug:
                    print("Address", hex(a), "failed:", e)

        raise OSError("MS5611 init failed. Last error: {}".format(last_err))

    def _read_prom(self, addr):
        C = []
        for i in range(7):
            off = self.PROM_BASE + i * 2
            self.i2c.writeto(addr, bytes([off]))
            data = self.i2c.readfrom(addr, 2)
            C.append((data[0] << 8) | data[1])
        return C

    def _read_adc(self):
        self.i2c.writeto(self.address, b'\x00')  # CMD_ADC_READ
        data = self.i2c.readfrom(self.address, 3)
        return (data[0] << 16) | (data[1] << 8) | data[2]


    def read(self):
        C = self.C

        # Pressure
        self.i2c.writeto(self.address, bytes([self.CMD_CONVERT_D1]))
        time.sleep_ms(20)
        D1 = self._read_adc()

        # Temperature
        self.i2c.writeto(self.address, bytes([self.CMD_CONVERT_D2]))
        time.sleep_ms(20)
        D2 = self._read_adc()

        dT = D2 - C[5] * 256
        TEMP = 2000 + (dT * C[6]) / (1 << 23)
        OFF = C[2] * (1 << 16) + (C[4] * dT) / (1 << 7)
        SENS = C[1] * (1 << 15) + (C[3] * dT) / (1 << 8)

        if TEMP < 2000:
            T2 = (dT * dT) / (1 << 31)
            OFF2 = 5 * ((TEMP - 2000) ** 2) / 2
            SENS2 = OFF2 / 2
            TEMP -= T2
            OFF -= OFF2
            SENS -= SENS2

        P = (D1 * SENS / (1 << 21) - OFF) / (1 << 15)

        return TEMP / 100.0, P / 100.0

