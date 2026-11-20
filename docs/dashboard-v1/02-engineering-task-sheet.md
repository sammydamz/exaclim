# Exaclim Dashboard V1 — Engineering Task Sheet

Version 1.0 · 19 November 2026 · Planned implementation work, not completed features

> Current status: see [the 20 November implementation audit](04-implementation-audit.md) for the delivered work and remaining gaps. This original plan is preserved as a baseline. Its Python-first deployment proposal was superseded by the user-approved Hono + Workers + D1 stack.

## 1. How to use this sheet

This sheet implements the accompanying PRD and the 24 original requirement IDs. ENG01–ENG27 are independently assignable work packages with dependencies, acceptance criteria, proposed file targets and QA links. File paths below are proposed destinations unless they already exist. Owner roles are recommended disciplines, not assignments to named people. Estimates are rough productive person-days for an engineer familiar with the stack; they exclude procurement, clinical/legal review and physical test access. Do not add them up as a guaranteed calendar schedule. All implementation status remains Planned.

The dashboard has three core areas only. Login, compact setup and a priority emergency banner support them. No individual health view, analytics/reporting screen, station sensor or SMS work is included.

## 2. Architecture and boundaries

Reuse the Python model/forecast modules as libraries where suitable, and retain the Vite/Web Components frontend with @ui-sdk/core and @ui-sdk/web. The local stdlib HTTP prototype is not a production authenticated service. Proposed service implementation: a maintained Python API framework with typed request/response validation and a maintained identity integration, with SQLite for a single-instance synthetic demo and PostgreSQL/migrations before concurrent protected-data deployment. ENG01/ENG03 confirm those choices before dependencies change.

Data path: autonomous watch → BLE shared crew phone → authenticated HTTPS ingestion → privacy-filtered site service → authenticated supervisor screen. Public weather → backend forecast adapter → versioned risk policy → site-local forecast and suggestions. The gateway aggregates routine watch data locally. Individual dose, history, clothing and acclimatization must not enter routine cloud payloads. Named help is a separately authorized exception.

The exact wrist device, native gateway capability and occupational policy are external dependencies. A browser BLE permission prompt is not proof of background multi-watch support. Use a versioned synthetic gateway adapter for development while physical qualification proceeds. Do not mark D11–D13 physically complete from a simulator.

## 3. Work sequence and implementation slices

- Foundation: ENG01–ENG04 establish scope, theme, auth and durable schemas.
- Parallel application work: setup/assignment/privacy (ENG05–ENG07), forecast/policy (ENG08–ENG09), aggregate ingestion (ENG10), suggestions (ENG11), help/acknowledgement (ENG12–ENG13).
- Supervisor screen: ENG14–ENG18 integrate the three areas, emergency priority and freshness.
- Device lane: ENG20 qualifies the watch; ENG21 qualifies the phone; ENG19 provisions private context; ENG22 reconciles durable delivery; ENG23 adds reviewed acclimatization.
- Verification/release: ENG24–ENG27 supply traceable software evidence and separate physical/pilot gates.

Dependencies are gate-specific: a Demo may consume the versioned simulated watch/gateway contract from ENG20/ENG21 before their physical qualification is complete. Bench/Pilot completion still requires the real tasks; a simulated dependency must be labeled in the task record.

Build an end-to-end synthetic vertical slice early: login → configured site → two privacy-safe crews → today/tomorrow fixture → aggregate update → suggestion → named synthetic help → server-confirmed acknowledgement. Then inject missing data, small crews and delayed delivery. The operational watch lane must not be hidden by a polished UI. No estimate here promises that all physical work fits the hackathon submission window.

## 4. API contract outline

All routes below are proposed V1 routes, not existing endpoints. Errors are structured as `code`, readable `message`, `request_id` and safe field details; never echo private payloads or credentials. Use UTC instants and explicit source/assignment/policy versions. Return 401 for missing/expired identity, 403 for denied site scope, 409 for version conflict, 422 for validated input failure and 503 for unavailable dependencies. Protected responses are private/no-store; use explicit application-scoped aggregate caching only as described in the PRD.

