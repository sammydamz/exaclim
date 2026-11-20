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

## Interface copy and library component update

20 November 2026: replaced custom main, crew, recommendation and emergency card surfaces with Web Awesome `wa-card`; status badges and the account avatar also use Web Awesome. UI SDK continues to own interactive controls. Removed repeated demo notices, em dashes, slogans and visible policy identifiers. A single “Sample forecast” source label remains. Stale readings, group privacy and help acknowledgement behavior remain visible. Setup now finishes loading before opening, preventing an in-flight response from overwriting edits.

`npm test` passed 72 tests (exit 0). `npm run test:browser` passed all 25 checks (exit 0), including library card registration, concise copy, mobile layout, setup persistence and emergency flows. Strict Cloudflare TypeScript checking passed (exit 0). Updated screenshots and results: `docs/evidence/ui-copy-refresh/`.

Updated Cloudflare deployment version: `3d623cb1-c421-4c25-ab91-a33caa465249`. `npm run deploy` completed with exit 0.
