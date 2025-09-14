import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://localhost',
        changeOrigin: true,
        rewrite: (path) => path,
      },
    },
  },
  build: {
    sourcemap: true,
    outDir: resolve(__dirname, '../src/student_auth/accounts/static/build'),
    emptyOutDir: false,
    rollupOptions: {
      input: {
        start: resolve(__dirname, 'src/pages/start.ts'),
        contest: resolve(__dirname, 'src/pages/contest.ts'),
        admin: resolve(__dirname, 'src/pages/admin.ts'),
        admin_dashboard: resolve(__dirname, 'src/pages/admin_dashboard.ts'),
        create_contest: resolve(__dirname, 'src/pages/create_contest.ts'),
        delete_contest: resolve(__dirname, 'src/pages/delete_contest.ts'),
        evaluation: resolve(__dirname, 'src/pages/evaluation.ts'),
        login: resolve(__dirname, 'src/pages/login.ts'),
        register: resolve(__dirname, 'src/pages/register.ts'),
        home: resolve(__dirname, 'src/pages/home.ts'),
      },
      output: {
        entryFileNames: (chunk) => `${chunk.name}.js`,
        chunkFileNames: 'chunks/[name].js',
        assetFileNames: (asset) => {
          if (asset.name && asset.name.endsWith('.css')) return 'styles/[name][extname]'
          return 'assets/[name][extname]'
        },
      },
    },
  },
})
