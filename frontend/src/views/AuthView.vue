<template>
  <div class="scene">
    <img :src="heroHouse" alt="언덕 위 노란 집과 하얀 울타리" />
  </div>

  <header class="topnav">
    <div class="brand">
      <img :src="logoWhite" alt="살만해" />
    </div>
    <RouterLink to="/" class="back">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 12H5M12 19l-7-7 7-7" />
      </svg>
      이전으로
    </RouterLink>
  </header>

  <main class="stage">
    <div class="auth-card">
      <template v-if="mode === 'login'">
        <h2>로그인</h2>
        <p class="sub">계정에 로그인하고 이어서 둘러보세요</p>
        <form @submit.prevent="handleLogin">
          <div class="field">
            <label for="email">이메일</label>
            <div class="field-input">
              <input
                id="email"
                v-model="email"
                type="email"
                placeholder="you@example.com"
                autocomplete="email"
                required
              />
            </div>
          </div>
          <div class="field">
            <label for="password">비밀번호</label>
            <div class="field-input">
              <input
                id="password"
                v-model="password"
                :type="showPw ? 'text' : 'password'"
                placeholder="••••••••••"
                autocomplete="current-password"
                required
              />
              <button type="button" class="field-toggle" @click="showPw = !showPw" aria-label="비밀번호 표시 전환">
                {{ showPw ? '숨김' : '보기' }}
              </button>
            </div>
          </div>
          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
          <button type="submit" class="btn-submit" :disabled="loading">
            {{ loading ? '로그인 중…' : '로그인' }}
          </button>
        </form>
        <p class="signup-line">
          아직 계정이 없으신가요?
          <a href="#" @click.prevent="switchMode('register')">회원가입</a>
        </p>
      </template>

      <template v-else>
        <h2>회원가입</h2>
        <p class="sub">살만해에 가입하고 내 집 마련을 시작하세요</p>
        <form @submit.prevent="handleRegister">
          <div class="field">
            <label for="reg-name">이름</label>
            <div class="field-input">
              <input
                id="reg-name"
                v-model="name"
                type="text"
                placeholder="홍길동"
                autocomplete="name"
                required
              />
            </div>
          </div>
          <div class="field">
            <label for="reg-email">이메일</label>
            <div class="field-input">
              <input
                id="reg-email"
                v-model="email"
                type="email"
                placeholder="you@example.com"
                autocomplete="email"
                required
              />
            </div>
          </div>
          <div class="field">
            <label for="reg-password">비밀번호</label>
            <div class="field-input">
              <input
                id="reg-password"
                v-model="password"
                :type="showPw ? 'text' : 'password'"
                placeholder="8자 이상"
                autocomplete="new-password"
                minlength="8"
                required
              />
              <button type="button" class="field-toggle" @click="showPw = !showPw" aria-label="비밀번호 표시 전환">
                {{ showPw ? '숨김' : '보기' }}
              </button>
            </div>
          </div>
          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
          <button type="submit" class="btn-submit" :disabled="loading">
            {{ loading ? '가입 중…' : '회원가입' }}
          </button>
        </form>
        <p class="signup-line">
          이미 계정이 있으신가요?
          <a href="#" @click.prevent="switchMode('login')">로그인</a>
        </p>
      </template>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import heroHouse from '@/assets/hero_house.jpg'
import logoWhite from '@/assets/logo-white.png'

const router = useRouter()

const mode = ref('login')
const email = ref('')
const password = ref('')
const name = ref('')
const showPw = ref(false)
const loading = ref(false)
const errorMsg = ref('')

function switchMode(next) {
  mode.value = next
  email.value = ''
  password.value = ''
  name.value = ''
  showPw.value = false
  errorMsg.value = ''
}

