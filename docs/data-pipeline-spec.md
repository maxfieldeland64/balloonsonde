# Data pipeline spec

Status: spec only. This is the science end of the project: turn raw logs into clean profiles and compare them with model forecasts.

## Inputs

1. **Onboard log** (`log_NNNN.csv` from the sonde flash). Complete, 1 Hz. This is the primary record.
2. **Ground log** (raw `+RCV` lines plus parsed frames). Partial, about every 5 s, with RSSI and SNR. Used as a backup and for the live track.
3. **Model data:** HRRR (CONUS) and IFS (ECMWF open data), at the nearest forecast cycles to launch time.

Raw data is never edited. Cleaned data is written to new files.

## Raw schema (onboard log, one row per second)

| Column | Unit | Notes |
|---|---|---|
| t_ms | ms | Time since boot |
| utc | hhmmss | GPS time (blank if no fix) |
| lat, lon | deg | |
| alt_gps | m | MSL |
| sats, fix | | |
| spd, hdg | m/s, deg | |
| temp | deg C | BME280 |
| rh | % | BME280 |
| press | hPa | BME280 |
| vbat | V | |
| state | 0-6 | |
| flags | hex | Fault bits |

## Processing steps

1. **Load and parse** into an `xarray.Dataset` with a time coordinate (UTC, using GPS time where available, otherwise interpolated from boot time).
2. **Quality control** (flag, don't delete):
   - Physical range checks (temperature -90 to 50 C, RH 0-105 %, pressure 1-1100 hPa).
   - Drop rows with no 3D fix from position-dependent steps.
   - Spike removal (median filter or a rate-of-change limit).
   - Humidity flagged below about -40 C and in cloud, where the BME280 is unreliable and slow.
   - Check consistency between GPS altitude and pressure altitude.
3. **Segment the flight** by vertical velocity: ascent, burst, descent, landed. Use the ascent profile as the primary dataset. Descent data has a different ventilation and falls faster, so treat it as lower quality.
4. **Derived variables:**
   - Pressure altitude (hypsometric or standard atmosphere), geopotential height.
   - Potential temperature: `theta = T * (1000 / p) ** 0.2854` (T in K, p in hPa).
   - Dew point (Magnus formula) and mixing ratio from RH, T and p.
   - Ascent rate (smoothed `d(alt)/dt`).
5. **Output** as NetCDF and/or Zarr with CF-style attribute names, units and a flight metadata block (launch time and place, hardware version, firmware version, fill and lift notes).

## Model comparison

For each flight:

1. **Fetch forecasts** for the cycles nearest the launch (HRRR and IFS). Use the Herbie package for HRRR and the `ecmwf-opendata` client for IFS, or query an existing archive (such as a Zarr store) if one is available.
2. **Interpolate in space and time:** for every sonde sample, take the model's horizontal field at (lat, lon) by bilinear interpolation and linearly interpolate between forecast valid times.
3. **Interpolate in the vertical:** use the model's pressure-level fields and interpolate to the measured pressure (log-p). Or interpolate the sonde to the model's levels.
4. **Compare:** bias, RMSE and MAE per layer (for example by 50 hPa bins) for T, RH, and (via the hypsometric relation) geopotential height. Plot sonde vs HRRR vs IFS profiles and difference profiles.
5. **Report:** one summary page per flight (see `analysis/` notebooks).

## Known measurement limits (write these into every report)

- **Solar heating:** the BME280 reads high in daytime at altitude. Consider a night or dawn launch for cleaner temperatures, or at least flag and discuss the day launch.
- **Time lag:** humidity especially lags, and it degrades quickly in the cold.
- **BME280 pressure accuracy:** about +/-1 hPa at room temperature and worse at low pressure. Compare with a local reference before launch to estimate any offset.
- **Single sensor:** no redundancy. Outliers can't be cross-checked.
- **Descent:** faster fall rates and a different sensor ventilation lower the quality.

## Code layout

```
analysis/
  qc.py             # QC flags and filters
  derive.py         # derived variables
  models.py         # HRRR and IFS retrieval and interpolation
  compare.py        # metrics and plots
  notebooks/        # per-flight reports
  tests/
data/               # git-ignored: raw/ and processed/
```

## Testing

- Unit tests for the derived-variable functions against known values.
- A synthetic profile with known errors, to confirm the QC flags and the metrics code.
- Re-run the whole pipeline on a recorded test flight file to confirm outputs are reproducible.
