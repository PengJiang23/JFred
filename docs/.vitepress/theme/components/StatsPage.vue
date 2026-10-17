<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { withBase } from 'vitepress'
import { communityEnabled, getPublicStats } from '../community'
import { topics } from '../content'
const loading = ref(true), error = ref(''), updated = ref('')
const total = ref({pageviews:0,visitors:0}), today = ref({pageviews:0,visitors:0})
const days = ref<{label:string,pageviews:number,visitors:number}[]>([])
const articles = ref<{title:string,href:string,visitors:number}[]>([])
const peak = computed(()=>Math.max(1,...days.value.map(d=>d.pageviews)))
async function load() {
 loading.value=true; error.value=''
 if(!communityEnabled()) {error.value='访客统计在服务器主站提供，镜像和本地预览不连接内网服务。';loading.value=false;return}
 try {
  const now=Date.now(), day=86400000, midnight=Math.floor((now+8*3600000)/day)*day-8*3600000
  const [all,current,series,ranking]=await Promise.all([
   getPublicStats(),getPublicStats(undefined,midnight,now),
   Promise.all(Array.from({length:7},async(_,i)=>{const start=midnight-(6-i)*day;const s=await getPublicStats(undefined,start,Math.min(start+day-1,now));return {label:new Date(start).toLocaleDateString('zh-CN',{timeZone:'Asia/Shanghai',month:'numeric',day:'numeric'}),...s}})),
   Promise.all(topics.flatMap(t=>t.chapters.filter(c=>!c.href.endsWith('/')).map(async c=>({...c,...await getPublicStats(withBase(c.href))}))))
  ])
  total.value=all;today.value=current;days.value=series;articles.value=ranking.sort((a,b)=>b.visitors-a.visitors)
  updated.value=new Date().toLocaleString('zh-CN',{timeZone:'Asia/Shanghai',hour12:false})
 } catch {error.value='暂时无法读取统计。请稍后重试，现有文章仍可正常阅读。'}
 finally {loading.value=false}
}
onMounted(load)
</script>
<template>
 <main class="stats-page">
  <p class="eyebrow">A SMALL WINDOW INTO THIS SITE</p><h1>看看内容被如何阅读。</h1>
  <p class="stats-intro">只展示汇总数字。阅读按北京时间每天去重，同一天反复刷新不会增加文章热度。</p>
  <div class="stats-toolbar"><span>{{updated ? `更新于 ${updated} · 北京时间` : '读取自托管统计服务'}}</span><button @click="load" :disabled="loading">{{loading?'读取中…':'刷新统计'}}</button></div>
  <p v-if="error" role="status">{{error}}</p>
  <template v-else>
   <section class="stats-kpis" aria-label="访客概览">
    <div><span>今日浏览</span><strong>{{loading?'—':today.pageviews.toLocaleString()}}</strong><small>PV · 含重复浏览</small></div>
    <div><span>今日去重访问</span><strong>{{loading?'—':today.visitors.toLocaleString()}}</strong><small>当日匿名访客标识</small></div>
    <div><span>累计浏览</span><strong>{{loading?'—':total.pageviews.toLocaleString()}}</strong><small>服务启用以来</small></div>
    <div><span>累计去重访问</span><strong>{{loading?'—':total.visitors.toLocaleString()}}</strong><small>跨日分别计入，不等于实际人数</small></div>
   </section>
   <section class="stats-panel"><h2>最近七天</h2><p>柱高为浏览量，下方同时列出去重访问。</p>
    <div class="stats-days"><div v-for="d in days" :key="d.label" class="stats-day"><strong>{{d.pageviews}}</strong><div class="stats-bar-track"><div :style="{height:Math.max(2,d.pageviews/peak*100)+'%'}"></div></div><span>{{d.label}}</span><small>{{d.visitors}} 去重</small></div></div>
   </section>
   <section class="stats-panel"><h2>文章阅读热度</h2><p>按各文章累计的每日去重阅读排序；跨天访问会分别累计。</p>
    <ol class="stats-ranking"><li v-for="a in articles" :key="a.href"><a :href="withBase(a.href)">{{a.title}}</a><span>{{a.visitors}} 阅读</span></li></ol>
   </section>
  </template>
  <p class="stats-footnote">Umami 自托管统计 · 不公开访客明细。共享网络、浏览器设置与拦截插件会影响计数。<a :href="withBase('/privacy')">查看统计口径与隐私说明 ↗</a></p>
 </main>
</template>
<style scoped>
.stats-page{max-width:1100px;margin:auto;padding:72px 32px 88px}.eyebrow{font-size:11px;letter-spacing:.16em;color:var(--vp-c-text-3)}h1{font-size:clamp(30px,4vw,44px);line-height:1.3;letter-spacing:-.04em;margin:22px 0}.stats-intro{color:var(--vp-c-text-2);max-width:650px;line-height:1.9}.stats-toolbar{display:flex;justify-content:space-between;align-items:center;gap:16px;font-size:12px;color:var(--vp-c-text-2);margin:32px 0 20px}.stats-toolbar button{padding:8px 14px;border:1px solid var(--vp-c-divider);border-radius:8px;color:var(--vp-c-text-1)}button:disabled{opacity:.5}.stats-kpis{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--vp-c-divider);border-radius:14px}.stats-kpis>div{padding:24px 20px;display:flex;flex-direction:column;gap:10px}.stats-kpis>div+div{border-left:1px solid var(--vp-c-divider)}.stats-kpis span,.stats-kpis small{font-size:12px;color:var(--vp-c-text-2)}.stats-kpis strong{font-size:34px;line-height:1.2;font-weight:550}.stats-panel{margin-top:32px;padding:28px;border:1px solid var(--vp-c-divider);border-radius:14px}.stats-panel h2{font-size:20px;font-weight:550}.stats-panel p,.stats-footnote{font-size:12px;color:var(--vp-c-text-2);line-height:1.8;margin-top:8px}.stats-days{display:flex;gap:20px;margin-top:26px}.stats-day{flex:1;min-width:0;display:flex;align-items:center;flex-direction:column;gap:8px;font-size:12px}.stats-bar-track{width:100%;height:120px;display:flex;align-items:flex-end;background:#f6f7fb;border-radius:5px;overflow:hidden}.stats-bar-track>div{width:100%;background:#7285ad}.stats-day small{color:var(--vp-c-text-3);font-size:11px}.stats-ranking{margin-top:20px;list-style:none;padding:0}.stats-ranking li{display:flex;justify-content:space-between;gap:20px;border-top:1px solid var(--vp-c-divider);padding:15px 0;font-size:14px}.stats-ranking li span{white-space:nowrap;color:var(--vp-c-text-2);font-size:12px}.stats-footnote{margin-top:30px}.stats-footnote a{display:block;color:var(--vp-c-brand-1)}@media(max-width:650px){.stats-page{padding:44px 22px}.stats-kpis{grid-template-columns:repeat(2,1fr)}.stats-kpis>div+div{border-left:0}.stats-kpis>div:nth-child(even){border-left:1px solid var(--vp-c-divider)}.stats-kpis>div:nth-child(n+3){border-top:1px solid var(--vp-c-divider)}.stats-panel{padding:20px}.stats-days{gap:8px}.stats-day small{font-size:9px}.stats-toolbar{align-items:flex-start}.stats-ranking li{font-size:13px}}
</style>
