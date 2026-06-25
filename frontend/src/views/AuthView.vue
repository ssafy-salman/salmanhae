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

        <!-- Step 1: 이메일 입력 -->
        <form v-if="registerStep === 'email'" @submit.prevent="handleSendCode">
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
          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
          <button type="submit" class="btn-submit" :disabled="loading">
            {{ loading ? '발송 중…' : '인증코드 발송' }}
          </button>
        </form>

        <!-- Step 2: 인증코드 입력 -->
        <form v-else-if="registerStep === 'code'" @submit.prevent="handleVerifyCode">
          <div class="field">
            <label>이메일</label>
            <div class="field-input">
              <input :value="email" type="email" readonly />
            </div>
          </div>
          <div class="field">
            <label for="reg-code">인증코드</label>
            <div class="field-input">
              <input
                id="reg-code"
                v-model="verifyCode"
                type="text"
                placeholder="6자리 코드 입력"
                maxlength="6"
                required
              />
            </div>
          </div>
          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
          <button type="submit" class="btn-submit" :disabled="loading">
            {{ loading ? '확인 중…' : '확인' }}
          </button>
        </form>

        <!-- Step 3: 닉네임·비밀번호 입력 -->
        <form v-else @submit.prevent="handleRegister">
          <div class="field">
            <label for="reg-nickname">닉네임</label>
            <div class="field-input">
              <input
                id="reg-nickname"
                v-model="nickname"
                type="text"
                placeholder="홍길동"
                autocomplete="name"
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
import { useAuthStore } from '@/store/authStore.js'
import { sendVerificationEmail, verifyEmail } from '@/api/auth.js'

const router = useRouter()
const auth = useAuthStore()

const mode = ref('login')
const registerStep = ref('email')

const email = ref('')
const password = ref('')
const nickname = ref('')
const verifyCode = ref('')
const showPw = ref(false)
const loading = ref(false)
const errorMsg = ref('')

function switchMode(next) {
  mode.value = next
  registerStep.value = 'email'
  email.value = ''
  password.value = ''
  nickname.value = ''
  verifyCode.value = ''
  showPw.value = false
  errorMsg.value = ''
}

function parseError(e, fallback) {
  const code = e?.response?.data?.code
  if (code === 'INVALID_VERIFICATION_CODE') return '인증코드가 올바르지 않습니다.'
  if (code === 'EMAIL_ALREADY_EXISTS') return '이미 가입된 이메일입니다.'
  if (code === 'EMAIL_NOT_VERIFIED') return '이메일 인증을 먼저 완료해주세요.'
  return e?.response?.data?.message ?? fallback
}

async function handleLogin() {
  loading.value = true
  errorMsg.value = ''
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    errorMsg.value = parseError(e, '로그인에 실패했습니다.')
  } finally {
    loading.value = false
  }
}

async function handleSendCode() {
  loading.value = true
  errorMsg.value = ''
  try {
    await sendVerificationEmail(email.value)
    registerStep.value = 'code'
  } catch (e) {
    errorMsg.value = parseError(e, '인증코드 발송에 실패했습니다.')
  } finally {
    loading.value = false
  }
}

async function handleVerifyCode() {
  loading.value = true
  errorMsg.value = ''
  try {
    await verifyEmail(email.value, verifyCode.value)
    registerStep.value = 'info'
  } catch (e) {
    errorMsg.value = parseError(e, '인증에 실패했습니다.')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  loading.value = true
  errorMsg.value = ''
  try {
    await auth.signup(email.value, password.value, nickname.value)
    switchMode('login')
  } catch (e) {
    errorMsg.value = parseError(e, '회원가입에 실패했습니다.')
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
