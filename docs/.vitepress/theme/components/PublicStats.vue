<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { withBase } from 'vitepress'
import { getPublicStats } from '../community'
const stats = ref<{ pageviews:number; visitors:number } | null>(null)
onMounted(async () => { try { stats.value = await getPublicStats() } catch { /* Display an honest unavailable state. */ } })
</script>
<template><div class="jf-public-stats"><span>站点访问</span><span>浏览 {{ stats ? stats.pageviews.toLocaleString() : '—' }}</span><span>去重访问 {{ stats ? stats.visitors.toLocaleString() : '—' }}</span><a :href="withBase('/privacy')">按自然日去重 · 统计说明 ↗</a></div></template>
