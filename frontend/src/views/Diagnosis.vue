<template>
  <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
    <div class="border-b border-slate-100 pb-4 mb-6">
      <h2 class="text-xl font-black text-slate-900">🛡️ HUG 보증보험 적격성 및 권리관계 정밀 자가진단기</h2>
      <p class="text-sm text-slate-500 mt-1">HUG 126% 기준, 선순위 임차보증금, 근저당, 임대인 세금 체납 여부를 함께 계산합니다.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <form class="lg:col-span-6 space-y-4 bg-slate-50 p-5 rounded-2xl border border-slate-100" @submit.prevent>
        <div>
          <label class="block text-sm font-black text-slate-700 mb-2">1. 주택 유형</label>
          <div class="grid grid-cols-2 gap-2">
            <button type="button" @click="buildingType = 'multi'" :class="typeButtonClass('multi')">다가구 / 단독주택</button>
            <button type="button" @click="buildingType = 'apt'" :class="typeButtonClass('apt')">아파트 / 오피스텔 / 다세대</button>
          </div>
          <p class="text-[11px] text-slate-400 mt-1">다가구는 호실별 등기가 없어 선순위 세입자 보증금을 별도로 확인해야 합니다.</p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <InputMoney label="공시가격" v-model="form.publicPrice" />
          <InputMoney label="실제 매매 시세" v-model="form.marketPrice" />
          <InputMoney label="내 계약 희망 보증금" v-model="form.deposit" />
          <InputMoney label="선순위 근저당" v-model="form.collateral" />
        </div>

        <div v-if="buildingType === 'multi'">
          <InputMoney label="선순위 임차보증금 총합" v-model="form.seniorDeposits" />
          <p class="text-[11px] text-slate-400 mt-1">공인중개사에게 선순위 임차인 정보 확인서를 요구해 확인할 수 있습니다.</p>
        </div>

        <div class="bg-white p-3 rounded-xl border border-slate-200">
          <label class="block text-xs font-black text-slate-700 mb-2">임대인 세금 완납 검증 여부</label>
          <div class="space-y-2 text-xs text-slate-600">
            <label class="flex items-center gap-2 cursor-pointer"><input v-model="form.taxChecked" type="radio" value="yes" class="accent-brand" /> 국세/지방세 완납 증명서 확인 완료</label>
            <label class="flex items-center gap-2 cursor-pointer"><input v-model="form.taxChecked" type="radio" value="no" class="accent-brand" /> 확인하지 못함 / 거부당함</label>
          </div>
        </div>
      </form>

      <section class="lg:col-span-6 space-y-4">
        <div :class="['p-5 rounded-2xl border shadow-sm space-y-4', result.panelClass]">
          <div class="flex items-center justify-between gap-3">
            <span class="text-xs text-slate-500 font-black">임차 자산 안전 권리진단 등급</span>
            <span :class="['text-xs font-black px-3 py-1 rounded-full', result.badgeClass]">{{ result.status }}</span>
          </div>

          <div class="grid grid-cols-2 gap-4 text-xs bg-white p-3 rounded-xl border border-white/80">
            <div><span class="text-slate-400 block">HUG 126% 상한선</span><b class="text-slate-800">{{ money(result.hugLimit) }} 만원</b></div>
            <div><span class="text-slate-400 block">선순위 총채무</span><b class="text-slate-800">{{ money(result.totalSeniorDebt) }} 만원</b></div>
            <div><span class="text-slate-400 block">임대인 세금 체크</span><b :class="form.taxChecked === 'yes' ? 'text-emerald-600' : 'text-rose-600'">{{ form.taxChecked === 'yes' ? '검증 완료' : '미검증 위험' }}</b></div>
            <div><span class="text-slate-400 block">종합 전세가율</span><b class="text-slate-800">{{ result.debtRatio }}%</b></div>
          </div>

          <p class="text-sm text-slate-700 leading-relaxed" v-html="result.message"></p>
        </div>

        <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
          <h3 class="text-sm font-black text-slate-900 mb-3">📋 계약 전 필수 서류 체크리스트</h3>
          <div class="space-y-2 text-xs text-slate-600">
            <p :class="form.taxChecked === 'yes' ? 'line-through text-slate-400' : 'font-bold text-rose-600'">1. 국세 및 지방세 완납증명서</p>
            <p :class="buildingType === 'multi' ? 'font-bold text-brand-dark' : 'text-slate-400'">2. 선순위 임차인 정보 제공 확인서</p>
            <p>3. 등기부등본 을구 및 당일 신규 대출 금지 특약</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, ref } from 'vue'

