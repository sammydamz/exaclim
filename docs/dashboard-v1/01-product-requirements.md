# Exaclim Supervisor Dashboard — Product Requirements

Version 1.0 · 19 November 2026 · Implementation specification for review

## 1. Purpose, authority and status

Help a supervisor plan today and tomorrow around heat, monitor crews, and respond to worker help calls. The core screen has exactly three information areas: heat forecast, crew status, and suggested breaks/rotation. A priority emergency banner and essential login/setup flows support those areas; they are not additional analytics modules.

Source: the user's two-page `Exaclim_Dashboard_Requirements.pdf`, version 1 draft. Original requirement IDs D1–D15, P1–P3, S1–S3 and U1–U3 are retained throughout the delivery pack. Prior user direction supplies the Exaclim name, installed UI SDK foundation, and Deel screenshot references. This PRD expands the source into implementable behavior; additions and unresolved choices are identified as proposals. The source remains a draft; proposed implementation details and unresolved release decisions are identified explicitly.

This is a new target specification, not a claim that the existing prototype already complies. No product code has been changed to implement this specification. Technical targets below are proposed acceptance targets, not observed performance or occupational limits.

## 2. User and jobs to be done

The only dashboard role is a supervisor. Supervisors can access only their assigned sites and crews. A crew lead can carry the shared phone; this describes an operational responsibility, not another dashboard role.

1. Before a shift, find today's and tomorrow's high-risk windows and plan heavier tasks accordingly.
2. During a shift, see crew-level green/amber/red counts, the most cautious crew state and the age/completeness of the data.
3. Review break or shade-rotation advice while retaining operational judgment.
4. On a help call, identify the worker and crew, use the site emergency procedure, and acknowledge receipt.
5. Configure the site, create crews, assign a watch, and complete private watch-local issuance settings.

Success means the correct information and next action are understandable, freshness is never disguised, and the dashboard does not expose individual exposure histories. Clinical effectiveness and productivity improvement require later field evidence.

## 3. Scope and deliberate exclusions

### Included in target V1

Supervisor authentication; one primary responsive screen; today/tomorrow forecast; multiple crews; privacy-safe grouping; caution-first suggestions; an acknowledged/unacknowledged emergency lifecycle; location and crew setup; watch assignment; a shared-phone gateway contract; and local-only clothing/acclimatization provisioning.

### Excluded from supervisor V1

On-site sensor stations; individual worker score/history/detail pages; worker/clinician/employer role portals; reports/analytics screens; GPS trails; physiological diagnosis; payroll or disciplinary features; SMS/voice and other additional delivery channels. Emergency audit records needed for integrity are internal operational records, not an analytics product. This specification does not require a custom trained ML model.

### Submission demonstration versus operational V1

A hackathon demonstration may simulate a watch, phone gateway and forecast, provided every simulated source and unimplemented physical feature is explicit. It must not claim actual Bluetooth delivery, independent watch operation, real-world lead time, clinical thresholds or verified health protection. Target V1 requires physical qualification and the security/privacy gates in the QA plan before use with real workers.

## 4. Changes from the current repository

| Existing prototype | Target decision from the new source |
|---|---|
| Crew, private badge and system tabs | One supervisor dashboard; move the badge/safety scenario harness to development-only tooling |
| Independent aggregate fixture | Real crew aggregate contract, or explicitly labeled simulated gateway events in demo mode |
| Suppression below five | Group small crews to a minimum of three under P2; suppress when safe grouping is impossible |
| Unnamed single-session emergency | Authorized named help call with crew, occurrence time, delivery time and acknowledgement |
| In-memory anonymous sessions | Authenticated supervisor identity, site authorization and durable operational state |
| Twelve synthetic forecast points | Site-local today and tomorrow coverage, with explicit missing hours and risk labels |
| Fixed planning text | Deterministic advice derived from forecast and privacy-safe combined crew exposure context |
| Station/badge concept | Watch plus shared crew phone; no on-site sensor station dependency in dashboard V1 |