async function handleLogin() {
  loading.value = true
  errorMsg.value = ''
  try {
    // TODO: useAuthStore().login({ email, password }) 연결
    router.push('/')
  } catch (e) {
    errorMsg.value = e?.response?.data?.message ?? '로그인에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  loading.value = true
  errorMsg.value = ''
  try {
    // TODO: useAuthStore().register({ name, email, password }) 연결
    switchMode('login')
  } catch (e) {
    errorMsg.value = e?.response?.data?.message ?? '회원가입에 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@font-face {
  font-family: 'Pretendard';
  src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/woff2/Pretendard-Regular.woff2') format('woff2');
  font-weight: 400;
}
@font-face {
  font-family: 'Pretendard';
  src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/woff2/Pretendard-Medium.woff2') format('woff2');
  font-weight: 500;
}
@font-face {
  font-family: 'Pretendard';
  src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/woff2/Pretendard-SemiBold.woff2') format('woff2');
  font-weight: 600;
}
@font-face {
  font-family: 'Pretendard';
  src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/woff2/Pretendard-Bold.woff2') format('woff2');
  font-weight: 700;
}
@font-face {
  font-family: 'Pretendard';
  src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/woff2/Pretendard-ExtraBold.woff2') format('woff2');
  font-weight: 800;
}

.scene {
  position: fixed;
  inset: 0;
  overflow: hidden;
  background: #cfe3ee;
  z-index: 0;
}
.scene img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 50% 50%;
  display: block;
}
.scene::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(6,12,11,.32) 0%, rgba(6,12,11,.04) 16%, rgba(8,16,14,.16) 55%, rgba(6,12,11,.6) 100%),
    linear-gradient(90deg, rgba(6,12,11,.14) 0%, rgba(6,12,11,0) 32%);
}

.topnav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 3;
  padding: 8px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.topnav .brand img {
  height: 34px;
  width: auto;
  display: block;
  filter: drop-shadow(0 1px 8px rgba(0,0,0,.3));
}
.topnav .back {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255,255,255,.92);
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  text-shadow: 0 1px 10px rgba(0,0,0,.3);
}
.topnav .back svg {
  width: 16px;
  height: 16px;
}

.stage {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  overflow: hidden;
}

.auth-card {
  width: 100%;
  max-width: 380px;
  max-height: 100%;
  overflow: auto;
  background: #ffffff;
  border-radius: 22px;
  padding: 34px 32px;
  box-shadow: 0 50px 90px -30px rgba(0,0,0,.45);
  font-family: 'Pretendard', sans-serif;
  color: #0d1110;
}

.auth-card h2 {
  font-size: 21px;
  font-weight: 800;
  letter-spacing: -0.01em;
  margin-bottom: 6px;
}
.auth-card .sub {
  font-size: 13px;
  color: #9ca3a1;
  margin-bottom: 24px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #0d1110;
  margin-bottom: 7px;
}
.field-input {
  position: relative;
  display: flex;
  align-items: center;
}
.field input {
  width: 100%;
  height: 46px;
  padding: 0 15px;
  background: #ffffff;
  border: 1.5px solid #eceeed;
  border-radius: 11px;
  color: #0d1110;
  font-family: 'Pretendard', sans-serif;
  font-size: 13.5px;
  transition: border-color .15s ease, box-shadow .15s ease;
}
.field input::placeholder {
  color: #c2c7c5;
}
.field input:focus {
  outline: none;
  border-color: #01bfa6;
  box-shadow: 0 0 0 3px rgba(1, 191, 166, 0.12);
}
.field-toggle {
  position: absolute;
  right: 13px;
  background: none;
  border: none;
  color: #9ca3a1;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  padding: 4px;
}
.field-toggle:focus-visible {
  outline: 2px solid #01bfa6;
  border-radius: 4px;
}

.error-msg {
  font-size: 12px;
  color: #e53e3e;
  margin-top: -4px;
}

.btn-submit {
  width: 100%;
  height: 48px;
  margin-top: 4px;
  background: #0d1110;
  color: #fff;
  border: none;
  border-radius: 11px;
  font-family: 'Pretendard', sans-serif;
  font-size: 14.5px;
  font-weight: 700;
  cursor: pointer;
  transition: background .15s ease, transform .12s ease;
}
.btn-submit:hover:not(:disabled) {
  background: #019c87;
}
.btn-submit:active:not(:disabled) {
  transform: translateY(1px);
}
.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.btn-submit:focus-visible {
  outline: 2px solid #019c87;
  outline-offset: 2px;
}

.signup-line {
  text-align: center;
  margin-top: 18px;
  font-size: 12.5px;
  color: #9ca3a1;
}
.signup-line a {
  color: #0d1110;
  font-weight: 700;
  text-decoration: underline;
  cursor: pointer;
}

@media (max-width: 860px) {
  .stage { padding: 24px; }
  .auth-card { max-width: 360px; }
}
@media (max-height: 560px) {
  .auth-card { padding: 24px 26px; }
}
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}
</style>