| Operation | Proposed route | Contract and invariant |
|---|---|---|
| Dashboard snapshot | GET /api/v1/sites/{site}/dashboard | Site/timezone, privacy-filtered groups, suggestions, forecast freshness and authorized unacknowledged events; no individual routine risk |
| Forecast | GET /api/v1/sites/{site}/forecast?day=today-or-tomorrow | UTC valid interval plus local label/offset, risk/source/quality, window summaries and version |
| Setup | POST/PATCH /api/v1/sites and /sites/{site}/crews | Authenticated assignment scope, validated coordinates/timezone and optimistic version check |
| Watch assignment | POST /api/v1/sites/{site}/assignments | Watch, administrative worker identity, crew and assignment version; no clothing or acclimatization |
| Aggregate batch | POST /api/v1/gateway/batches | Gateway identity determines permitted scope; sequence, sample age/time, source quality, distinct-contributor counts, severity counts and eligible group summary |
| Help event | POST /api/v1/gateway/help-events | Immutable event ID, device/assignment version, trigger enum, occurred/received times and clock quality; no symptom narrative |
| Acknowledge | POST /api/v1/emergencies/{event}/ack | Authenticated supervisor, atomic first receipt, canonical server timestamp and idempotent repeat response; no watch-clear instruction |
| Live updates | GET /api/v1/sites/{site}/events | Authenticated server event stream with bounded reconnect cursor; polling fallback re-fetches canonical state |

A routine aggregate should include a stable privacy-group ID and membership version, expected active count, unique valid count, green/amber/red/unknown counts, effective sample time, receive time and sequence. Require green + amber + red + unknown = expected active count, with mutually exclusive states, and reject negative/fractional/overflow counts. Distinguish valid, fresh contributors from expected watches; enrollment is not a sensor sample. Unknown/stale payloads cannot reset the severity floor to green. Prefer group summaries over raw watch packets at the cloud boundary. Small-crew intake is a restricted aggregation input, never a readable small-crew endpoint. Withhold a budget summary from a phone with fewer than three valid contributors; if a combined summary cannot be produced without exposing private values, return missing-summary advice. Keep unresolved-help group floors independent of supervisor ACK state.

A help event needs assignment version and an event creation identifier that survives replay and reboot. Backend acknowledgement of durable ingestion is distinct from the supervisor acknowledgement. Phone upload success must not be mistaken for a human seeing the alert. Define both receipts explicitly.

## 5. Persistence, ordering and privacy review

Proposed tables/collections: supervisor/site access, sites, crews, workers' minimal administrative identity, watch assignments and versions, privacy group membership, latest aggregate snapshots, help events, acknowledgement receipts, gateway credentials and minimal access audit. Individual exposure history/profile tables are intentionally absent. Name/assignment access is restricted even though it is not itself a heat history.

Maintain unique constraints for active watch assignment, gateway batch identity and help event ID. Use transaction boundaries for transfer, event insertion and first acknowledgement. Keep event occurrence time immutable; append server receipt/ack times. Evaluate clock skew and sample age using trusted receipt context. Out-of-order older aggregates cannot overwrite a newer sequence or make an old event disappear.

Privacy grouping must happen before response serialization, not by hiding HTML. Gateway payload allowlists and server response schemas both enforce the boundary. Cache invalidation and site authorization apply equally to initial snapshots, polling, server events, developer endpoints and error messages. Retention/deletion must account for help still queued on an old assignment without keeping all history indefinitely. ENG25 resolves the actual retention durations and constraints.

## 6. Independent engineering jobs

### ENG01 — Approve source baseline, contracts and decision register

Priority: P0. Gate: Demo. Proposed owner: Product + technical lead. Estimate: 0.5–1 person-days.

Dependencies: none. Source requirements: D1, D9, D10, D11, D12, D13, D14, D15, P1, P2, U1. Test cases: QA19, QA27, QA42, QA44.

Proposed files: `docs/dashboard-v1/`.

- Review original 24 requirements, scope exclusions and all changes from the old prototype.
- Accept or amend the grouping policy, emergency receipt semantics, demo/physical gates, and hardware/language/policy decisions.

Status: Planned; no implementation completion is claimed.

### ENG02 — Implement Deel-inspired Exaclim theme and dashboard shell

Priority: P0. Gate: Demo. Proposed owner: Frontend. Estimate: 1–2 person-days.

Dependencies: ENG01. Source requirements: U1, U3, UX1. Test cases: QA36, QA37, QA38.

Proposed files: `web/styles.css`, `web/index.html`, `web/components/ui.js`.

- Use the supplied screenshot reference, accessible tokens and locally served Inter; preserve UI SDK semantics.
- Deliver one core screen with forecast, crew status and suggestions; emergency banner and setup are supporting flows.

Status: Planned; no implementation completion is claimed.

### ENG03 — Add authenticated supervisor identity and server-side site scope

