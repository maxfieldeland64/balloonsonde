"""Host-side tests for bme280.py (run with: pytest firmware/sonde/tests)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import bme280  # noqa: E402

# Calibration constants from the Bosch BMP280/BME280 datasheet example.
CAL = {
    "T1": 27504, "T2": 26435, "T3": -1000,
    "P1": 36477, "P2": -10685, "P3": 3024, "P4": 2855, "P5": 140,
    "P6": -7, "P7": 15500, "P8": -14600, "P9": 6000,
    "H1": 75, "H2": 369, "H3": 0, "H4": 336, "H5": 50, "H6": 30,
}


def test_datasheet_temperature_and_pressure():
    t, p, _ = bme280.compensate(519888, 415148, 30000, CAL)
    assert abs(t - 25.08) < 0.01
    assert abs(p * 100 - 100653.27) < 0.5  # Pa


def _float_humidity(adc_t, adc_h, c):
    """Datasheet floating-point humidity algorithm, used as an independent cross-check."""
    var1 = (adc_t / 16384.0 - c["T1"] / 1024.0) * c["T2"]
    var2 = ((adc_t / 131072.0 - c["T1"] / 8192.0) ** 2) * c["T3"]
    t_fine = var1 + var2
    v = t_fine - 76800.0
    v = (adc_h - (c["H4"] * 64.0 + c["H5"] / 16384.0 * v)) * (
        c["H2"] / 65536.0 * (1.0 + c["H6"] / 67108864.0 * v * (1.0 + c["H3"] / 67108864.0 * v)))
    v = v * (1.0 - c["H1"] * v / 524288.0)
    return max(0.0, min(100.0, v))


def test_integer_humidity_matches_float_algorithm():
    for adc_h in (20000, 28000, 33000, 40000):
        _, _, h = bme280.compensate(519888, 415148, adc_h, CAL)
        assert abs(h - _float_humidity(519888, adc_h, CAL)) < 0.5


def test_humidity_is_clamped():
    _, _, lo = bme280.compensate(519888, 415148, 0, CAL)
    _, _, hi = bme280.compensate(519888, 415148, 65535, CAL)
    assert lo == 0.0
    assert hi <= 100.0


def test_parse_calibration_layout():
    # Build the two register blocks from CAL and parse them back.
    import struct
    b1 = struct.pack("<HhhHhhhhhhhh", CAL["T1"], CAL["T2"], CAL["T3"], CAL["P1"], CAL["P2"],
                     CAL["P3"], CAL["P4"], CAL["P5"], CAL["P6"], CAL["P7"], CAL["P8"], CAL["P9"])
    b1 += bytes([0, CAL["H1"]])
    h4, h5 = CAL["H4"], CAL["H5"]
    b2 = struct.pack("<h", CAL["H2"]) + bytes([
        CAL["H3"], (h4 >> 4) & 0xFF, (h4 & 0x0F) | ((h5 & 0x0F) << 4), (h5 >> 4) & 0xFF, CAL["H6"] & 0xFF])
    assert bme280.parse_calibration(b1, b2) == CAL
