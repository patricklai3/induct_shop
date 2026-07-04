import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'
import path from 'path'

export default defineConfig({
  define: {
    'process.env.NODE_ENV': '"production"'
  },
  plugins: [
    frappeui({
      frappeProxy: false,
      jinjaBootData: false,
      buildConfig: false,
    }),
    vue(),
  ],
  build: {
    outDir: path.resolve(__dirname, '../induct_shop/public/js'),
    emptyOutDir: false, // Don't empty public/js, there are other files like project.js
    lib: {
      entry: path.resolve(__dirname, 'src/service_parts_selector.js'),
      name: 'ServicePartsSelectorBundle',
      formats: ['iife'],
      fileName: () => 'service_parts_selector.bundle.js'
    },
    rollupOptions: {
      output: {
        assetFileNames: (assetInfo) => {
          if (assetInfo.name === 'style.css') return 'service_parts_selector.bundle.css';
          return assetInfo.name;
        }
      }
    }
  },
  optimizeDeps: {
    exclude: ['frappe-ui'],
    include: [
      'feather-icons',
      'tippy.js',
      'engine.io-client',
      'socket.io-client',
      'debug',
    ],
  },
})
