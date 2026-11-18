import time
import usb_cdc
from adafruit_crickit import crickit
from adafruit_circuitplayground import cp

# ----- CONFIGURATION -----

PAN_MIN, PAN_MAX = 30, 150
TILT_MIN, TILT_MAX = 45, 135

STEP = 5
SMOOTHING = 0.15
UPDATE_INTERVAL = 0.01

# ----- HARDWARE -----

pan = crickit.servo_1
tilt = crickit.servo_2

serial = usb_cdc.console
serial.timeout = 0

cp.pixels.brightness = 0.15
cp.pixels.fill((0, 80, 100))

# ----- POSITION STATE -----

# Current commanded servo position
pan_pos = 90.0
tilt_pos = 90.0

# Desired servo position
pan_target = 90.0
tilt_target = 90.0

pan.angle = pan_pos
tilt.angle = tilt_pos

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))

def smooth_move(current, target):
    difference = target - current

    # Stop making tiny adjustments near the target
    if abs(difference) < 0.1:
        return target

    # Gradually approach the desired position
    return current + difference * SMOOTHING

print("Robot ready!")
print("WASD = move | 0 = center | ? = help")

# ----- MAIN LOOP -----

while True:
    key = ""

    # Read a command from the serial terminal
    if serial.in_waiting:
        data = serial.read(1)
        if data:
            key = data.decode("ascii").lower()

    # Physical CPX buttons
    if cp.button_a:
        key = "a" if cp.switch else "s"
    elif cp.button_b:
        key = "d" if cp.switch else "w"

    # Update target positions
    if key == "a":
        pan_target -= STEP
    elif key == "d":
        pan_target += STEP
    elif key == "w":
        tilt_target += STEP
    elif key == "s":
        tilt_target -= STEP
    elif key == "0":
        pan_target = 90
        tilt_target = 90
    elif key == "?":
        print("W/S tilt | A/D pan | 0 center")

    # Keep targets within safe limits
    pan_target = clamp(
        pan_target, PAN_MIN, PAN_MAX
    )
    tilt_target = clamp(
        tilt_target, TILT_MIN, TILT_MAX
    )

    # Smoothly approach both targets
    next_pan = smooth_move(pan_pos, pan_target)
    next_tilt = smooth_move(tilt_pos, tilt_target)

    # Only send commands when something changes
    if abs(next_pan - pan_pos) > 0.01:
        pan_pos = next_pan
        pan.angle = pan_pos

    if abs(next_tilt - tilt_pos) > 0.01:
        tilt_pos = next_tilt
        tilt.angle = tilt_pos

    time.sleep(UPDATE_INTERVAL)
