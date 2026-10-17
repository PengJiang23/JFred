<script setup lang="ts">
import { withBase } from 'vitepress'
import { topics } from '../content'
import Icon from './Icon.vue'
</script>
<template><div class="jf-topic-page"><span class="jf-section-label">EXPLORE BY TOPIC</span><h1>一个主题，一条线索。</h1><p class="jf-topic-intro">从感兴趣的地方开始。专题会随着新的笔记持续生长。</p><div class="jf-topic-directory"><section v-for="topic in topics" :key="topic.id"><div class="jf-topic-heading"><span class="jf-note-symbol" :class="topic.color"><Icon :name="topic.icon" /></span><div><h2><a :href="withBase(topic.href)">{{ topic.title }}</a></h2><span>{{ topic.count }}</span></div></div><p>{{ topic.description }}</p><ol><li v-for="chapter in topic.chapters"><a :href="withBase(chapter.href)">{{ chapter.title }}<Icon name="right" :size="15" /></a></li></ol></section></div><div class="jf-topic-other"><h2>工程实践</h2><a :href="withBase('/notes/deployment')">网站部署记录 ↗</a><a :href="withBase('/notes/workflow')">写作与更新流程 ↗</a><a :href="withBase('/privacy')">评论与统计说明 ↗</a></div></div></template>
