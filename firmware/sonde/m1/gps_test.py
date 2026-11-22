# M1 test 2: raw NMEA from the GPS on UART1 (Pico TX = GP4, RX = GP5) at 9600 baud.
# Run on the Pico: mpremote run m1/gps_test.py
# Take the board outdoors or to a window with a view of the sky.
import time
from machine import UART, Pin
from gps import nmea_valid, parse_gga

RUN_SECONDS = 120          # raise this for a cold start (can take several minutes)
PRINT_RAW = True           # print every line; set False to print only fix summaries

uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5), timeout=1000)

lines = good = bad = 0
types = {}
start = time.ticks_ms()
print("Listening for %d s ..." % RUN_SECONDS)

while time.ticks_diff(time.ticks_ms(), start) < RUN_SECONDS * 1000:
    raw = uart.readline()
    if not raw:
        continue
    try:
        line = raw.decode().strip()
    except UnicodeError:
        bad += 1
        continue
    lines += 1
    if nmea_valid(line):
        good += 1
        kind = line[3:6]
        types[kind] = types.get(kind, 0) + 1
        if PRINT_RAW:
            print(line)
        gga = parse_gga(line)
        if gga:
            print("   -> fix=%d sats=%d lat=%s lon=%s alt=%s" % (
                gga["fix"], gga["sats"], gga["lat"], gga["lon"], gga["alt"]))
    else:
        bad += 1

print("\nSummary: %d lines, %d valid, %d bad/garbled" % (lines, good, bad))
print("Sentence types seen:", types)
if good == 0:
    print("No valid NMEA: check wiring (GPS TX -> GP5, GPS RX -> GP4), power, and baud rate.")
