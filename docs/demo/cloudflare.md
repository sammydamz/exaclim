# Exaclim on Cloudflare Workers

This backend runs Hono and TypeScript on Workers with D1 persistence. It serves the Vite frontend through the Workers assets binding. Python remains a local reference implementation and is not part of the deployed runtime.

Use Node 24.22 or newer and the repository's pinned **new `cf` CLI**. No Wrangler configuration or command is needed.

```sh
npm ci
npm run cloudflare:dev
```

The local address is `http://127.0.0.1:8787`. Sign in with the synthetic account `demo@exaclim.test` / `Exaclim2026!`. All names, watches, forecasts and help events are synthetic. Local D1 is seeded idempotently on the first protected API request; existing state is retained. Resource names in `cloudflare.config.ts` are resolved by `cf`, rather than using invented account or database IDs.

```sh
npx tsc --noEmit -p cloudflare/tsconfig.json
npm run test:cloudflare-domain
python3 scripts/check_cloudflare.py --base-url http://127.0.0.1:8787
npm run cloudflare:build
```

The HTTP checker changes synthetic scenarios, verifies concurrent acknowledgement and disconnected help delivery, then restores normal heat state and signs out. It does not reset existing crews or delete historical help events. To check persistence, acknowledge a synthetic event, stop and restart the same local `cf dev` process using its existing local storage, then sign in and confirm that the event remains acknowledged and its unresolved group remains Red.

The Worker creates tables matching `cloudflare/schema.sql`: a versioned dashboard document, salted PBKDF2 demo identity, supervisor site grants, hashed sessions, and login attempt counters. Document writes use revision compare-and-swap with bounded retries so overlapping updates cannot silently overwrite each other. Acknowledgement preserves the first actor and timestamp and does not resolve help. Sessions expire after 12 hours; HTTPS cookies are Secure, HttpOnly and SameSite Strict. Mutations enforce same-origin checks and bounded allowlisted JSON. Static responses allow only local scripts, fonts and connections; inline styles support UI SDK runtime styling.

`EXACLIM_MODE` must equal `demo`; other values fail closed. This fixed-account implementation is for synthetic demonstrations. It is not a real-worker identity provider or physical watch/gateway deployment. No actual Bluetooth delivery, live weather or clinical effectiveness is claimed.

Deployed on 20 November 2026 using the authorized Cloudflare account and the new cf CLI. Live URL: https://exaclim.kasalite-business.workers.dev . The CLI provisioned D1 `exaclim-demo`; frontend assets and the Hono API run in Worker `exaclim`. No R2 bucket is needed for this demo. The deployment dry run, TypeScript check and local Workers/D1 HTTP and browser checks passed. The remote HTTP checker also passed authentication, authorization, grouping, concurrent acknowledgement and offline delivery.
