"""
Basic example for reading the OPT3001 light sensor (CJMCU-3001)

This example shows how to:
- Initialize the sensor
- Read light levels continuously
- Display results in lux

Hardware connections:
- VCC to 3.3V
- GND to GND
- SDA to board SDA pin
- SCL to board SCL pin
"""

import time
import board
import busio
from opt3001 import OPT3001

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create sensor object
# Default address is 0x44 (ADDR pin to GND)
sensor = OPT3001(i2c)

print("OPT3001 Light Sensor Example")
print("Reading light levels every second...")
print("")

# Main loop - read and display light levels
while True:
    lux = sensor.lux
    print("Light level: " + str(round(lux, 2)) + " lux")
    time.sleep(1.0)
