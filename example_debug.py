"""
Debug example for the OPT3001 light sensor (CJMCU-3001)

This example helps troubleshoot sensor issues by:
- Verifying I2C communication
- Checking device IDs
- Reading raw register values
- Displaying configuration register bits
- Showing conversion progress

Use this if your sensor returns 0.0 lux or seems unresponsive.
"""

import time
import board
import busio
from opt3001 import OPT3001

print("OPT3001 Debug Example")
print("=" * 50)
print("")

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

print("Step 1: Scanning I2C bus...")
while not i2c.try_lock():
    pass
try:
    devices = i2c.scan()
    print("Found I2C devices at addresses:")
    for device in devices:
        print("  0x" + hex(device)[2:].upper())
    if 0x44 not in devices and 0x45 not in devices and 0x46 not in devices and 0x47 not in devices:
        print("WARNING: No OPT3001 found at expected addresses (0x44-0x47)")
finally:
    i2c.unlock()

print("")

# Try to create sensor
print("Step 2: Initializing OPT3001...")
try:
    sensor = OPT3001(i2c, address=0x44)
    print("SUCCESS: Sensor initialized")
except RuntimeError as e:
    print("ERROR: " + str(e))
    print("Check your wiring and I2C address")
    while True:
        pass

print("")

# Read device IDs
print("Step 3: Reading device identification...")
config_reg = sensor._read_register(0x7E)
print("  Manufacturer ID: 0x" + hex(config_reg)[2:].upper() + " (expected 0x5449)")
device_reg = sensor._read_register(0x7F)
print("  Device ID: 0x" + hex(device_reg)[2:].upper() + " (expected 0x3001)")

print("")

# Read and decode configuration
print("Step 4: Reading configuration register...")
config = sensor.get_config()
print("  Config register: 0x" + hex(config)[2:].upper().zfill(4))

# Decode config bits
range_num = (config >> 12) & 0x0F
conv_time = (config >> 11) & 0x01
mode = (config >> 9) & 0x03
conv_ready = (config >> 7) & 0x01

print("  Range number: " + str(range_num) + " (1100b = auto range)")
print("  Conversion time: " + ("800ms" if conv_time else "100ms"))
print("  Mode: " + str(mode) + " (0=shutdown, 1=single, 2=continuous)")
print("  Conversion ready: " + ("Yes" if conv_ready else "No"))

print("")

# Read raw result register multiple times
print("Step 5: Reading raw result register (5 samples)...")
for i in range(5):
    raw = sensor._read_register(0x00)
    exponent = (raw >> 12) & 0x0F
    mantissa = raw & 0x0FFF
    lux = 0.01 * (2 ** exponent) * mantissa

    print("  Sample " + str(i + 1) + ":")
    print("    Raw value: 0x" + hex(raw)[2:].upper().zfill(4))
    print("    Exponent: " + str(exponent) + ", Mantissa: " + str(mantissa))
    print("    Calculated lux: " + str(round(lux, 2)))

    time.sleep(0.2)

print("")

# Test using high-level API
print("Step 6: Testing high-level API (10 readings)...")
for i in range(10):
    lux = sensor.read_lux()
    exp, mant = sensor.read_raw()
    print("  Reading " + str(i + 1) + ": " + str(round(lux, 2)) + " lux (E=" + str(exp) + ", M=" + str(mant) + ")")
    time.sleep(0.5)

print("")
print("Debug test complete!")
print("")
print("Troubleshooting tips:")
print("- If all readings are 0.0 lux, check sensor is not covered")
print("- If exponent and mantissa are both 0, check I2C wiring")
print("- If conversion ready is always 0, sensor may be in shutdown mode")
print("- Typical indoor light: 100-500 lux")
print("- Bright room: 500-1000 lux")
print("- Direct sunlight: 10000+ lux")
