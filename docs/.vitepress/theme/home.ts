// 首页内容：修改这里即可更新展示文案、项目和笔记。
export const home = {
  name: 'JFred',
  author: 'PengJiang',
  github: 'https://github.com/PengJiang23',
  headline: ['把想法，', '变成可用的东西。'],
  description: '你好，我是 PengJiang。这里是我的数字空间，收藏代码、实践与灵感，也记录从一个想法到一次实现的过程。',
  projects: [
    { number: '01', title: 'JFred', category: 'PERSONAL WEBSITE', description: '一个不断生长的个人空间。用文字整理思考，用代码把想法变成日常。', stack: ['VitePress', 'Vue', 'TypeScript'], href: 'https://github.com/PengJiang23/JFred', action: '查看 GitHub', visual: 'website' },
    { number: '02', title: '从提交，到上线。', category: 'BUILD IN PUBLIC', description: '把这个网站的部署过程写下来：从 GitHub Actions 到 Compose，再到 OpenResty。', stack: ['GitHub Actions', 'Docker', 'OpenResty'], href: '/notes/deployment', action: '阅读实践记录', visual: 'pipeline' },
  ],
  notes: [
    { title: '一个网站是怎样上线的', category: '部署实践', tag: 'DEPLOYMENT', description: '构建、镜像与反向代理，串起从代码到网页的完整路径。', href: '/notes/deployment', read: '5 分钟', color: 'blue' },
    { title: '让每一次提交，都成为一次更新', category: '开发笔记', tag: 'WORKFLOW', description: '写作、预览与发布。给个人网站建立一个简单、可持续的更新流程。', href: '/notes/workflow', read: '3 分钟', color: 'peach' },
    { title: '用 Markdown，把内容写清楚', category: '开发笔记', tag: 'WRITING', description: '从标题、代码块到提示容器，探索 VitePress 的内容表达。', href: '/markdown-examples', read: '示例指南', color: 'mint' },
    { title: '让静态页面，也有动态表达', category: '开发笔记', tag: 'VITEPRESS', description: '在 Markdown 中使用 Vue，以及 VitePress 的运行时数据。', href: '/api-examples', read: '示例指南', color: 'lilac' },
  ],
}
