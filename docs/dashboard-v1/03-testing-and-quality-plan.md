# Exaclim Dashboard V1 — Testing and Quality Plan

Version 1.0 · 19 November 2026 · Target acceptance plan; all QA01–QA48 cases initially Not run

## 1. What this document proves and does not prove

This plan covers the new two-page dashboard specification, the PRD and engineering task sheet. It distinguishes unit/API/browser checks, review evidence and physical/pilot evidence. A planned case is not a passing result. Existing prototype tests may provide useful regression coverage, but do not prove the new login, three-person grouping, shared-phone gateway, named help or private issuance requirements.

The source's three supervisor areas, emergency identity exception, local watch behavior and privacy restrictions govern the tests. No clinical safety threshold, battery life, BLE range, field lead time or health benefit is validated by a synthetic browser run.

## 2. Release gates and result vocabulary

- Demo: synthetic software behavior verified, every simulated source labeled, no real worker data. Physical capabilities remain unverified until the separate gate.
- Hosted protected-data: real login, per-site authorization, reviewed storage/log/cache boundaries and secure deployment required before any non-synthetic identity/data is processed.
- Bench: exact watch/phone/firmware combination physically tested for independent alerts, BLE, power-loss behavior, persistent queues and private provisioning.
- Pilot: occupational policy, wearable qualification, language/usability, retention and applicable ethics/site/worker approvals completed, in addition to the technical gates.

Record results as Pass, Fail, Blocked, Not run, Not applicable with reason, or Expected failure only when deliberately marked and owned. Never convert a missing device, missing policy or unavailable reviewer to Pass. Critical emergency, privacy, authentication, data-quality and durability failures block the relevant release gate. No known critical failure can be waived by relabeling the build as ready. Major failures need repair or a documented scope reduction consistent with the source; a required feature cannot simply be omitted without a product decision.

## 3. Test layers and environments

Use deterministic unit tests for risk floors, clocks, privacy partitions and suggestions. Use a real test database and concurrent requests for authorization, assignment, ingestion, acknowledgement and restart semantics. Use actual Chromium plus target mobile/desktop browsers for layout, keyboard, popup/focus and network behavior. Use a gateway simulator only for software protocol/error tests. Use real devices for radio, vibration, autonomous watch operation, background processing, power and queue durability. Use human review for occupational content, translation, outdoor usability and untrained-user comprehension.

Proposed browser matrix: current Chrome desktop, Android Chrome, iOS Safari and Firefox desktop for the supervisor web app. The native gateway matrix is separately tied to the qualified Android phone/OS and watch firmware. Browser-only Bluetooth is not presumed supported. Run at 360/390/768/1440/1920 CSS px, 200% zoom, keyboard-only, touch and reduced motion. Check RTL only if a selected language requires it; SDK baseline support is not proof of translated content.

For performance use ≥20 measured runs per named profile, fixed build/device/network and an explicitly stated percentile calculation. Clock-controlled functional boundary tests must not rely on wall-clock sleeps. Network tests use the proposed profile in the PRD, an extended complete outage, delayed/reordered packets and bounded backend timeouts. Monitor browser errors and CSP violations; distinguish deliberately injected offline errors from unexpected failures.

## 4. Synthetic fixture inventory

Create named fixtures for: a complete green crew; one amber; one red among green; mixed fresh/stale; absent forecast; stale cached forecast; missing local hours; DST midnight; crews 2+1 and 2+4; site with only two; contributors falling below three; duplicate/reassigned watch; old-assignment delayed help; multiple simultaneous help calls; bad device clock; concurrent acknowledgements; failed/offline ack; backend/phone/watch restart; queue full; issuance canaries; expired/revoked credentials; and long/missing translated strings.

All identities are artificial and visibly synthetic. Inject a fixed clock, provider/gateway adapter and stable event IDs. Reuse the same versioned schemas in fixtures and operational code so mocks cannot silently diverge. Keep private canaries out of shared screenshots/log exports; scans should record absence/presence and field paths, not leak the canary into public evidence.

## 5. Detailed acceptance cases

### QA01 — Today/tomorrow forecast coverage

Requirements: D1, D3. Gate: Demo. Method: API + browser. Severity: Major.

Preconditions: Fixed clock, saved site location/timezone and a deterministic hourly provider response.

Steps: Open Today and Tomorrow; inspect every valid local hour and the day switch.

