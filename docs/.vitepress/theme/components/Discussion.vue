<script setup lang="ts">
import { computed } from 'vue'
import { useData, useRoute, withBase } from 'vitepress'
import Giscus from '@giscus/vue'
import { canonicalPath } from '../community'
const { frontmatter } = useData()
const route = useRoute()
const discussionTerm = computed(() => `JFred ${canonicalPath(route.path.replace(withBase('/'), '/'))}`)
</script>
<template>
  <section v-if="frontmatter.comments !== false" class="jf-discussion" aria-labelledby="discussion-title">
    <h2 id="discussion-title">交流与补充</h2>
    <p class="jf-discussion-notice">使用 GitHub 账号参与讨论，评论公开保存在 GitHub Discussions。<a href="https://github.com/PengJiang23/JFred/discussions" target="_blank" rel="noopener noreferrer">前往 GitHub 讨论</a><a :href="withBase('/privacy')">了解说明</a></p>
    <ClientOnly>
      <Giscus :key="discussionTerm" repo="PengJiang23/JFred" repo-id="R_kgDONP0I7g"
        category="Announcements" category-id="DIC_kwDONP0I7s4DIxGQ"
        mapping="specific" :term="discussionTerm" strict="1"
        reactions-enabled="1" emit-metadata="0" input-position="top"
        theme="noborder_light" lang="zh-CN" loading="lazy" />
    </ClientOnly>
  </section>
</template>
