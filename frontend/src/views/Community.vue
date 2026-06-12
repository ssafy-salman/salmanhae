<template>
  <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4 mb-4">
      <div>
        <h2 class="text-lg font-black text-slate-900">💬 {{ currentRegionLabel }} 주거 토크룸</h2>
        <p class="text-xs text-slate-500 mt-0.5">치안, 방음, 안전거리, 유흥업소 소음 등 직접 겪은 동네 실황을 공유합니다.</p>
      </div>
      <button @click="isModalOpen = true" class="bg-brand hover:bg-brand-dark text-white font-black text-xs px-4 py-2.5 rounded-xl shadow-sm transition">후기 작성하기</button>
    </div>

    <div v-if="store.communityForCurrentRegion.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <article v-for="post in store.communityForCurrentRegion" :key="post.id" class="bg-slate-50 border border-slate-200 p-4 rounded-xl flex flex-col gap-2.5 hover:shadow-sm transition">
        <div class="flex items-center justify-between">
          <span class="bg-brand-light text-brand-dark border border-brand/10 text-[10px] font-black px-2 py-0.5 rounded-full">{{ post.category }}</span>
          <span class="text-amber-500 text-xs">{{ stars(post.rate) }}</span>
        </div>
        <div>
          <h4 class="font-black text-slate-900 text-sm leading-snug">{{ post.title }}</h4>
          <p class="text-xs text-slate-600 mt-2 leading-relaxed">{{ post.content }}</p>
        </div>
        <div class="flex items-center justify-between text-[10px] text-slate-400 border-t border-slate-200/60 pt-2 mt-auto">
          <span>작성자: {{ post.author }}</span>
          <span>{{ post.date }}</span>
        </div>
      </article>
    </div>
    <div v-else class="text-center py-16 text-slate-400 text-sm">등록된 후기가 없습니다. 첫 글을 남겨주세요.</div>

    <div v-if="isModalOpen" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-[110] p-4">
      <form @submit.prevent="submit" class="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-md w-full p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 class="font-black text-slate-900">✍️ 실거주 후기 작성</h3>
          <button type="button" @click="isModalOpen = false" class="w-7 h-7 bg-slate-100 rounded-full text-slate-500">✕</button>
        </div>
        <label class="block"><span class="form-label">카테고리</span><select v-model="form.category" class="form-input"><option>실거주 꿀팁</option><option>치안 및 안전</option><option>방음/관리비</option></select></label>
        <label class="block"><span class="form-label">제목</span><input v-model="form.title" required class="form-input" placeholder="밤길 안전 상태나 방음 상태 공유" /></label>
        <label class="block"><span class="form-label">상세 내용</span><textarea v-model="form.content" required rows="4" class="form-input" placeholder="직접 거주하며 느낀 장단점을 적어주세요."></textarea></label>
        <div class="grid grid-cols-2 gap-2">
          <label class="block"><span class="form-label">닉네임</span><input v-model="form.author" class="form-input" /></label>
          <label class="block"><span class="form-label">거주 안전 별점</span><select v-model.number="form.rate" class="form-input"><option :value="5">★★★★★</option><option :value="4">★★★★☆</option><option :value="3">★★★☆☆</option><option :value="2">★★☆☆☆</option></select></label>
        </div>
        <button class="w-full bg-brand hover:bg-brand-dark text-white font-black text-sm py-3 rounded-xl shadow transition">후기 등록하기</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import useMapStore from '../store/mapStore'

const store = useMapStore()
const isModalOpen = ref(false)
const form = reactive({ category: '실거주 꿀팁', title: '', content: '', author: '익명', rate: 5 })
const currentRegionLabel = computed(() => store.regions.find((region) => region.value === store.currentRegion)?.label || '현재 지역')
const stars = (rate) => '★★★★★'.slice(0, rate) + '☆☆☆☆☆'.slice(0, 5 - rate)
const submit = () => {
  store.addCommunityPost({ ...form })
  form.title = ''
  form.content = ''
  form.author = '익명'
  form.rate = 5
  isModalOpen.value = false
}
</script>
