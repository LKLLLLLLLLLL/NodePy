import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ModalManager from './ModalManager.vue'
import App from './App.vue'

const pinia = createPinia()

const app = createApp(App)
app.component('ModalManager', ModalManager)
app.use(pinia)
app.mount('#app')

