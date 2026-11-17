# Ground station spec

Status: spec only.

## Components

1. **Receiver hardware:** a RYLR896 on a Pico (second board from the 2-pack), or a RYLR896 on a USB-UART adapter plugged directly into a laptop.
2. **Receiver firmware (Pico):** a transparent bridge.
3. **Host software (Python):** ingest, validate, store, display, recovery help.

## Receiver firmware (if using a Pico)

- Configure the radio at boot with the same band, parameters and network ID as the sonde (see [telemetry-protocol.md](telemetry-protocol.md)). Address 2.
- Forward every `+RCV=...` line unchanged to the USB serial port.
- Accept a few simple host commands over USB (for example `CFG?` to print settings). Keep it minimal.
- Blink an LED on each valid frame.

## Host software

Language: Python 3.11+. Dependencies kept small: `pyserial`, `pandas` or the standard library for storage, one plotting/mapping library for the dashboard.

```
ground/
  receiver/        # Pico bridge firmware
  host/
    ingest.py      # serial reader, line parser, validator
    store.py       # raw + parsed storage
    app.py         # live dashboard
    sim.py         # replay a recorded file as a fake serial port
    tests/
```

### Requirements

| ID | Requirement |
|---|---|
| G1 | Read `+RCV` lines from a serial port, extract payloads, and validate the XOR checksum. |
| G2 | Append every raw line to a timestamped file before parsing, so nothing is lost on a parser bug. |
| G3 | Store parsed frames with host time, RSSI, SNR and the frame fields, in CSV or Parquet. |
| G4 | Report packet loss from `seq` gaps and the time since the last good frame. |
| G5 | Show a live view: latest values, altitude vs time, T/RH/P profiles vs altitude, ascent rate, battery voltage, signal strength. |
| G6 | Show a map of the track with the last known position and the predicted landing point. |
| G7 | Alert when contact is lost for more than 60 s, when the state becomes DESCENT, and when the battery is low. |
| G8 | Export the track as GPX/KML and the last known position as a link for a phone map. |
| G9 | Run offline on a laptop with no internet. Map tiles can be cached or skipped. |
| G10 | `sim.py` replays a recorded raw file at real or accelerated speed so the app can be tested without a radio. |

### Prediction

For the landing estimate, start simple: extrapolate the horizontal drift from the last few positions and the current descent rate. A better version can use a trajectory predictor with forecast winds (such as the CUSF/SondeHub predictor) before launch for planning.

### Staged build

1. **MVP:** serial reader, parser, raw and parsed storage, terminal printout.
2. **v1:** live plots and a track map, alerts.
3. **v2:** predicted landing, GPX/KML export, phone-friendly page.
4. **Stretch:** upload to a public tracking service. Only do this where its terms and band allow it.

## Testing

- Unit tests for the parser with good, corrupt and truncated frames.
- A recorded "fake flight" file in `ground/host/tests/data/` for the simulator.
- Field test: sonde in a car, receiver at a fixed point (see [test-plan.md](test-plan.md)).
