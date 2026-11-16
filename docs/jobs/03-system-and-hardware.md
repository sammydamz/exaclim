# Job 03 — System architecture and hardware design

Exaclim · Climate-Resilient Worker Health · 16 November 2026

**Deliverable status:** design complete for a software-led hackathon prototype. The hardware is an engineering proposal, not a built, certified or field-tested product. This document specifies a bench prototype and the evidence required before deployment.

## 1. Design decision

Use two devices: a fixed environmental station and a worker alert badge. The station supplies zone conditions; the badge computes an illustrative exposure index locally and provides visible, audible and tactile alerts. A gateway supplies forecasts and uploads crew aggregates to the planning dashboard. Badge alerts must not depend on Internet access or a supervisor opening the dashboard.

For the submission, the working software simulates these devices and their failures. Physical procurement is not on the critical path. A later bench kit has one station and two badges; this is enough to test communication and behavior, not enough to validate an occupational safety product.

Do not call the index a measured personal heat dose or a medically validated safe work allowance. The badge measures neither core body temperature nor physiological strain.

## 2. System diagram

The intended data flow is:

**Environmental station → authenticated zone readings over BLE → worker badge → local alert outputs.**

**Weather forecast service → gateway → forecast cache → crew planning dashboard.**

**Badge → crew aggregation at gateway → supervisor crew view**, only if the worker opted in and the cohort meets the minimum-size rule.

**Help button → local emergency outputs immediately → gateway emergency channel when reachable.** A lost gateway must not suppress local outputs. The badge cannot promise remote rescue delivery when its radio path is unavailable; the worker must also use the site's established emergency procedure.

| Layer | Responsibility | Failure boundary |
|---|---|---|
| Station | Sample air temperature/humidity, validate sensor status, publish timestamped data | A fresh radio packet is not proof that the sensor sample is fresh |
| Badge | Context, local index, alert priority, acknowledgement, help state, local event ring buffer | Acknowledgement records receipt; it does not prove a rest break occurred |
| Gateway | Verify data, distribute forecasts, collect consented contributions, form aggregates | Internet failure must not disable local processing |
| Server | Serve aggregate crew planning and synthetic demo scenarios | No real worker deployment without authentication and server-side authorization |
| Dashboard | Display cohort risk, source freshness and planning suggestions | No individual exposure drilldown in supervisor role |

## 3. Bench hardware shortlist

| Part | Selected direction | Why | Qualification still required |
|---|---|---|---|
| Badge controller | Adafruit Feather nRF52840 Express or equivalent supported nRF52840 board | Maintained Arduino BSP; BLE; readily replaceable development board | Verify exact board revision, pinout, battery connection and delivered stock |
| Station controller | Same board family for bench consistency | Reduces separate toolchains and communication differences | Station sample timing and radio duty-cycle measurements |
| Air temperature/humidity | SHT4x breakout | Maintained I2C library; environmental telemetry input | Exact variant/specification, calibration, radiation shield and placement |
| Motion sensor | Optional LIS3DH breakout | Maintained I2C/SPI library | No validated conversion from wrist/arm motion to metabolic workload |
| Haptic output | DRV2605L breakout and compatible ERM/LRA actuator | Maintained I2C driver library; dedicated actuator driver | Motor type, voltage, current and waveform configuration |
| Visible output | Three separate high-visibility LEDs with resistors | Clear status even without a phone | Sunlight visibility, current and accessible non-color cues |
| Sound | Suitable buzzer with transistor/MOSFET driver if required | Alert channel in addition to light/vibration | Site-noise audibility and hearing-protection compatibility |
| Inputs | Two large sealed momentary buttons | Separate acknowledge and help actions | Glove usability, accidental activation and sealing |
| Power | Protected rechargeable battery compatible with board charger | Portable bench badge | Connector polarity, charge limits, protection and thermal review |
| Enclosure | Prototype clip/armband enclosure | Keeps device away from modifying certified PPE | Water/dust ingress, drop, snag, comfort and thermal testing |

Use development boards for the hackathon design. A custom PCB adds schedule and verification risk without improving the software demonstration. ESP32 remains an alternative if the team already owns suitable boards; do not mix wireless protocols in the first bench build.

## 4. Measurement limits and zone placement