Priority: P0. Gate: Hosted protected-data demo / Pilot. Proposed owner: Backend + security. Estimate: 2–4 person-days.

Dependencies: ENG01. Source requirements: U1, P1, P3. Test cases: QA23, QA35, QA48.

Proposed files: `exaclim/auth.py`, `exaclim/api/`, `tests/test_auth.py`.

- Use maintained session/OIDC integration; no anonymous cookie or frontend role toggle as authentication.
- Enforce site scope on every read/write; separate revocable gateway credentials; test CSRF and session expiry.

Status: Planned; no implementation completion is claimed.

### ENG04 — Create durable operational schema and versioned API contracts

Priority: P0. Gate: Demo. Proposed owner: Backend. Estimate: 1–2 person-days.

Dependencies: ENG01. Source requirements: D4, D6, D9, D10, D14, P1. Test cases: QA22, QA24, QA41.

Proposed files: `exaclim/storage.py`, `exaclim/contracts.py`, `migrations/`, `tests/test_contracts.py`.

- Persist sites, crews, assignments, aggregate snapshots, events and acknowledgement receipts with migrations.
- Forbid routine individual health/profile fields in dashboard/cloud schemas; add unique event and assignment constraints.

Status: Planned; no implementation completion is claimed.

### ENG05 — Build site and crew setup flows

Priority: P0. Gate: Demo. Proposed owner: Frontend + backend. Estimate: 1–2 person-days.

Dependencies: ENG02, ENG03, ENG04. Source requirements: D1, D14, U3. Test cases: QA25, QA26, QA36.

Proposed files: `web/components/setup.js`, `exaclim/api/sites.py`.

- Validate crew names, coordinates and IANA timezone; empty site has an actionable setup state.
- Save atomically, show inline errors, preserve unsaved edits on failure, confirm durable success.

Status: Planned; no implementation completion is claimed.

### ENG06 — Implement watch assignment and versioned issuance identity

Priority: P0. Gate: Demo / Bench. Proposed owner: Backend + gateway. Estimate: 1–2 person-days.

Dependencies: ENG04, ENG05. Source requirements: D9, D14, P1. Test cases: QA25, QA27, QA48.

Proposed files: `exaclim/api/assignments.py`, `exaclim/assignment_service.py`.

- One active worker/crew assignment per watch; no client-forged site or assignment version.
- Delayed help resolves the assignment at occurrence, not the new wearer; revoke or transfer with auditable scope.

Status: Planned; no implementation completion is claimed.

### ENG07 — Implement non-overlapping privacy groups and response filtering

Priority: P0. Gate: Demo. Proposed owner: Backend + privacy reviewer. Estimate: 1–2 person-days.

Dependencies: ENG04, ENG05. Source requirements: D4, D5, D7, P1, P2, P3. Test cases: QA09, QA10, QA11, QA12, QA13, QA24.

Proposed files: `exaclim/privacy.py`, `tests/test_privacy.py`.

- Group small crews within a site to at least three; no overlapping totals or independent small-crew breakdowns.
- Suppress counts/budget below three valid contributors and invalidate prior cached group responses on membership change.

Status: Planned; no implementation completion is claimed.

### ENG08 — Extend public weather adapter to site-local today/tomorrow

Priority: P0. Gate: Demo. Proposed owner: Backend. Estimate: 1–2 person-days.

Dependencies: ENG04, ENG05. Source requirements: D1, D3, S3. Test cases: QA01, QA02, QA04, QA05, QA46.

Proposed files: `exaclim/forecast.py`, `tests/test_forecast.py`.

- Return complete local-day hour buckets, provider/fetch/issue provenance and explicit missing hours.
- Handle provider errors, timezone/DST and stale cache; never silently substitute synthetic data in operational mode.

Status: Planned; no implementation completion is claimed.

### ENG09 — Version risk classification and conservative policy interfaces

Priority: P0. Gate: Demo; expert gate for Pilot. Proposed owner: Model + occupational reviewer. Estimate: 1–2 plus review person-days.

Dependencies: ENG01, ENG04. Source requirements: D2, D5, D7, D15, S1, S2, S3. Test cases: QA03, QA07, QA14, QA16, QA42.

Proposed files: `exaclim/policy.py`, `exaclim/engine.py`, `tests/test_policy.py`.

- Keep the illustrative demo policy explicitly named; obtain review before claiming occupational validity.
- Expose conservative severity floor, unknown/stale behavior and policy version; do not invent clinical time-to-limit or work/rest rules.

