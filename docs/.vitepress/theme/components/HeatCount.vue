<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { withBase } from 'vitepress'
import { getPublicStats } from '../community'
const props = defineProps<{ path: string }>()
const reads = ref<number | null>(null)
let request = 0
async function load() {
  const current = ++request
  reads.value = null
  try { const value = await getPublicStats(withBase(props.path)); if (current === request) reads.value = value.visitors } catch { /* Optional analytics must not block reading. */ }
}
onMounted(load)
watch(() => props.path, load)
</script>
<template><span class="jf-heat" title="累计去重阅读：同一 IP 与浏览器，每个北京时间自然日、同一页面计一次；不同天分别累计。">{{ reads === null ? '阅读 —' : `阅读 ${reads.toLocaleString()}` }}</span></template>
