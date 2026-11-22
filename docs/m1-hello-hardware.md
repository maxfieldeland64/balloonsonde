# M1: Hello hardware

Goal: prove each part works on its own before building anything on top. Three short tests, each with its own wiring, then a two-radio link test.

Nothing here is flight code. Use jumper wires or a breadboard; no soldering is needed except the header pins on parts that arrived without them.

Status of the scripts: the pure logic (BME280 compensation, NMEA parsing, radio reply parsing) is unit tested on a laptop. The scripts that talk to the real hardware have **not** been run on a Pico yet. Expect to fix small things on the first run, and note them in [test-log.md](test-log.md).

## 0. What you need

- Pico (sonde) and a second Pico (ground) with a USB cable
- BME280 board, GPS board (NEO-6M), two RYLR896 radios
- Jumper wires, a computer with a USB port
- Tools on the computer: [Thonny](https://thonny.org) (easiest) **or** `pip install mpremote`

## 1. Flash MicroPython

1. Download the latest stable MicroPython `.uf2` for the Raspberry Pi Pico (RP2040) from micropython.org/download/RPI_PICO/. If your boards turn out to be a Pico 2 (RP2350), use the `RPI_PICO2` build instead.
2. Hold the **BOOTSEL** button, plug the Pico into USB, then release it. A drive named `RPI-RP2` appears.
3. Drag the `.uf2` file onto that drive. The Pico reboots by itself.
4. Check it works. With mpremote: `mpremote connect list` shows the port, then `mpremote exec "print('hello')"`. With Thonny: choose the interpreter *MicroPython (Raspberry Pi Pico)* at the bottom right, and the Shell shows `>>>`.
5. Do the same for the second Pico.

## 2. Copy the files to the Pico

From the `firmware/sonde/` folder in this repo:

```
mpremote cp bme280.py : + cp gps.py : + cp lora.py :
```

(In Thonny: open each file, then File > Save as > Raspberry Pi Pico, keeping the same file name.)

The `m1/` scripts are run directly, so you don't need to copy them:

```
mpremote run m1/bme280_test.py
```

(In Thonny: open the script and press Run. It uses the modules you copied.)

## 3. Test 1: BME280

Power off the Pico (unplug USB) before changing wires.

| BME280 pin | Pico pin |
|---|---|
| VCC / VIN | 3V3 (pin 36) |
| GND | any GND |
| SDA | GP8 (pin 11) |
| SCL | GP9 (pin 12) |

Run `m1/bme280_test.py`.

**Pass:**
- The I2C scan lists `0x76` or `0x77`.
- It reports `BME280` (chip id `0x60`). If it says `BMP280 (NO humidity!)` the board is mislabeled. Contact the seller for a return, since you need humidity.
- Temperature is within about 2 C of a room thermometer. Pressure is plausible for Bishop (roughly 850-870 hPa at 4,150 ft, which is lower than sea-level weather reports, because those are corrected to sea level). Humidity rises when you breathe near the sensor.

## 4. Test 2: GPS

| GPS pin | Pico pin |
|---|---|
| VCC | 3V3 (pin 36) |
| GND | any GND |
| TX | GP5 (pin 7) |
| RX | GP4 (pin 6) |

TX and RX cross over: the GPS's TX goes to the Pico's RX pin.

Take it outdoors (or to a window with open sky) and run `m1/gps_test.py`. A cold start can take a few minutes, so raise `RUN_SECONDS` if you need to. The module's small LED usually starts blinking once it has a fix.

**Pass:**
- Lines starting with `$GPGGA`, `$GPRMC` and so on scroll by, and the summary shows mostly valid lines.
- Within a few minutes the `-> fix=` line shows `fix=1` (or higher), `sats` of 4 or more, and a latitude and longitude near Bishop.

If no valid lines appear: swap the TX and RX wires, check that VCC is on 3V3, and confirm the baud rate (9600 is the default for this module).

## 5. Test 3: Radio AT commands

| RYLR896 pin | Pico pin |
|---|---|
| VDD | 3V3 (pin 36) |
| GND | any GND |
| TXD | GP1 (pin 2) |
| RXD | GP0 (pin 1) |

Check the pin labels printed on your module rather than assuming a pin order. Also check the antenna is attached before powering the radio.

Run `m1/radio_test.py`.

**Pass:**
- `AT` replies `+OK`.
- `AT+VER?` replies with a version string (for example `+VER=...`).
- The query commands reply with values rather than `None` or an error.

If every reply is `None`: check the TX/RX crossover and power. If you get garbage, the module may be set to a different baud rate; try 9600 in the script.

Then set `CONFIGURE = True` and run it again once. It applies the project defaults (915 MHz band, SF9, network 6, address 1, 15 dBm) and prints a readback. Each reply should be `+OK`.

## 6. Test 4: Radio link between the two Picos

Wire the second Pico with a second RYLR896 the same way as step 5.

1. On the ground Pico: `mpremote connect <port> run m1/radio_link_rx.py` (address 2).
2. On the sonde Pico: `mpremote connect <port> run m1/radio_link_tx.py` (address 1). Use `mpremote connect list` to see the two port names.
3. The ground side should print `from 1 data='HELLO,1' RSSI=... SNR=...` every 2 seconds.

**Pass:** packets arrive reliably at a few meters, then across the house, with RSSI in the usual range (stronger than about -100 dBm nearby).

Keep the antennas upright and a couple of centimeters away from other wiring.

## 7. Record results

Add a row per test to [test-log.md](test-log.md). If something needed changing in the scripts, fix it and commit it so the repo matches what worked.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `ImportError: no module named bme280` | The `.py` files were not copied to the Pico (step 2). |
| `OSError: [Errno 5] EIO` or an empty I2C scan | SDA/SCL swapped, loose jumper, or no power on the sensor. |
| Chip id `0x58` | The board is a BMP280, not a BME280. |
| GPS prints nothing | TX/RX not crossed, no power, or a loose wire. |
| GPS prints lines but no fix | Not enough sky view; wait longer outdoors. |
| Radio replies `None` | TX/RX swapped, wrong baud rate, or no power. |
| Radio replies `+ERR=...` | Command syntax or a value out of range. |
| Packets don't arrive | Different network ID, band, or address on the two radios. Run the readback on both. |

## Done when

- [ ] MicroPython runs on both Picos.
- [ ] BME280 reads sensible temperature, pressure and humidity.
- [ ] GPS shows valid NMEA and gets a fix outdoors.
- [ ] Radio answers AT commands and holds the project settings.
- [ ] Two radios exchange packets.

Then M2 (the sonde sends real sensor frames) is next. See [roadmap.md](roadmap.md).
