import { bindings, defineConfig } from 'cf/config';
import * as entrypoint from './cloudflare/worker.ts' with { type: 'cf-worker' };

// Resource names are resolved by cf; no fabricated account/database IDs.
export default defineConfig({
  worker: {
    name: 'exaclim',
    entrypoint,
    compatibilityDate: '2026-11-19',
    env: {
      DB: bindings.d1({ name: 'exaclim-demo' }),
      ASSETS: bindings.assets(),
      EXACLIM_MODE: bindings.text('demo'),
    },
    assets: { runWorkerFirst: true, notFoundHandling: 'none' },
  },
});
