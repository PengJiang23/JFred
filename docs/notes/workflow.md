---
title: 让每一次提交，都成为一次更新
description: 用 Markdown、Vue 和自动部署维护个人网站。
---

# 让每一次提交，都成为一次更新

一个个人网站最重要的不是第一次上线，而是之后还能轻松更新。JFred 的内容、样式和部署配置都放在同一个仓库里。

## 本地预览

第一次克隆后，安装依赖并启动开发服务器：

```bash
npm ci
npm run docs:dev
```

打开终端中显示的地址。修改 Markdown 或 Vue 文件时，页面会自动更新。

## 写一篇笔记

在 `docs/notes/` 新建一个 Markdown 文件，例如 `my-note.md`：

```md
---
title: 新笔记的标题
description: 用一句话介绍这篇笔记。
---

# 新笔记的标题

从一个具体的问题开始记录。
```

然后在 `docs/.vitepress/theme/content.ts` 的 `featuredNotes` 列表中添加标题、摘要、分类和链接。链接写成 `/notes/my-note` 即可，不需要手动加上 `/blog/`。

专题章节在 `content.ts` 中集中维护，侧边栏与快捷导航会同步更新。工程实践的侧边栏可编辑 `docs/.vitepress/config.mts`。

## 调整首页

- **首页文案**：`docs/.vitepress/theme/home.ts`。
- **专题、章节、笔记卡片**：`docs/.vitepress/theme/content.ts`。
- **首页布局和交互**：`docs/.vitepress/theme/components/HomePage.vue`。
- **颜色、字号、间距和移动端布局**：`docs/.vitepress/theme/style.css`。

首页的快捷导航会自动读取笔记列表。添加笔记后，搜索入口也会一起更新。

## 发布之前

按服务器的路径做一次构建检查：

```bash
VITEPRESS_BASE=/blog/ npm run docs:build
```

确认页面正常后，再提交和推送：

```bash
git add .
git commit -m "Update website content"
git push origin master
```

GitHub Actions 会构建新镜像，然后更新服务器。通过 Actions 页面确认任务成功，再访问网站检查结果。

## 评论、阅读量与备份

文章下方接入 Artalk 评论，审核通过后公开。阅读量由 Umami 提供，显示按自然日去重的累计阅读；具体口径见[评论与统计说明](/privacy)。文章上线后尽量保持路径稳定，以免把同一篇文章的统计与讨论分散到多个地址。

评论和统计数据库独立于网站容器保存。服务器每天导出一致性备份，Duplicati 通过 OpenList 连接阿里云盘；首次云盘授权与备份加密口令需要在管理界面完成。操作与恢复说明保存在仓库 `deploy/community/README.md`。
