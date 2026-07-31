import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'
import path from 'path'

export default defineConfig({
  plugins: [
    frappeui({
      frappeProxy: true,
      jinjaBootData: true,
      buildConfig: {
        indexHtmlPath: '../induct_shop/www/frontend.html',
      },
    }),
    vue(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  optimizeDeps: {
    // frappe-ui ships unbuilt source with `~icons/lucide/*` virtual imports
    // that esbuild's prebundler cannot resolve. Skip prebundling for it; the
    // frappeui vite plugin handles the icon resolution at request time.
    exclude: ['frappe-ui'],
    // After excluding frappe-ui, its transitive CJS deps still need to be
    // converted to ESM for the browser — list them explicitly so Vite
    // prebundles them.
    include: [
      'feather-icons',
      'tippy.js',
      'showdown',
      'engine.io-client',
      'socket.io-client',
      'debug',
    ],
  },
  build: {
    outDir: '../induct_shop/public/frontend',
    emptyOutDir: true,
    target: 'es2022',
  },
})
