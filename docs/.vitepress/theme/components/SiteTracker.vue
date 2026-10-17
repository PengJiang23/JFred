<script setup lang="ts">
import { onMounted } from 'vue'
import { withBase } from 'vitepress'
import { communityEnabled, websiteId, canonicalPath } from '../community'
onMounted(() => {
  if (!communityEnabled() || document.getElementById('jfred-analytics')) return
  ;(window as any).jfredBeforeSend = (_type: string, payload: any) => {
    if (payload.url) payload.url = canonicalPath(new URL(payload.url, window.location.origin).pathname)
    return payload
  }
  const script = document.createElement('script')
  script.id = 'jfred-analytics'; script.defer = true
  script.src = withBase('/metrics/script.js')
  script.dataset.websiteId = websiteId
  script.dataset.beforeSend = 'jfredBeforeSend'
  script.dataset.doNotTrack = 'true'
  script.dataset.excludeSearch = 'true'
  document.head.appendChild(script)
})
</script>
<template><span hidden aria-hidden="true"></span></template>
