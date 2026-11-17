# Sonde firmware spec

Status: spec only. Nothing is implemented yet.

## Summary

The firmware runs on a Raspberry Pi Pico (RP2040). It reads a BME280 and a u-blox GPS once per second, transmits a short ASCII packet over a RYLR896 LoRa module every few seconds, and logs every sample to onboard flash. It must keep working without any ground contact and must recover from brown-outs and hangs on its own.

## Language and structure

- **Language:** MicroPython first, for development speed. The RP2040 has plenty of headroom. Port hot paths to C only if needed.
- **Layout:** `firmware/sonde/`

```
firmware/sonde/
  main.py          # boot, self-test, main loop, state machine
  config.py        # pins, rates, thresholds, radio settings
  bme280.py        # driver + compensation
  gps.py           # NMEA parser, UBX config (airborne mode) and verify
  lora.py          # RYLR896 AT-command driver
  logger.py        # onboard CSV logging
  battery.py       # VSYS voltage via ADC
  telemetry.py     # frame builder + checksum
  tests/           # host-side unit tests (pytest) for parsers and frames
```

## Requirements

### Sensing

| ID | Requirement |
|---|---|
| S1 | Read BME280 temperature, humidity and pressure once per second in forced mode. |
| S2 | Detect the chip ID at startup: 0x60 is BME280, 0x58 is BMP280 (no humidity). Report the ID in the first packet and in the log. |
| S3 | Try I2C addresses 0x76 and 0x77. |
| S4 | Apply Bosch compensation formulas from the datasheet using the stored calibration data. |
| S5 | Parse GPS sentences GGA (time, position, fix quality, sats, altitude) and RMC (speed, course, status). NMEA only; do not rely on NAV-PVT because the NEO-6M may not support it. |
| S6 | Read battery voltage (VSYS/3 on ADC3) and the RP2040 internal temperature sensor every few seconds. |

### GPS airborne mode (critical)

Without airborne (<1 g) mode, many u-blox chips stop reporting position above about 18 km. The firmware must:

1. At boot, send `UBX-CFG-NAV5` with mask `0x0001` (dynamic model only) and `dynModel = 6` (airborne <1 g). Compute the Fletcher-8 checksum in code.
2. Poll `UBX-CFG-NAV5` back and check `dynModel == 6`.
3. Retry up to 3 times. If the setting never reads back, set a `GPS_NOAIR` flag in every packet and in the log.
4. Optionally save the setting with `UBX-CFG-CFG` if the board has EEPROM.

Clone modules may ignore this. Treat the readback as the source of truth, not the send.

### Radio

| ID | Requirement |
|---|---|
| R1 | Configure the RYLR896 at boot (see [telemetry-protocol.md](telemetry-protocol.md)): band, parameters, network ID, address, power. Read back and verify. |
| R2 | Send one telemetry frame every 5 s during ascent and every 10 s during descent. Never block the sensor loop waiting on the radio. |
| R3 | Ignore received traffic. This is a one-way link in v1. |
| R4 | If the radio does not answer an `AT` ping, reset it, log a fault, and continue logging. |

### Logging

| ID | Requirement |
|---|---|
| L1 | Append one CSV row per second to flash, with every field in the telemetry frame plus raw GPS time and the fault flags. |
| L2 | Flush to flash at least every 10 s so a power loss loses at most about 10 s of data. |
| L3 | Create a new log file each boot (`log_0001.csv`, `log_0002.csv`, ...). Never overwrite a previous flight. |
| L4 | At 1 Hz and about 100 bytes per row, 3 hours is about 1 MB. Check free space at boot and refuse to start a new log below a safe threshold (for example 200 KB), but keep transmitting. |

### Reliability

| ID | Requirement |
|---|---|
| F1 | Enable the hardware watchdog (about 8 s timeout). Feed it from the main loop. |
| F2 | A fault in one sensor must never stop the others, the radio or logging. Catch exceptions per sensor and set a fault bit. |
| F3 | On boot after a watchdog reset or brown-out, resume logging in a new file and mark a `RESET` flag in the next packets. |
| F4 | Total boot time under 10 s to first packet (GPS fix may take longer). |

## State machine

States are derived from GPS altitude and vertical speed, not from wall-clock timers.

```
BOOT -> SELFTEST -> WAIT_FIX -> PREFLIGHT -> ASCENT -> DESCENT -> LANDED
```

| State | Entry condition | Behavior |
|---|---|---|
| BOOT | Power on | Init peripherals, start watchdog |
| SELFTEST | After boot | Check BME280, GPS airborne mode, radio, flash. Send a status packet. |
| WAIT_FIX | Self-test done | Wait for a 3D fix. Send a packet every 5 s. |
| PREFLIGHT | Fix and stable | Normal telemetry. Wait for launch. |
| ASCENT | Climb more than 200 m above the launch point and vertical speed above 1 m/s for 10 s | Telemetry every 5 s |
| DESCENT | Altitude drops more than 500 m below the maximum and vertical speed below -3 m/s | Telemetry every 10 s |
| LANDED | Altitude changes by less than 5 m over 60 s while below 3000 m above the launch point | Beacon every 30 s to save power |

The state number is sent in each packet so the ground station can mark phases.

## Configuration constants (config.py)

All thresholds, pins, rates and radio parameters live in `config.py`. Nothing hard-coded elsewhere.

## Testing

- **Unit tests (host):** NMEA parser (valid and corrupt lines), UBX framing and checksum, BME280 compensation against Bosch reference values, frame builder and checksum.
- **Bench tests:** see [test-plan.md](test-plan.md).
- **Replay mode:** a build flag that feeds a recorded NMEA file and fake sensor values so the state machine and radio can be tested without flying.

## Definition of done (v1)

- Boots reliably on battery, runs unattended for 4 hours in the bench test.
- Airborne mode confirmed by readback on every boot.
- Packets arrive at the ground receiver with a valid checksum and expected fields.
- Onboard log survives a power cut within 10 s.
- State machine passes the replay test through all phases.

## Open questions

- Whether to log with MicroPython's filesystem (littlefs) or a raw binary format for speed and reliability.
- Whether to add a low-battery behavior (reduce TX rate) or just run flat out.
- Whether a second BME280 at a different address is worth the added mass for an independent measurement.
- GPS update rate (1 Hz default). Higher rates probably aren't needed.