const InputMoney = defineComponent({
  props: { label: String, modelValue: Number },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () => h('label', { class: 'block' }, [
      h('span', { class: 'block text-xs font-black text-slate-700 mb-1' }, props.label),
      h('div', { class: 'relative' }, [
        h('input', {
          value: props.modelValue,
          type: 'number',
          class: 'w-full pr-12 pl-3 py-2 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand focus:outline-none font-bold text-right text-xs bg-white',
          onInput: (event) => emit('update:modelValue', Number(event.target.value))
        }),
        h('span', { class: 'absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 text-xs pointer-events-none' }, '만원')
      ])
    ])
  }
})

const buildingType = ref('multi')
const form = ref({
  publicPrice: 12000,
  marketPrice: 20000,
  deposit: 10000,
  collateral: 3000,
  seniorDeposits: 5000,
  taxChecked: 'yes'
})

const money = (value) => Math.round(value).toLocaleString()
const typeButtonClass = (type) => buildingType.value === type
  ? 'py-3 bg-brand text-white border border-brand rounded-xl font-black text-xs shadow-sm'
  : 'py-3 bg-white text-slate-700 border border-slate-200 rounded-xl font-black text-xs hover:bg-slate-50'

const result = computed(() => {
  const seniorDeposits = buildingType.value === 'multi' ? Number(form.value.seniorDeposits || 0) : 0
  const hugLimit = Math.round(Number(form.value.publicPrice || 0) * 1.26)
  const totalSeniorDebt = Number(form.value.collateral || 0) + seniorDeposits
  const totalDebt = totalSeniorDebt + Number(form.value.deposit || 0)
  const debtRatio = form.value.marketPrice ? Math.round((totalDebt / Number(form.value.marketPrice)) * 100) : 0
  const hugEligible = Number(form.value.deposit || 0) <= hugLimit

  if (!hugEligible) {
    return {
      hugLimit,
      totalSeniorDebt,
      debtRatio,
      status: '계약 불가 위험',
      panelClass: 'bg-rose-50 border-rose-200',
      badgeClass: 'bg-rose-200 text-rose-950',
      message: `보증금이 HUG 126% 가입 한도인 <b>${money(hugLimit)}만원</b>을 초과했습니다. 반환보증 가입이 어려운 상태라 계약 회피를 권장합니다.`
    }
  }
  if (debtRatio >= 80) {
    return {
      hugLimit,
      totalSeniorDebt,
      debtRatio,
      status: '선순위 과다 위험',
      panelClass: 'bg-rose-50 border-rose-200',
      badgeClass: 'bg-rose-200 text-rose-950',
      message: `보증보험 한도 안에는 있지만 선순위 채권을 포함한 부채비율이 <b>${debtRatio}%</b>입니다. 경매 상황에서 보증금 회수가 불안정할 수 있습니다.`
    }
  }
  if (form.value.taxChecked === 'no') {
    return {
      hugLimit,
      totalSeniorDebt,
      debtRatio,
      status: '세금 체납 확인 필요',
      panelClass: 'bg-amber-50 border-amber-200',
      badgeClass: 'bg-amber-100 text-amber-800',
      message: '부채비율은 비교적 안정적이지만 임대인의 국세·지방세 체납을 확인하지 못했습니다. 완납증명서 또는 열람 동의 특약이 필요합니다.'
    }
  }
  if (debtRatio >= 60) {
    return {
      hugLimit,
      totalSeniorDebt,
      debtRatio,
      status: '주의',
      panelClass: 'bg-amber-50 border-amber-200',
      badgeClass: 'bg-amber-100 text-amber-800',
      message: `보증보험 가입 기준은 충족하지만 종합 전세가율이 <b>${debtRatio}%</b>입니다. 시세 하락과 추가 권리 변동을 확인하세요.`
    }
  }
  return {
    hugLimit,
    totalSeniorDebt,
    debtRatio,
    status: '안심',
    panelClass: 'bg-emerald-50 border-emerald-200',
    badgeClass: 'bg-emerald-100 text-emerald-800',
    message: `HUG 한도 안에 있고 총 부채비율도 <b>${debtRatio}%</b>로 양호합니다. 전입신고와 확정일자를 즉시 확보하세요.`
  }
})
</script>
