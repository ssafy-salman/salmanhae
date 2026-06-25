import { createRouter, createWebHistory } from 'vue-router'
import MapExplorer from '../views/MapExplorer.vue'
import Diagnosis from '../views/Diagnosis.vue'
import Community from '../views/Community.vue'
import Recommend from '../views/Recommend.vue'
import Chatbot from '../views/Chatbot.vue'
import AuthView from '../views/AuthView.vue'
import { useAuthStore } from '../store/authStore.js'

const routes = [
  { path: '/', name: 'MapExplorer', component: MapExplorer },
  { path: '/login', name: 'Auth', component: AuthView },
  { path: '/diagnosis', name: 'Diagnosis', component: Diagnosis },
  { path: '/recommend', name: 'Recommend', component: Recommend },
  { path: '/chat', name: 'Chatbot', component: Chatbot, meta: { requiresAuth: true } },
  { path: '/community', name: 'Community', component: Community }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach((to, _, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
