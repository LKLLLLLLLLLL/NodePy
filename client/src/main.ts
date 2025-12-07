// 引入全局样式
import './common/node.scss'

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
import AuthenticatedServiceFactory from './utils/AuthenticatedServiceFactory.ts'

// 开发环境特殊处理
if (import.meta.env.DEV) {

  // 关键调用：刷新认证服务
  AuthenticatedServiceFactory.refreshService();

} else {
  console.log('生产模式：使用缓存的服务实例');
}

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

