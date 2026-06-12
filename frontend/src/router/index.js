import { createRouter, createWebHistory } from 'vue-router'
import MapExplorer from '../views/MapExplorer.vue'
import Diagnosis from '../views/Diagnosis.vue'
import Community from '../views/Community.vue'
import Recommend from '../views/Recommend.vue'
import Chatbot from '../views/Chatbot.vue'

const routes = [
  { path: '/', name: 'MapExplorer', component: MapExplorer },
  { path: '/diagnosis', name: 'Diagnosis', component: Diagnosis },
  { path: '/recommend', name: 'Recommend', component: Recommend },
  { path: '/chat', name: 'Chatbot', component: Chatbot },
  { path: '/community', name: 'Community', component: Community }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

export default router
