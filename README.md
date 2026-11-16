# Exaclim

Worker heat-risk research prototype for the Climate-Resilient Worker Health challenge. The crew dashboard and private badge simulator use explicitly synthetic data.

Frontend components and interactions are built on **`@ui-sdk/core` with `@ui-sdk/web`**, pinned to the same version. Vite bundles the frontend; the Python standard-library service provides the scenario API and serves the build.

This is an illustrative workflow demonstrator, not a validated occupational safety instrument. The index is not WBGT, core temperature, a safe work allowance or a medical prediction.

## Setup and run

Requires Node.js 22.12+ and Python 3.12+. Use the existing checkout.

```sh
cd /workspace/exaclim
npm ci
npm run build
npm start
```

The Python server binds to loopback port 8000. Use a local development browser; no public deployment is configured. Never enter real worker data.

For frontend development, leave the Python service running and start Vite in another terminal:

```sh
npm run dev
```

Vite runs on port 5173 and proxies `/api` to the Python service. A production-style run uses `npm run build` followed by `npm start`.

## UI foundation

- Component registration and shared helpers: `web/components/ui.js`.
- Application markup: `web/index.html`.
- Scenario/API orchestration: `web/app.js`.
- Shared UI SDK theme tokens and Exaclim layout: `web/styles.css`.
- UI SDK handles tabs, button actions/pending state, number fields, selects, checkbox, switch, meter, and the reset alert dialog.
- `exaclim.agent` exposes the SDK bridge in the browser for local component inspection and tests. No model or external agent service is connected automatically.

Read `AGENTS.md` and the installed SDK skill before changing components. Import each component from its own entry. Use SDK `action` / `valuechange` / `checkedchange` events and controller APIs rather than hand-written interaction roles.

## Validation

```sh
npm test
```

This builds the UI and runs 23 Python unit/integration tests. The backend implementation lives in `exaclim/`.

Real-browser validation requires the optional Playwright dependency and Chromium (`/usr/bin/chromium` in this environment):

```sh
python3 -m pip install -r requirements-browser.txt
npm run test:browser
```

The browser script manages its own temporary server. It checks actual scenario flows, emergency retention, offline/reconnection behavior, dialog cancel/confirm/focus, SDK keyboard navigation, required fields, SDK agent actions, contrast tokens and phone layout.

## Demonstration boundaries

- Crew counts are independent synthetic fixtures, suppressed below five workers. They do not aggregate the private badge sessions.
- Badge sessions use a random HttpOnly, SameSite cookie. State lives in server memory and expires after eight hours of inactivity. This is not production authentication or authorization.
- Help latches emergency state. Acknowledgement or cooler inputs cannot clear it. The reset dialog clears only the synthetic session; it does not resolve a real incident.
- The open page demonstrates offline fallback and pending-help retries. It is not an offline-installable PWA or badge firmware. Server restarts and cookie loss lose server session state.
- Forecast defaults to a labeled fixture. `/api/forecast?mode=live` attempts Open-Meteo and explicitly labels synthetic fallback when unavailable. Current managed networking blocks live access. Adapter tests use mocked responses; no live-data success is claimed.
- English and draft French messages are implemented. Reviewed Twi, voice, SMS, physical devices, a trained personal heat-strain model and clinical validation are not implemented.
- UI SDK uses runtime layout styles, so the local server's CSP permits inline styles while keeping scripts restricted to local bundles. Do not treat this demonstration as deployment hardening.

## Reports and PDFs

Editable job reports are in `docs/jobs/`, with validation evidence in `docs/evidence/`.

```sh
python3 -m pip install -r requirements-pdf.txt
python3 scripts/export_pdfs.py --output /workspace/artifacts/exaclim-jobs
```

PDF dependencies are independent of the application. Supplier budget figures remain internal allowances, not verified quotes. Project licensing has not been selected; UI SDK's own license remains with its package. Open-Meteo data requires attribution and its current usage terms apply.
