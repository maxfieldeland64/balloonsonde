# Test plan

Run these in order. Do not fly until the first four pass.

## 1. Bench test (free)

| Check | Pass criteria |
|---|---|
| Power from the AA holder | Boots, switch works, no resets over 30 min |
| BME280 | Chip ID read, temperature within about 2 C of a room thermometer, pressure within a few hPa of a local reference |
| GPS | Gets a 3D fix outdoors or at a window within a few minutes |
| GPS airborne mode | `UBX-CFG-NAV5` poll shows `dynModel = 6` after boot, every time |
| Radio | Ground receiver gets frames with valid checksums at close range |
| Onboard log | File grows; power-cycle mid-run loses at most about 10 s |
| Battery voltage | `vbat` reads close to a multimeter measurement |

## 2. Endurance test

| Check | Pass criteria |
|---|---|
| Run for 4 hours on a fresh set of lithium cells | No resets, log continues, voltage still above about 2.7 V |

## 3. Cold test (freezer)

| Check | Pass criteria |
|---|---|
| Sealed sonde in a freezer for 1 hour with fresh lithium cells | Still runs, still logs, radio still works when removed. No condensation inside after warming |

A home freezer is about -18 C. Real flight cold is far lower, so this is a sanity check only.

## 4. Drive test

| Check | Pass criteria |
|---|---|
| Sonde in a car driven up a high road (for example a mountain pass), receiver at a fixed point | Pressure altitude tracks GPS altitude; radio range is recorded vs distance; GPS holds a fix |

Record RSSI and SNR against distance to estimate range.

## 5. Tethered test (optional)

Use a small balloon on a short line, kept low and away from people, roads, power lines and airspace issues. Checks the mounting, antenna orientation and sensor exposure under real motion. Skip this if conditions are windy.

## 6. Cheap balloon flight (optional)

A 200 g balloon is the smallest that suits this payload. The 100 g balloon has too little net lift. It tests the launch, tracking and recovery chain before the full flight. Doesn't test cold or GPS altitude limits as well as the earlier steps.

## 7. Full flight

300 g balloon filled to the calculated lift. Follow [flight-ops.md](flight-ops.md).

## Pass/fail log

Keep one row per test run in `docs/test-log.md` (date, firmware version, hardware version, result, notes).
