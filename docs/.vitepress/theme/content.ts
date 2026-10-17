export const topics = [
  { id: 'ai', title: 'AI 学习', en: 'ARTIFICIAL INTELLIGENCE', icon: 'code', color: 'blue', description: '从模型原理到应用工程，再用案例与评测检验理解。', href: '/topics/ai/', count: '导读 + 7 章', chapters: [
    { title: '导读 · AI 系统学习指南', href: '/topics/ai/' },
    { title: '01 · 前沿与发展方向', href: '/topics/ai/frontiers' },
    { title: '02 · 模型原理与应用工程', href: '/topics/ai/foundations' },
    { title: '03 · 真实案例与可信评测', href: '/topics/ai/cases' },
    { title: '04 · 学习路线与练手项目', href: '/topics/ai/roadmap' },
    { title: '05 · 术语表与概念边界', href: '/topics/ai/glossary' },
    { title: '06 · 参考资料与论文索引', href: '/topics/ai/references' },
    { title: '07 · 调研方法与插图许可', href: '/topics/ai/methodology' },
  ] },
  { id: 'finance', title: '理财笔记', en: 'PERSONAL FINANCE', icon: 'sun', color: 'peach', description: '记录现金流、财务目标与复盘方法，把事实和假设分开。', href: '/topics/finance/', count: '2 篇笔记', chapters: [
    { title: '专题导览', href: '/topics/finance/' },
    { title: '先看清自己的现金流', href: '/topics/finance/cash-flow' },
    { title: '把财务目标写成可复盘的计划', href: '/topics/finance/goals' },
  ] },
  { id: 'hobbies', title: '兴趣档案', en: 'LIFE & CURIOSITY', icon: 'book', color: 'mint', description: '给阅读、探索与日常实践，留一个可以持续整理的地方。', href: '/topics/hobbies/', count: '2 篇笔记', chapters: [
    { title: '专题导览', href: '/topics/hobbies/' },
    { title: '一份轻量的阅读记录', href: '/topics/hobbies/reading' },
    { title: '给兴趣建一个小档案', href: '/topics/hobbies/practice' },
  ] },
]
export const featuredNotes = [
  { title: 'AI 系统学习指南', category: 'AI 学习', tag: 'AI LEARNING', description: '原有调研的分章阅读版：前沿、原理、案例、学习路线、术语与参考资料。', href: '/topics/ai/', read: '导读 + 7 章', color: 'blue' },
  { title: '从模型原理到可维护的 AI 应用', category: 'AI 学习', tag: 'FOUNDATIONS', description: 'Token、Attention、Transformer、训练、推理，以及后端工程师的应用设计。', href: '/topics/ai/foundations', read: '学习指南 · 第 2 章', color: 'lilac' },
  { title: '先看清自己的现金流', category: '理财笔记', tag: 'CASH FLOW', description: '一张最小收支表，把实际发生、已承诺支出和未来预估分开。', href: '/topics/finance/cash-flow', read: '记录方法', color: 'peach' },
  { title: '一份轻量的阅读记录', category: '兴趣档案', tag: 'READING', description: '记录问题、出处和自己的理解，让阅读留下可回看的线索。', href: '/topics/hobbies/reading', read: '实用模板', color: 'mint' },
  { title: '真实案例与可信评测', category: 'AI 学习', tag: 'EVALUATION', description: '从开源实现到业务结果，理解证据范围、测试集和失败分析。', href: '/topics/ai/cases', read: '学习指南 · 第 3 章', color: 'blue' },
  { title: '一个网站是怎样上线的', category: '工程实践', tag: 'DEPLOYMENT', description: '这个网站实际使用的构建、镜像、反向代理与发布链路。', href: '/notes/deployment', read: '实践记录', color: 'lilac' },
]
