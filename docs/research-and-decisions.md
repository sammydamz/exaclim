# Exaclim: research and proposed decisions

Prepared 16 November 2026. This is a decision brief, not evidence of a validated safety device.

## Evidence and submission constraints

This brief draws on the team's proposal and the **Climate-Resilient Worker Health** challenge requirements to guide research, scope decisions and development.

The event PDF states: working prototype and technical documentation, assumptions and limitations due 20 November 2026; registration closed 10 November; teams up to five; worldwide participation; no mandatory model, platform or device. The submission date is 20 November 2026. Check the submission portal for the final artifact checklist when packaging the entry.

The challenge sets out six requirements: dynamic risk assessment; graded multilingual warnings; worker-first governance; field readiness and failure fallback; supervisor decision support; and safety/productivity measures. Physiological sensing is optional. Crew-level assessment is permitted.

## Recommended scope to settle

Build a working software prototype for one construction-site scenario in Ghana, with clearly labeled synthetic workers and weather scenarios. Keep agriculture as phase two, initially commercial farms; do not claim smallholder coverage through an employer dashboard.

Keep the heat-dosimeter product framing as an analogy, but label the prototype output **illustrative exposure index**. It is not absorbed heat, core temperature, a diagnosis, or a validated personal safety allowance. Avoid claiming that a remaining budget means continued work is safe.

Deliver a crew planning dashboard, separate worker badge simulator, scenario controls, a transparent risk engine, forecast integration with explicit source/freshness, and reproducible tests. A concept render/video supports the working demonstration; it cannot replace it.

Do not require physical hardware procurement for submission. Deliver a schematic, component shortlist, communication contract, enclosure concept, and bench/pilot validation plan. Firmware and real-device behavior must be labeled untested until exercised on hardware.

## Challenge-to-evidence map

| Requirement | Prototype demonstration | Post-hackathon validation before field deployment |
|---|---|---|
| Dynamic risk | Environment + declared work intensity, clothing, shift context and acclimatization; explain each contributing factor | Expert-approved model and site measurements |
| Graded warnings | Green, amber, red and emergency states; words/icons alongside colors; acknowledge and help controls | Human-factors testing in noise, sunlight and gloves |
| Governance | Crew aggregates only; minimum crew size; no individual drilldown; synthetic data only | Legal review, worker consultation and access-control audit |
| Field readiness | Offline simulation, stale sensor, lost forecast, restart and emergency scenarios | Heat, dust, water, battery, radio and PPE testing |
| Decision support | Forecast risk windows and conservative rotation/break suggestions | Supervisor usability and expert-reviewed schedules |
| Measures | Definitions and simulated event log, separated from real outcomes | Prospective pilot with adjudication and reporting protocol |

## What is needed for submission versus a later pilot

The post-hackathon validation column above describes evidence needed before real-world deployment. It is not an unfinished hackathon submission checklist. This distinction is our interpretation of the supplied challenge material; the final event rules and submission portal govern the entry.

For submission, demonstrate a working software prototype using clearly labeled realistic simulated scenarios. Show graded alerts, emergency escalation, sensor/network failure fallback, crew planning and privacy behavior. Include reproducible test results, model sources and assumptions, architecture, hardware feasibility, and explicit limitations. Define the requested safety and productivity measures without inventing field results. Any incomplete feature must be identified honestly.

Before submission, verify the occupational guidance used in calculations, review hardware availability and indicative costs, check competitor claims, and check the portal's required artifacts. We do not need a trained personal heat-strain model to demonstrate this scope; explain exactly which forecasting and risk calculations are implemented.

For a later pilot, obtain expert review of thresholds, appropriate ethics/site approvals, worker consultation and deployment agreements. Validate measurements against reference equipment and test battery life, radio range, heat, dust, water, PPE compatibility and usability. Establish real-world warning lead time, false-alarm rates and health outcomes through an appropriate evaluation. These are future validation activities unless the entry claims they have already been achieved or the final event rules specifically require them.

A software simulation demonstrates system behavior, not clinical effectiveness or field-tested hardware reliability. Do not claim prevention of heat illness, certification or measured field performance from simulated results.

## Model and measurement decisions

Select NIOSH's 2016 *Criteria for a Recommended Standard: Occupational Exposure to Heat and Hot Environments* as the proposed primary guidance, pending direct verification and occupational-health review. Consider ISO 7243 for WBGT measurement and ISO 7933 for a later heat-strain model; do not claim implementation or compliance without reviewing the applicable material. NIOSH is technical guidance, not automatically Ghanaian law.

Air temperature and relative humidity are useful inputs but do not directly measure occupational WBGT. Outdoor assessment must consider radiant heat, air movement and appropriate wet-bulb/globe instrumentation. A cheap humidity breakout is not a substitute for a validated WBGT instrument. A motion sensor also does not reliably establish metabolic workload; use declared task categories first, and treat motion as an experimental supporting signal.

Use an externally supplied numerical weather forecast rather than train a weather model. Open-Meteo is a practical candidate: its maintained README describes global hourly forecasts, no API key for non-commercial access, and attribution requirements. Forecast grid weather is not site microclimate. Preserve source, issue/fetch time, coordinates and stale-data handling. Do not label weather-service integration as a proprietary trained AI model.

First release: transparent deterministic risk calculations and scenario-based look-ahead. A future learned local forecast correction or sensor anomaly model requires real observations, held-out evaluation and documented training data. Synthetic training alone cannot demonstrate clinical prediction. Predicted time to an illustrative threshold is not observed warning lead time before heat strain.

