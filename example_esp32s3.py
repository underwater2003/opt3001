"""
ESP32-S3-specific example for the OPT3001 light sensor (CJMCU-3001)

This example is optimized for ESP32-S3 boards with built-in RGB LED support.
Shows color-coded feedback based on light levels.

Hardware connections (typical ESP32-S3):
- VCC to 3.3V
- GND to GND
- SDA to GPIO8 (or other SDA pin)
- SCL to GPIO9 (or other SCL pin)

Note: Adjust pin numbers based on your specific ESP32-S3 board
"""

import time
import board
import busio
from opt3001 import OPT3001

# Create I2C bus
# ESP32-S3 typically uses GPIO8/GPIO9 or board.SDA/board.SCL
try:
    i2c = busio.I2C(board.SCL, board.SDA)
except Exception:
    # Fallback to specific pins if board.SCL/SDA not defined
    i2c = busio.I2C(board.IO9, board.IO8)

# Create sensor object
sensor = OPT3001(i2c)

print("OPT3001 on ESP32-S3")
print("Reading light sensor...")
print("")

# Optional: If your board has NeoPixel, uncomment below
# import neopixel
# pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
#
# def set_color_by_lux(lux_value):
#     """Set NeoPixel color based on light level."""
#     if lux_value < 10:
#         pixel[0] = (0, 0, 50)  # Blue - very dark
#     elif lux_value < 100:
#         pixel[0] = (50, 0, 50)  # Purple - dark
#     elif lux_value < 500:
#         pixel[0] = (50, 50, 0)  # Yellow - normal
#     else:
#         pixel[0] = (50, 0, 0)  # Red - bright

# Main loop
while True:
    lux = sensor.lux

    # Print reading
    print(str(round(lux, 2)) + " lux")

    # Optional: Update NeoPixel if available
    # set_color_by_lux(lux)

    time.sleep(1.0)
