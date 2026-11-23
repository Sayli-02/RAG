import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/auth': proxyApi(),
      '/documents': proxyApi(),
      '/assistant': proxyApi(),
      '/comparison': proxyApi(),
      '/research': proxyApi(),
      '/compliance': proxyApi(),
      '/analytics': proxyApi(),
      '/evaluation': proxyApi(),
      '/health': proxyApi(),
    },
  },
})

function proxyApi() {
  return {
    target: 'http://127.0.0.1:8000',
    bypass(req) {
      // Browser navigations ask for HTML. Those stay in the React app.
      const accept = req.headers.accept || ''
      if (req.method === 'GET' && accept.includes('text/html')) {
        return '/index.html'
      }
    },
  }
}