Enforce invariants: forecast/model outputs cannot reduce the conservative baseline; help/symptom reporting always escalates; acknowledgement never clears an emergency; missing or implausible data never produces a reassuring green state; emergencies remain latched until an explicit authorized resolution. Do not infer symptoms from index values.

## Hardware shortlist and design choices

| Component | Recommended direction | Qualification needed |
|---|---|---|
| Zone measurement | Calibrated WBGT instrument as reference; SHT4x-based station only as an environmental telemetry experiment | Compare against reference across shade/sun, airflow and mounting conditions |
| Badge controller | BLE-capable nRF52840 development board; ESP32 alternative if already owned | Final board choice, local availability and measured power |
| Motion | Optional LIS3DH breakout over I2C | Validate motion interpretation; no physiological claims |
| Alerts | Distinct LEDs, buzzer, vibration motor with suitable driver, two large buttons | Visibility, audibility, accessibility and glove trials |
| Communications | Zone BLE broadcast, badge-local state, optional gateway uplink | Range/site interference, authentication, replay protection and stale timestamps |
| Power | Protected rechargeable battery and compatible charger in documented enclosure | Runtime measurement, thermal and charging safety; no full-shift claim yet |
| Mounting | Clip/armband concept; do not drill or alter certified PPE | Worker/PPE review, snag and comfort assessment |

No supplier prices or quotes have been verified. Do not publish a fabricated hardware total, IP rating, battery life or calibration accuracy. Obtain quotes including shipping, Ghana import costs, enclosure, calibration/reference rental, spares and assembly. Treat a one-station/two-badge bench kit separately from the multi-zone pilot budget.

## Privacy, language and pilot proposals

Use English for the initial working UI and select Twi as the proposed first Ghanaian language for an Accra-area construction scenario, subject to actual workers' preference. Obtain fluent-speaker review before claiming translation readiness. Do not synthesize unreviewed medical/emergency voice instructions as if validated.

Proposed supervisor aggregation minimum: five active consenting workers, with suppression below that count. This is a design choice, not a legal safe harbor. Prevent differencing across filters/time windows. A frontend hidden panel is not enforced authorization; implement worker/supervisor separation on the server before handling real people.

Keep detailed exposure history local to the worker by default, with no cloud upload in the demonstration. Employer ownership of hardware must not imply ownership of worker information. Do not collect GPS trails, diagnosis or disciplinary scores. Set actual retention and controller/processor responsibilities through Ghana Act 843 review and worker consultation; do not promise a made-up statutory retention period. Consent must include a practical no-penalty alternative.

No pilot partner, occupational-health expert or ethics approval is confirmed. These remain human dependencies. Start with non-human bench/simulation testing; obtain the appropriate institutional ethics determination and site/worker agreements before a human pilot. Never invent partner endorsements.

## Evaluation plan

Test emergency priority, acknowledgement behavior, stale/invalid measurements, offline operation, restart persistence, conservative model floor, aggregation suppression and forecast provenance. Show actual test results with counts. Label all scenario outcomes synthetic.

For a future pilot define: lead time from delivered warning to independently defined/adjudicated event; unnecessary alerts divided by adjudicated alerts; missed events divided by adjudicated events; control adherence among actionable alerts; symptoms/incidents with exposure denominators; emergency acknowledgement and response intervals; agreed compliance measures that do not penalize workers; and heat-attributable lost hours with a documented comparator. Do not infer real-world false-alarm rates or health benefit from the simulator.

## Research ledger

Accessed 16 November 2026:

- Verified: [Open-Meteo maintained README](https://github.com/open-meteo/open-meteo). Forecast access, model sources, non-commercial access and attribution. Source-code AGPL and weather-data CC BY terms are distinct; review deployment terms before commercialization.
- Verified: [Adafruit SHT4X library](https://github.com/adafruit/Adafruit_SHT4X). Temperature/humidity interface over I2C; no WBGT validation established.
- Verified: [Adafruit LIS3DH library](https://github.com/adafruit/Adafruit_LIS3DH). Accelerometer interfaces over I2C/SPI; no metabolic-workload accuracy established.
- Verified: [Zephyr project README](https://github.com/zephyrproject-rtos/zephyr). Possible future embedded platform, not required for the software demo.
- Pending direct access: [NIOSH 2016-106](https://www.cdc.gov/niosh/docs/2016-106/default.html), [OSHA heat technical guidance](https://www.osha.gov/heat-exposure/otm), [Open-Meteo API documentation](https://open-meteo.com/en/docs), supplier listings, Ghana regulator guidance and competitor documentation. HTTPS proxy returned 403 for attempted NIOSH, OSHA, Open-Meteo, Adafruit, Sensirion and hackathon-page requests. This is an access limitation, not evidence about their contents.

The draft's October 2026 ILO Ghana statistic remains unverified; omit it from the pitch until the original publication is checked. Candidate competitor research: OSHA-NIOSH Heat Safety Tool, Kestrel WBGT instruments, Kenzen and SlateSafety. Do not claim our features are unique or competitors lack them until their current official documentation is reviewed.

## Submission sequence

1. Package the entry for the 20 November 2026 submission date using the portal's required artifacts.
2. Settle this proposed scope and verify occupational guidance, hardware options and competitor facts once research access is available.
3. Build and test the working software, with synthetic fixtures and explicit limitations.
4. Produce consistent hardware renders, BOM status, architecture, model card, governance brief and pilot plan.
5. Record an actual software walkthrough; label simulated hardware and generated concept imagery. Package links, reproducible instructions and honest test evidence per portal requirements.
