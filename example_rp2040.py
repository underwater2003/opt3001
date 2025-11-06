"""
RP2040-specific example for the OPT3001 light sensor (CJMCU-3001)

This example is optimized for Raspberry Pi Pico and other RP2040 boards.
It demonstrates simple, memory-efficient reading with built-in LED feedback.

Hardware connections (Raspberry Pi Pico):
- VCC to 3.3V (pin 36)
- GND to GND (pin 38)
- SDA to GP0 (pin 1) or GP2 (pin 4)
- SCL to GP1 (pin 2) or GP3 (pin 5)
"""

import time
import board
import busio
import digitalio
from opt3001 import OPT3001

# Set up built-in LED on RP2040
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Create I2C bus using default pins
# For Pico: GP0=SDA, GP1=SCL (or GP2=SDA, GP3=SCL)
i2c = busio.I2C(board.GP1, board.GP0)

# Create sensor object
sensor = OPT3001(i2c)

print("OPT3001 on RP2040")
print("LED blinks when light level changes significantly")
print("")

# Track previous reading
previous_lux = sensor.lux
threshold = 50  # Lux change threshold for LED blink

# Main loop
while True:
    current_lux = sensor.lux

    # Calculate change from previous reading
    change = abs(current_lux - previous_lux)

    # Blink LED if change is significant
    if change > threshold:
        led.value = True
        time.sleep(0.1)
        led.value = False
        print("Large change detected! " + str(round(current_lux, 2)) + " lux")

    # Regular update
    print(str(round(current_lux, 2)) + " lux")

    previous_lux = current_lux
    time.sleep(0.5)