Expected: Both local calendar days are represented; every hour is labeled with time, risk and quality. No fabricated values replace absent hours.

Evidence: Provider fixture, API body, visible hourly/window assertions.

Status: Not run for target V1.

### QA02 — Site timezone, midnight and daylight-saving boundaries

Requirements: D1, D3. Gate: Demo. Method: Unit + API + browser. Severity: Major.

Preconditions: Accra fixture and a DST-observing test site; clock under test control.

Steps: Use a browser in a different timezone; cross midnight and spring/fall clock changes.

Expected: Labels follow site calendar days; 23/25-hour days and repeated offsets are unambiguous. No assumption that every two-day interval has exactly 48 buckets.

Evidence: Timestamp/offset golden cases and screen assertions.

Status: Not run for target V1.

### QA03 — Risk labels and contiguous high-risk windows

Requirements: D2, D3, S2. Gate: Demo. Method: Unit + browser. Severity: Critical.

Preconditions: Versioned illustrative classification fixture with explicit band boundaries.

Steps: Exercise each band boundary; combine adjacent red hours; insert a missing hour and a date boundary.

Expected: Green/Amber/Red have words/symbols. Red windows use half-open intervals and split at unknown hours/day boundaries; policy version remains explicit.

Evidence: Boundary tests, interval outputs and accessible-name assertions.

Status: Not run for target V1.

### QA04 — Absent and partial forecast coverage

Requirements: D1, D3, S3. Gate: Demo. Method: API + browser fault injection. Severity: Critical.

Preconditions: Provider response has null/missing/invalid hours.

Steps: Remove one high-risk hour, then remove the entire response.

Expected: Missing slots are Unknown/Caution, never zero/green. Partial red windows do not bridge unknown data.

Evidence: Fault fixture, quality-state assertions and error screenshot.

Status: Not run for target V1.

### QA05 — Forecast refresh failure and stale cache

Requirements: D1, S3, U2. Gate: Demo. Method: Clock-controlled API/browser. Severity: Critical.

Preconditions: Cached forecast with trusted fetch/issue metadata; proposed 6-hour freshness timeout.

Steps: Fail subsequent fetches; advance to timeout and beyond; load an expired cached response.

Expected: Fetch failure is visible; cached source/time is retained without false freshness; expired coverage is cautious. Operational mode does not silently load a synthetic forecast.

Evidence: Controlled-clock outputs and request/provenance log.

Status: Not run for target V1.

### QA06 — Distinct contributor counts and completeness

Requirements: D4, D6, D11. Gate: Demo. Method: Unit + ingestion API. Severity: Critical.

Preconditions: Crew has six active assigned watches with known states.

Steps: Send duplicated packets, then a watch transfer, stale contributions and valid updates.

Expected: Counts reflect distinct active assignments; G+A+R+Unknown equals expected count; duplicates cannot inflate contributors.

Evidence: Ingestion fixture and aggregate invariant checks.

Status: Not run for target V1.

### QA07 — Most-at-risk crew floor with unknown members

Requirements: D5, S1, S2, S3. Gate: Demo. Method: Unit + browser. Severity: Critical.

Preconditions: Mixed green, amber, red and unknown contributions.

Steps: Add one red member to an otherwise green group; lose data; send only one fresh green contribution.

Expected: Overall routine severity is at least the highest known state; missing data imposes caution and preserves known red. One green sample cannot make the group all-clear.

Evidence: Severity lattice/property checks and browser states.

Status: Not run for target V1.

### QA08 — Measurement age versus receive time and future clocks

Requirements: D6, S3, U2. Gate: Demo. Method: Clock-controlled unit/API/browser. Severity: Critical.

Preconditions: Samples include sample time, receive time, age, sequence and clock quality.

Steps: Replay an old sample with a new receipt; jump client clock; send a future timestamp; cross 120-second freshness boundary.

Expected: Packet receipt does not refresh the measurement. Implausible time is rejected/flagged, and local UI expiry occurs without a server message.

Evidence: Sample-age traces and monotonic-clock assertions.

Status: Not run for target V1.

### QA09 — Combine small crews 2+1

Requirements: D4, D5, D7, P1, P2. Gate: Demo. Method: Unit + API + browser. Severity: Critical.

Preconditions: Same-site crews A=2 and B=1, all valid and fresh.

Steps: Generate privacy groups and load the dashboard/API.

