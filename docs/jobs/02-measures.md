# Job 02 — Measures, evaluation and evidence plan

Exaclim | Submission specification | 16 November 2026

## What this report establishes

The challenge asks for alert lead time, false-alarm rate, adherence to controls, heat-related symptoms/incidents, emergency escalation, compliance and lost work time. Add missed events and system reliability so a favorable alert count cannot hide failures. The prototype may demonstrate how these are recorded using synthetic scenarios; it cannot establish health benefit, clinical prediction accuracy or field reliability.

Keep three evidence categories separate: executed software checks, simulated workflow observations and future field measurements. Missing evidence is “not measured,” never zero. Acknowledge is a receipt event, not proof that someone took a break. A sensor threshold crossing is not a clinical heat-strain event.

## Definitions and denominators

| Measure | Operational definition and denominator | Source and interpretation |
|---|---|---|
| Warning lead time | For each independently adjudicated event, event-onset time minus first relevant delivered warning time within a predeclared lookback window | Paired delivery and event records; report median, range and matched/unmatched counts. Negative values mean warning after onset. No warning is a missed event, not infinite lead time |
| Unnecessary-alert proportion | Alerts adjudicated unnecessary divided by all alerts adjudicated; multiply by 100 | Blinded occupational-health review using a written rubric; report unreviewed count. This is an alert-level proportion, not the statistical false-positive rate among all non-events |
| Statistical false-positive rate, if evaluated | Non-event observation windows with a false positive divided by all independently classified non-event windows | Requires predeclared observation windows and complete reference labels; otherwise do not report this rate |
| Missed-event proportion | Adjudicated events without a relevant prior delivered warning within the lookback window divided by all adjudicated events | Incident review and warning linkage; report uncertain onset/labels separately |
| Control adherence | Actionable alert episodes with a verified recommended action started within the defined response window divided by actionable episodes with adequate follow-up | Worker-controlled confirmation or consented observation; show missing follow-up. Also show coverage across all actionable episodes |
| Symptoms/incidents | Adjudicated or consistently defined reported cases, with category and severity | Report cases per 1,000 exposed worker-hours where denominator quality permits; counts may rise because reporting improves |
| Emergency escalation | Count of help/emergency episodes; time from local trigger to delivered escalation, responder acknowledgement and first assistance | Separate each interval; undelivered or unresolved cases are not assigned zero response time |
| Participation and operational compliance | Consenting wearers divided by eligible workers; valid monitoring hours divided by intended monitoring hours; completed site controls divided by scheduled controls | Report separately. Voluntary nonparticipation is not worker misconduct or a disciplinary ranking |
| Heat-attributable lost work time | Hours classified heat-related under a written protocol, divided by scheduled worker-hours where comparison is needed | Record planned preventive breaks separately from illness-related absence; compare like tasks, staffing and weather |
| Data availability | Valid fresh samples divided by expected samples; valid monitored time divided by scheduled monitored time | Exclude duplicates and replayed readings; report outages and sensor coverage |
| Technical delivery latency | Local event-to-local-display and event-to-gateway-confirmation intervals | Monotonic timing where possible; this measures system speed, not warning lead time before illness |
| Forecast error | Prediction minus matched reference observation at predeclared horizons; summarize MAE and sample count | Compare the same variable, location/height and time interval; grid weather error does not validate personal heat-strain prediction |

The lookback and response windows are protocol settings to agree with the occupational-health reviewer before a pilot. Do not choose them after viewing results. For the simulator, use explicitly labeled scenario windows and avoid presenting their values as medically justified.

## Event counting and clock rules

Count an alert episode once when severity first enters an actionable band or increases materially. Repeated transmissions and acknowledge events belong to the same episode. A later, independently defined recovery followed by renewed risk can begin another episode; document that recovery rule before analysis. Keep emergency episodes separate and link them to ordinary alerts where appropriate.

Prototype boundary tests should cover illustrative index values immediately below/at/above 40 and 70, and sensor ages below/at/above 120 seconds. The current design marks age greater than 120 seconds stale. These are software settings for deterministic testing, not validated occupational action thresholds.

