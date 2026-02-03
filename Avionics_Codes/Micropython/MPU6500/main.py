from machine import Pin, I2C, SPI
import os, time, sdcard
from ms5611 import MS5611
from mpu6500 import MPU6500

# ---------------- I2C (your confirmed wiring) ----------------
i2c = I2C(
    0,
    sda=Pin(4),
    scl=Pin(5),
    freq=100_000
)

print("I2C scan:", [hex(a) for a in i2c.scan()])

# ---------------- SENSORS ----------------
baro = MS5611(i2c, debug=False)
imu  = MPU6500(i2c)

# ---------------- SPI SD ----------------
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
sd  = sdcard.SDCard(spi, Pin(17))
os.mount(sd, "/sd")

# ---------------- OUTPUTS ----------------
motor = Pin(3, Pin.OUT)
ledr  = Pin(0, Pin.OUT)
ledg  = Pin(1, Pin.OUT)
ledb  = Pin(2, Pin.OUT)

ledg.value(1)   # ready

# ---------------- LOG FILE ----------------
f = open("/sd/flight.csv","w")
f.write("ms,p_mbar,ax,ay,az,alt_raw,alt_filt\n")

# ---------------- BASE PRESSURE ----------------
print("Calibrating ground pressure...")
p_sum = 0
for _ in range(10):
    _, p = baro.read()
    p_sum += p
    time.sleep_ms(50)

p0 = p_sum / 10
print("Ground pressure p0 =", p0, "mbar")

# ---------------- FILTER PARAMS ----------------
OVERSAMPLE_N = 3
MAX_STEP = 6        # meters per sample
EMA_UP = 0.7
EMA_DOWN = 0.25
DEPLOY_COUNT = 6

# ---------------- STATE ----------------
ema_alt = 0
prev_alt = 0
down = 0

# ---------------- FUNCTIONS ----------------
def altitude_from_pressure_mbar(p):
    # ratio cancels units → mbar OK
    return 44330 * (1 - (p/p0)**0.1903)

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

# ---------------- MAIN LOOP ----------------
print("Flight loop started")

while True:

    # ---- BARO ----
    p = read_pressure_oversampled()
    alt_raw = altitude_from_pressure_mbar(p)

    # ---- SPIKE LIMIT ----
    delta = alt_raw - prev_alt
    if delta > MAX_STEP:
        alt_raw = prev_alt + MAX_STEP
    elif delta < -MAX_STEP:
        alt_raw = prev_alt - MAX_STEP

    prev_alt = alt_raw

    # ---- EMA FILTER ----
    prev_ema = ema_alt
    alt_filt = ascent_ema(ema_alt, alt_raw)
    ema_alt = alt_filt

    # ---- IMU ----
    ax, ay, az = imu.accel()

    # ---- APOGEE DETECT ----
    if alt_filt < prev_ema:
        down += 1
    else:
        down = 0

    if down >= DEPLOY_COUNT:
        motor.value(1)
        ledr.value(1)

    # ---- LOG ----
    f.write("{},{},{},{},{},{},{}\n".format(
        time.ticks_ms(), p, ax, ay, az, alt_raw, alt_filt))

    if time.ticks_ms() % 200 == 0:
        f.flush()

    time.sleep_ms(20)   # 50 Hz