Expected: One stable three-person combined group appears; neither constituent has a separate risk or budget breakdown.

Evidence: Group partition, JSON allowlist and rendered-card assertions.

Status: Not run for target V1.

### QA10 — Combine 2+4 without overlapping totals

Requirements: D4, D7, P2. Gate: Demo. Method: Unit + API. Severity: Critical.

Preconditions: Same-site crews A=2 and B=4.

Steps: Combine whole crews; request any supported group/filter view.

Expected: One six-person group; B is not also independently exposed. API cannot recover A by subtraction through an alternate route/filter.

Evidence: Grouping invariant and negative endpoint tests.

Status: Not run for target V1.

### QA11 — Insufficient total population

Requirements: D4, P2, S3. Gate: Demo. Method: API + browser. Severity: Critical.

Preconditions: Only two eligible participants in a site.

Steps: Load dashboard and request group, suggestion and stream data.

Expected: No numeric risk counts or combined budget are exposed; a clear insufficient-contributors state and general cautious advice appear. No cross-site borrowing.

Evidence: All response channels and empty-state capture.

Status: Not run for target V1.

### QA12 — Valid contributors drop below privacy minimum

Requirements: D4, D6, D7, P1, P2, S3. Gate: Demo. Method: Clock-controlled API/browser. Severity: Critical.

Preconditions: Previously valid group of three, then one/two stale or absent contributors.

Steps: Expire contributing data and replay a cached older full breakdown.

Expected: Current numeric breakdown/budget is suppressed; stale cached data is not represented as current or reused for unsafe inference. Caution remains visible.

Evidence: Transition trace, cache expiry and API assertions.

Status: Not run for target V1.

### QA13 — Membership change, filters and cache cannot defeat grouping

Requirements: P1, P2, P3, U2. Gate: Demo. Method: Privacy integration + security review. Severity: Critical.

Preconditions: Two sites and several crews, with a privacy-group version change.

Steps: Change assignment/filters, switch sites, replay prior group/cache versions and request old identifiers.

Expected: No overlapping active partitions or cross-site access; invalid prior data is removed. Setup identities cannot be joined to individual routine health.

Evidence: Negative API matrix and cache inspection.

Status: Not run for target V1.

### QA14 — Suggestions respond to forecast and group summary

Requirements: D7, S2. Gate: Demo. Method: Unit/property + browser. Severity: Critical.

Preconditions: Same crew under rising/falling weather and high/low group summaries.

Steps: Vary forecast and group exposure independently; feed a low mean containing a high-severity member.

Expected: Both inputs influence explainable advice. The most severe member/caution floor is not masked by an average or weaker forecast.

Evidence: Decision fixtures, policy version and severity property checks.

Status: Not run for target V1.

### QA15 — Advice is not automatic control adherence

Requirements: D8, P3, U3. Gate: Demo. Method: Browser + content review. Severity: Major.

Preconditions: Suggestion displayed with an actionable explanation.

Steps: View/dismiss suggestion; acknowledge a help event; inspect persisted operational events.

Expected: Advice remains labeled as advice; neither viewing nor acknowledgement records that a worker rested or completed a control.

Evidence: UI copy and event-state assertions.

Status: Not run for target V1.

### QA16 — No crew budget, no invented time-to-limit

Requirements: D7, D8, S2, S3. Gate: Demo. Method: Unit + browser. Severity: Critical.

Preconditions: Group summary is unavailable, below privacy minimum or malformed.

Steps: Request suggestions despite valid forecast.

Expected: Manual/site-plan advice and missing-data reason appear; no fake dose value, clinical time-to-limit or unapproved precise rest prescription.

Evidence: Suggestion fallback fixtures and schema checks.

Status: Not run for target V1.

### QA17 — Healthy-path named help priority and latency

Requirements: D9, P1, S1, U1. Gate: Demo. Method: API + browser + timing harness. Severity: Critical.

Preconditions: Authorized supervisor, mapped synthetic worker, healthy network and clock instrumentation.

Steps: Ingest help while forecast/crew is green and while another UI request is pending.

Expected: Banner takes priority with worker, crew and occurrence time; p95 backend-durable-receipt-to-visible target ≤2s over ≥20 runs. No private dose/profile appears.

Evidence: Per-hop timestamps, browser captures and percentile calculation.

Status: Not run for target V1.

### QA18 — Multiple, delayed and bad-clock help events

