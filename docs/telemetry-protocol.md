# Telemetry protocol

Status: draft v0.1.

## Radio settings (RYLR896, US 915 MHz)

All are AT commands over UART at 115200 baud by default. Verify the actual defaults on your module with `AT` and `AT+PARAMETER?`.

| Setting | Command | Starting value | Notes |
|---|---|---|---|
| Band | `AT+BAND=915000000` | 915 MHz | Must match on both modules |
| Parameters | `AT+PARAMETER=9,7,1,12` | SF9, BW 125 kHz, CR 4/5, preamble 12 | Tune later; higher SF means more range and slower air time |
| Network ID | `AT+NETWORKID=6` | 6 | Same on both |
| Address | `AT+ADDRESS=1` (sonde) / `AT+ADDRESS=2` (ground) | | |
| Power | `AT+CRFOP=15` | 15 dBm | The module's maximum; do not exceed |

Transmit: `AT+SEND=<dest address>,<length>,<payload>` for example `AT+SEND=2,80,$BS,...`.
Receive: `+RCV=<src>,<length>,<payload>,<RSSI>,<SNR>` on the ground module.

The payload is sent as ASCII. Keep to printable characters and avoid commas inside the AT command parsing issue by relying on the length field (the module parses by length). Confirm this behavior on the real modules. Max payload per the module docs is 240 bytes; frames here are about 80-90 bytes.

Air time estimates: roughly 0.3-0.5 s per frame at SF9/125 kHz. Treat as an estimate until measured.

## Frame format

ASCII, one frame per message, NMEA-style:

```
$BS,<seq>,<utc>,<lat>,<lon>,<alt>,<sats>,<fix>,<spd>,<hdg>,<temp>,<rh>,<press>,<vbat>,<state>*<cs>
```

Example (checksum computed for this exact body):

```
$BS,1042,171205,37.3610,-118.3950,4210.5,9,3,12.4,271,-3.2,41.5,612.80,3.18,2*1E
```

| # | Field | Unit | Example | Notes |
|---|---|---|---|---|
| 1 | seq | count | 1042 | Increments every transmitted frame, wraps at 65535 |
| 2 | utc | hhmmss | 171205 | GPS time (UTC). Empty if no fix |
| 3 | lat | deg | 37.3610 | 4 decimals (about 11 m) |
| 4 | lon | deg | -118.3950 | |
| 5 | alt | m | 4210.5 | GPS altitude above MSL |
| 6 | sats | count | 9 | |
| 7 | fix | 0-3 | 3 | 0 none, 2 = 2D, 3 = 3D |
| 8 | spd | m/s | 12.4 | Ground speed |
| 9 | hdg | deg | 271 | Course over ground |
| 10 | temp | deg C | -3.2 | BME280 |
| 11 | rh | % | 41.5 | BME280 |
| 12 | press | hPa | 612.80 | BME280 |
| 13 | vbat | V | 3.18 | VSYS |
| 14 | state | 0-6 | 2 | See state machine |

Empty fields mean the value is unavailable. Extra status flags (fault bits, GPS airborne OK, reset) are sent in a separate `$BF` frame every 60 s:

```
$BF,<seq>,<flags_hex>,<bme_chip_id>,<gps_nav_model>,<uptime_s>,<log_free_kb>*<cs>
```

### Checksum

XOR of every byte between `$` and `*` (exclusive), as two uppercase hex digits. Same as NMEA. The ground software rejects frames with a bad or missing checksum and counts them.

The LoRa layer also has its own CRC. If bit errors ever slip through in practice, upgrade to CRC-16/CCITT in a new frame version (`$BT`).

## Versioning

- The 3-letter tag is the format version: `$BS` is v1 telemetry, `$BF` is v1 flags.
- Never change the meaning of a field under the same tag. Add fields only at the end, and bump the tag if the order changes.

## Ground side

- Parse `+RCV=` lines, extract the payload by the stated length, and validate the checksum.
- Store the raw line plus a host timestamp, RSSI and SNR with every frame.
- Detect gaps in `seq` to report packet loss.
