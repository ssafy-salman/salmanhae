# 04. UI_GUIDE

> 메인 서비스는 **왼쪽 지도 + 오른쪽 챗봇** 구조를 유지하고, 전체 톤은 ChatGPT처럼 깔끔하게 가져간다.  
> 랜딩페이지의 픽셀/터미널/패브릭 감성은 핵심 UI를 방해하지 않는 수준에서 이스터에그처럼만 사용한다.

---

## 1. Design Direction

### 핵심 방향

살만해의 서비스 UI는 "AI가 조건에 맞는 집을 찾아주는 지도 기반 챗봇 서비스"처럼 보여야 한다.

- **왼쪽:** 지도 기반 매물 탐색 영역
- **오른쪽:** AI 챗봇 대화 영역
- **전체 분위기:** 흰 배경, 넓은 여백, 둥근 패널, 낮은 대비의 라인
- **브랜드 감성:** 픽셀 패턴, 모노스페이스 라벨, 민트톤, 작은 그래픽 장식

### 한 줄 정의

> 깔끔한 AI 서비스 UI에, 랜딩페이지의 픽셀 감성을 아주 작게 섞은 지도형 부동산 탐색 인터페이스

---

## 2. Layout Principle

### Main Service Layout

```text
┌──────────────────────────────────────────────┐
│ Header                                       │
├───────────────────────┬──────────────────────┤
│                       │                      │
│ Map Area              │ Chatbot Area         │
│                       │                      │
│ - 검색창              │ - AI 대화            │
│ - 필터                │ - 추천 카드          │
│ - 매물 마커           │ - 하단 입력창        │
│ - 시세/안전 요약      │                      │
│                       │                      │
└───────────────────────┴──────────────────────┘
```

### 권장 비율

| 영역 | 비율 | 설명 |
|------|-----:|------|
| 지도 영역 | 55~60% | 사용자가 매물을 위치 기반으로 확인하는 핵심 영역 |
| 챗봇 영역 | 40~45% | 조건 입력, 추천 이유, RAG 상담을 제공하는 영역 |
| 헤더 | 64~76px | 로고, 찜한 매물, 로그인 정도만 배치 |

---

## 3. Visual Tone

### 전체 톤

- 기본 배경은 완전한 흰색보다 살짝 민트가 도는 오프화이트를 사용한다.
- 주요 패널은 흰색 또는 반투명 흰색으로 처리한다.
- 그림자는 강하게 넣지 않고, 부드러운 확산형 그림자를 사용한다.
- 지도와 챗봇 모두 복잡한 대시보드처럼 보이면 안 된다.

### 사용 키워드

```
clean / soft minimal / map based / chat first
quiet pixel / terminal label / rounded panel / soft mint
```

### 피해야 하는 키워드

```
cute house illustration / neon dashboard / heavy pixel art
game UI / too many cards / colorful infographic
```

---

## 4. Color System

### Primary Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | `#F4F7F5` | 전체 배경 |
| `--surface` | `#FFFFFF` | 카드, 패널, 챗봇 버블 |
| `--surface-soft` | `#F8FAF8` | 보조 패널, 필터 영역 |
| `--text` | `#141916` | 기본 텍스트 |
| `--muted` | `#6F7C72` | 설명, 보조 텍스트 |
| `--line` | `#DFE7E1` | 패널 경계선 |
| `--dark` | `#101311` | 주요 버튼, 사용자 메시지 |
| `--mint` | `#D9F3DD` | 강조 배경, 선택된 지도 마커 |
| `--mint-deep` | `#BDDFC5` | 민트 계열 테두리 |
| `--denim` | `#17283A` | 랜딩페이지 감성 포인트 |
| `--cream` | `#E5D5BF` | 패브릭/빈티지 포인트 |

### 사용 규칙

- 검정색은 CTA, 사용자 메시지, 활성 상태에만 사용한다.
- 민트색은 선택 상태, 추천 마커, 작은 포인트에만 사용한다.
- 데님/크림 컬러는 메인 서비스에서는 거의 쓰지 않고, 랜딩페이지나 작은 이스터에그에만 사용한다.

---

## 5. Typography

### 기본 폰트

```css
font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
```

### 픽셀/터미널 폰트

```css
font-family: "Galmuri11", "IBM Plex Mono", "SFMono-Regular", Menlo, Consolas, monospace;
```

### 사용 규칙

| 용도 | 폰트 |
|------|------|
| 일반 본문 | Sans-serif |
| 챗봇 메시지 | Sans-serif |
| 지도 검색창 | Sans-serif |
| `FEATURE 01` 같은 라벨 | Pixel/Mono |
| 상태 배지 | Pixel/Mono |
| 작은 이스터에그 문구 | Pixel/Mono |

### 예시

```
FEATURE 01 / PROPERTY MATCH
MAP READY / VER 1.0
RAG GUIDE / CONTRACT CHECK
```

---

## 6. Component Guide

### Header

- 높이: 64~76px
- 왼쪽: 심볼 + `살만해` + 작은 서비스 설명
- 오른쪽: `찜한 매물`, `로그인`
- 배경: 흰색 또는 반투명 흰색 / border-radius: 20~24px / shadow 약하게

```
[살] 살만해                      [찜한 매물] [로그인]
     AI PROPERTY AGENT / MAP + CHAT
```

### Map Panel

- 상단 검색창, 필터 버튼, 안전/시세 토글
- 매물 마커, 선택 매물 팝업, 하단 요약 카드

#### 지도 마커

