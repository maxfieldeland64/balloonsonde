"""REYAX RYLR896 AT-command helper (MicroPython UART).

Commands end in CRLF. Replies look like +OK, +ERR=<n>, or +NAME=value.
Received packets arrive as +RCV=<addr>,<len>,<data>,<rssi>,<snr>.
"""
import time


def parse_rcv(line):
    """Parse '+RCV=1,5,HELLO,-45,12'. Returns a dict or None.

    The payload may itself contain commas, so it is cut out by the stated length.
    """
    line = line.strip()
    if not line.startswith("+RCV="):
        return None
    rest = line[5:]
    try:
        a_end = rest.index(",")
        addr = int(rest[:a_end])
        l_end = rest.index(",", a_end + 1)
        n = int(rest[a_end + 1:l_end])
        data = rest[l_end + 1:l_end + 1 + n]
        tail = rest[l_end + 1 + n:]
        if not tail.startswith(","):
            return None
        rssi, snr = tail[1:].split(",")
        return {"src": addr, "len": n, "data": data, "rssi": int(rssi), "snr": int(snr)}
    except ValueError:
        return None


class RYLR:
    def __init__(self, uart):
        self.uart = uart

    def flush(self):
        while self.uart.any():
            self.uart.read()

    def readline(self, timeout_ms=1000):
        """Return one decoded line (without CRLF) or None on timeout."""
        deadline = time.ticks_add(time.ticks_ms(), timeout_ms)
        buf = b""
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            if self.uart.any():
                ch = self.uart.read(1)
                if ch == b"\n":
                    try:
                        return buf.decode().strip()
                    except UnicodeError:
                        return ""
                buf += ch
            else:
                time.sleep_ms(2)
        return None

    def cmd(self, text, timeout_ms=1000):
        """Send an AT command, return the first reply line (or None)."""
        self.flush()
        self.uart.write(text.encode() + b"\r\n")
        return self.readline(timeout_ms)

    def configure(self, address, network_id=6, band=915000000, sf=9, bw=7, cr=1, preamble=12, power=15):
        """Set the radio to the project defaults. Returns a list of (command, reply)."""
        steps = [
            "AT+BAND=%d" % band,
            "AT+PARAMETER=%d,%d,%d,%d" % (sf, bw, cr, preamble),
            "AT+NETWORKID=%d" % network_id,
            "AT+ADDRESS=%d" % address,
            "AT+CRFOP=%d" % power,
        ]
        return [(s, self.cmd(s)) for s in steps]

    def send(self, dest, payload):
        return self.cmd("AT+SEND=%d,%d,%s" % (dest, len(payload), payload), timeout_ms=3000)
