# Exaclim

Use the existing checkout; do not create worktrees unless requested. The product name is Exaclim everywhere.

Frontend components and interactions use `@ui-sdk/core` with the same-version `@ui-sdk/web` adapter. Before UI changes, follow `node_modules/@ui-sdk/core/skills/ui-sdk/SKILL.md` and the installed Web Components documentation. Read only relevant component pages. Do not hand-roll controls the SDK provides. Keep reusable parts in `web/components/`, and preserve synthetic-data labels and emergency priority.

Run `npm ci`, `npm test`, and, for interface changes, `npm run test:browser`. Python backend is in `exaclim/`. The frontend is built with Vite into ignored `dist/`, which the local Python server serves. Do not check in node_modules, generated caches, or real worker information.
