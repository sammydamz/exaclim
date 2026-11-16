# Exaclim — Executive Summary and Pilot Plan

Job 05 • Submission planning report • 16 November 2026

## Executive summary

Exaclim is a worker-first heat-exposure warning and crew-planning concept for construction sites in Ghana. It combines work-zone environmental information, declared task intensity and shift context to explain rising heat risk and support earlier action. A wearable badge is intended to deliver visible, audible and tactile alerts without requiring every worker to own a smartphone. A crew dashboard is intended to help supervisors plan rest, task timing and rotation while keeping detailed individual information outside the supervisor view.

The hackathon scope is a working software prototype with clearly labeled synthetic scenarios and simulated hardware. It demonstrates graded alerts, forward planning, an emergency help control and cautious behavior when sensor or network data becomes unavailable. Its risk calculation is an illustrative exposure index. It does not measure core body temperature, diagnose heat illness or establish an individual's safe remaining work time. Forecast integration, if enabled, supplies weather-model information; it is not proof of a trained or clinically validated personal heat-strain predictor.

The design separates a transparent baseline calculation from future forecast correction and personalization research. A forecast or later machine-learning component may increase caution but cannot weaken the baseline alert. Worker-reported symptoms or a help request override every calculated state. Acknowledging an alert confirms receipt; it does not clear an emergency or imply that conditions have become safe.

The first intended field setting is one construction site. The next phase would extend to commercial farms with a comparable worksite and support structure. Smallholder and informal-worker deployment would require a different ownership, maintenance, communication and emergency-support model and is outside the first pilot.

The submission will provide software evidence and an implementation path, rather than claim clinical effectiveness. Before people rely on the system, the team must obtain occupational-health review, appropriate ethics and site permissions, worker consultation, reference-instrument validation and physical-device testing. No partner, clinician, ethics approval, field outcome or supplier endorsement is represented as secured.

## Problem and intended users

Outdoor work changes throughout the day. Sun exposure, humidity, wind, task intensity, clothing and acclimatization can change the risk even when a general weather forecast stays the same. A worker may have no smartphone, limited connectivity or difficulty noticing a phone alert in a noisy worksite. A supervisor needs actionable group information without turning health prevention into individual surveillance.

The initial design serves three roles:

- Workers receive understandable alerts and can acknowledge receipt or request help. The personal display must remain readable without a supervisor account.
- Supervisors receive group-level conditions and planning prompts, not individual clinical histories, worker rankings or productivity scores.
- Designated site responders use the existing emergency process. Any later occupational-health sharing is separately governed and worker-authorized where appropriate.

The initial geographic scenario is an Accra-area construction site. English is the prototype language. Twi is a proposed first additional language, subject to actual workers' language needs and fluent-speaker review. The team must not claim reviewed multilingual deployment while translations remain pending.

## Challenge fit and submission boundaries

The Climate-Resilient Worker Health challenge asks for dynamic assessment, graded warnings, worker-first governance, field readiness, supervisor decision support and safety/productivity measures. Optional physiological sensing is not required for this concept. The proposed environment-and-task approach avoids collecting body measurements in the first release.

The submission date is 20 November 2026. The team should package artifacts according to its submission portal. The following boundary applies regardless of presentation quality:

| Submission evidence | Later deployment evidence |
|---|---|
| Running synthetic scenarios with expected and actual software results | Outcomes measured in consenting workers under an approved protocol |
| Software tests of emergency, stale-data and offline state transitions | Instrumented radio, battery, weather-resistance and human-factors trials |
| Documented assumptions, model limitations and data sources | Expert-approved operating thresholds and validated measurement placement |
| Privacy behavior demonstrated with synthetic data | Real identity/access management, security review and governance agreements |
| Hardware diagram, shortlist and cost assumptions | Purchased/assembled hardware, calibration and verified supplier costs |

A simulated sensor outage demonstrates software behavior when data is absent. It does not establish physical offline reliability, successful radio operation on a site or a full-shift battery life. The final submission must distinguish implemented, simulated, specified and deferred features.

## Delivery and accountability

Roles below are proposed responsibilities, not claims that named people have accepted them. One person may hold more than one role, but safety sign-off should receive independent review.

| Role | Responsibility | Required evidence |
|---|---|---|
| Product/submission lead | Scope, artifact consistency and final claims | Final artifact checklist and claims review |
| Software lead | Reproducibility, UI and state behavior | Versioned code, setup instructions and test output |
| Embedded/hardware lead | Component selection and bench validation | Wiring record, measurement logs and safety checks |
| Occupational-health reviewer | Assessment approach, alert actions and escalation boundaries | Written review before any worker-facing reliance |
| Worker representative | Language, voluntariness, usability and misuse concerns | Consultation notes and accessible worker information |
| Site safety lead | Existing controls, response capacity and incident procedure | Site-specific emergency and heat-control plan |
| Data-governance lead | Lawful processing, access, retention and response | Data map, agreements and review record |