Record event occurrence time, receipt time and processing time separately in UTC, plus source and clock quality. Preserve scenario-relative time for accelerated demonstrations. Never interpret a 20-second accelerated demo as a real 20-minute physiological process. If clocks are unsynchronized, mark interval estimates uncertain rather than subtracting incompatible timestamps.

Use stable synthetic episode IDs for demonstration. Real worker identifiers, symptoms and incident details must remain in the worker/authorized clinical workflow, not the supervisor dashboard. Crew aggregates require minimum-size suppression and protection against repeated-filter differencing. Participation information must not identify workers who decline.

## Minimum event schema

Each technical or synthetic record should include: schema version; event ID; scenario/run ID; source; synthetic flag; event type; occurrence and receive timestamps; source freshness; severity before/after; reason codes; delivery channel and status; acknowledge time if present; resolution time/status if present; and model/configuration version. Log aggregate scope and suppressed status for crew outputs.

Do not store raw diagnosis, GPS trails or free-text worker health details in the generic telemetry log. If future research requires individual linkage, use a separate access-controlled consented dataset and retention protocol. The proposed schema is a specification; the validation report must identify the actual implemented fields.

## Software acceptance matrix

| Case | Assertion that must be tested | Evidence to retain |
|---|---|---|
| Fresh low-risk synthetic input | Valid result with explanations and source age | Unit/integration test |
| Rising illustrative exposure | Deterministic severity transitions at documented demo settings | Boundary tests; no clinical interpretation |
| Emergency at any index | Emergency wins over environmental/model state | Priority test |
| Acknowledge emergency | Emergency latch retained | State-transition test |
| Stale, missing, implausible input | No reassuring green; previous higher severity preserved | Parameterized invalid-input tests |
| Forecast lower than baseline | Output cannot lower the baseline | Conservative-floor test |
| Offline/reconnect | No false delivery confirmation; local warnings remain | Functional scenario |
| Small crew | Counts/individual detail suppressed under policy | Privacy/API test, not just hidden HTML |
| Worker/supervisor separation | Unauthorized individual-data request rejected if accounts exist | Authorization test or explicit no-real-data limitation |
| Restart | Safety state and timestamps handled as documented | Persistence test or documented gap |

Report actual counts of passing, failing and skipped tests with command and run date. “All tests pass” is insufficient without confirming meaningful cases executed. Do not invent results in this specification; attach the implementation validation report after execution.

## Suggested submission evidence bundle

Provide a reproducible command to run tests; saved test output or summary tied to a repository version; fixture descriptions; a screenshot/export of the crew view; alert reason examples; a stale-data and emergency scenario trace; model assumptions; source attribution; and a limitations table. Include a sample synthetic metrics export if implemented, labeled on every page or file.

An example calculation may explain a metric, but must be labeled arithmetic illustration: if four of ten reviewed synthetic alerts are classified unnecessary, the illustrative proportion is 40%. This is not observed performance and should not be used as a pitch result. Prefer actual executed scenario counts where available.

## Future pilot evaluation, not a submission prerequisite

Before enrolling people, obtain the appropriate ethics determination, site permissions, occupational-health reviewer and worker consultation. Predefine eligible participants, tasks, heat conditions, reference measurements, outcome definitions, observation windows and emergency procedures. Participation must be voluntary with an equivalent protective pathway for nonparticipants.

Begin with bench/reference comparison and usability testing. Then use a prospective feasibility pilot to assess monitoring coverage, alert comprehension, response workflow and acceptability. Do not claim a small short pilot can establish reductions in rare severe heat illness. A later effectiveness study needs a justified sample size, comparator, confounder control and independent outcome adjudication.

Analyze workload, weather, clothing, acclimatization and changes in reporting when comparing periods. Describe missingness, withdrawals and unreviewed alerts. Where justified and consented, examine language/task-group differences without publishing reidentifiable small groups. Use intervals and uncertainty appropriate to sample size rather than reporting a single precise percentage as proof.

## Honest submission wording

“The prototype demonstrates heat-risk workflow behavior using synthetic scenarios. Executed software tests assess alert priority, failure handling and aggregation behavior. Clinical thresholds, physical hardware performance and health outcomes have not been validated in the field. The measures and prospective evaluation plan specify how those claims would be assessed before deployment.”

Basis: supplied Climate-Resilient Worker Health challenge and project research brief. This is an evaluation design, not a field-results report.