The new source governs these product differences. Earlier reports remain historical planning documents; they must not be used to retain excluded features or the obsolete group-size default.

## 5. Primary screen and visual language — UX1

The dashboard is one route. Top to bottom: lightweight Exaclim header with site selection, connection/freshness and setup control; unacknowledged emergency banner when present; page title/site-local date; heat forecast; crew status and break/rotation cards. On small screens, use a single column in that order. Setup opens in SDK dialogs/drawers; logging in precedes the dashboard.

Use the supplied Deel references for the pale lavender header treatment, light page, white rounded cards, subdued inset rows, dark primary buttons, underlined secondary selection, centered dialogs and clear saved feedback. Use Exaclim branding and worksite content. Do not add unused HR navigation, financial examples, decorative status widgets or an AI chat panel.

Keep `@ui-sdk/core` and `@ui-sdk/web` for control semantics and interaction. The community Deel skill supplies design guidance; its inconsistent extracted colors do not override the screenshots or accessibility. Use locally served Inter where licensed and available, a coherent 4px spacing scale, readable responsive headings, 15–16px body text, at least 44px primary touch targets, visible focus and keyboard navigation. Proposed text/control contrast targets are WCAG 2.2 AA: 4.5:1 ordinary text, 3:1 large text and meaningful control/focus edges. Heat colors always have labels and distinct symbols.

## 6. Forecast requirements — D1, D2, D3

Show today's and tomorrow's site-local calendar days. Every hour has a start time, risk label, source type and data-quality state. Coverage follows the site's IANA timezone rather than the supervisor browser's timezone. Store time as UTC instants; derive local labels at display time. Preserve offset information for repeated daylight-saving hours. Missing hours are Unknown, never Green.

Default to today with a clear tomorrow selector. Supervisors can inspect each hourly value without hover alone. Risk is Green, Amber or Red; missing/stale data adds an Unknown/Caution label and icon, not an invented fourth clinical category. Summarize contiguous red windows, for example “Tomorrow 11:00–15:00: high risk.” Treat windows as half-open intervals, so 11:00 through 14:00 hourly buckets end at 15:00. Do not merge across a missing hour or a local-day boundary.

The backend retrieves a public weather forecast for saved site coordinates. Open-Meteo is the proposed adapter; verify current terms, attribution, availability and any commercial usage requirement before deployment. Preserve provider, coordinates, fetch time, forecast valid times, provider issue time if available, model/policy version and live/cached/synthetic mode. A fetch time is not a provider issue time.

A forecast weather model is not construction-site WBGT or a personal heat-strain predictor. The current invented index must not be relabeled as a medically approved risk model. All green/amber/red mappings and work/rest advice need an explicit versioned policy. Synthetic demo policy may be used for demonstration with a prominent label. Physical/clinical release requires occupational-health review.

## 7. Crew status — D4, D5, D6, P1, P2

Each permitted visible crew/group displays its label, green/amber/red counts, expected active contributors, fresh contributors, unknown contributors, last valid sample time, last server receipt time and overall state. “Last updated” must refer to the measurements, not merely a successful page refresh. Counts use distinct currently assigned watches, not packet count.

Overall heat state is the most severe known contributing state. Unknown or stale contributors impose at least Amber/Caution and preserve previously known Red until fresh evidence permits a downgrade. Show completeness separately; one fresh green packet cannot make a partly disconnected crew green. A help event is an emergency override above routine heat states; do not blend it into a normal green/amber/red count or infer that a routine red means a diagnosed emergency.

While a watch reports an unresolved help state, retain at least a Red crew/group floor and a non-identifying “Help state active” marker, even after the named banner is acknowledged. Routine counts remain separate from this override. Only fresh, trusted watch-local resolution evidence can remove that help floor; an ACK or missing connection cannot.

### Proposed deterministic grouping policy