A body-worn air sensor can be affected by body heat, clothing, direct solar heating and enclosure thermal lag. Keep the principal environmental sensor at a representative work zone in a suitable ventilated radiation shield; record its height, shade/sun conditions and distance from unusual heat sources. Select final placement with an occupational hygienist rather than assuming a universal mounting position.

Air temperature and humidity alone are not occupational WBGT. A WBGT assessment needs appropriate instrumentation and accounting for radiant heat and other environmental factors. Use a calibrated/reference WBGT instrument for comparison in a later bench/site study. Do not label an SHT4x-derived estimate as measured WBGT. Neither forecast grid weather nor one station guarantees that every worker experiences the same microclimate.

Workload is declared from the task category in the prototype. Motion data is optional and experimental; it must never downgrade a declared heavy-work category because a worker is relatively still.

## 5. Functional wiring plan

This is a block-level wiring plan, not a fabrication-ready electrical schematic. Resolve exact GPIO assignments and electrical ratings against the chosen board revision before assembly.

| Connection | Rule |
|---|---|
| SHT4x VCC/GND/SDA/SCL | Use the breakout's documented supply range; 3.3 V logic where compatible; common ground |
| LIS3DH SDA/SCL | Share I2C only after checking addresses and total pull-up loading |
| DRV2605L SDA/SCL and motor terminals | Set correct actuator mode; connect motor to driver, not directly to a GPIO |
| LED channels | One resistor per LED; calculate from supply, forward voltage and target current; use driver stages if GPIO limits require |
| Buzzer | Check load against GPIO limits; use switching stage and suppression appropriate to the chosen load |
| Acknowledge/help buttons | Separate GPIOs, defined pulls, debouncing; no floating inputs |
| Battery | Protected pack, correct connector polarity and charger match; no exposed terminals |
| USB | Bench flashing and charging; strain relief and accessible disconnect |

Disconnect power before rewiring. Do not charge inside an untested sealed enclosure exposed to heat. Do not claim intrinsic safety or use the prototype in explosive atmospheres. A prototype clip must not require drilling a hard hat or altering other certified PPE.

## 6. Communication contract

Proposed station sampling interval: 10 seconds; badge receive expectation: at least every 30 seconds. Proposed stale threshold: 120 seconds from sample time, with monotonic-age handling locally. These are engineering demo defaults, not occupational thresholds; validate power, reliability and response needs before field use.

The following is a logical JSON contract. It is **not** a packet claimed to fit in a legacy BLE advertisement. Encode a compact version or transfer over authenticated GATT; measure actual payload size and fragmentation. BLE radio support alone does not establish application authentication.

Station fields: `schema_version`, `station_id`, `zone_id`, `boot_id`, `sequence`, `sampled_at`, `sample_age_seconds`, `temperature_c`, `relative_humidity_pct`, `sensor_status`, `battery_status`, `key_id`, and an authenticated integrity tag in the transport implementation.

Badge event fields: `schema_version`, rotating `badge_session_id`, `event_id`, `sequence`, `occurred_at` or monotonic elapsed time, `event_type`, `alert_level`, `reason_codes`, `source_quality`, `acknowledged`, and `consent_scope`. Avoid names, diagnoses, continuous GPS and raw motion streams. Do not send detailed individual exposure histories into a supervisor-accessible store.

Validation rules: reject malformed values, impossible humidity, duplicate/replayed sequence values, stale sample times and unknown schemas; handle station reboot with a new authenticated boot identifier. Record a reason code for rejection and enter the cautious fallback. A malicious future timestamp must not keep a sample fresh forever. Establish age locally using receive time plus validated sample age when no trusted wall clock is available.

Provision devices using a documented pairing/key process. Use authenticated encryption for the chosen channel and separate zone-data permissions from emergency handling. Key rotation, revocation and secure firmware updates are deployment requirements; this software submission does not demonstrate them on embedded hardware.

## 7. Alert and recovery behavior

The local risk engine evaluates at least once per update and on every help/input event. Emergency has highest priority and remains latched until explicit resolution. Acknowledge may silence a bounded sound pattern according to the alert specification but never clear an emergency or reset accumulated exposure. Restart must not silently erase an unresolved emergency or stale-data condition.

If a station becomes stale, make data quality visible and maintain at least the last elevated state or cautious warning, whichever is more protective. Forecast estimates can support planning but must be labeled estimates. If no usable environment source exists, show unknown/cautious, use the site's manual checklist/rest procedure and instruct the user to seek a measured assessment. Do not silently convert unknown to green.

