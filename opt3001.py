"""
CircuitPython driver for the OPT3001 ambient light sensor (CJMCU-3001 breakout)

The OPT3001 is a digital ambient light sensor from Texas Instruments
that measures illuminance in lux via I2C.

* Author: CircuitPython Community
* Tested on: RP2040, ESP32-S3
"""

import time
from micropython import const

# I2C addresses (depending on ADDR pin connection)
OPT3001_ADDRESS = const(0x44)  # ADDR pin to GND (default)
OPT3001_ADDRESS_ALT1 = const(0x45)  # ADDR pin to VDD
OPT3001_ADDRESS_ALT2 = const(0x46)  # ADDR pin to SDA
OPT3001_ADDRESS_ALT3 = const(0x47)  # ADDR pin to SCL

# Register addresses
_REG_RESULT = const(0x00)
_REG_CONFIG = const(0x01)
_REG_LOW_LIMIT = const(0x02)
_REG_HIGH_LIMIT = const(0x03)
_REG_MANUFACTURER_ID = const(0x7E)
_REG_DEVICE_ID = const(0x7F)

# Configuration register bits
_CONFIG_RN = const(0xF000)  # Range number field
_CONFIG_CT = const(0x0800)  # Conversion time (0=100ms, 1=800ms)
_CONFIG_M = const(0x0600)   # Mode of conversion operation
_CONFIG_OVF = const(0x0100) # Overflow flag
_CONFIG_CRF = const(0x0080) # Conversion ready flag
_CONFIG_FH = const(0x0040)  # Flag high field
_CONFIG_FL = const(0x0020)  # Flag low field
_CONFIG_L = const(0x0010)   # Latch field
_CONFIG_POL = const(0x0008) # Polarity field
_CONFIG_ME = const(0x0004)  # Mask exponent field
_CONFIG_FC = const(0x0003)  # Fault count field

# Mode values
MODE_SHUTDOWN = const(0x00)
MODE_SINGLE_SHOT = const(0x01)
MODE_CONTINUOUS = const(0x02)

# Conversion time values
CONVERSION_100MS = const(0)
CONVERSION_800MS = const(1)

# Expected IDs
_MANUFACTURER_ID = const(0x5449)  # "TI" in ASCII
_DEVICE_ID = const(0x3001)