A crew with at least three distinct active participants is eligible for its own aggregate row. A crew with one or two must join a stable, non-overlapping privacy group within the same authorized site. Prefer combining small crews; add a whole eligible crew if necessary and remove that crew's standalone row. For example, A=2 and B=1 becomes one three-person row; A=2 and B=4 becomes one six-person row, with no separate B row. Never show overlapping totals that allow subtraction to recover a small crew.

If the entire authorized population is below three, or valid contributions for a group are fewer than three, suppress its numeric breakdown and combined budget. Show “Group status unavailable — insufficient contributors” and a cautious operational state. Do not borrow data across sites or create fictional participants. Overall caution may be shown without revealing which worker/crew produced it. Keep membership stable for the shift; apply assignment changes atomically and invalidate cached prior group breakdowns. A minimum group size alone is not a guarantee against reidentification.

Setup can list administrative crew membership and watch assignments because D14 requires assignment. It never joins those identities to routine risk, budget, freshness or health histories. The emergency exception is handled separately. No individual routine health endpoint may exist behind a hidden frontend control.

## 8. Suggested breaks and rotation — D7, D8, S2

For each visible privacy group, show the next recommended action and planning window, an explanation, source/freshness, policy version and confidence/limitations. Suggestions use upcoming forecast and gateway-computed crew exposure summaries. Individual budgets remain off the dashboard and cloud APIs. A group summary is released only when the same privacy/completeness rules are satisfied.

For groups spanning multiple crew phones, the backend must combine authenticated crew aggregates into one non-overlapping permitted group before dashboard publication. The cloud boundary must not receive a one-person numeric budget disguised as a group summary: a phone with fewer than three valid contributors withholds that summary. If no eligible combined budget can be formed without revealing a private value, the group receives the explicit missing-summary fallback below. Per-crew intake is restricted; no small-crew breakdown is available through read/stream endpoints. This limitation must be visible, not hidden by invented budget values.

The engine should use a conservative group statistic defined in the approved policy; a mean alone can conceal a high-risk member. Its minimum caution floor is the group's most severe state and data-quality condition. A lower forecast or a suggestion must never downgrade that floor. When the summary is unavailable, display general site-control advice rather than a fabricated time-to-limit or exact rest prescription.

Concrete rest duration, recovery rate and acclimatization progression are not set by this PRD. They require an expert-approved policy. The demonstration may use explicit scenario timings, never described as safe work allowances. “Advice — supervisor decides” stays visible. No action is recorded as completed merely because advice was viewed or a banner acknowledged.

## 9. Help calls and acknowledgement — D9, D10, D13, S1

Show a high-priority banner above the main content as soon as an authorized help event reaches the server/browser. Show worker display name, crew, occurrence time, server delivery time and a delayed-delivery indicator when relevant. The explicit exception to aggregate-only visibility is the identity required to respond; do not include an individual dose, clothing, acclimatization, diagnosis or symptom narrative.

Sort multiple unacknowledged events by occurrence time, while clearly marking newly received delayed events. Never drop an older event because a newer one exists. Unknown identities display “Unassigned watch — help requested” with authorized device/crew context; do not invent a worker name. A bad clock must be labeled “Occurrence time unverified”; retain receipt time.

Lifecycle: queued on watch → queued on phone → received/unacknowledged → acknowledged. A watch or phone deletes its queued event only after the next durable hop confirms receipt. Server ingestion deduplicates by event ID. Acknowledgement is an authenticated, atomic server operation recording supervisor and server time. A failed/offline acknowledgement remains visibly pending and does not remove the banner. Repeated acknowledgements are idempotent. Acknowledging one event must not acknowledge others.

D10 means the dashboard's urgent banner can leave the unacknowledged queue after confirmed acknowledgement. It does not mean the worker is safe or the watch emergency is resolved. The response/session may show a short acknowledged receipt; minimal operational records remain durable under the retention policy. Acknowledgement does not send a clear command to the watch or lower a heat state. Real incident resolution follows the site's emergency procedure and an independently qualified watch-local workflow, not a new dashboard role or analytics page.

