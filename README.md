# OPT3001 CircuitPython Driver

CircuitPython driver for the **OPT3001** ambient light sensor (commonly found on **CJMCU-3001** breakout boards).

The OPT3001 is a high-precision digital ambient light sensor from Texas Instruments that measures illuminance in lux via I2C communication.

## Features

- ✅ Full CircuitPython 9.x support
- ✅ Tested on RP2040 and ESP32-S3
- ✅ Continuous and single-shot measurement modes
- ✅ Configurable conversion time (100ms or 800ms)
- ✅ Automatic full-scale range selection
- ✅ Raw value access (exponent and mantissa)
- ✅ Device ID verification
- ✅ Low power shutdown mode
- ✅ No type hints, no complex features - pure CircuitPython

## Hardware Connections

### Basic Wiring

| CJMCU-3001 Pin | Microcontroller |
|----------------|-----------------|
| VCC            | 3.3V            |
| GND            | GND             |
| SDA            | SDA pin         |
| SCL            | SCL pin         |

### I2C Address Selection

The OPT3001 supports four I2C addresses based on the ADDR pin connection:

| ADDR Pin | I2C Address |
|----------|-------------|
| GND      | 0x44 (default) |
| VDD      | 0x45 |
| SDA      | 0x46 |
| SCL      | 0x47 |

## Installation

1. Copy `opt3001.py` to your CircuitPython device's `lib` folder
2. Or place it in the same directory as your code

## Quick Start

```python
import time
import board
import busio
from opt3001 import OPT3001

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create sensor object
sensor = OPT3001(i2c)

# Read light level
while True:
    lux = sensor.lux
    print("Light level:", lux, "lux")
    time.sleep(1.0)
```

## API Reference

### Class: `OPT3001`

#### Constructor

```python
OPT3001(i2c, address=0x44)
```

**Parameters:**
- `i2c`: The I2C bus object (from `busio.I2C`)
- `address`: I2C address (default: `0x44`)

**Raises:**
- `RuntimeError`: If sensor is not detected

---

#### Methods

##### `read_lux()`

Read the current light level in lux.

**Returns:** `float` - Light level in lux

```python
lux = sensor.read_lux()
```

---

##### `read_raw()`

Read the raw exponent and mantissa values from the sensor.

**Returns:** `tuple` - `(exponent, mantissa)`

The OPT3001 uses a special format: `lux = 0.01 * (2^exponent) * mantissa`

```python
exp, mantissa = sensor.read_raw()
```

---

##### `configure(mode, conversion_time, range_auto)`

Configure the sensor operating parameters.

**Parameters:**
- `mode`: Operating mode
  - `MODE_SHUTDOWN`: Low power mode
  - `MODE_SINGLE_SHOT`: One conversion per trigger
  - `MODE_CONTINUOUS`: Continuous conversions (default)
- `conversion_time`: Conversion duration
  - `CONVERSION_100MS`: 100ms per reading
  - `CONVERSION_800MS`: 800ms per reading (default, more accurate)
- `range_auto`: Use automatic full-scale range (default: `True`)

```python
from opt3001 import MODE_CONTINUOUS, CONVERSION_100MS

sensor.configure(mode=MODE_CONTINUOUS, conversion_time=CONVERSION_100MS)
```

---

##### `single_shot()`

Trigger a single conversion and return the result.

**Returns:** `float` - Light level in lux

This method automatically waits for the conversion to complete.

```python
lux = sensor.single_shot()
```

---

##### `is_conversion_ready()`

Check if a new conversion result is available.

**Returns:** `bool` - `True` if conversion is ready

```python
if sensor.is_conversion_ready():
    lux = sensor.read_lux()
```

---

##### `check_device_id()`

Verify the device is an OPT3001 by checking manufacturer and device IDs.

**Returns:** `bool` - `True` if IDs match

```python
if sensor.check_device_id():
    print("OPT3001 detected!")
```

---

##### `deinit()`

Put the sensor into shutdown mode to save power.

```python
sensor.deinit()
```

---

#### Properties

##### `lux`

Read-only property that returns the current light level in lux.

```python
current_lux = sensor.lux
```

---

### Constants

#### I2C Addresses
- `OPT3001_ADDRESS` = `0x44` (ADDR to GND)
- `OPT3001_ADDRESS_ALT1` = `0x45` (ADDR to VDD)
- `OPT3001_ADDRESS_ALT2` = `0x46` (ADDR to SDA)
- `OPT3001_ADDRESS_ALT3` = `0x47` (ADDR to SCL)

