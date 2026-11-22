# Roadmap

## Milestones

- [x] **M0 Parts:** order and receive all parts (see `hardware/bom.csv`).
- [ ] **M1 Hello hardware:** flash MicroPython, read the BME280, read raw NMEA from the GPS, send an AT command to the radio. See [m1-hello-hardware.md](m1-hello-hardware.md).
- [ ] **M2 Link:** sonde sends test frames, ground receives and validates them.
- [ ] **M3 Firmware v1:** all requirements in [firmware-spec.md](firmware-spec.md), unit tests passing, replay test passing.
- [ ] **M4 Ground v1:** MVP then live plots and map ([ground-station-spec.md](ground-station-spec.md)).
- [ ] **M5 Soldered build:** move from jumpers to the perfboard, mount in a housing, weigh it.
- [ ] **M6 Tests:** bench, endurance, cold, drive ([test-plan.md](test-plan.md)).
- [ ] **M7 Flight 1:** full launch and recovery ([flight-ops.md](flight-ops.md)).
- [ ] **M8 Analysis v1:** QC, derived variables, HRRR and IFS comparison ([data-pipeline-spec.md](data-pipeline-spec.md)).

## Backlog / ideas

- Second BME280 or a better humidity sensor.
- Radiation shield design and a night launch for cleaner temperatures.
- Two-way link for commands (for example change TX rate).
- Cut-down or a backup tracker for recovery.
- Public data page for each flight.
- Port firmware to C/Pico SDK if MicroPython timing becomes an issue.

## Open questions

- Does the NEO-6M clone accept and hold airborne mode?
- What is the real radio range at SF9 from altitude to the Owens Valley and surrounding terrain?
- Day or night launch for the first flight?
- Where is a good launch site with a safe recovery area?
- Do we want to upload data publicly, and to what?