A confirmed ACK removes the named urgent queue entry, not the group’s unresolved-help floor. The crew card can retain a non-identifying active-help marker without introducing a fourth core information area or exposing individual measurements.

No network means no real-time remote delivery guarantee. A watch out of range still alerts the worker/nearby people; the named dashboard banner appears only on reconnection and delivery. Avoid “immediately delivered” language across an unavailable radio or Internet link.

## 10. Gateway, watch and issuance — D11–D15

Each crew has one shared phone. It receives watch data over Bluetooth, forms permitted aggregates and forwards them over HTTPS. The watch runs its own calculation and alerts without a phone, Internet or an open dashboard. BLE gateway operation is a separate engineering dependency from the responsive dashboard: background scanning, multiple connections and reconnection must be validated on the exact phone/OS/watch combination. A generic browser or any commercial smartwatch cannot be assumed to provide those capabilities.

Watch-local inputs and any cached forecast must have explicit validity limits. If fresh context is unavailable without the phone, retain a conservative local warning/rest procedure rather than treating an old forecast as current. No on-site station is required by this dashboard version; the exact environmental measurement/risk approach remains part of watch/policy qualification.

The proposed first physical gateway target is managed Android with a native foreground BLE service; this is an architectural proposal pending hardware qualification. The supervisor web app supports desktop/mobile browsing independently. Browser-only Bluetooth is not the default physical plan; a synthetic gateway adapter supports development until the physical route is proven.

Create crews, set coordinates and timezone, and assign a watch through compact setup flows. A watch has one active assignment at a time. Version each assignment and retain enough restricted identity mapping to associate delayed help events with the worker assigned when the event occurred. Transfers must not attribute a queued old event to the new wearer. Assignments require explicit save and durable success feedback; uncertain saves are not displayed as confirmed.

Clothing and acclimatization are configured locally when the watch is issued. Proposed clothing choices are ordinary/restrictive, and acclimatization choices new/returning/acclimatized, pending occupational review. The exact categories and progression schedule remain unapproved. These values pass directly from a local issuance view through the phone to the watch, not through server forms, request logs, cloud storage, analytics or dashboard responses. The main dashboard does not display them. Device confirmation establishes provisioning success.

Qualified wear days should update acclimatization locally, with no double counting across reboots or replayed samples, and support a local manual correction. Watch reassignment must clear prior wearer context and exposure according to a reviewed process without erasing pending help-event provenance. Automatic progression is disabled for real deployment until the wear-day definition, absence/decay and expert-approved schedule are agreed; demo progression is simulated and labeled.

## 11. Freshness and weak-connection behavior — S3, U2

Proposed engineering defaults: watch samples every 30 seconds; gateway uploads every 30 seconds; crew freshness timeout 120 seconds from effective sample time; backend forecast refresh every 60 minutes and forecast cache stale after 6 hours without a successful fetch. These are configurable technical targets, not occupational standards. “Fresh” requires current valid coverage and plausible sample time, not just a packet's recent arrival.

The dashboard uses server push with polling fallback and ages displayed data locally when disconnected. After 120 seconds a crew becomes cautious without waiting for the server. Show stale age, last verified update and connection status. Never relabel an old sample as fresh on reconnect. On initial load with no cache, display Unknown/Caution rather than zero/green. A future timestamp cannot postpone staleness forever.

Permit an already-open supervisor page to show previously authorized non-identifying aggregates while offline. Cache only allowed aggregate snapshots, with site/supervisor scope and expiry. Do not persist named emergency details or watch issuance context in browser storage. Do not cache protected API responses with a generic service worker. Logout/site change clears scoped state. Offline login is not supported.

## 12. Authentication, privacy and operational data

Use a maintained identity/session solution with server-enforced supervisor-to-site authorization; a UI role toggle or an anonymous cookie is not login. All site, crew, assignment, aggregate and emergency operations check scope. Gateway credentials are separate, revocable and scoped to one site/crew assignment. Production transport is HTTPS, with Secure/HttpOnly/SameSite session cookies, CSRF defenses and bounded request sizes.

