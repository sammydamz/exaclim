# Exaclim

Use the existing checkout; do not create worktrees unless requested. The product name is Exaclim everywhere.

Frontend components and interactions use `@ui-sdk/core` with the same-version `@ui-sdk/web` adapter. Before UI changes, follow `node_modules/@ui-sdk/core/skills/ui-sdk/SKILL.md` and the installed Web Components documentation. Read only relevant component pages. Do not hand-roll controls the SDK provides. Use Web Awesome `wa-card` for card surfaces; do not create custom card components. New components must come from an installed library. Keep product copy concise and avoid em dashes or repeated demo disclaimers. Label sample forecast data once at its source. Keep reusable parts in `web/components/`, and preserve source provenance and emergency priority.

Run `npm ci`, `npm test`, and, for interface changes, `npm run test:browser`. The deployed backend is Hono + TypeScript in `cloudflare/`, running on Workers with D1 via the new cf CLI. Python in `exaclim/` is a local reference. Run `npm run test:cloudflare-domain` and type checking for deployed API changes. Frontend entry is root `index.html`; Vite builds local assets into ignored `dist/`. Do not check in node_modules, generated caches, or real worker information.

## Deel-inspired design reference

Before visual design changes, also read `.agents/skills/deel/SKILL.md` and `docs/design/deel-reference.md`. The installed skill is community-authored guidance, not an official Deel library. The user's supplied Deel screenshots and accessibility requirements take precedence over contradictory extracted tokens. Keep UI SDK components for behavior; use the Deel reference for visual treatment. Preserve Exaclim branding, heat-risk semantics and all existing safety behavior.