Status: Planned; no implementation completion is claimed.

### ENG10 — Implement gateway aggregate ingestion and current crew state

Priority: P0. Gate: Demo / Bench. Proposed owner: Backend + gateway. Estimate: 2–3 person-days.

Dependencies: ENG04, ENG06, ENG07, ENG09. Source requirements: D4, D5, D6, D7, D11, P1, P2, S3. Test cases: QA06, QA07, QA08, QA12, QA24, QA33, QA41.

Proposed files: `exaclim/ingestion.py`, `exaclim/crew_service.py`, `tests/test_ingestion.py`.

- Count distinct active watches; validate counts, completeness, sequences, time provenance and privacy groups.
- Advance age from measurement time; reject replay/future timestamps and preserve a known red floor under data loss.

Status: Planned; no implementation completion is claimed.

### ENG11 — Build explainable suggestions from forecast and group summary

Priority: P0. Gate: Demo; policy gate for Pilot. Proposed owner: Backend + model. Estimate: 1–2 person-days.

Dependencies: ENG07, ENG08, ENG09, ENG10. Source requirements: D7, D8, S2, S3. Test cases: QA14, QA15, QA16.

Proposed files: `exaclim/suggestions.py`, `tests/test_suggestions.py`.

- Use approved group statistics plus forecast, never a mean that conceals the highest severity.
- Return action, window, rationale, limitations and provenance; missing summary yields manual-plan advice, not invented timings.

Status: Planned; no implementation completion is claimed.

### ENG12 — Persist and deduplicate authorized help events

Priority: P0. Gate: Demo. Proposed owner: Backend. Estimate: 1–2 person-days.

Dependencies: ENG03, ENG04, ENG06. Source requirements: D9, D13, P1, S1. Test cases: QA17, QA18, QA22, QA27, QA30, QA33.

Proposed files: `exaclim/emergencies.py`, `tests/test_emergencies.py`.

- Ingest help/symptom trigger as a priority event with immutable ID and assignment version.
- Preserve occurred/received times and delayed/clock quality; no raw symptom narrative or personal dose in dashboard payload.

Status: Planned; no implementation completion is claimed.

### ENG13 — Implement atomic acknowledgement receipts

Priority: P0. Gate: Demo. Proposed owner: Backend. Estimate: 0.5–1 person-days.

Dependencies: ENG12. Source requirements: D10, S1. Test cases: QA19, QA20, QA21, QA22.

Proposed files: `exaclim/api/emergency_ack.py`.

- Authenticate acknowledging supervisor, persist server timestamp and return canonical receipt idempotently.
- Never clear watch emergency or acknowledge other events; failed/offline receipt stays unconfirmed.

Status: Planned; no implementation completion is claimed.

### ENG14 — Build today/tomorrow forecast and high-risk windows

Priority: P0. Gate: Demo. Proposed owner: Frontend. Estimate: 1–2 person-days.

Dependencies: ENG02, ENG08, ENG09. Source requirements: D1, D2, D3, U1. Test cases: QA01, QA02, QA03, QA04, QA36, QA37.

Proposed files: `web/components/forecast.js`.

- Render local hours, accessible severity labels and high-risk window summaries without hover dependency.
- Make source/freshness and absent data clear; do not merge across unknown hours or dates.

Status: Planned; no implementation completion is claimed.

### ENG15 — Build crew cards with grouping, completeness and freshness

Priority: P0. Gate: Demo. Proposed owner: Frontend. Estimate: 1–2 person-days.

Dependencies: ENG02, ENG07, ENG10. Source requirements: D4, D5, D6, P1, P2, S3, U1. Test cases: QA06, QA07, QA08, QA09, QA10, QA11, QA12, QA13, QA37.

Proposed files: `web/components/crew-status.js`.

- Use only allowed aggregate response fields; names do not become routine individual drilldowns.
- Support loading, no crews, grouped/suppressed, stale, partially disconnected and fresh red/amber/green states.

Status: Planned; no implementation completion is claimed.

### ENG16 — Build suggested break/rotation cards

Priority: P0. Gate: Demo. Proposed owner: Frontend. Estimate: 0.5–1 person-days.

Dependencies: ENG02, ENG11. Source requirements: D7, D8, U1, U3. Test cases: QA14, QA15, QA16, QA37.

Proposed files: `web/components/suggestions.js`.

- Present action/window, explanation, data quality and advice-only wording.
- Do not auto-complete a rest action or imply the suggestion overrides the crew floor.

Status: Planned; no implementation completion is claimed.