| 상태 | 스타일 |
|------|--------|
| 기본 | 흰색 원형 마커 + subtle shadow |
| 선택됨 | 민트 배경 원형 마커 + stronger shadow |
| 비추천/흐림 | opacity 낮춤 |

### Chatbot Panel

ChatGPT처럼 보여야 한다.

- 입력창은 하단 고정
- AI 메시지: 흰색 버블 / 사용자 메시지: 검정 버블
- 추천 카드는 메시지 흐름 안에 자연스럽게 배치

| 메시지 | 배경 | 텍스트 |
|--------|------|--------|
| AI | `#FFFFFF` | `#141916` |
| User | `#101311` | `#FFFFFF` |

### Recommendation Card

```
혜화역 도보 3분 원룸        추천
보증금 500 / 월 45만
10.2평 · 풀옵션 · 엘리베이터 · 채광 좋음
```

- border-radius: 18px / background: white / border: `#DFE7E1`
- selected 상태에서는 검정 outline 사용

### Input / Composer

```
[추천 ⌄] 메시지를 입력하세요...                         [↑]
```

- 둥근 pill 형태 / 배경 흰색 / 버튼 검정색
- mode 버튼은 mono font 사용 가능

---

## 7. Brand Motif Usage

| 요소 | 사용 위치 | 강도 |
|------|----------|------|
| 픽셀 dot pattern | 패널 코너, 지도 배경 일부 | 낮음 |
| `FEATURE 01` 라벨 | 요약 카드, 하단 metric | 중간 |
| 모노스페이스 텍스트 | 상태 배지, 작은 라벨 | 중간 |
| 민트톤 | 선택 상태, 추천 마커 | 낮음~중간 |
| 패브릭/데님 질감 | 메인 서비스에서는 거의 사용 안 함 | 매우 낮음 |

### 픽셀 패턴

```css
.pixel-pattern {
  background-image: radial-gradient(#101311 1px, transparent 1px);
  background-size: 9px 9px;
  opacity: 0.08;
}
```

> 픽셀 감성은 "브랜드를 기억하게 하는 장식"이지, "서비스 사용성을 압도하는 그래픽"이 아니다.

---

## 8. Page-Specific Guide

| 페이지 | 방향 |
|--------|------|
| Landing | 픽셀/터미널 폰트 적극 사용, 데님/패브릭 질감 사용 가능, `FEATURE 01/02/03` 섹션 |
| Main Service | 지도+챗봇 중심, 그래픽은 작고 은은하게, 색은 흰색/민트/검정 위주 |
| Login / Signup | 중앙 카드형 폼, 로고와 작은 픽셀 패턴만 |
| Saved Properties | 카드 리스트 + 지도 미니뷰, 추천 이유·안전 점수·시세 비교 함께 노출 |

---

## 9. Do / Don't

### Do

- 왼쪽 지도, 오른쪽 챗봇 구조를 유지한다.
- 메인 UI는 흰색, 여백, 둥근 패널 중심으로 만든다.
- 픽셀/터미널 감성은 작은 라벨과 패턴에만 사용한다.
- 선택된 매물은 지도와 챗봇 카드가 동시에 바뀌게 한다.
- 추천 이유, 안전 점수, 시세 비교를 한눈에 보여준다.

### Don't

- 픽셀 그래픽을 화면 전체에 크게 깔지 않는다.
- 귀여운 집 일러스트를 메인 모티프로 쓰지 않는다.
- 너무 많은 색을 쓰지 않는다.
- 카드와 배지를 과하게 늘려 대시보드처럼 만들지 않는다.
- 지도보다 챗봇이, 또는 챗봇보다 지도가 지나치게 압도하지 않게 한다.

---

## 10. CSS Token

```css
:root {
  --bg: #F4F7F5;
  --surface: #FFFFFF;
  --surface-soft: #F8FAF8;
  --text: #141916;
  --muted: #6F7C72;
  --line: #DFE7E1;
  --dark: #101311;
  --mint: #D9F3DD;
  --mint-deep: #BDDFC5;
  --denim: #17283A;
  --cream: #E5D5BF;

  --radius-xl: 32px;
  --radius-lg: 24px;
  --radius-md: 18px;
  --radius-sm: 12px;

  --shadow: 0 24px 60px rgba(18, 28, 19, 0.08);
  --shadow-soft: 0 12px 28px rgba(18, 28, 19, 0.06);

  --font-sans: -apple-system, BlinkMacSystemFont, "Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
  --font-mono: "Galmuri11", "IBM Plex Mono", "SFMono-Regular", Menlo, Consolas, monospace;
}
```

---

## 11. Implementation Notes

### Frontend 작업 우선순위

1. `MapPanel`과 `ChatPanel`을 먼저 분리한다.
2. 선택된 매물 상태를 공통 store로 관리한다.
3. 지도 마커 클릭 시 챗봇 추천 카드도 active 처리한다.
4. 챗봇 추천 카드 클릭 시 지도 팝업도 변경한다.
5. RAG 답변, 시세 분석, 안전 분석은 챗봇 메시지 타입으로 분리한다.

### 추천 컴포넌트 구조

```
components/
  layout/
    AppHeader
    ServiceShell
  map/
    MapPanel
    MapSearchBar
    MapMarker
    PropertyPopup
    MapMetrics
  chat/
    ChatPanel
    ChatHeader
    ChatMessage
    ChatComposer
    RecommendationCard
  common/
    Button
    Pill
    Badge
    PixelPattern
```

---

## 12. Final Reference

> "이 화면은 집을 찾는 서비스답게 실용적이고 깔끔한데, 자세히 보면 살만해만의 픽셀 감성이 작게 숨어 있다."
