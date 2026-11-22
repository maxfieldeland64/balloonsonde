# M1 test 3: talk to the RYLR896 over UART0 (Pico TX = GP0, RX = GP1) at 115200 baud.
# Run on the Pico: mpremote run m1/radio_test.py
# Set CONFIGURE = True once to apply the project radio settings (sonde address 1).
from machine import UART, Pin
from lora import RYLR

CONFIGURE = False
ADDRESS = 1          # sonde = 1, ground station = 2

uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1), timeout=100)
radio = RYLR(uart)

for q in ("AT", "AT+VER?", "AT+ADDRESS?", "AT+NETWORKID?", "AT+BAND?", "AT+PARAMETER?", "AT+CRFOP?"):
    print("%-16s -> %s" % (q, radio.cmd(q)))

if CONFIGURE:
    print("\nConfiguring (address %d) ..." % ADDRESS)
    for step, reply in radio.configure(ADDRESS):
        print("%-28s -> %s" % (step, reply))
    print("\nReadback:")
    for q in ("AT+ADDRESS?", "AT+NETWORKID?", "AT+BAND?", "AT+PARAMETER?", "AT+CRFOP?"):
        print("%-16s -> %s" % (q, radio.cmd(q)))