### ENG17 — Build priority named help banner and receipt feedback

Priority: P0. Gate: Demo. Proposed owner: Frontend. Estimate: 1–2 person-days.

Dependencies: ENG02, ENG12, ENG13. Source requirements: D9, D10, D13, P1, S1, U1. Test cases: QA17, QA18, QA19, QA20, QA21, QA36.

Proposed files: `web/components/emergency-banner.js`.

- Render all unacknowledged authorized events, worker/crew/time and delayed delivery; keep help above normal cards.
- Announce accessibly without trapping focus; disable repeated receipt action while pending and remove only after confirmed ack.

Status: Planned; no implementation completion is claimed.

### ENG18 — Implement live updates, bounded polling and stale/offline cache policy

Priority: P0. Gate: Demo. Proposed owner: Frontend + backend. Estimate: 1–2 person-days.

Dependencies: ENG10, ENG12, ENG15, ENG17. Source requirements: D6, D13, S3, U2. Test cases: QA05, QA08, QA20, QA34, QA35, QA46.

Proposed files: `web/services/connection.js`, `exaclim/api/stream.py`.

- Use server events with polling fallback; reconnection invalidates old data instead of resetting sample age.
- Age aggregates locally, scope allowed caches, never persist named alerts or private provisioning data, clear state on logout/site switch.

Status: Planned; no implementation completion is claimed.

### ENG19 — Implement local-only clothing/acclimatization provisioning

Priority: P0. Gate: Bench; simulate for Demo. Proposed owner: Gateway + firmware + privacy. Estimate: 2–3 person-days.

Dependencies: ENG06, ENG20, ENG21. Source requirements: D14, D15, P1. Test cases: QA24, QA25, QA31, QA32.

Proposed files: `gateway/provisioning/`, `firmware/provisioning/`.

- Send private issuance settings directly to the watch; no server form round-trip, logs, analytics or production agent bridge access.
- Validate simple reviewed options and wait for device confirmation; failure does not show issued/confirmed.

Status: Planned; no implementation completion is claimed.

### ENG20 — Qualify watch and implement autonomous alert firmware

Priority: P0. Gate: Bench / Pilot. Proposed owner: Embedded engineer. Estimate: 3–7 plus procurement person-days.

Dependencies: ENG01, ENG09. Source requirements: D2, D11, D12, D13, D15, S1, S2, S3. Test cases: QA28, QA29, QA32, QA43.

Proposed files: `firmware/`, `docs/hardware/watch-qualification.md`.

- Select an actual programmable BLE wrist device; prove physical button, green/amber/red and vibration without phone/network.
- Persist emergency and required local context through reboot; publish versioned minimal radio protocol and power evidence.

Status: Planned; no implementation completion is claimed.

### ENG21 — Build qualified shared-phone BLE gateway

Priority: P0. Gate: Bench; adapter for Demo. Proposed owner: Android + embedded. Estimate: 4–8 person-days.

Dependencies: ENG04, ENG06, ENG20. Source requirements: D11, D12, D13, P1. Test cases: QA28, QA29, QA30, QA33, QA43.

Proposed files: `gateway/android/`, `gateway/simulator/`.

- Prove exact phone/OS/watch compatibility, reconnection and background service behavior before relying on real radio.
- Aggregate locally and forward only permitted fields; a simulator uses the same contract and stays visibly synthetic.

Status: Planned; no implementation completion is claimed.

### ENG22 — Implement durable queues, hop receipts and delayed-event reconciliation

Priority: P0. Gate: Demo simulation / Bench physical. Proposed owner: Gateway + backend + embedded. Estimate: 2–4 person-days.

Dependencies: ENG10, ENG12, ENG20, ENG21. Source requirements: D6, D9, D11, D12, D13, D14, S1, S3. Test cases: QA18, QA22, QA27, QA29, QA30, QA33, QA43.

Proposed files: `gateway/queue/`, `firmware/event_queue/`, `exaclim/reconciliation.py`.

- Persist events before hop acceptance; upstream deletion requires next-hop durable receipt, with replay-safe IDs.
- Test phone/watch/backend restarts, queue pressure and old-assignment help after reassignment; never claim offline instant delivery.

Status: Planned; no implementation completion is claimed.

### ENG23 — Implement reviewed local acclimatization progression

Priority: P0. Gate: Pilot; synthetic schedule for Demo. Proposed owner: Embedded + occupational reviewer. Estimate: 1–2 plus review person-days.