class OPT3001:
    """Driver for the OPT3001 ambient light sensor."""

    def __init__(self, i2c, address=OPT3001_ADDRESS):
        """
        Initialize the OPT3001 sensor.

        Args:
            i2c: The I2C bus object (busio.I2C)
            address: The I2C address (default 0x44)
        """
        self.i2c = i2c
        self.address = address
        self._buffer = bytearray(2)

        # Verify device IDs
        if not self.check_device_id():
            raise RuntimeError("Failed to find OPT3001 sensor - check wiring!")

        # Configure for continuous conversion, 800ms conversion time
        self.configure(mode=MODE_CONTINUOUS, conversion_time=CONVERSION_800MS)

        # Wait for first conversion
        time.sleep(1.0)

    def _write_register(self, register, value):
        """Write a 16-bit value to a register."""
        self._buffer[0] = (value >> 8) & 0xFF
        self._buffer[1] = value & 0xFF

        while not self.i2c.try_lock():
            pass
        try:
            self.i2c.writeto_then_readfrom(self.address, bytes([register]), self._buffer, out_end=0, in_start=0)
            self.i2c.writeto(self.address, bytes([register, self._buffer[0], self._buffer[1]]))
        finally:
            self.i2c.unlock()

    def _read_register(self, register):
        """Read a 16-bit value from a register."""
        while not self.i2c.try_lock():
            pass
        try:
            self.i2c.writeto_then_readfrom(
                self.address,
                bytes([register]),
                self._buffer
            )
        finally:
            self.i2c.unlock()

        return (self._buffer[0] << 8) | self._buffer[1]

    def check_device_id(self):
        """
        Verify the device is an OPT3001 by checking manufacturer and device IDs.

        Returns:
            True if IDs match, False otherwise
        """
        try:
            manufacturer_id = self._read_register(_REG_MANUFACTURER_ID)
            device_id = self._read_register(_REG_DEVICE_ID)
            return manufacturer_id == _MANUFACTURER_ID and device_id == _DEVICE_ID
        except Exception:
            return False

    def configure(self, mode=MODE_CONTINUOUS, conversion_time=CONVERSION_800MS,
                  range_auto=True):
        """
        Configure the sensor operating mode.

        Args:
            mode: Operating mode (MODE_SHUTDOWN, MODE_SINGLE_SHOT, MODE_CONTINUOUS)
            conversion_time: Conversion time (CONVERSION_100MS or CONVERSION_800MS)
            range_auto: Use automatic full-scale range (default True)
        """
        # Build config value
        # Start with automatic full-scale range (RN=1100b = 0xC)
        config = 0xC000 if range_auto else 0x0000

        # Set conversion time
        if conversion_time == CONVERSION_800MS:
            config |= _CONFIG_CT

        # Set mode (bits 10-9)
        config |= (mode << 9)

        self._write_register(_REG_CONFIG, config)

    def read_raw(self):
        """
        Read the raw result register value.

        Returns:
            Tuple of (exponent, mantissa)
        """
        raw = self._read_register(_REG_RESULT)
        exponent = (raw >> 12) & 0x0F
        mantissa = raw & 0x0FFF
        return exponent, mantissa

    def read_lux(self):
        """
        Read the light level in lux.

        The OPT3001 uses a special format:
        lux = 0.01 * (2^exponent) * mantissa

        Returns:
            Light level in lux (float)
        """
        exponent, mantissa = self.read_raw()
        lux = 0.01 * (2 ** exponent) * mantissa
        return lux

    @property
    def lux(self):
        """
        Read the light level in lux (property).

        Returns:
            Light level in lux (float)
        """
        return self.read_lux()

    def is_conversion_ready(self):
        """
        Check if a new conversion is ready.

        Returns:
            True if conversion is ready, False otherwise
        """
        config = self._read_register(_REG_CONFIG)
        return bool(config & _CONFIG_CRF)

    def single_shot(self):
        """
        Trigger a single-shot conversion and wait for completion.

        Returns:
            Light level in lux (float)
        """
        # Configure for single-shot mode
        self.configure(mode=MODE_SINGLE_SHOT)

        # Wait for conversion to complete
        timeout = 1.0  # 1 second timeout
        start = time.monotonic()
        while not self.is_conversion_ready():
            if time.monotonic() - start > timeout:
                raise RuntimeError("Timeout waiting for conversion")
            time.sleep(0.01)

        return self.read_lux()

    def set_low_limit(self, lux):
        """
        Set the low limit threshold in lux.

        Args:
            lux: Low limit threshold in lux
        """
        exponent, mantissa = self._lux_to_raw(lux)
        raw = (exponent << 12) | mantissa
        self._write_register(_REG_LOW_LIMIT, raw)

    def set_high_limit(self, lux):
        """
        Set the high limit threshold in lux.

        Args:
            lux: High limit threshold in lux
        """
        exponent, mantissa = self._lux_to_raw(lux)
        raw = (exponent << 12) | mantissa
        self._write_register(_REG_HIGH_LIMIT, raw)

    def _lux_to_raw(self, lux):
        """
        Convert lux value to exponent and mantissa.

        Args:
            lux: Light level in lux

        Returns:
            Tuple of (exponent, mantissa)
        """
        # Find the best exponent and mantissa
        # lux = 0.01 * (2^exponent) * mantissa
        # mantissa = lux / (0.01 * 2^exponent)

        for exp in range(12):
            mantissa = int(lux / (0.01 * (2 ** exp)))
            if mantissa <= 4095:  # 12-bit mantissa max
                return exp, mantissa

        # If we get here, use max values
        return 11, 4095

    def deinit(self):
        """Put the sensor into shutdown mode to save power."""
        self.configure(mode=MODE_SHUTDOWN)
