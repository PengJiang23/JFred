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

然后在 `docs/.vitepress/theme/home.ts` 的 `notes` 列表中添加标题、摘要、分类和链接。链接写成 `/notes/my-note` 即可，不需要手动加上 `/blog/`。

如果需要把文章加入侧边栏，可以编辑 `docs/.vitepress/config.mts`。

## 调整首页

- **文案、项目、笔记**：`docs/.vitepress/theme/home.ts`。
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
