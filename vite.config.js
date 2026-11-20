import { defineConfig } from 'vite';

export default defineConfig(async () => {
  const onCloudflare = process.env.EXACLIM_CLOUDFLARE === '1';
  const plugins = onCloudflare
    ? (await import('@cloudflare/vite-plugin')).cloudflare({ remoteBindings: false, inspectorPort: false })
    : [];
  return {
    root: '.',
    plugins,
    server: onCloudflare
      ? { port: 8787 }
      : { port: 5173, proxy: { '/api': 'http://127.0.0.1:8000' } },
    build: {
      outDir: 'dist',
      emptyOutDir: true,
      rollupOptions: {
        output: {
          entryFileNames: 'app.js',
          chunkFileNames: 'assets/[name]-[hash].js',
          assetFileNames: asset => asset.names.some(name => name.endsWith('.css')) ? 'styles.css' : 'assets/[name]-[hash][extname]',
        },
      },
    },
  };
});
