# 살만해 — Frontend

![로고](./public/salman_full_logo.png)

AI 에이전트 기반 부동산 탐색 서비스 **살만해**의 Vue 3 프론트엔드입니다.

---

## 기술 스택

| 구분 | 사용 기술 |
| --- | --- |
| Framework | Vue 3 (Composition API) |
| Build | Vite |
| Routing | Vue Router |
| State | Pinia |
| Styling | Tailwind CSS |
| HTTP | Axios |
| Map | 네이버지도 SDK |
| Icon | @lucide/vue |

---

## 화면 구성

| 화면 | 파일 | 설명 | 단계 |
| --- | --- | --- | --- |
| 지도 탐색 | `MapExplorer.vue` | 매물 마커, 필터, 실거래가/안전 레이어, 상세 드로어 | MVP |
| AI 에이전트 | `Chatbot.vue` | 매물 추천, 법률 상담, 시세·안전 분석 챗봇 | MVP |
| 찜 목록 | `Wishlist.vue` | 관심 매물 저장·조회 | MVP |
| 커뮤니티 | `Community.vue` | 지역 후기 (MVP 제외, 확장) | 확장 |

---

## 실행 방법

```bash
pnpm install
pnpm dev
```

```bash
pnpm build
```

---

## 프로젝트 구조

```
salmanhae-vue/
├── public/
│   ├── salman_symbol_logo.png
│   └── salman_full_logo.png
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── common/
│   │   ├── map/
│   │   └── chat/
│   ├── composables/
│   │   ├── useMapBounds.js
│   │   └── useAsyncState.js
│   ├── router/
│   ├── services/
│   │   ├── apiClient.js
│   │   ├── propertyApi.js
│   │   ├── safetyApi.js
│   │   ├── chatApi.js
│   │   └── wishlistApi.js
│   ├── store/
│   │   ├── mapStore.js
│   │   ├── authStore.js
│   │   └── chatStore.js
│   └── views/
│       ├── MapExplorer.vue
│       ├── Chatbot.vue
│       ├── Wishlist.vue
│       └── Community.vue
├── vite.config.js
└── package.json
```

---

## 상세 문서

- `docs/01_frontend_development_plan.md` — 개발 계획 및 단계
- `docs/02_api_integration_contract.md` — API 연동 기준
- 전체 기능 명세: `artifact/docs/02_mvp_scope.md`
