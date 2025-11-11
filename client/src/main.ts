//basic
import { createApp } from 'vue'
import router from './router/index.ts'
import ModalManager from './ModalManager.vue'
import App from './App.vue'

//pinia
import { createPinia } from 'pinia'

//vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

//element-plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

//authenticated service factory
import AuthenticatedServiceFactory from './utils/api/services/AuthenticatedServiceFactory.ts'

/**
 * 应用启动初始化
 */
console.group('应用启动初始化');
console.log('环境:', import.meta.env.MODE);

// 开发环境特殊处理
if (import.meta.env.DEV) {
  console.log('开发模式：刷新认证服务以确保使用最新API');
  
  // 关键调用：刷新认证服务
  AuthenticatedServiceFactory.refreshService();
  
  console.log('认证服务已更新到最新版本');
  
  // 开发环境额外提示
  console.log('开发提示:');
  console.log('   - 在控制台输入 AuthenticatedServiceFactory.devRefresh() 手动刷新服务');
  console.log('   - 输入 AuthenticatedServiceFactory.getServiceStatus() 查看服务状态');
} else {
  console.log('生产模式：使用缓存的服务实例');
}

console.groupEnd();

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
})

const pinia = createPinia()

const app = createApp(App)

app.component('ModalManager', ModalManager)

app.use(vuetify)
app.use(ElementPlus)
app.use(router)
app.use(pinia)

app.mount('#app')