Requirements: D9, D13, S1. Gate: Demo. Method: Integration + browser. Severity: Critical.

Preconditions: Several events with different occurrence/arrival times and one untrusted clock.

Steps: Deliver new, older queued and unknown-assignment events in mixed order.

Expected: Every unacknowledged event remains reachable. Delayed/clock-unverified labels show; no invented name/time, no overwritten event.

Evidence: Event stream/order assertions and multi-event screenshots.

Status: Not run for target V1.

### QA19 — Confirmed acknowledgement is not watch resolution

Requirements: D10, S1. Gate: Demo. Method: API + browser + firmware contract. Severity: Critical.

Preconditions: One visible help event and independently latched watch/simulator state.

Steps: Acknowledge as an authorized supervisor and inspect server receipt and watch state.

Expected: Only after durable success does that banner leave the unacknowledged queue. Server actor/time is recorded; watch latch and safety state remain unchanged. The crew/group retains at least Red and a non-identifying active-help marker until trusted local resolution.

Evidence: Canonical receipt, banner transition and no-clear-command assertion.

Status: Not run for target V1.

### QA20 — Acknowledgement timeout/offline/server failure

Requirements: D10, S3, U2. Gate: Demo. Method: API/browser fault injection. Severity: Critical.

Preconditions: Unacknowledged event; requests can time out or return 5xx.

Steps: Click acknowledge during outage and retry after reconnect.

Expected: Banner remains visible with unconfirmed/pending status until canonical receipt. Retry is safe; no optimistic disappearance or success toast on failure.

Evidence: Pending/failure/retry screenshots and request log.

Status: Not run for target V1.

### QA21 — Concurrent acknowledgement and event isolation

Requirements: D9, D10. Gate: Demo. Method: Concurrent API integration. Severity: Critical.

Preconditions: Two supervisors authorized for one event and a second unacknowledged event.

Steps: Race acknowledgement calls and replay their idempotency keys.

Expected: One canonical first-ack actor/time; later responses agree; no duplicate effects and second event remains unacknowledged.

Evidence: Transaction/concurrency assertions and receipt records.

Status: Not run for target V1.

### QA22 — Service restart preserves emergency truth

Requirements: D9, D10, D13, S1. Gate: Demo. Method: Durability integration. Severity: Critical.

Preconditions: Persistent store contains one received/unacknowledged and one acknowledged event.

Steps: Restart backend between ingestion and UI display, then after acknowledgement; replay events.

Expected: Unacknowledged event reappears; acknowledged event stays acknowledged; no record loss, fake new occurrence time or duplicate alerts.

Evidence: Restart/replay trace tied to database snapshot/build.

Status: Not run for target V1.

### QA23 — Supervisor login, expired session and site authorization

Requirements: U1, P1, P3. Gate: Protected-data demo / Pilot. Method: Security/API/browser. Severity: Critical.

Preconditions: Two supervisors, separate sites, expired and missing credentials.

Steps: Request snapshot, stream, setup, assignments, emergency and ack through forged IDs/cookies; attempt cross-origin mutations.

Expected: 401/403 and CSRF protections apply; no cross-site identifiers, health data or cached named details leak; gateway credentials cannot act as supervisors.

Evidence: Endpoint authorization matrix and sanitized responses.

Status: Not run for target V1.

### QA24 — Forbidden personal data never crosses cloud boundary

Requirements: P1, P3, D15. Gate: Demo schemas / Pilot real data. Method: Schema tests + data-flow inspection. Severity: Critical.

Preconditions: Payload capture, server/storage/log access and synthetic canary values.

Steps: Try sending individual score/history, clothing, acclimatization, body values and free-text symptoms; inspect every response/storage/log.

Expected: Schemas reject forbidden routine fields; canaries absent from cloud/analytics/logs/dashboard; only minimal authorized emergency identity is exposed.

Evidence: Schema-negative tests, canary scans and data-flow review.

Status: Not run for target V1.

### QA25 — Administrative assignment does not expose individual risk

Requirements: D14, P1, P3. Gate: Demo. Method: API + browser privacy review. Severity: Critical.

Preconditions: Supervisor opens setup and assignments for an enrolled worker.

Steps: Inspect setup, identifiers, API joins, hidden UI and development routes.

Expected: Administrative name/watch/crew mapping supports issuance but exposes no personal heat budget/history or risk drilldown.

