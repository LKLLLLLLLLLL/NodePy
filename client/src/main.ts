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

