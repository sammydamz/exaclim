# Job 04 — Risk and forecast model design

Status: implemented and unit-tested as an illustrative software scenario engine. No personal heat-strain model has been trained. No clinical or occupational exposure limit has been calibrated. Prepared 16 November 2026 for Exaclim.

## Purpose and boundary

Exaclim demonstrates earlier operational caution using environmental observations, declared task context and forecast scenarios. The current implementation supports a single synthetic worker. Its output is an **illustrative exposure index**, not measured absorbed heat, body temperature, WBGT, diagnosis, remaining safe work time or a prescription. The heat-dosimeter analogy describes a product intention; it is not a metrological claim.

The primary occupational guidance selected for review is NIOSH's 2016 *Criteria for a Recommended Standard: Occupational Exposure to Heat and Hot Environments*. Direct access has been blocked by the environment proxy, so the implementation does not claim to reproduce NIOSH limits. ISO 7243 (WBGT) and ISO 7933 (predicted heat strain) are candidates for later expert review, not standards implemented by this engine. Local legal duties must be assessed separately.

## Working implementation

Code: `exaclim/engine.py`, function `evaluate(payload)`. The function is pure: no network, personal identity, storage or side effects. The server is responsible for trusted session state and emergency resolution authorization. The function returns a JSON-compatible dictionary.

Required inputs are temperature in Celsius, humidity percentage, declared workload (`light`, `moderate`, `heavy`), clothing (`ordinary`, `protective`), acclimatization flag, elapsed exposure minutes and sensor age seconds. Required values missing, malformed or outside declared bounds trigger cautious fallback. Boolean values must be booleans, not strings. Numeric inputs reject NaN, infinity and booleans.

Bounds are engineering validation limits, not the range in which work is safe: temperature -10 to 60°C; humidity 0–100%; exposure duration 0–960 minutes; sensor age 0–604800 seconds. They do not establish sensor accuracy. Data older than **120 seconds** is stale. This timeout is a demonstration configuration requiring field communication analysis.

## Transparent illustrative formula

Score = min(100, temperature contribution + humidity contribution + workload contribution + clothing contribution + acclimatization contribution + duration contribution).

- Temperature: max(0, (temperature °C − 25) × 4).
- Humidity: max(0, relative humidity % − 40) × 0.3.
- Workload: light 0; moderate 10; heavy 20.
- Clothing: ordinary 0; protective 12.
- Acclimatization: declared acclimatized 0; otherwise 8.
- Duration: elapsed exposure minutes ÷ 12.

Green: score below 40. Amber: score at least 40 and below 70. Red: score at least 70. Emergency is a separate explicit help state and is never inferred from score alone.

**Every coefficient and the 40/70 thresholds are illustrative software parameters.** They were selected to demonstrate understandable state changes in synthetic scenarios; they have no established sensitivity, specificity or relationship to a human physiological limit. Do not apply them on site. Protective clothing is reduced to a coarse demonstration category, not a measured insulation correction. A binary acclimatization flag is declared context, not a medical determination.

This version does not integrate a time series of changing heat conditions. Its duration contribution is a simplified elapsed-exposure term. It must not be described as a physiologically validated cumulative dose. Rest does not automatically reset an emergency or erase observed exposure history. A later dose model would need explicit time integration, recovery assumptions, expert review and validation.

## Safety state rules

Baseline is calculated from current inputs when valid. Stale or invalid data produces at least amber and preserves an earlier red or emergency state. Invalid inputs yield a null score rather than a reassuring numeric result. A stale but otherwise valid reading can retain a numeric score only alongside its stale quality marker; this value is not fresh evidence.

Forecast rows can raise the final level above the current baseline, never lower it. Help requests, a retained emergency latch, or a previous emergency state always produce emergency. Acknowledgement is returned separately and never reduces severity. The engine has no `clear emergency` flag: an authorized server operation must resolve it explicitly. The server must not accept a client-supplied previous state as authoritative.

Routine advice remains grounded in the site's existing heat-control plan. Red asks the affected worker to stop the task, reach a cooler safe area and notify the designated supervisor. Emergency directs activation of the site procedure and urgent help. Software must not represent alert delivery as a completed emergency response.

## Forecast integration and provenance

Optional forecast rows accept `temperature_c`, `humidity_pct`, `minutes_ahead`, and an optional display `time`. Valid rows are sorted by minutes ahead. The same illustrative score is evaluated with projected elapsed exposure, capped at the duration validation bound. Invalid rows are excluded with an explicit count. The engine evaluates up to 72 rows; the server should enforce bounded request sizes.

The forecast response contains `status`, `rows`, `invalid_rows`, and `minutes_to_illustrative_red`. The latter means the first sampled forecast row meeting this demonstration threshold; it is **not time to heat illness**, a continuous crossing estimate, or safe work allowance. Rows may be coarse and uncertain. The engine itself does not authenticate weather provenance; ingestion must preserve provider, coordinates, fetch time, forecast timestamps, source type (live, cached or synthetic) and freshness. A synthetic fixture must never be silently labeled live.

Open-Meteo is selected as a practical external numerical weather forecast candidate. Its maintained README verifies hourly/global model access and free non-commercial usage without an API key, with data attribution requirements. External numerical weather prediction does not make this project's risk calculation a learned AI model. Air forecasts are not construction-site microclimate. Without radiant heat, wind, validated wet-bulb/globe measurements and instrument placement, no WBGT measurement claim is justified.

An absent forecast leaves the current baseline in force and returns `unavailable`; it does not make stale current measurements fresh. Loss of both sources requires the manual site plan and a visible cautious state. Real offline badge execution and radio behavior remain untested hardware work; browser/server simulation only demonstrates software states.

## What would qualify as a learned model later

A candidate later extension is forecast correction using paired zone measurements and weather-model output, with a held-out site/time split and comparison against the uncorrected weather forecast. Another is sensor anomaly detection validated against known failures. Neither is implemented or needed to demonstrate this transparent baseline. Human physiology prediction requires a separate evidence basis, consent and expert-led evaluation. Synthetic examples cannot establish clinical predictive performance.

Forecast or learned components must not suppress the conservative baseline. Record algorithm/version, inputs, uncertainty and reasons behind each change without collecting unnecessary worker health data.

## Validation and acceptance

The existing unittest suite covers explainable low and high scenarios, monotonic effects of declared workload/PPE, stale boundary and red preservation, malformed inputs, emergency priority, acknowledgement separation, forecast escalation without lowering baseline, sorting, invalid forecast rows and input non-mutation. Run from repository root: `python3 -m unittest discover -s tests -v`.

These tests validate software invariants only. They are not a validation of heat-risk prediction or a field-trial result. Before deployment: verify the selected guidance, consult an occupational-health expert, select a physically appropriate measurement model, calibrate instruments, define exposure/recovery behavior, validate warning performance and perform field/human-factors tests with appropriate approvals.

## Sources and remaining evidence

- NIOSH 2016-106: https://www.cdc.gov/niosh/docs/2016-106/default.html — selected guidance, direct text not verified in this task due to blocked access.
- OSHA heat technical guidance: https://www.osha.gov/heat-exposure/otm — direct text not verified due to blocked access.
- Open-Meteo maintained project README: https://github.com/open-meteo/open-meteo — reviewed 16 November 2026.
- Open-Meteo endpoint documentation: https://open-meteo.com/en/docs — integration details require current direct verification; no live-data success is claimed in this model report.

Submission deliverable: functioning transparent demonstration, reproducible test evidence, clear explanation and limitations. Post-hackathon validation: standards implementation, physiological validity, field prediction accuracy and deployment reliability. Those are distinct claims.
