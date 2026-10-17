import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base: process.env.VITEPRESS_BASE || "/JFred/",
  title: "JFred",
  description: "代码、实践与灵感。PengJiang 的个人数字空间。",
  lang: 'zh-CN',
  appearance: false,
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '首页', link: '/' },
      { text: '项目', link: '/#projects' },
      { text: '笔记', link: '/#notes' }
    ],

    sidebar: [
      {
        text: '实践记录',
        items: [
          { text: '一个网站是怎样上线的', link: '/notes/deployment' },
          { text: '网站的更新流程', link: '/notes/workflow' }
        ]
      },
      {
        text: '写作与开发',
        items: [
          { text: 'Markdown Examples', link: '/markdown-examples' },
          { text: 'Runtime API Examples', link: '/api-examples' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/PengJiang23/JFred' }
    ]
  }
})
