"""
Advanced example for the OPT3001 light sensor (CJMCU-3001)

This example demonstrates:
- Single-shot mode for power saving
- Reading raw values (exponent and mantissa)
- Different I2C addresses
- Device ID verification

Hardware connections:
- VCC to 3.3V
- GND to GND
- SDA to board SDA pin
- SCL to board SCL pin
- ADDR to GND for 0x44 (or VDD for 0x45, SDA for 0x46, SCL for 0x47)
"""

import time
import board
import busio
from opt3001 import OPT3001, MODE_CONTINUOUS, MODE_SINGLE_SHOT, CONVERSION_100MS

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create sensor object
# Change address if ADDR pin is connected differently:
# 0x44 = GND (default)
# 0x45 = VDD
# 0x46 = SDA
# 0x47 = SCL
sensor = OPT3001(i2c, address=0x44)

print("OPT3001 Advanced Example")
print("")

# Verify device IDs
if sensor.check_device_id():
    print("Device ID verified - OPT3001 detected")
else:
    print("Warning: Device ID mismatch")

print("")

# Example 1: Continuous mode with raw values
print("Example 1: Continuous mode (10 readings)")
sensor.configure(mode=MODE_CONTINUOUS, conversion_time=CONVERSION_100MS)
time.sleep(0.2)  # Wait for first conversion

for i in range(10):
    exp, mantissa = sensor.read_raw()
    lux = sensor.read_lux()
    print("Reading " + str(i + 1) + ": exp=" + str(exp) + ", mantissa=" + str(mantissa) + ", lux=" + str(round(lux, 2)))
    time.sleep(0.2)

print("")

# Example 2: Single-shot mode for power saving
print("Example 2: Single-shot mode (5 readings)")
print("This mode saves power between readings")

for i in range(5):
    lux = sensor.single_shot()
    print("Reading " + str(i + 1) + ": " + str(round(lux, 2)) + " lux")
    time.sleep(2.0)  # Wait 2 seconds between readings

print("")

# Example 3: Check conversion ready flag
print("Example 3: Polling conversion ready flag")
sensor.configure(mode=MODE_CONTINUOUS, conversion_time=CONVERSION_100MS)

for i in range(5):
    # Wait for conversion to be ready
    while not sensor.is_conversion_ready():
        time.sleep(0.01)

    lux = sensor.read_lux()
    print("Reading " + str(i + 1) + ": " + str(round(lux, 2)) + " lux")

print("")

# Example 4: Different light level descriptions
print("Example 4: Light level descriptions (continuous)")

def describe_light_level(lux_value):
    """Return a description of the light level."""
    if lux_value < 1:
        return "Very dark"
    elif lux_value < 50:
        return "Dark"
    elif lux_value < 200:
        return "Dim"
    elif lux_value < 500:
        return "Normal indoor"
    elif lux_value < 1000:
        return "Bright indoor"
    elif lux_value < 10000:
        return "Very bright"
    else:
        return "Direct sunlight"

sensor.configure(mode=MODE_CONTINUOUS)
time.sleep(1.0)

for i in range(10):
    lux = sensor.lux
    description = describe_light_level(lux)
    print(str(round(lux, 2)) + " lux - " + description)
    time.sleep(1.0)

# Clean up - put sensor in low power mode
print("")
print("Done! Putting sensor in shutdown mode...")
sensor.deinit()