Evidence: Response allowlist and production-route scan.

Status: Not run for target V1.

### QA26 — Site/crew creation and durable save errors

Requirements: D1, D14, U3. Gate: Demo. Method: API + browser. Severity: Major.

Preconditions: No site/crews; validation, conflict and save failures injectable.

Steps: Create valid site/crew; try invalid coordinates/timezone/blank names; fail and retry save.

Expected: Clear setup state, validated fields, durable successful values and local errors. Unsaved edits survive failure and success is not shown before confirmation.

Evidence: Form and reload assertions; validation fixtures.

Status: Not run for target V1.

### QA27 — Unique assignment and delayed help after watch transfer

Requirements: D9, D14, P1. Gate: Demo / Bench. Method: Transactional integration. Severity: Critical.

Preconditions: Watch was assigned to worker A, has queued help, then is assigned to B.

Steps: Attempt duplicate active assignment; transfer and deliver A’s old event.

Expected: Duplicate active assignment is rejected; event maps to A’s occurrence assignment without exposing B’s private context. Pending event provenance is retained.

Evidence: Assignment version/transaction/replay cases.

Status: Not run for target V1.

### QA28 — Independent watch alerts without phone/Internet

Requirements: D2, D11, D12, D13, S1, S3. Gate: Bench / Pilot. Method: Physical hardware test. Severity: Critical.

Preconditions: Qualified watch firmware and documented risk/demo input rig.

Steps: Power off phone, disable network and background dashboard; induce graded condition, stale source and help button.

Expected: Watch computes and displays graded alerts/vibration independently; local help alerts work. Dashboard never claims remote receipt while disconnected.

Evidence: Actual device video/logs, firmware/board IDs and power/alert observations.

Status: Not run for target V1.

### QA29 — Out-of-range watch queue and reboot

Requirements: D12, D13, S1. Gate: Bench / Pilot. Method: Physical radio/durability fault injection. Severity: Critical.

Preconditions: Watch beyond phone range, persistent event queue and firmware IDs.

Steps: Press help repeatedly as separate events, reboot watch before reconnection, then reconnect.

Expected: Local alert persists; distinct events survive reboot; replay deduplicates on delivery; watch deletes an event only after durable next-hop receipt.

Evidence: RF/power-cycle trace, queue contents and receipt IDs.

Status: Not run for target V1.

### QA30 — Phone Internet outage and durable upload

Requirements: D11, D13, D6. Gate: Demo simulation / Bench physical. Method: Gateway integration + physical test. Severity: Critical.

Preconditions: Phone receives BLE event while Internet is disabled; native gateway storage enabled.

Steps: Kill/restart gateway/phone, restore Internet, replay upload responses.

Expected: Queued events/aggregates retain sample/occurrence age; no duplicate events or false freshness; next-hop durable receipt controls deletion.

Evidence: Gateway logs, storage inspection and backend event records.

Status: Not run for target V1.

### QA31 — Issuance profile remains local and device-confirmed

Requirements: D14, D15, P1. Gate: Bench / Pilot. Method: BLE provisioning + privacy inspection. Severity: Critical.

Preconditions: Issuance uses synthetic clothing/acclimatization canaries; device can accept/reject config.

Steps: Set profile, inject BLE failure, retry; inspect HTTP, browser storage, agent snapshot, logs and cloud.

Expected: Only watch/local provisioning channel receives settings; no cloud copies or production agent access; no success before device confirmation.

Evidence: Canary leak scan and device confirmation transcript.

Status: Not run for target V1.

### QA32 — Local wear-day progression and correction

Requirements: D15, P1. Gate: Bench / Pilot. Method: Clock-controlled firmware + expert review. Severity: Critical.

Preconditions: Reviewed progression policy, or clearly synthetic schedule under demo label.

Steps: Replay same day, reboot, cross timezone/clock changes, simulate absence, manually change status and reassign watch.

Expected: No duplicate wear day; approved absence/decay and manual rules apply; prior wearer context clears correctly; nothing appears in dashboard/cloud.

Evidence: Policy approval/version and firmware golden cases.

Status: Not run for target V1.

### QA33 — Gateway authentication, replay and ordering

Requirements: D4, D6, D11, D13, P1, S3. Gate: Demo schemas / Bench transport. Method: Security + ingestion integration. Severity: Critical.

Preconditions: Signed/scoped device and gateway credentials; sequences and assignment versions.