The current team can complete software and planning artifacts before submission. Named site, clinical, worker and ethics contacts remain external dependencies for a human pilot; assigning a role in a document does not fill it.

## Phased pilot and go/no-go gates

The proposed durations are planning assumptions after submission, not booked dates or commitments. Progress depends on the exit gates, not elapsed time. Select the actual field period using local heat conditions and site readiness; do not promise a meaningful hot-weather evaluation from a short calendar window.

### Phase 0 — Submission prototype

Scope: synthetic workers, scenario weather, worker badge simulation, group dashboard, deterministic baseline and documented forecast handling. Do not recruit workers or expose real health data to the software.

Exit gate: a reviewer can start the project from its instructions, execute its scenario/test suite and distinguish software evidence from simulated hardware. All emergency and missing-data cases behave as specified. The presentation contains no unsupported health, battery, pricing or calibration claims. Prototype completion must be confirmed against the actual implementation and test report; this planning document does not certify it.

### Phase 1 — Non-human bench qualification

Indicative effort: two to four weeks after component arrival and reviewer availability, revised once hardware is selected.

Build one station and two badges, keeping device power and mechanical safety under qualified review. Compare environmental readings with an appropriate calibrated reference instrument. A temperature/humidity breakout alone is not a WBGT instrument. Test fresh, delayed, missing, implausible and replayed data. Exercise restarts, clock handling, battery depletion, alert drivers and emergency resolution.

Exit gate: repeatable bench records establish whether the selected hardware meets its documented engineering requirements. Calibrations, measurement uncertainty and failure handling are reviewed. Any full-shift battery, ingress or operating-temperature statement is supported by a defined test; an enclosure concept alone cannot establish an IP rating. No human exposure experiment is needed for this phase.

### Phase 2 — Governance and site preparation

Run alongside bench work. Seek one construction partner; no partner is currently confirmed. Establish a site safety lead, worker representatives and an occupational-health reviewer. Obtain the applicable institutional ethics determination and approvals before collecting human research data. Determine whether any regulatory authorization or device classification applies; do not assume a hackathon label removes obligations.

Map existing heat controls, water/shade access, work schedules and emergency resources. Agree how workers can decline or stop participation without employment consequences. Review language, literacy, disability access, PPE compatibility and local emergency instructions. Finalize what is measured, by whom, for what purpose and for how long.

Exit gate: signed site and data agreements, appropriate ethics determination, reviewed worker information, accessible opt-out route, a responding site safety service and an approved protocol. Consent alone does not resolve an employment power imbalance or replace a lawful processing basis.

### Phase 3 — Supervised feasibility study

Planning proposal: four to six weeks of observation at one site, adjusted for the actual heat season and agreed protocol. Determine recruitment and sample size with a qualified evaluator; do not treat a small convenience sample as powered to detect reduced heat illness.

Begin in shadow mode: record how the system would behave while existing site controls and human safety decisions remain authoritative. Any move to worker-facing alerts requires explicit safety review. Never withhold an established heat control, delay an emergency response or increase heat exposure for evaluation.

Evaluate data availability, measurement agreement, alert comprehension, missed/duplicate delivery, time to acknowledge, support burden, acceptability and operational feasibility. Record exposure denominators and loss to follow-up. Real symptoms/incidents require the pre-agreed reporting and independent review process. All suspected health events receive the site's normal care pathway regardless of study participation.

Exit gate: feasibility findings and safety review identify what works, what fails and which changes are necessary. No transition to broader use follows automatically from a demonstration or a positive satisfaction survey.

### Phase 4 — Reviewed effectiveness study and controlled expansion

Only after feasibility, define a sufficiently powered evaluation with a documented comparison approach, relevant confounders and independent clinical input. A simple before/after comparison cannot by itself separate weather, staffing, task changes and reporting effects from the intervention.

Expansion to commercial farms requires new site characterization, language/access review and emergency arrangements. Smallholder use is a separate discovery project, not an automatic extension of the construction pilot.

## Stop conditions and incident handling

Suspend experimental reliance when a component can give reassuring output with missing/invalid inputs, emergency help cannot reach an available human responder, battery or charging presents a hazard, a device compromises PPE, or an unresolved privacy/security incident exposes worker information. Existing site safety procedures remain active during suspension.

The site safety lead handles immediate care and controls. The technical lead preserves relevant engineering evidence without unnecessary identifiers. The governance lead applies the agreed incident and legal response process. Restart requires documented correction and appropriate independent review; worker acknowledgement alone cannot authorize it.

## Worker-first governance and Act 843 review

