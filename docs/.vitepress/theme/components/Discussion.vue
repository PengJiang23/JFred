<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useData, useRoute, withBase } from 'vitepress'
import { communityEnabled, canonicalPath } from '../community'
const { frontmatter, page } = useData()
const route = useRoute()
const container = ref<HTMLElement>()
const state = ref('loading')
let instance: any
let version = 0
let loaded: Promise<any> | undefined
function loadArtalk() {
  if ((window as any).Artalk) return Promise.resolve((window as any).Artalk)
  if (loaded) return loaded
  loaded = new Promise((resolve, reject) => {
    if (!document.getElementById('jfred-artalk-css')) {
      const style = document.createElement('link'); style.id = 'jfred-artalk-css'; style.rel = 'stylesheet'; style.href = withBase('/comments/dist/Artalk.css'); document.head.appendChild(style)
    }
    const script = document.createElement('script'); script.src = withBase('/comments/dist/Artalk.js'); script.onload = () => resolve((window as any).Artalk); script.onerror = () => { script.remove(); loaded = undefined; reject(new Error('无法连接评论服务')) }; document.head.appendChild(script)
  })
  return loaded
}
async function mountComments() {
  const current = ++version
  instance?.destroy(); instance = undefined
  if (frontmatter.value.comments === false) return
  state.value = communityEnabled() ? 'loading' : 'disabled'
  if (!communityEnabled()) return
  try {
    const Artalk = await loadArtalk()
    await nextTick()
    if (current !== version || !container.value) return
    instance = Artalk.init({ el: container.value, server: withBase('/comments'), site: 'JFred', pageKey: canonicalPath(route.path), pageTitle: page.value.title, darkMode: false, pvAdd: false, useBackendConf: false, locale: 'zh-CN', emoticons: [], avatarURLBuilder: () => '', placeholder: '分享你的问题、补充资料或不同理解。新评论审核后公开。', noComment: '还没有评论，欢迎留下第一条讨论。' })
    state.value = 'ready'
  } catch { if (current === version) state.value = 'error' }
}
onMounted(mountComments)
watch(() => route.path, () => nextTick(mountComments))
onUnmounted(() => { version++; instance?.destroy() })
</script>
<template><section v-if="frontmatter.comments !== false" class="jf-discussion" aria-labelledby="discussion-title"><h2 id="discussion-title">交流与补充</h2><p class="jf-discussion-notice">评论审核后公开。昵称会展示，邮箱不公开；评论服务会保留必要的 IP 等信息用于反垃圾。<a :href="withBase('/privacy')">了解说明</a></p><p v-if="state === 'disabled'" class="jf-discussion-status">评论在服务器站点提供。</p><p v-else-if="state === 'error'" class="jf-discussion-status">评论服务暂不可用。<button @click="mountComments">重新加载</button></p><p v-else-if="state === 'loading'" class="jf-discussion-status">正在加载评论…</p><div ref="container"></div></section></template>
