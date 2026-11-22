# M1 radio link test, receiver side (the ground Pico, address 2).
# Run on the ground Pico: mpremote run m1/radio_link_rx.py
from machine import UART, Pin
from lora import RYLR, parse_rcv

uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1), timeout=100)
radio = RYLR(uart)

for step, reply in radio.configure(address=2):
    print("%-28s -> %s" % (step, reply))

print("Waiting for packets ...")
while True:
    line = radio.readline(timeout_ms=5000)
    if line is None:
        print("(no packet in 5 s)")
        continue
    pkt = parse_rcv(line)
    if pkt:
        print("from %d  data=%r  RSSI=%d dBm  SNR=%d dB" % (pkt["src"], pkt["data"], pkt["rssi"], pkt["snr"]))
    elif line:
        print(line)