Ghana's Data Protection Act, 2012 (Act 843) is the proposed local legal review starting point. This report is a governance design, not a legal determination. Verify applicable rules with qualified advice and the relevant regulator before real processing, including controller obligations, any registration requirements, cross-border hosting and treatment of health-related information. Do not claim that a particular retention period, group size or consent form automatically establishes compliance.

For the demonstration, use synthetic identities and no real health or location histories. For a later pilot, collect only the variables required by an approved purpose. Avoid medical diagnoses, continuous GPS trails and employment performance scoring. Detailed personal history should remain worker-local by default, with tightly governed sharing if genuinely needed.

The proposed minimum visible supervisor group is five active consenting participants. This is a product rule, not a legal safe harbor. Suppress small groups and prevent repeated filtering or time-window changes from revealing an individual. Group-level summaries can still be sensitive when the site context makes workers identifiable. The backend must enforce access restrictions before real deployment; hiding UI fields is insufficient.

Employer ownership of a badge does not grant unrestricted rights to worker information. Badge-return procedures must remove prior worker data before reassignment. The real retention schedule must identify each data class, purpose, deletion mechanism, exceptional preservation requirements and responsible party. Define the shortest justified schedule with the reviewer; no statutory number is asserted here.

Participation information must explain what is collected, visible to whom, why it is needed and how to stop participation. Provide a practical no-penalty alternative to wearing a badge. Prohibit disciplinary use and unrelated employment decisions through access controls, contracts, auditing and an accessible complaint route. Worker involvement is a continuing governance activity, not one consent checkbox.

## Competitive position and evidence status

The proposed position is the combination of worker-local alerts, cautious failure behavior, explainable calculations and restricted crew planning. These are design goals; the team has not established that they are unique. Do not describe competitors as phone-only, privacy-poor or incapable of offline operation without current official evidence.

The initial research verified Open-Meteo's maintained project README and Adafruit's SHT4X and LIS3DH libraries. These establish relevant forecast and component interfaces, not product differentiation or occupational safety effectiveness. Direct standards, regulator and commercial product pages were blocked during the initial research pass.

| Candidate comparison | Question to verify from current official documentation | Status |
|---|---|---|
| OSHA-NIOSH Heat Safety Tool | How does its forecast/index guidance, task context and alert delivery compare? | Current feature comparison pending |
| Kestrel WBGT instruments | Which models provide appropriate reference measurements and site workflows? | Current model/specification comparison pending |
| Kenzen | Which sensing, worker alerts and deployment/governance options are documented? | Current product comparison pending |
| SlateSafety | Which device, connectivity, alert and access-control options are documented? | Current product comparison pending |

Until those checks are complete, use a problem-and-design comparison rather than a superiority claim. Supplier logos, customer names and certification claims must not imply endorsement.

## Adoption and sustainability hypotheses

The first potential adopter is a construction operator able to maintain reference measurements, charge/inspect badges and provide real rest/cooling and emergency support. A dashboard without the ability to act on alerts does not solve the occupational problem.

A future service could bundle hardware maintenance, calibration management, training and privacy-preserving planning software. This is a business hypothesis, not validated willingness to pay. Validate purchasing authority, worker trust, maintenance responsibility, recurring costs and alternatives through interviews. Quote bench-kit costs separately from per-worker deployment and recurring service costs. Avoid using purported productivity benefits as a reason to overrule worker protection.

## Claims and handover checklist

Before submission, confirm that the executive summary matches the actual code and latest test output. Replace future-tense feature claims with implemented claims only when demonstrated. Keep the following distinctions visible in every artifact:

- Software behavior can be tested on synthetic scenarios; clinical effectiveness remains unproven.
- A forecast is a forecast, and an illustrative index is not a validated personal heat-dose limit.
- A component shortlist is not an assembled, calibrated or certified wearable.
- An intended pilot is not a secured partner or an approved human study.
- Defined metrics are not measured field outcomes.
- A concept image or simulated badge is not footage of a tested device.

The next production handover is the demo: show the actual prototype using its tested scenarios, identify all simulated inputs and hardware, and explain the post-hackathon validation gates. Demo recording and presentation production are outside this report's completed scope.

## Reference and provenance note

Challenge requirements and the submission date are drawn from the challenge material supplied by the team. The design and research status are aligned with the repository's research-and-decisions report. The NIOSH 2016 heat criteria, ISO measurement/model standards and Act 843 are review starting points; this document does not assert that their full texts have been reviewed or that the design complies with them.

Verified technical source candidates: [Open-Meteo project](https://github.com/open-meteo/open-meteo), [Adafruit SHT4X library](https://github.com/adafruit/Adafruit_SHT4X) and [Adafruit LIS3DH library](https://github.com/adafruit/Adafruit_LIS3DH). These are not evidence of worker outcomes.
