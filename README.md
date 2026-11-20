# Exaclim

Supervisor heat-risk dashboard for the Climate-Resilient Worker Health challenge.

Live synthetic demo: https://exaclim.kasalite-business.workers.dev

Sign in: **demo@exaclim.test** / **Exaclim2026!**. Use fictional data only.

## Stack and run

The deployed API uses **Hono + TypeScript + Cloudflare Workers + D1**. Workers assets serve the Vite frontend. Components and interactions use matching versions of `@ui-sdk/core` and `@ui-sdk/web`, with a Deel-inspired visual treatment. Cards and status badges use Web Awesome library components. Notifications use UI SDK Toast. Custom replacement components and decorative action icons are prohibited. Deployment uses the new **cf CLI**.

```sh
npm ci
npm run cloudflare:dev
```

Open http://127.0.0.1:8787. Use Node 24.22+ (the verified environment uses 24.22.1). Cloudflare setup, persistence and deployment details are in [the deployment guide](docs/demo/cloudflare.md).

```sh
npm run cloudflare:check
npm run deploy
```

Authentication must already be configured for your Cloudflare account. The scripts use `XDG_CONFIG_HOME=/workspace/.config`; adjust this path for another machine. Never commit Cloudflare credentials.

## Dashboard behavior

The supervisor view contains today's/tomorrow's forecast, privacy-grouped crew status and break/rotation suggestions. Setup supports sites, crews and synthetic watch assignment. Demo controls exercise rising heat, stale connections, reconnect, help and delayed delivery.

Routine groups require at least three contributors; smaller crews are combined without overlapping members. Named help is the identity exception. Acknowledgement removes the pending banner only after a durable server receipt, and retains the unresolved group's Red state. Offline help delivery is simulated through a persisted outbox. Stale readings remain cautious.

All forecasts, workers, watches and delivery events are synthetic. The illustrative model is not WBGT, core temperature, a clinical prediction or a validated safe work allowance. Physical watches, Bluetooth integration, native gateway, live weather, reviewed translations and clinical validation remain outside this demo. R2 is not provisioned because this version has no uploaded-file workflow.

## Source and checks

- `index.html`, `web/app.js`, `web/styles.css`, `web/components/ui.js`: frontend.
- `cloudflare/worker.ts`: Hono routes, authentication, D1 and asset delivery.
- `cloudflare/domain.ts`: privacy grouping, synthetic forecasting and alert behavior.
- `cloudflare.config.ts`: cf deployment and resource bindings.
- `exaclim/`: Python reference implementation and original research engine; Python is not deployed.

```sh
npm test
npm run test:cloudflare-domain
python3 scripts/check_cloudflare.py --base-url http://127.0.0.1:8787
python3 scripts/check_dashboard_v1.py --base-url http://127.0.0.1:8787 --backend-label 'Hono + Workers + D1'
```

Browser checks require `requirements-browser.txt` and Chromium. The harness can also start the Python reference server with `npm run test:browser`. Read `AGENTS.md` before interface changes.

## Reports

The [PRD, engineering sheet and planned acceptance cases](docs/dashboard-v1/README.md) define the target. Executed software checks cover part of that plan; they do not establish physical-device or field validation. Research reports are in `docs/jobs/`; demo guidance is in `docs/demo/`. Supplier budget figures remain allowances rather than verified quotes.