#### Operating Modes
- `MODE_SHUTDOWN` - Low power mode
- `MODE_SINGLE_SHOT` - Single conversion on demand
- `MODE_CONTINUOUS` - Continuous conversions

#### Conversion Times
- `CONVERSION_100MS` - 100ms conversion time
- `CONVERSION_800MS` - 800ms conversion time (more accurate)

---

## Examples

### Basic Reading

See `example_basic.py` for a simple continuous reading example.

```python
import time
import board
import busio
from opt3001 import OPT3001

i2c = busio.I2C(board.SCL, board.SDA)
sensor = OPT3001(i2c)

while True:
    print("Light:", sensor.lux, "lux")
    time.sleep(1.0)
```

### Single-Shot Mode (Power Saving)

Single-shot mode is useful for battery-powered applications:

```python
from opt3001 import OPT3001

i2c = busio.I2C(board.SCL, board.SDA)
sensor = OPT3001(i2c)

# Take one reading
lux = sensor.single_shot()
print("Light level:", lux, "lux")

# Sensor automatically goes back to shutdown mode
```

### Advanced Usage

See `example_advanced.py` for demonstrations of:
- Raw value reading
- Conversion ready polling
- Different I2C addresses
- Light level descriptions

### Platform-Specific Examples

- **RP2040**: `example_rp2040.py` - LED feedback on light changes
- **ESP32-S3**: `example_esp32s3.py` - Optimized for ESP32-S3 boards

---

## Specifications

| Parameter | Value |
|-----------|-------|
| Supply Voltage | 1.6V - 3.6V (3.3V typical) |
| I2C Speed | Up to 2.6 MHz |
| Measurement Range | 0.01 lux to 83,000 lux |
| Resolution | 0.01 lux |
| Conversion Time | 100ms or 800ms |
| Current Consumption (Active) | 1.8 μA typical |
| Current Consumption (Shutdown) | 0.3 μA typical |

---

## Troubleshooting

### "Failed to find OPT3001 sensor"

1. Check wiring connections (VCC, GND, SDA, SCL)
2. Verify I2C address matches your ADDR pin connection
3. Try scanning I2C bus:
   ```python
   while not i2c.try_lock():
       pass
   print("I2C addresses:", [hex(x) for x in i2c.scan()])
   i2c.unlock()
   ```

### Readings seem incorrect

1. Ensure proper conversion time - use 800ms for better accuracy
2. Check that the sensor is not covered or obstructed
3. Verify sensor is in continuous mode for repeated readings

### Memory errors on small boards

This driver is optimized for CircuitPython and uses minimal memory. If you encounter memory issues:
1. Use single-shot mode instead of continuous
2. Reduce the number of imports
3. Use `gc.collect()` periodically

---

## Technical Details

### Lux Calculation

The OPT3001 stores readings in a special format using an exponent and mantissa:

```
Raw value = [E3:E0][R11:R0]
Lux = 0.01 × 2^E × R
```

Where:
- E = 4-bit exponent (bits 15-12)
- R = 12-bit mantissa (bits 11-0)

This allows a wide dynamic range (0.01 to 83,000 lux) with high resolution.

### Register Map

| Address | Register | Description |
|---------|----------|-------------|
| 0x00 | Result | Conversion result |
| 0x01 | Configuration | Operating mode settings |
| 0x02 | Low Limit | Low threshold |
| 0x03 | High Limit | High threshold |
| 0x7E | Manufacturer ID | 0x5449 ("TI") |
| 0x7F | Device ID | 0x3001 |

---

## License

This driver is provided as-is for use with CircuitPython projects.

## Resources

- [OPT3001 Datasheet](https://www.ti.com/product/OPT3001)
- [CircuitPython Documentation](https://docs.circuitpython.org/)
- [CJMCU-3001 Breakout Info](https://github.com/adafruit/circuitpython)

---

## Contributing

Issues and improvements are welcome! This driver follows CircuitPython best practices and is designed to work on resource-constrained microcontrollers.

**Requirements:**
- No type hints
- No f-string line breaks
- Simple, explicit code
- Compatible with CircuitPython 9.x
- Tested on RP2040 and ESP32-S3