Steps: Send forged packets, revoked credentials, duplicate IDs, out-of-order/future sequence/time and wrong-site batch.

Expected: Forged/out-of-scope data rejected; valid replay idempotent; older data cannot overwrite fresher state or clear emergencies.

Evidence: Protocol-negative tests and sanitized audit events.

Status: Not run for target V1.

### QA34 — Weak connection and complete outage

Requirements: S3, U2. Gate: Demo. Method: Browser network throttling + clock control. Severity: Critical.

Preconditions: Proposed profile: 400 kbps down, 100 kbps up, 400ms RTT, 60s outage plus extended expiry.

Steps: Load, interrupt and reconnect; advance beyond crew/forecast timeout without server push.

Expected: Age/connection/missing-source states stay clear; no fake all-clear or refreshed timestamp; reconnect obtains canonical data and pending ack truth.

Evidence: Network profile, timed state captures and request timeline.

Status: Not run for target V1.

### QA35 — Cache, logout and site-switch isolation

Requirements: P1, P2, U1, U2. Gate: Protected-data demo / Pilot. Method: Browser storage/security inspection. Severity: Critical.

Preconditions: Authorized site A loaded, named help present, second site available.

Steps: Go offline, inspect storage/service-worker cache, logout, switch site and return/back/reload.

Expected: Only allowed scoped aggregate cache persists; no named emergency/profile at rest in browser; logout/site change clears prior visible state; offline login denied.

Evidence: Storage/cache dump with synthetic canaries and navigation assertions.

Status: Not run for target V1.

### QA36 — SDK keyboard, modal, error and saved feedback

Requirements: U1, U3, UX1. Gate: Demo. Method: Real browser + assistive-technology review. Severity: Major.

Preconditions: All controls wired through SDK parts; keyboard and screen reader available.

Steps: Navigate entire screen; open/close setup; Cancel/Escape/confirm; trigger inline errors; use SDK agent where allowed.

Expected: Controls named and reachable, focus returns predictably, emergencies announced without trapping focus, pending/disabled states correct, saved feedback follows actual success.

Evidence: Keyboard/agent tests and screen-reader observations.

Status: Not run for target V1.

### QA37 — Responsive, zoom, touch and outdoor readability

Requirements: U1, UX1. Gate: Demo layout / Pilot outdoor. Method: Real browsers/devices + visual review. Severity: Major.

Preconditions: 360/390/768/1440/1920px, 200% zoom, touch phone and physical daylight access.

Steps: Read forecast/crew/advice and emergency; zoom, rotate and use touch; compare risk labels in grayscale.

Expected: No hidden critical content/horizontal workflow overflow; ≥44px primary targets; contrast targets met; labels/symbols distinguish severity. Outdoor pass requires real observation.

Evidence: Viewport screenshots, contrast measurements and outdoor observation record.

Status: Not run for target V1.

### QA38 — Untrained supervisor comprehension

Requirements: U3, D8. Gate: Pilot / optional demo usability evidence. Method: Moderated formative usability. Severity: Major.

Preconditions: Proposed minimum five representative supervisors who have not used Exaclim; synthetic tasks.

Steps: Ask each to find tomorrow’s red window, identify cautious crew, interpret stale state and acknowledge a help alert without coaching.

Expected: Proposed success target: ≥4/5 finish each task correctly within two minutes and distinguish receipt from incident resolution. Report failures rather than call the UI intuitive by inspection.

Evidence: Consent-appropriate anonymized task notes and actual completion/time counts.

Status: Not run for target V1.

### QA39 — Emergency and cold-load performance distribution

Requirements: D9, U1, U2. Gate: Demo measured / Pilot repeat. Method: Instrumented performance. Severity: Major.

Preconditions: Defined healthy and weak-link profiles, fixed build, ≥20 runs each.

Steps: Measure backend-durable-help-receipt to visible banner and authenticated cold dashboard render.

Expected: Report sample count and p50/p95; proposed targets ≤2s healthy help p95 and ≤5s weak-link cold render p95. Offline radio delay excluded and reported separately.

Evidence: Raw timing samples, environment/network profile and percentile method.

Status: Not run for target V1.

### QA40 — Candidate software capacity and physical limits

Requirements: D4, D11, U2. Gate: Demo software / Bench physical. Method: Load + radio qualification. Severity: Major.

Preconditions: 10 crews ×20 synthetic watches; separate real qualified device set.

