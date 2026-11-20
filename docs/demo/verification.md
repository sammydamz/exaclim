# Executed software checks — 20 November 2026

Live deployment: https://exaclim.kasalite-business.workers.dev

Runtime: Hono + TypeScript + Workers, persisted D1 `exaclim-demo`, Workers static assets. Deployed using cf CLI. Version: `6a7ce771-f364-47ac-99df-3c2334df9476`.

- 72 Python reference, API and persistence tests passed.
- 16 TypeScript domain tests passed.
- TypeScript strict check and cf deployment dry run passed.
- Local Workers/D1 API smoke checks passed.
- Local Workers/D1 browser harness: 25 passed, zero failures.
- Remote API smoke checks passed, including authorization, private-field rejection, concurrent acknowledgement and disconnected help replay.
- Remote Chromium harness: 25 passed, zero failures. Screenshots and machine-readable results are in `docs/evidence/dashboard-v1/`.

The managed environment requires an HTTPS proxy. The HTTP checker uses an explicit application user agent. Remote browser checks used the managed proxy and the explicit test-only `--ignore-https-errors` flag for its inspection certificate; normal application TLS settings are unchanged. The remote HTTP checker and curl succeeded with certificate checking enabled.

Tests used synthetic accounts and modified demo state. The site name and normal scenario were restored afterward; synthetic setup and acknowledged event history remain persisted in D1. Screenshot evidence reflects test-time data and freshness.

These executed checks cover part of the PRD acceptance plan. They do not establish all 48 planned cases, physical watch delivery, clinical accuracy, field usability or production identity management. See the PRD and demo runbook for those boundaries.
