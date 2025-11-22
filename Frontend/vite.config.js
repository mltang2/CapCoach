import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/CapCoach',
  build: {
    // Put the static build at the repo root so GitHub Pages "docs/" source can find it
    outDir: '../docs'
  }
})
