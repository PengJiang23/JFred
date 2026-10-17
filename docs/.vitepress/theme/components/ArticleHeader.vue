<script setup lang="ts">
import { useData, useRoute, withBase } from 'vitepress'
import HeatCount from './HeatCount.vue'
const { frontmatter } = useData()
const route = useRoute()
</script>
<template><div class="jf-article-meta" v-if="frontmatter.comments !== false"><a :href="withBase('/topics/')">{{ frontmatter.topic || '工程实践' }}</a><span>·</span><HeatCount :path="route.path.replace(withBase('/'), '/')" /><span v-if="frontmatter.sourceDate">· 调研截止 {{ String(frontmatter.sourceDate).slice(0,10) }}</span></div></template>
