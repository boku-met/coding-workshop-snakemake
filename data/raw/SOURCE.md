# GeoSphere Austria source record

`vienna_hohe_warte_tlmax.csv` is a fixed CSV snapshot from the GeoSphere
Austria Data Hub. It is bundled so the workshop does not depend on network
access.

## Source

- Dataset: `klima-v2-1d`, quality-checked Austrian station data at daily resolution
- Dataset DOI: <https://doi.org/10.60669/gs6w-jd70>
- Dataset page: <https://data.hub.geosphere.at/en/dataset/klima-v2-1d?lang=en>
- License: Creative Commons Attribution 4.0 International

The following generated block identifies the bundled snapshot.

<!-- BEGIN GENERATED DATA SNAPSHOT -->
- Station: station `5904`, Wien Hohe Warte
- Parameter: `tlmax`, maximum 2 m air temperature in degrees Celsius
- Requested interval: 1991-04-01 through 2026-09-28
- Usable interval: 1991-04-01 through 2026-09-28
- Retrieved: 2026-09-29
- SHA-256: `4c0d3ecc1e80b8f83ed1432561144f16bcb41a7535f0f1999b894aab0c47ccf4`

Exact request:

```text
https://dataset.api.hub.geosphere.at/v1/station/historical/klima-v2-1d?parameters=tlmax&station_ids=5904&start=1991-04-01&end=2026-09-28&output_format=csv
```
<!-- END GENERATED DATA SNAPSHOT -->

The requested cutoff can be newer than the latest usable observation because
quality-checked values may be published with a delay.

## Native columns

| Column | Meaning |
|---|---|
| `time` | Observation date and time in UTC |
| `station` | Station identifier |
| `tlmax` | Daily maximum 2 m air temperature in degrees Celsius |
| `substation` | Individual station contributing to a combined series; absent from this snapshot |

A heat day is counted when the daily maximum temperature is at least 30 °C,
following [GeoSphere Austria's climate-index definition](https://klimaportal.geosphere.at/informationsportal-klimawandel/neoklim_hitze.html).