Steps: Send concurrent batches/help events; exercise reconnection, background service and queue pressure.

Expected: No lost incidents or grouping leaks at declared tested software load. Real BLE watch-count limit is published from physical tests, never inferred from HTTP load.

Evidence: Load outputs and separate phone/OS/watch radio report.

Status: Not run for target V1.

### QA41 — Malformed aggregates and bounded inputs

Requirements: D4, D6, S3. Gate: Demo. Method: Unit/fuzz/schema/API. Severity: Critical.

Preconditions: Bounded ingress schema and invalid-value corpus.

Steps: Send negative/fractional/overflow counts, mismatched totals, huge JSON integers, NaN, null, large bodies and invalid timezone/sequence.

Expected: Reject safely with structured errors; no process crash or false fresh/green state; private payload not echoed.

Evidence: Corpus results and error-code/response checks.

Status: Not run for target V1.

### QA42 — Source mode and clinical-claim integrity

Requirements: D1, D7, D12, D15, S2. Gate: Demo / Pilot review. Method: Content + source/configuration review. Severity: Critical.

Preconditions: Demo and operational modes, failed live forecast and illustrative policy.

Steps: Inspect visible labels, README, build config, API provenance and submission claims.

Expected: Simulation is explicit; no automatic synthetic operational fallback, invented clinical limits, trained-AI claim or physical Bluetooth/battery claim from mocks.

Evidence: Mode screenshots, policy metadata and reviewed limitations list.

Status: Not run for target V1.

### QA43 — Queue capacity, backpressure and reset ordering

Requirements: D12, D13, S1, S3. Gate: Bench / Pilot. Method: Physical fault injection + durable queue tests. Severity: Critical.

Preconditions: Qualified storage budgets and emergency reserve policy recorded first.

Steps: Fill normal queues, generate emergency, power-cycle during write/receipt and reset/reassign with pending event.

Expected: No silent emergency eviction; queue-full/unconfirmed-delivery visible; local help remains active. Durable receipts and reset ordering preserve pending event provenance.

Evidence: Queue limits, power-failure logs and validated recovery traces.

Status: Not run for target V1.

### QA44 — Production surface excludes old/out-of-scope views

Requirements: P1, P3, U1. Gate: Demo / Pilot. Method: Route/build inspection + browser. Severity: Critical.

Preconditions: Production supervisor build plus separately restricted developer harness.

Steps: Enumerate routes/menus/API and attempt old worker/system/testing paths; scan frontend for raw histories.

Expected: Three core areas only; no individual health or reports/analytics/station/SMS module. Harness is not reachable in protected production; brand is Exaclim.

Evidence: Build route inventory and negative access assertions.

Status: Not run for target V1.

### QA45 — Language selection, fallback and reviewed emergency copy

Requirements: U1, U3, D9. Gate: Demo declared / Pilot reviewed. Method: Localization/browser + fluent review. Severity: Major.

Preconditions: English baseline; additional languages only if actually supplied/reviewed.

Steps: Switch language where supported, remove a translation, test long strings and emergency updates.

Expected: Fallback is readable and explicit; no invented Twi support or stale emergency wording. Actual initial languages are listed; workers review pilot content.

Evidence: Translation inventory/version, screenshots and reviewer record.

Status: Not run for target V1.

### QA46 — Provider time/provenance and timeout hygiene

Requirements: D1, D3, D6, S3. Gate: Demo. Method: Adapter unit/API fault injection. Severity: Critical.

Preconditions: Provider with/without issue time, stale response, coordinates and timeout fixtures.

Steps: Delay requests, omit issue time, send wrong coordinates or outdated coverage and cross local day boundary.

Expected: Fetch/issue/valid times remain distinct; wrong/expired data is flagged; timeout is bounded and cannot block a newly arrived help event.

Evidence: Adapter fixtures, request timing and independent-help assertion.

Status: Not run for target V1.

### QA47 — Retention/deletion with queued identity attribution

Requirements: D9, D13, D14, P1, P3. Gate: Pilot. Method: Clock-controlled storage + privacy review. Severity: Critical.

Preconditions: Approved retention schedule and queue reconciliation policy; short test TTLs only.

Steps: Advance retention/deletion, deliver a still-queued old-assignment event, rotate credentials and inspect expiry.

