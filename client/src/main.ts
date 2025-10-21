import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ModalManager from './ModalManager.vue'
import App from './App.vue'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

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
app.use(pinia)

app.mount('#app')

