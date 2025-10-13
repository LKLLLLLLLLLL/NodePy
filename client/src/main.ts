import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ModalManager from './ModalManager.vue'
import App from './App.vue'

const pinia = createPinia()

const app = createApp(App)
app.use(pinia)
app.mount('#app')

const modalManager = createApp(ModalManager)
modalManager.use(pinia)
modalManager.mount('#modal')