Expected: Only necessary identity link persists within approved constraints; attributable queued help is not silently relabeled/deleted; unrelated data expires and no indefinite history appears.

Evidence: Policy version, synthetic deletion/attribution tests and audit review.

Status: Not run for target V1.

### QA48 — Gateway/watch retirement and credential revocation

Requirements: D11, D14, P1, P3. Gate: Bench / Pilot. Method: Security + assignment integration. Severity: Critical.

Preconditions: Assigned gateway/watch with revocable credentials.

Steps: Retire/transfer device, revoke old token and attempt uploads/reads/acknowledgements.

Expected: Revoked access fails; no cross-site reuse; pending legitimate events use the documented reconciliation path, not a permanent bypass.

Evidence: Revocation/transfer tests and scoped audit records.

Status: Not run for target V1.

## 6. Release quality checklist

- Product: all 24 source IDs are traced; source changes from the old prototype are explicit; no unrequested fourth core dashboard area or individual health view.
- Safety behavior: help overrides routine state; ACK is receipt only; stale/unknown is cautious; suggestions cannot lower the floor; delayed delivery is honest.
- Privacy: three-person non-overlapping group rules verified at API/cache level; profile values stay watch-local; named help limited to authorized scope; no disciplinary feature.
- Reliability: durable events/ACK survive restart; every queue has receipts/replay behavior; sample age never becomes receive age; outages do not imply all-clear.
- UX: SDK control names and agent restrictions correct; keyboard/focus, touch size, contrast, zoom and target browsers checked; inline errors/pending/saved states reflect actual outcomes.
- Source/claim integrity: live/cached/synthetic mode visible; exact model/policy/firmware/build recorded; no trained model, physical performance or clinical benefit asserted without evidence.
- Operations: identity provider, HTTPS, CSRF/session controls, gateway revocation, storage migrations, backups/restore and retention ownership documented before protected-data release.
- Evidence: exact commands and exit codes, tests actually executed, case statuses/counts, failures/skips/blocks, artifacts and reviewer approvals recorded. No zero-test or formatter-only readiness claim.

## 7. Execution record and ownership

Each run should record build commit/source digest, UTC timestamp, mode, fixture/policy/schema version, device/OS/browser, network profile, command/runner and exit code, intended and executed counts, actual result per QA ID, evidence path, defect ID, tester and reviewer. Physical results additionally need board/watch/phone/firmware IDs, power state, environmental conditions and measured observations. Do not attach real worker health data to the repository.

Use `qa-cases.csv` as the editable test sheet, `engineering-tasks.csv` for ownership/dependencies and `requirements-traceability.csv` to audit coverage. Test statuses remain Not run until the relevant target behavior is implemented and exercised. The pack's document checks validate traceability and export integrity, not target application compliance.

## 8. Regression and rollout

Start with the existing engine/forecast/emergency invariants and current UI SDK controls. Replace tests whose expectations intentionally change (five-person suppression, worker tabs, unnamed single-session help) with explicit new-product tests. Do not weaken assertions to preserve a green suite. Review a source change and a requirement change together when they alter accepted behavior.

For a synthetic build, run the core/API suite and real browser suite plus the targeted V1 cases that exist. Before protected-data/physical rollout, add the security, storage, gateway and hardware suites and complete reviewer gates. Use a feature-gated synthetic mode, versioned migrations, reversible deployment and a rollback that does not erase queued emergencies. Validate restore and reconciliation before declaring the physical/pilot release ready.

## 9. Existing prototype baseline executed for this package

On 19 November 2026, `npm test` completed successfully: the build passed and 23 existing Python tests passed. `npm run test:browser` also completed successfully: the build passed and 22 existing Chromium workflow checks passed. Both commands returned exit status 0. Logs, source hashes and the checked Git HEAD are in `baseline/` beside this document.

These checks exercised the current synthetic prototype. They do not complete QA01–QA48 or establish the new supervisor V1 requirements. In particular, current code still uses anonymous in-memory sessions, a five-person suppression fixture, private worker tabs, no multi-crew grouping, no named durable emergency service, no persistent crew/watch setup and no actual BLE gateway/watch. The current forecast is a short synthetic scenario by default, not the new complete today/tomorrow site-local planning view.

Readiness conclusion: regression baseline passes; the new dashboard remains to be implemented and accepted. Physical, policy and real-data gates remain open. The new requirement/task/test pack has its own document-consistency checks, which must not be confused with application or field validation.
