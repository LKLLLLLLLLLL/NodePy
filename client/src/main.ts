import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ModalManager from './ModalManager.vue'
import App from './App.vue'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const vuetify = createVuetify({
  components,
  directives,
})

const pinia = createPinia()

const app = createApp(App)

app.component('ModalManager', ModalManager)

app.use(vuetify)
app.use(ElementPlus)
app.use(pinia)

app.mount('#app')

