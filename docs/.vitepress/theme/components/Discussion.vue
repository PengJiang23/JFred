<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useData, useRoute, withBase } from 'vitepress'
import { canonicalPath } from '../community'
const { frontmatter } = useData()
const route = useRoute()
const container = ref<HTMLElement>()
const state = ref('loading')
let version = 0
let timer: ReturnType<typeof setTimeout> | undefined
async function mountComments() {
  const current = ++version
  clearTimeout(timer)
  await nextTick()
  if (!container.value || frontmatter.value.comments === false) return
  container.value.replaceChildren()
  state.value = 'loading'
  const script = document.createElement('script')
  script.src = 'https://giscus.app/client.js'
  script.async = true
  script.crossOrigin = 'anonymous'
  const path = canonicalPath(route.path.replace(withBase('/'), '/'))
  const settings: Record<string,string> = {
    repo: 'PengJiang23/JFred', 'repo-id': 'R_kgDONP0I7g',
    category: 'Announcements', 'category-id': 'DIC_kwDONP0I7s4DIxGQ',
    mapping: 'specific', term: `JFred ${path}`, strict: '1',
    'reactions-enabled': '1', 'emit-metadata': '0', 'input-position': 'top',
    theme: 'noborder_light', lang: 'zh-CN', loading: 'lazy'
  }
  for (const [key,value] of Object.entries(settings)) script.setAttribute(`data-${key}`,value)
  script.onload = () => { if (current === version) { clearTimeout(timer); state.value = 'ready' } }
  script.onerror = () => { if (current === version) { clearTimeout(timer); state.value = 'error' } }
  timer = setTimeout(() => { if (current === version) state.value = 'error' },15000)
  container.value.appendChild(script)
}
onMounted(mountComments)
watch(() => route.path, mountComments)
onUnmounted(() => { version++; clearTimeout(timer) })
</script>
<template>
  <section v-if="frontmatter.comments !== false" class="jf-discussion" aria-labelledby="discussion-title">
    <h2 id="discussion-title">交流与补充</h2>
    <p class="jf-discussion-notice">使用 GitHub 账号参与讨论，评论公开保存在 GitHub Discussions。<a href="https://github.com/PengJiang23/JFred/discussions" target="_blank" rel="noopener noreferrer">前往 GitHub 讨论</a><a :href="withBase('/privacy')">了解说明</a></p>
    <p v-if="state === 'error'" class="jf-discussion-status">评论暂未加载，可直接前往 GitHub 讨论。<button @click="mountComments">重新加载</button></p>
    <p v-else-if="state === 'loading'" class="jf-discussion-status">正在加载评论…</p>
    <div ref="container" class="giscus"></div>
  </section>
</template>