Cloud schemas permit administrative identities, aggregate snapshots and minimal emergency records. They reject routine individual scores/history, clothing, acclimatization, body measurements and raw symptom text. No ranking by productivity, discipline or employment suitability is provided. Do not expose the development agent bridge to production provisioning or named-emergency data without a reviewed authorization policy.

Retention durations and controller/processor responsibilities require a team-approved policy before a real pilot. Retain only the identity/assignment history required for queued event attribution and emergency accountability; implement expiry/deletion and access audit. No statutory retention period is invented here. Ghana Act 843 and applicable site/ethics obligations require qualified review before real worker data is processed.

## 13. Proposed nonfunctional acceptance targets

These are design targets to test, not results already achieved.

- Healthy-path emergency delivery: after an event is durably received by the backend, visible to an authenticated active dashboard within 2 seconds at p95 on the defined healthy test network. This excludes offline watch-to-phone delay; measure each hop separately.
- Readable layout at 360, 390, 768, 1440 and 1920 CSS px, keyboard and touch use, 200% zoom and reduced motion. Prioritize outdoor readability; sunlight qualification needs physical testing.
- Proposed weak-link test profile: 400 kbps down, 100 kbps up, 400ms round-trip latency, then 60 seconds complete outage. No false-fresh/green state; pending acknowledgements remain unconfirmed.
- Cold dashboard load target ≤5 seconds at p95 on that weak-link profile after authentication, measured over at least 20 runs. Versioned static assets, local fonts and no unnecessary blocking third-party resources.
- Candidate bench capacity: 10 crews and up to 20 assigned watches per crew. This is a software stress-test input, not a BLE hardware-capacity claim. Hardware testing must establish actual supported limits.
- Durable incident/acknowledgement recovery across service restart; no duplicate side effects on replay, safe backpressure and explicit queue-full states. Storage budgets and queue capacities require device qualification.

## 14. Acceptance summary and release definitions

The complete original 24 requirements must have a named engineering task and test case. The accompanying traceability CSV is the review index. Each delivery must declare mode: Synthetic demo, Bench validated, or Pilot approved. A demo can pass software behavior checks with simulated devices; it cannot pass physical-device or clinical gates through simulation.

Before a software demonstration: supervisor-only core screen, provenance, labeled forecasts, aggregate privacy/grouping, meaningful suggestions, reliable named synthetic help/acknowledgement, setup persistence and automated failure scenarios. Authentication must be real for any hosted protected-data workflow; a simulated login must be labeled and restricted to synthetic demonstration data.

Before a physical pilot: compatible qualified watch/phone; independent alerts; reliable offline queue; reviewed model and acclimatization policy; real authentication/authorization; reviewed data retention; worker/site consent and appropriate ethics determination; human-readable language review and physical usability tests. No silent waiver turns an untested critical requirement into a pass.

## 15. Decision register

| Decision | Current proposed direction | Remaining decision/evidence |
|---|---|---|
| Watch model | BLE-capable programmable wrist device with help input and independent alerts | Exact SKU, SDK, firmware access, power, radio and button qualification; no model confirmed |
| Gateway platform | Managed Android native BLE foreground service | Exact Android versions/phone and supported watch count; background/restart tests |
| Languages | English first; Twi next if site workers prefer it | Team choice and fluent-worker review; French from old prototype is not automatically carried forward |
| Risk/work-rest/acclimatization policy | Versioned transparent policy; synthetic policy for demo only | Occupational-health expert approval and physical measurement approach |
| Grouping | Stable, non-overlapping groups of at least three within one site | Team acceptance of whole-crew combination and under-contributor suppression |
| Freshness/performance | Engineering defaults and targets in sections 11–13 | Field-derived thresholds and capacity measurements |
| Login provider and retention | Maintained supervisor identity; minimal records | Provider selection, recovery flow, retention owner and duration before real-data release |

No question above prevents preparing the design/task/test package. Hardware, policy, language and real-data release tasks remain conditional until the relevant evidence exists.
