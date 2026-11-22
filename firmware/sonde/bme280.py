"""BME280 driver (MicroPython, I2C) with Bosch integer compensation.

The compensation math is a pure function so it can be unit tested on a
laptop against the Bosch datasheet example values.
"""
import struct

CHIP_BME280 = 0x60
CHIP_BMP280 = 0x58  # no humidity sensor


def _s8(v):
    return v - 256 if v > 127 else v


def parse_calibration(block1, block2):
    """block1 = 26 bytes from 0x88, block2 = 7 bytes from 0xE1. Returns a dict."""
    t1, t2, t3, p1, p2, p3, p4, p5, p6, p7, p8, p9 = struct.unpack("<HhhHhhhhhhhh", block1[:24])
    h1 = block1[25]
    h2 = struct.unpack("<h", block2[0:2])[0]
    h3 = block2[2]
    h4 = (_s8(block2[3]) << 4) | (block2[4] & 0x0F)
    h5 = (_s8(block2[5]) << 4) | (block2[4] >> 4)
    h6 = _s8(block2[6])
    return {
        "T1": t1, "T2": t2, "T3": t3,
        "P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5,
        "P6": p6, "P7": p7, "P8": p8, "P9": p9,
        "H1": h1, "H2": h2, "H3": h3, "H4": h4, "H5": h5, "H6": h6,
    }


def compensate(adc_t, adc_p, adc_h, c):
    """Return (temp_C, pressure_hPa, humidity_pct) from raw ADC values."""
    # Temperature (datasheet 32-bit integer algorithm)
    var1 = (((adc_t >> 3) - (c["T1"] << 1)) * c["T2"]) >> 11
    var2 = (((((adc_t >> 4) - c["T1"]) * ((adc_t >> 4) - c["T1"])) >> 12) * c["T3"]) >> 14
    t_fine = var1 + var2
    temp_c = ((t_fine * 5 + 128) >> 8) / 100.0

    # Pressure (datasheet 64-bit integer algorithm); result in Pa
    v1 = t_fine - 128000
    v2 = v1 * v1 * c["P6"]
    v2 = v2 + ((v1 * c["P5"]) << 17)
    v2 = v2 + (c["P4"] << 35)
    v1 = ((v1 * v1 * c["P3"]) >> 8) + ((v1 * c["P2"]) << 12)
    v1 = (((1 << 47) + v1) * c["P1"]) >> 33
    if v1 == 0:
        press_hpa = 0.0
    else:
        p = 1048576 - adc_p
        p = (((p << 31) - v2) * 3125) // v1
        v1 = (c["P9"] * (p >> 13) * (p >> 13)) >> 25
        v2 = (c["P8"] * p) >> 19
        p = ((p + v1 + v2) >> 8) + (c["P7"] << 4)
        press_hpa = (p / 256.0) / 100.0

    # Humidity (datasheet 32-bit integer algorithm); result in %RH
    x = t_fine - 76800
    x = (((((adc_h << 14) - (c["H4"] << 20) - (c["H5"] * x)) + 16384) >> 15)
         * (((((((x * c["H6"]) >> 10) * (((x * c["H3"]) >> 11) + 32768)) >> 10) + 2097152)
             * c["H2"] + 8192) >> 14))
    x = x - (((((x >> 15) * (x >> 15)) >> 7) * c["H1"]) >> 4)
    x = 0 if x < 0 else x
    x = 419430400 if x > 419430400 else x
    hum = (x >> 12) / 1024.0

    return temp_c, press_hpa, hum


class BME280:
    def __init__(self, i2c, addr=None):
        self.i2c = i2c
        self.addr = addr if addr is not None else self._find()
        self.chip_id = self.i2c.readfrom_mem(self.addr, 0xD0, 1)[0]
        self.has_humidity = self.chip_id == CHIP_BME280
        if self.chip_id not in (CHIP_BME280, CHIP_BMP280):
            raise OSError("unexpected chip id 0x%02X at 0x%02X" % (self.chip_id, self.addr))
        self.i2c.writeto_mem(self.addr, 0xE0, b"\xB6")  # soft reset
        self._sleep_ms(5)
        b1 = self.i2c.readfrom_mem(self.addr, 0x88, 26)
        b2 = self.i2c.readfrom_mem(self.addr, 0xE1, 7)
        self.cal = parse_calibration(b1, b2)

    def _find(self):
        found = self.i2c.scan()
        for a in (0x76, 0x77):
            if a in found:
                return a
        raise OSError("no BME280/BMP280 at 0x76 or 0x77 (scan: %s)" % [hex(x) for x in found])

    @staticmethod
    def _sleep_ms(ms):
        import time
        time.sleep_ms(ms)

    def read(self):
        """One forced-mode measurement. Returns (temp_C, pressure_hPa, humidity_pct)."""
        # osrs_h x1, then osrs_t x1, osrs_p x1, forced mode
        self.i2c.writeto_mem(self.addr, 0xF2, b"\x01")
        self.i2c.writeto_mem(self.addr, 0xF4, b"\x25")
        self._sleep_ms(15)
        d = self.i2c.readfrom_mem(self.addr, 0xF7, 8)
        adc_p = (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)
        adc_t = (d[3] << 12) | (d[4] << 4) | (d[5] >> 4)
        adc_h = (d[6] << 8) | d[7]
        t, p, h = compensate(adc_t, adc_p, adc_h, self.cal)
        if not self.has_humidity:
            h = float("nan")
        return t, p, h
