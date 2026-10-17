import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import { topics } from './theme/content'

const topicSidebar = topics.map(t => ({ text: t.title, collapsed: false, items: t.chapters.map(c => ({ text: c.title, link: c.href })) }))
export default withMermaid(defineConfig({
  base: process.env.VITEPRESS_BASE || '/JFred/',
  title: 'JFred',
  description: 'AI 学习、理财笔记和兴趣档案。PengJiang 的个人知识与生活记录。',
  lang: 'zh-CN',
  appearance: false,
  cleanUrls: true,
  mermaid: { theme: 'neutral', securityLevel: 'strict' },
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '专题', link: '/topics/' },
      { text: 'AI 学习', link: '/topics/ai/' },
      { text: '理财', link: '/topics/finance/' },
      { text: '兴趣', link: '/topics/hobbies/' },
      { text: '访客统计', link: '/stats' },
    ],
    sidebar: [
      ...topicSidebar,
      { text: '工程实践', items: [
        { text: '网站部署记录', link: '/notes/deployment' },
        { text: '写作与更新流程', link: '/notes/workflow' },
      ] },
    ],
    outline: { level: [2,3], label: '本章目录' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    sidebarMenuLabel: '专题与章节',
    returnToTopLabel: '回到顶部',
    socialLinks: [{ icon: 'github', link: 'https://github.com/PengJiang23/JFred' }],
  },
}))
