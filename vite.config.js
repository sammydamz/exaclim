import { defineConfig } from 'vite';

export default defineConfig({
  root: 'web',
  server: { port: 5173, proxy: { '/api': 'http://127.0.0.1:8000' } },
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'app.js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: asset => asset.names.some(name => name.endsWith('.css')) ? 'styles.css' : 'assets/[name]-[hash][extname]',
      },
    },
  },
});
