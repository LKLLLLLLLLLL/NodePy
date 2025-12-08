import vue from '@vitejs/plugin-vue'
import type { ServerResponse } from 'http'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default ({ mode }: { mode: string }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiUrl = env.VITE_API_URL || 'http://localhost:8000'

  const basePath = mode === 'production' ? '/static/' : '/'

  return defineConfig({
    base: basePath,
    plugins: [
      vue(),
      vueDevTools(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: apiUrl,
          changeOrigin: true,
          secure: false,
          configure: (proxy, options) => {
            // 添加错误处理，当目标服务器不可用时返回 503
            proxy.on('error', (err, req, res) => {
              // 类型断言为 ServerResponse，避免 TypeScript 错误
              const response = res as ServerResponse
              response.writeHead(503, { 'Content-Type': 'application/json' })
              response.end(JSON.stringify({ error: 'Service Unavailable', message: '服务器未启动或网络连接失败' }))
            })
          }
        }
      }
    }
  })
}
