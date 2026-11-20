# Exaclim — demo release checklist and capability record

Prepared 19 November 2026. **TO_VERIFY means a target exists, not an implemented or passed capability.** The release owner must replace it only after inspecting the final running build and record evidence. Old baseline tests do not establish the new dashboard's conformance.

## Release record

- Build/commit: TO_VERIFY
- Verification date and reviewer: TO_VERIFY
- Python/API suite result and evidence path: TO_VERIFY
- Browser suite result and evidence path: TO_VERIFY
- Three-minute rehearsal result: TO_VERIFY
- Local no-public-Internet rehearsal result: TO_VERIFY
- Known limitations accepted for synthetic demo: TO_VERIFY

Record actual pass/fail/skipped counts from the current run. Do not convert planned QA cases to “passed” because a similar older test succeeded. Do not present unmeasured PRD performance targets as achieved latency or capacity.

## Capability/source matrix

| Capability | Actual source/boundary to inspect | Status before release verification |
|---|---|---|
| Supervisor login and logout | Local backend session; published synthetic demo account only | TO_VERIFY |
| Three-area responsive dashboard | Built local web app using installed UI SDK; Deel-inspired presentation | TO_VERIFY |
| Today/tomorrow forecast | Synthetic scenario by default; any live adapter must show provider, site/timezone and source freshness | TO_VERIFY |
| Risk and work/rest advice | Versioned illustrative demo policy; no approved clinical thresholds | TO_VERIFY |
| Crew sizes 5 + 2 + 1 | Synthetic fixtures; smaller crews combined into stable non-overlapping group of three | TO_VERIFY |
| Routine identity privacy | Server responses and UI expose permitted aggregates; setup identities never join routine health values | TO_VERIFY |
| Named help and delayed help | Synthetic device events with occurrence/receipt provenance | TO_VERIFY |
| ACK persistence and Red help floor | Durable backend acknowledgement; independent unresolved-help state | TO_VERIFY |
| Resolution | Explicit simulator action standing in for trusted watch-local evidence | TO_VERIFY |
| Site coordinates/names, crew creation and watch assignment | Saved administrative records; synthetic devices only | TO_VERIFY |
| Data-connection failure and reconnect | Demo scenario; honest age/completeness and conservative state | TO_VERIFY |
| Local fallback | Prebuilt assets plus running local backend and synthetic forecast | TO_VERIFY |
| Physical watches / BLE gateway / independent watch alerts | Hardware/native gateway not implemented by this software demo | NOT IMPLEMENTED — disclose |
| Clinical validation / field battery, range, heat and dust qualification | No approved physical pilot or clinical outcome evidence | NOT VALIDATED — disclose |
| Trained personal heat-strain AI | No trained or clinically validated personal model claimed | NOT CLAIMED |

## Required rehearsal checks

- [ ] Sign-in works; unauthorized site requests are rejected; logout removes access and scoped UI state.
- [ ] Dashboard has only forecast, crews and suggestions as core areas; simulator is an explicit demo drawer.
- [ ] Today/tomorrow follow saved site timezone; source labels distinguish synthetic/live/cached and missing hours are Unknown/Caution.
- [ ] Crews of two and one have no standalone numeric routine risk rows; the three-person combined row does not overlap another row.
- [ ] Help reveals only the authorized response identity/context, not personal exposure, clothing, acclimatization or diagnoses.
- [ ] ACK is confirmed by the server, is idempotent, and cannot clear active-help Red floor; restart retains its durable record.
- [ ] Delayed help displays both occurrence and receipt times and remains actionable.
- [ ] Connection loss ages data honestly; reconnect does not make old readings fresh; pending ACK is not displayed as success.
- [ ] Named emergency information is not persisted in generic browser caches/storage.
- [ ] Site/crew/watch changes have explicit saved feedback and remain after reload.
- [ ] Setup does not send private watch-local issuance values to cloud endpoints.
- [ ] UI remains usable by keyboard and on the intended presentation/mobile sizes.
- [ ] Fresh local build runs with public Internet unavailable; offline login without the local backend is not promised.
- [ ] The recording uses the verified build and labels simulation, policy limitations and physical dependencies.

These checks are planned until executed. The root release owner should link current test artifacts and note any manual-only, skipped or failed item explicitly.

## Publication gate

A synthetic software demo may proceed with clearly disclosed unimplemented hardware and unvalidated clinical performance. A failed critical privacy, emergency-state, provenance or stale-data check blocks a claim that the software behavior is verified; fix it or explicitly narrow the demonstration and claim. No checklist entry authorizes real-worker use.

Before a physical pilot, the separate hardware, model, identity/security, governance, language, ethics and site-response gates in the PRD still apply. Demo readiness is not pilot approval.
