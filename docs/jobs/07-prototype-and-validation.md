# Job 07 — Working prototype and validation handover

Prepared 16 November 2026. Status: working local software prototype, demonstrated with synthetic scenarios. Demo recording and presentation production are reserved for the next stage.

## What has been built

The repository contains a responsive crew dashboard, a separate private badge simulator, a deterministic risk engine, a weather forecast adapter, explicit synthetic fixtures, server-enforced emergency state and reproducible tests. Python serves the application using its standard library; HTML, CSS and JavaScript now use @ui-sdk/core and the same-version @ui-sdk/web adapter, bundled locally with Vite. No CDN resources are required. All interactive controls use SDK parts and controller events.

The crew page displays independent synthetic aggregate counts and suppresses them below five workers. It deliberately does not derive the displayed crew from private worker sessions. This proves the demonstration's separation, not real-world anonymization or a production aggregation system. The badge page allows temperature, humidity, declared workload, clothing, acclimatization, duration and sensor age to change. It displays a level, illustrative index, action, input quality and reasons.

The optional look-ahead calculates six future synthetic scenario points and may raise the warning above the present baseline. Its threshold-crossing time is not a medical lead time or safe remaining work duration. The dashboard's scheduling recommendation is a fixed synthetic scenario recommendation, not a validated optimization algorithm.

English messages are implemented. An optional French draft message demonstrates the second-language path; it needs field-language review. Twi and audio are not implemented. No SMS, real responder notification, BLE radio, physical badge or station is connected.

## How to run

From the repository root, with Node.js 22.12+ and Python 3.12+:

```sh
npm ci
npm run build
npm start
```

The server binds to loopback. Use a local development browser on port 8000; no public deployment or cloud preview link is configured. The current cloud instance has been started and exercised with functional requests and actual browser interactions. Future tasks must restart the process; publication does not preserve running processes.

Core validation:

```sh
npm test
```

Optional real-browser checks, with Playwright and Chromium installed:

```sh
python3 -m pip install -r requirements-browser.txt
npm run test:browser
```

PDF export is independent of application startup and uses the optional `requirements-pdf.txt` dependency:

```sh
python3 scripts/export_pdfs.py --output /workspace/artifacts/exaclim-jobs
```

## Executed validation results

The latest recorded run completed **23 Python unittest tests, all passing**, and **22 real Chromium browser checks, all passing**. JavaScript syntax checking also passed. These are software tests, not human studies or field-device tests. No test was skipped in those recorded runs.

| Executed check group | Evidence established |
|---|---|
| Engine: 10 unit tests | Explainable scores, hot conditions, input limits including huge integers, exact severity and freshness boundaries, workload/PPE effects, emergency priority, forecast escalation and conservative floor |
| Forecast adapter: 3 unit tests | Parsing and provenance using mocked provider responses, rejected expired/misaligned/null/nonfinite data; no live-service success implied |
| Server: 10 integration tests | Session isolation, crew suppression/independence, stale age progression, invalid/malformed requests, cross-origin rejection, emergency cannot be cleared by ACK or forged lower state, optional projection and static application responses |
| Chromium: 22 interaction checks | Routine/hot/stale behavior, suppression, emergency retention, French message display, projection wording, offline help/reconnection, page reload, help during delayed evaluation, responsive views, SDK keyboard and agent actions, reset-dialog focus, contrast tokens and no unexpected browser/CSP errors |
| Actual weather request | Live provider unavailable under current managed network; explicit `synthetic-fallback` returned with no live fetch time |

The browser checks count twenty-two named workflow assertions, not twenty-two separate clinical cases. A browser reload retaining an emergency uses the same live server session; it does not prove persistence across a server restart or lost cookie. The 390px viewport checks absence of horizontal overflow across all three views, not a full accessibility certification.

Reproducible evidence files: `docs/evidence/software-tests.txt`, `browser-checks.txt`, `javascript-syntax.txt`, `live-forecast-check.json`, and `manifest.json`. The manifest records source-file SHA-256 hashes and the executed commands. It identifies the workspace contents tested without implying a Git push or published deployment.

## Emergency and missing-data behavior

A help action immediately latches an emergency in the browser and sends a request to the server. The help control remains usable while another scenario request is pending. A failed help transmission is stored as a pending flag in session storage and retried on reconnection/refresh. The UI says delivery is unconfirmed and directs use of the site's existing emergency procedure. A successful request records software state only; it does not contact responders.

The server ignores client attempts to assert a lower trusted previous state. An explicit `emergency: true` may raise severity, but a false flag cannot clear it. Acknowledge records receipt only. Only the prominently labeled synthetic-session reset, confirmed through the SDK alert dialog, clears the demonstration latch. Cancel and Escape preserve the state and return focus to the reset trigger.

Required malformed measurements return a cautious state rather than a reassuring number. Readings older than 120 seconds cannot produce green. The server advances reading age with elapsed monotonic time and the browser refreshes worker state every fifteen seconds. A browser offline event displays at least amber and preserves an earlier red/emergency display.

This application is not an installable offline PWA and does not implement production badge firmware. Its already-open page can demonstrate lost-connectivity behavior; loading the entire application for the first time without its local server is not supported.

## Privacy and security boundary

No real worker data is needed or permitted in this demonstration. The server uses a random HttpOnly, SameSite cookie to separate synthetic sessions and serves only allowlisted static files. JSON responses are non-cacheable; scripts/assets are local; no analytics is included. The in-memory state expires after eight hours of inactivity. Cookie/session loss or a server restart loses that state. Browser pending-help storage is not hardware nonvolatile storage or a complete incident record.

A worker tab and a crew tab are not production role authorization. Anyone using the same browser session can access its synthetic worker view. Deployment needs authenticated roles, reviewed authorization, encrypted transport/storage as appropriate, data lifecycle controls, access auditing and a lawful governance process. The minimum crew size of five is a demonstration choice, not a guarantee against reidentification or differencing.

## What is ready for the next stage

Seven independent reports and editable sources, working synthetic software, model and API implementation, hardware communication/design specification, a transparently unquoted planning BOM, reproducible software tests and PDF export tooling are prepared. Use these to produce an honest recorded walkthrough and final presentation. Demo production itself is intentionally left unrecorded.

External evidence is still outstanding: verified supplier quotes and stock, direct review of selected occupational guidance and current competitor claims, reviewed Ghanaian-language content, a named pilot partner, expert validation and the applicable ethics/legal determinations. Physical testing and real health/productivity results belong to the post-hackathon deployment plan. Do not describe the entry as field validated or the planning budget as supplier quoted.

Live research access is restricted in the current runtime. Domain additions have been saved to the environment draft, but saving a draft is not runtime activation or publication. This package remains usable with labeled synthetic data; no unverified source claim is needed to run it.

## Exaclim UI SDK migration

The product, Python module, interface, report titles and export paths now use Exaclim. Core and Web Components adapter are pinned to 0.1.0-beta.3, the installed npm latest release. Vite bundles all browser dependencies locally. The browser agent bridge is tested against named controls and discoverable choices; no model service or WebMCP tools are connected automatically.

The SDK owns keyboard focus, ARIA relationships, popup dismissal and component change semantics. Application code owns the synthetic scenario and emergency rules. Shared tokens and component registration establish the base for subsequent site/dashboard design work; this is not a claim that the visual design is final.
