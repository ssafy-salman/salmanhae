import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/main.css'
import { useAuthStore } from './store/authStore.js'
import { useChatSessionStore } from './store/chatSessionStore.js'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

useAuthStore().restoreSession()
useChatSessionStore().restoreSessions()

app.mount('#app')
