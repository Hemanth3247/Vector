from machine import I2C, Pin, SPI
import time, os
from ms5611 import MS5611
from mpu6500 import MPU6500

from sdcard import SDCard

# PINS
SDA = 4
SCL = 5

LED_R = Pin(0, Pin.OUT)
LED_G = Pin(1, Pin.OUT)
LED_B = Pin(2, Pin.OUT)

MOTOR = Pin(3, Pin.OUT)

# I2C
i2c = I2C(0, sda=Pin(SDA), scl=Pin(SCL), freq=100_000)
baro = MS5611(i2c)
imu = MPU6500(i2c)

# SPI + SD 
spi = SPI(0, baudrate=1_000_000, polarity=0, phase=0,sck=Pin(18), mosi=Pin(19), miso=Pin(16))
cs = Pin(17, Pin.OUT)

sd = SDCard(spi, cs)
os.mount(sd, "/sd")

log = open("/sd/flight.csv", "w")
log.write("t,pressure,alt_raw,alt_med,alt_ema,ax,ay,az\n")

# FILTER PARAMS
EMA_ALPHA = 0.75
med_buf = []
ema_alt = None

# BARO ALTITUDE
P0 = None  # ground reference pressure

def altitude_from_pressure(p, p0):
    # standard barometric formula (meters)
    return 44330 * (1 - (p/p0) ** 0.1903)

def median3(a,b,c):
    return sorted([a,b,c])[1]

# LED HELPERS
def led(r,g,b):
    LED_R.value(r)
    LED_G.value(g)
    LED_B.value(b)

# DEPLOY
deployed = False
def deploy():
    global deployed
    if deployed:
        return
    MOTOR.value(1)
    time.sleep(1)
    MOTOR.value(0)
    deployed = True

# SET GROUND
print("Hold rocket steady — sampling ground pressure...")
ps = []
for _ in range(15):
    _, p = baro.read()
    ps.append(p)
    time.sleep(0.1)

P0 = sum(ps)/len(ps)
print("Ground reference set:", P0)

led(0,1,0)  # GREEN

# FLIGHT STATE
prev_ema = None
fall_count = 0

# MAIN LOOP
t0 = time.ticks_ms()

while True:

    # READ SENSORS
    temp, pressure = baro.read()
    ax, ay, az = imu.accel()

    alt_raw = altitude_from_pressure(pressure, P0)

    # MEDIAN3
    med_buf.append(alt_raw)
    if len(med_buf) < 3:
        alt_med = alt_raw
    else:
        alt_med = median3(med_buf[-3], med_buf[-2], med_buf[-1])

    # EMA
    if ema_alt is None:
        ema_alt = alt_med
    else:
        ema_alt = EMA_ALPHA*alt_med + (1-EMA_ALPHA)*ema_alt

    # STATE DETECTION
    if prev_ema is not None:
        if ema_alt > prev_ema:
            led(0,0,1)   # BLUE = rising
            fall_count = 0
        else:
            led(1,0,0)   # RED = falling
            fall_count += 1

    # APOGEE DEPLOY
    if fall_count >= 6 and not deployed:
        print("APOGEE DETECTED — DEPLOY")
        deploy()

    prev_ema = ema_alt

    # LOG RAW + FILTERED
    t = time.ticks_diff(time.ticks_ms(), t0)/1000
    log.write("{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.3f},{:.3f},{:.3f}\n".format(t, pressure, alt_raw, alt_med, ema_alt, ax, ay, az))
    log.flush()

    print("{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.3f},{:.3f},{:.3f}\n".format(t, pressure, alt_raw, alt_med, ema_alt, ax, ay, az))
    time.sleep(0.02)   # ~50 Hz
