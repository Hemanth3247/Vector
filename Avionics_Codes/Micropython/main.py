from machine import Pin, I2C, SPI
import os, time, sdcard
from ms5611 import MS5611
from mpu6500 import MPU6500

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
sd  = sdcard.SDCard(spi, Pin(17))
os.mount(sd, "/sd")

baro = MS5611(i2c)
imu  = MPU6500(i2c)

motor = Pin(3, Pin.OUT)
ledr  = Pin(0, Pin.OUT)
ledg  = Pin(1, Pin.OUT)
ledb  = Pin(2, Pin.OUT)

ledg.value(1)

f = open("/sd/flight.csv","w")
f.write("ms,p,ax,ay,az,alt_raw,alt_filt\n")

_, p0 = baro.read()

def altitude_from_pressure(p):
    return 44330 * (1 - (p/p0)**0.1903)

OVERSAMPLE_N = 3        # baro reads per loop
MAX_STEP = 8            # meters per sample allowed change
EMA_UP = 0.7            # fast upward response
EMA_DOWN = 0.25         # slow downward response
DEPLOY_COUNT = 6        # consecutive descent samples

ema_alt = 0
prev_alt = 0
down = 0

def read_pressure_oversampled():
    s = 0
    for _ in range(OVERSAMPLE_N):
        _, p = baro.read()
        s += p
    return s / OVERSAMPLE_N

def ascent_ema(prev, new):
    if new > prev:
        a = EMA_UP
    else:
        a = EMA_DOWN
    return prev + a*(new - prev)

while True:

    p = read_pressure_oversampled()
    alt_raw = altitude_from_pressure(p)

    delta = alt_raw - prev_alt
    if delta > MAX_STEP:
        alt_raw = prev_alt + MAX_STEP
    elif delta < -MAX_STEP:
        alt_raw = prev_alt - MAX_STEP

    prev_alt = alt_raw

    alt_filt = ascent_ema(ema_alt, alt_raw)
    ema_alt = alt_filt

    ax, ay, az = imu.accel()

    if alt_filt < ema_alt:
        down += 1
    else:
        down = 0

    if down >= DEPLOY_COUNT:
        motor.value(1)
        ledr.value(1)   # red = deploy

    f.write("{},{},{},{},{},{},{}\n".format(
        time.ticks_ms(), p, ax, ay, az, alt_raw, alt_filt))

    if time.ticks_ms() % 200 == 0:
        f.flush()

    time.sleep_ms(20)   # ~50 Hz loop
