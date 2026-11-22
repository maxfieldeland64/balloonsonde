# M1 radio link test, transmitter side (the sonde Pico, address 1).
# Run on the sonde Pico: mpremote run m1/radio_link_tx.py
import time
from machine import UART, Pin
from lora import RYLR

uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1), timeout=100)
radio = RYLR(uart)

for step, reply in radio.configure(address=1):
    print("%-28s -> %s" % (step, reply))

seq = 0
while True:
    seq += 1
    msg = "HELLO,%d" % seq
    print("send %-12s -> %s" % (msg, radio.send(2, msg)))
    time.sleep(2)
