# Accra public weather check

On 20 November 2026, all 48 hourly temperature and humidity pairs in the authenticated Accra dashboard matched a separate Open-Meteo request for the same coordinates and two dates. The deployed response recorded a fetch at 14:54:37 UTC but labeled its status synthetic. This PR fixes the API and browser labels, reads the D1 cache on subsequent requests, preserves the original fetch timestamp and keeps help visible during a cold-cache provider outage. Open-Meteo does not supply an issue timestamp in that response; generation time in milliseconds measures processing duration.

## Station comparison

One exploratory month, February 2025, at the configured Accra site (5.6037, −0.1870). Kotoka International Airport (DGAA, about 2.2 km away) supplied 628 usable on-the-hour matches out of 672 possible hours per horizon. Observations come from Iowa Environmental Mesonet's ASOS/METAR archive. Only complete station temperature/humidity pairs at matching UTC hours were used. Open-Meteo supplies DWD ICON Global forecasts from its Previous Runs API. The returned grid centre was 5.625, −0.125. The production endpoint uses Open-Meteo's default model selection, so these results characterize the archived ICON feed. Data attribution: Open-Meteo, CC BY 4.0, with DWD ICON input; station archive: Iowa Environmental Mesonet.

| Screening rule | Archived horizon | Mean absolute error (°C) | Correct red hours | Missed red hours | False red hours |
|---|---|---:|---:|---:|---:|
| Existing air temperature ≥32°C | 1 day | 0.79 | 44 | 47 | 9 |
| Existing air temperature ≥32°C | 2 days | 0.83 | 47 | 44 | 14 |
| Candidate heat index ≥103°F | 1 day | 1.85 | 0 | 15 | 1 |
| Candidate heat index ≥103°F | 2 days | 1.96 | 0 | 15 | 0 |

Each row compares a forecast quantity with the same quantity at the station. Error is in air temperature for the first two rows and derived heat index for the last two. The two rules define different red events. Hours within a hot period are correlated. The candidate missed all 15 observed red heat-index hours at each horizon and remains offline. Neither rule establishes safe working conditions. Station temperature and humidity cannot establish radiant heat, worker strain or health outcomes.

The archive's previous-day fields represent nominal forecasts from 24 and 48 hours earlier. Exact issue times and first warning lead times are unavailable in this dataset. Same-day evaluation, other seasons and on-site verification remain open. Capture timestamped operational forecasts prospectively before estimating those metrics. No local correction was fitted to this evaluation month.

## Reproduce

Run from the repository root with Python 3 and Node 22.12 or newer. The checked-in CSV holds the matched source values in Celsius and percent relative humidity.

~~~sh
python3 scripts/accra_observations.py > /tmp/accra.csv
node scripts/score-accra.ts /tmp/accra.csv
~~~

Sources: [Open-Meteo previous runs](https://open-meteo.com/en/docs/previous-runs-api), [weather data licence](https://open-meteo.com/en/licence), [IEM station archive and its quality limitations](https://mesonet.agron.iastate.edu/request/download.phtml), [NOAA heat index equation](https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml).
