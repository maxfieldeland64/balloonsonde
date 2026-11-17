# Flight operations

All numbers here are estimates. Check them with a scale and a predictor before launch.

## Lift calculation

At Bishop, CA (about 4,150 ft / 1,260 m), air is about 1.08 kg/m3 and helium is about 0.15 kg/m3, so each cubic meter of helium gives about **0.9 kg of gross lift**.

Target gross lift:

```
balloon (300 g) + payload and parachute (about 100-150 g) + free lift (about 250 g)
= about 650-700 g
```

That is about 0.7-0.8 m3 of helium (roughly 25-28 cubic feet) and an ascent rate of around 4-5 m/s.

The manufacturer's suggested fill for the 300 g balloon (1.5-1.8 m3, about 800 g net lift) is for heavy payloads. Filling to that with a 100 g payload would climb too fast. Fill to the lift you calculate, not to the suggested volume.

How to measure: attach the real payload, hang the balloon on a hanging scale (or tie it to a known weight), and add gas until the net upward pull equals the target free lift. Recheck after tying off.

A lighter fill gives a slower climb and usually a higher burst altitude. The listing states 18 km at the manufacturer's fill. Expect something between about 18 and 25 km. Treat this as unverified.

## Pre-launch checklist

- [ ] Batteries fresh and swapped in. Switch on.
- [ ] GPS fix and airborne mode confirmed. Check the readback.
- [ ] BME280 reads reasonable values (temperature, humidity, pressure vs a local reference).
- [ ] Ground receiver sees packets from the sonde, with good RSSI.
- [ ] Onboard log is writing. Check the file size is growing.
- [ ] Payload weighed. Line and parachute attached. Pull-test the line is under the 50 lb limit.
- [ ] Balloon filled to the calculated free lift. Neck tied off cleanly.
- [ ] Weather and winds checked. Predicted landing area reviewed. Airspace checked.
- [ ] Recovery plan made and someone told.
- [ ] Ground station running and logging before release.

## Launch

1. Fill outdoors in light wind. Keep the balloon and neck clear of rough surfaces.
2. Hold the payload on the line, switch on, wait for a GPS fix and a good telemetry packet.
3. Release and watch the ascent rate on the ground station.

## Recovery

- Use the last received position and the predicted trajectory. Note the last packet time and altitude.
- Winds aloft in winter can carry a payload a long way. Expect to drive.
- The onboard log has the full record even if radio contact is lost. It must survive the landing, so protect the board.
- Before approaching a landing site, check land access and safety.

## After the flight

- Merge the ground-station log with the onboard log. See [data-pipeline-spec.md](data-pipeline-spec.md).
- Note what went wrong and right in a flight report (date, fill, ascent rate, burst altitude, landing location, issues).
