"""NMEA helpers for the GPS (pure functions, MicroPython and CPython).

UBX airborne-mode configuration is added in milestone M3.
"""


def nmea_checksum(body):
    """XOR of the characters between '$' and '*'."""
    c = 0
    for ch in body:
        c ^= ord(ch)
    return c


def nmea_valid(line):
    """True if the line looks like $...*HH and the checksum matches."""
    line = line.strip()
    if not line.startswith("$") or "*" not in line:
        return False
    body, _, cs = line[1:].partition("*")
    if len(cs) < 2:
        return False
    try:
        return nmea_checksum(body) == int(cs[:2], 16)
    except ValueError:
        return False


def _deg(value, hemi):
    """ddmm.mmmm / dddmm.mmmm to signed decimal degrees."""
    if not value:
        return None
    dot = value.index(".")
    d = int(value[: dot - 2])
    m = float(value[dot - 2:])
    deg = d + m / 60.0
    return -deg if hemi in ("S", "W") else deg


def parse_gga(line):
    """Parse a GGA sentence. Returns a dict, or None if it is not a valid GGA."""
    if not nmea_valid(line):
        return None
    f = line.strip()[1:].split("*")[0].split(",")
    if not f[0].endswith("GGA") or len(f) < 10:
        return None
    try:
        quality = int(f[6]) if f[6] else 0
        return {
            "utc": f[1],
            "lat": _deg(f[2], f[3]),
            "lon": _deg(f[4], f[5]),
            "fix": quality,
            "sats": int(f[7]) if f[7] else 0,
            "alt": float(f[9]) if f[9] else None,
        }
    except ValueError:
        return None