Show a periodic alive indication distinct from an active warning. Distinguish low battery and sensor failure from heat-risk severity, so a maintenance fault is not mistaken for a normal work signal. A powered-off badge cannot alert; use pre-shift checks, replacement devices and manual/site signals as independent safeguards.

## 8. Privacy boundaries

The supervisor sees crew aggregates only, with a proposed minimum of five participating workers and fixed cohorts/time windows to reduce differencing. Suppress small groups; do not expose individual identities via logs, exports, APIs or error messages. The bench kit has two physical badges, so a live two-person supervisor aggregate should remain suppressed; a synthetic cohort can demonstrate the dashboard.

The help function involves a tension: assistance needs a discoverable location/person while routine privacy limits identification. Keep a separate explicit emergency workflow, disclose the limited emergency information shared, and never treat it as permission for routine individual tracking. In the software demo use synthetic identity and show local escalation separately from remote delivery status.

Worker detailed data stays local by default; opt-in sharing and a no-penalty alternative must be practical. Hardware ownership does not establish ownership of worker information. Ghana Act 843 responsibilities, retention and controller/processor roles require legal and worker review before collecting real data.

## 9. Verification plan

| Stage | Test | Evidence and acceptance basis |
|---|---|---|
| Software submission | Emergency priority, stale/future/invalid input, offline fallback, acknowledgement, restart and aggregate suppression | Reproducible automated results and synthetic functional walkthrough |
| Bench electronics | Outputs, button debounce, battery protection, charge behavior, disconnect and brownout | Measured results tied to exact board/battery revisions; no uncontrolled resets hiding alerts |
| Measurement | Compare environmental telemetry against reference instruments across operating conditions | Error/freshness analysis; qualified reviewer sets acceptable criteria |
| Radio | Packet loss, interference, blocked path, multiple stations and moving badges | Measured delivery/age distributions and correctly triggered fallback |
| Power | Full representative operating cycle, repeated alert bursts, low battery and restart | Recorded current/time trace and runtime; retain reserve margin for warnings |
| Human factors | Glove buttons, sunlight, noise, vibration, accessibility and PPE | Approved test protocol and worker feedback before field use |
| Environment | Heat, water/dust, drops and enclosure checks | Appropriate qualified test evidence before any rating claim |

No field thresholds, battery-life specification, IP rating or communication range is established by this report.

## 10. Power calculation and test record

Estimate runtime as `usable_capacity_mAh / measured_average_current_mA`. Usable capacity must account for cell condition, temperature, discharge limits and conversion losses. Do not use nominal capacity alone as measured usable capacity.

Illustrative arithmetic only: a nominal 500 mAh pack with a planning usable fraction of 0.70 yields 350 mAh. At 15 mA measured average the arithmetic would be about 23 hours; at 40 mA it would be about 8.8 hours. Neither current nor usable fraction has been measured for our hardware, so these numbers are sensitivity examples, not runtime claims.

Log board revision, firmware commit, battery model/age, charge state, ambient conditions, radio duty cycle, LED/buzzer/vibration patterns, measured average/peak current, low-battery timing and actual shutdown time. Repeat realistic and worst-case alert scenarios. Set a full-shift requirement only after the pilot shift length and safe reserve are agreed.

## 11. Sources and unresolved evidence

Official maintainer repositories accessed 16 November 2026:

- [Adafruit nRF52 Arduino BSP](https://github.com/adafruit/Adafruit_nRF52_Arduino): explicitly supports Feather nRF52840 Express and documents installation.
- [Adafruit SHT4X](https://github.com/adafruit/Adafruit_SHT4X): temperature/humidity I2C library.
- [Adafruit LIS3DH](https://github.com/adafruit/Adafruit_LIS3DH): I2C/SPI accelerometer library.
- [Adafruit DRV2605 library](https://github.com/adafruit/Adafruit_DRV2605_Library): I2C haptic driver support.

A direct request to the Feather product listing returned proxy HTTP 403. Current stock, price, shipping, dimensional drawings and electrical specifications were not verified from the listing. Obtain the actual manufacturer datasheets and board schematics before assembly. Verified library support is not evidence that a board is available locally or medically appropriate.
