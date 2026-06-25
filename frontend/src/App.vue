<template>
  <div class="min-h-screen bg-white text-slate-800 flex flex-col">
    <header v-if="$route.name !== 'Auth'" class="app-header">
      <div class="app-header__brand">
        <img :src="logoBlack" alt="살만해" />
      </div>
      <nav class="app-header__nav">
        <RouterLink to="/" class="app-header__link" active-class="app-header__link--active">지도</RouterLink>
        <RouterLink to="/chat" class="app-header__link" active-class="app-header__link--active">챗봇</RouterLink>
      </nav>
      <div class="app-header__right">
        <template v-if="auth.isLoggedIn">
          <button class="app-header__cta" @click="handleLogout">로그아웃</button>
        </template>
        <template v-else>
          <RouterLink to="/login" class="app-header__cta">로그인</RouterLink>
        </template>
      </div>
    </header>

    <main :class="['flex-1', !['Auth', 'Chatbot'].includes($route.name) && 'max-w-7xl w-full mx-auto p-4']">
      <router-view />
    </main>

    <footer v-if="!['Auth', 'Chatbot'].includes($route.name)" class="bg-white border-t border-slate-200 py-4 px-4 text-center">
      <p class="text-xs text-slate-400">© 2026 살만해.</p>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import logoBlack from '@/assets/logo-black.png'
import { useAuthStore } from '@/store/authStore.js'

const router = useRouter()
const auth = useAuthStore()

async function handleLogout() {
  await auth.logout()
  router.push('/')
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: #ffffff;
  padding: 8px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-header__brand img {
  height: 34px;
  width: auto;
  display: block;
}

.app-header__nav {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  background: #f4f4f6;
  border-radius: 10px;
  padding: 3px;
  gap: 2px;
}

.app-header__link {
  font-size: 13px;
  font-weight: 500;
  color: rgba(13, 17, 16, 0.5);
  text-decoration: none;
  padding: 4px 14px;
  border-radius: 7px;
  transition: color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
  white-space: nowrap;
}
.app-header__link:hover {
  color: #0d1110;
}
.app-header__link--active {
  background: #ffffff;
  color: #0d1110;
  font-weight: 700;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.app-header__right {
  display: flex;
  align-items: center;
}

.app-header__cta {
  padding: 5px 14px;
  background: #0d1110;
  color: #ffffff;
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  border-radius: 999px;
  transition: background 0.15s ease;
}
.app-header__cta:hover {
  background: #374151;
}
button.app-header__cta {
  border: none;
  cursor: pointer;
  font-family: inherit;
}
</style>
