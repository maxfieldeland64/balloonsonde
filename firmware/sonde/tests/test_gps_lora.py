"""Host-side tests for gps.py and lora.py parsers (run with: pytest firmware/sonde/tests)."""
import os
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import gps  # noqa: E402

# lora.py imports `time` and uses MicroPython-only helpers at runtime; the parser is pure.
import lora  # noqa: E402

GGA = "$GPGGA,092750.000,5321.6802,N,00630.3372,W,1,8,1.03,61.7,M,55.2,M,,*76"


def test_checksum_valid_and_invalid():
    assert gps.nmea_valid(GGA)
    assert not gps.nmea_valid(GGA.replace("*76", "*77"))
    assert not gps.nmea_valid("garbage")
    assert not gps.nmea_valid("$GPGGA,1,2,3")


def test_parse_gga():
    g = gps.parse_gga(GGA)
    assert g["fix"] == 1 and g["sats"] == 8
    assert abs(g["lat"] - 53.361337) < 1e-5
    assert abs(g["lon"] + 6.505620) < 1e-5
    assert g["alt"] == 61.7


def test_parse_gga_no_fix():
    body = "GPGGA,092750.00,,,,,0,00,99.99,,,,,,"
    line = "$%s*%02X" % (body, gps.nmea_checksum(body))
    g = gps.parse_gga(line)
    assert g["fix"] == 0 and g["lat"] is None and g["alt"] is None


def test_parse_gga_ignores_other_sentences():
    body = "GPRMC,092750.00,A,5321.6802,N,00630.3372,W,0.02,31.66,280511,,,A"
    line = "$%s*%02X" % (body, gps.nmea_checksum(body))
    assert gps.parse_gga(line) is None


def test_parse_rcv_simple():
    r = lora.parse_rcv("+RCV=1,5,HELLO,-45,12")
    assert r == {"src": 1, "len": 5, "data": "HELLO", "rssi": -45, "snr": 12}


def test_parse_rcv_payload_with_commas():
    r = lora.parse_rcv("+RCV=1,9,HELLO,1,2,-60,9")
    assert r["data"] == "HELLO,1,2" and r["rssi"] == -60 and r["snr"] == 9


def test_parse_rcv_rejects_bad_lines():
    assert lora.parse_rcv("+OK") is None
    assert lora.parse_rcv("+RCV=1,5,HELLO") is None