Dependencies: ENG09, ENG19, ENG20. Source requirements: D15, P1. Test cases: QA31, QA32.

Proposed files: `firmware/acclimatization/`, `docs/hardware/policy-review.md`.

- Define qualifying wear day, timezone, absence/decay, manual change and reassignment behavior with an expert.
- Count days once across reboots and clock change; keep profile local and label any demo schedule unvalidated.

Status: Planned; no implementation completion is claimed.

### ENG24 — Build V1 fixtures and automated integration/browser coverage

Priority: P0. Gate: Demo. Proposed owner: QA + frontend + backend. Estimate: 2–3 person-days.

Dependencies: ENG07, ENG08, ENG11, ENG13, ENG14, ENG15, ENG16, ENG17, ENG18. Source requirements: D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, P1, P2, S1, S2, S3, U1, U2. Test cases: QA01, QA03, QA09, QA14, QA17, QA19, QA20, QA34, QA36, QA42, QA44.

Proposed files: `tests/dashboard_v1/`, `scripts/check_dashboard_v1.py`.

- Use deterministic fixture clock, dates, assignments and fault injections tied to the same API contracts.
- Retain useful old tests but replace obsolete five-person grouping/single-worker UI assumptions; do not mark new cases passed from old evidence.

Status: Planned; no implementation completion is claimed.

### ENG25 — Review privacy, security, retention and credential lifecycle

Priority: P0. Gate: Protected-data / Pilot. Proposed owner: Security + privacy lead. Estimate: 1–3 plus review person-days.

Dependencies: ENG03, ENG04, ENG06, ENG07, ENG12, ENG13, ENG19. Source requirements: P1, P2, P3, U1. Test cases: QA13, QA23, QA24, QA25, QA31, QA35, QA47, QA48.

Proposed files: `docs/security/`, `exaclim/retention.py`, `tests/test_authorization.py`.

- Inspect APIs, storage, logs, analytics, browser caches and local provisioning for forbidden data or cross-site access.
- Set actual retention policy, least-privilege access and deletion constraints for queued events; review Act 843 and relevant pilot obligations.

Status: Planned; no implementation completion is claimed.

### ENG26 — Validate usability, accessibility, performance and supported capacity

Priority: P0. Gate: Demo software / Bench physical. Proposed owner: QA + design + gateway. Estimate: 1–3 plus physical tests person-days.

Dependencies: ENG02, ENG14, ENG15, ENG16, ENG17, ENG18, ENG21. Source requirements: U1, U2, U3, UX1. Test cases: QA36, QA37, QA38, QA39, QA40, QA45.

Proposed files: `tests/performance/`, `docs/evidence/dashboard-v1/`.

- Execute keyboard, screen-reader, contrast, responsive, outdoor/large-text and weak-network checks against stated targets.
- Record p95 latency/load runs and candidate software capacity separately from physical radio capacity; no unsupported pilot claims.

Status: Planned; no implementation completion is claimed.

### ENG27 — Assemble traceable release evidence and reviewed handover

Priority: P0. Gate: Demo then Pilot gate. Proposed owner: Technical lead + QA. Estimate: 0.5–1 person-days.

Dependencies: ENG24, ENG25, ENG26. Source requirements: D12, D13, D15, S1, S2, S3, U1, U2, U3. Test cases: QA22, QA28, QA29, QA30, QA32, QA42, QA43, QA44, QA45, QA47, QA48.

Proposed files: `docs/evidence/dashboard-v1/`, `README.md`, `downloads/`.

- Publish exact build/hash, execution results, source modes, known limitations and reproducible commands.
- Separate Demo/Bench/Pilot gates, block critical failures, preserve rollback evidence and hand over demo recording separately.

Status: Planned; no implementation completion is claimed.

## 7. Completion and handover definition

A task is complete only when its code/configuration is reviewed, linked tests execute, actual results are recorded, and relevant privacy/accessibility/failure behavior is checked. “PDF written” and “simulator shown” do not complete a physical requirement. Before merging, update requirement-to-task-to-test links, remove obsolete UI routes from the production build, and run the applicable unit, API, browser, security and physical checks. Keep meaningful old invariants while replacing their obsolete product assumptions.

For each PR/handover record: task IDs, source IDs, changed behavior, migration/rollback considerations, commands and exact exit status, test artifacts, source mode and unresolved gates. Do not record private worker information in screenshots or test fixtures. The master task CSV/JSON provides an editable planning sheet; actual owners and dates can be assigned without rewriting the technical acceptance criteria.
