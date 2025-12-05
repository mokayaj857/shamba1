import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      // This ensures React Refresh works properly
      jsxRuntime: 'classic',
      // Enable fast refresh
      fastRefresh: true,
    })
  ],
  define: {
    global: 'globalThis',
    // Prevent ethereum provider conflicts
    'window.ethereum': 'window.ethereum',
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      // Ensure single React instance
      'react': fileURLToPath(new URL('./node_modules/react', import.meta.url)),
      'react-dom': fileURLToPath(new URL('./node_modules/react-dom', import.meta.url)),
      'react-i18next': fileURLToPath(new URL('./node_modules/react-i18next', import.meta.url)),
    },
  },
  optimizeDeps: {
    esbuildOptions: {
      define: {
        global: 'globalThis',
      },
    },
    // Force include these to prevent multiple instances
    include: [
      'react',
      'react-dom',
      'react-i18next',
      'i18next',
      'i18next-browser-languagedetector',
    ],
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    commonjsOptions: {
      include: [/node_modules/],
      transformMixedEsModules: true,
    },
  },
})
