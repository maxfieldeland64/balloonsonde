# Sonde firmware

Flight firmware is not written yet (milestone M3). See [../../docs/firmware-spec.md](../../docs/firmware-spec.md) for the requirements and [../../docs/telemetry-protocol.md](../../docs/telemetry-protocol.md) for the packet format.

## What is here now (milestone M1)

| File | Purpose |
|---|---|
| `bme280.py` | BME280 driver with Bosch integer compensation |
| `gps.py` | NMEA checksum and GGA parsing |
| `lora.py` | RYLR896 AT-command helper and `+RCV` parser |
| `m1/` | Hardware test scripts for the Pico |
| `tests/` | Host-side unit tests (`pytest firmware/sonde/tests`) |

Follow [../../docs/m1-hello-hardware.md](../../docs/m1-hello-hardware.md) to flash MicroPython and run the tests.
