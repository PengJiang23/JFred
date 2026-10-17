import { h } from 'vue'
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import HomePage from './components/HomePage.vue'
import TopicsPage from './components/TopicsPage.vue'
import Discussion from './components/Discussion.vue'
import ArticleHeader from './components/ArticleHeader.vue'
import SiteTracker from './components/SiteTracker.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    'doc-before': () => h(ArticleHeader),
    'doc-after': () => h(Discussion),
    'layout-bottom': () => h(SiteTracker),
  }),
  enhanceApp({ app }) {
    app.component('HomePage', HomePage)
    app.component('TopicsPage', TopicsPage)
  },
} satisfies Theme
