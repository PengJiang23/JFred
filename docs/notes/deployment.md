---
title: 一个网站是怎样上线的
description: JFred 从 GitHub 提交到服务器上线的部署实践。
---

# 一个网站是怎样上线的

网站的内容用 Markdown 维护，页面由 VitePress 生成。发布时，不需要登录服务器逐个复制文件：推送到 GitHub 的 `master` 分支，就会触发自动部署。

## 从代码到页面

```text
推送到 master
      ↓
GitHub Actions 构建静态网站
      ↓
构建 Docker 镜像并推送到 GHCR
      ↓
服务器 runner 调用固定部署命令
      ↓
Compose 更新容器并检查健康状态
      ↓
OpenResty 转发 /blog/ 请求
```

构建工作在 GitHub 的托管机器上完成。服务器只负责拉取构建好的镜像和运行服务。

## 为什么把网站放进镜像

镜像里包含网页文件和静态文件服务器。每次发布使用确定的镜像摘要，方便确认服务器实际运行的是哪个版本，也方便回退。

Compose 管理容器的启动、重启和健康检查。如果新容器没有通过检查，部署脚本会尝试恢复上一版镜像。

## /blog/ 路径如何工作

服务器版本通过 `VITEPRESS_BASE=/blog/` 构建，页面内的资源和链接都会带上这个路径。

OpenResty 将 `/blog/` 转发给本机 `127.0.0.1:18080` 上的静态服务，并去掉前面的 `/blog/`。容器的端口只监听本机，由 OpenResty 统一对外提供访问。

GitHub Pages 仍然使用 `/JFred/` 路径，同一份源码可以分别构建到两个地址。

## 查看发布结果

每次更新后，可以在仓库的 **Actions → Deploy JFred to Lenovo** 中查看构建和部署结果。部署任务还会检查网站入口是否可以正常访问。

服务器上查看容器状态和日志：

```bash
sudo docker compose -f /opt/stacks/jfred/compose.yaml ps
sudo docker compose -f /opt/stacks/jfred/compose.yaml logs --tail=100 -f
```

## 权限保持简单

服务器上的 Deploy Key 只能读取这个仓库。部署 runner 不直接使用 Docker socket，而是调用一个由 root 持有、仅接受指定镜像仓库地址的部署脚本。拉取镜像所用的 GitHub 凭证由当次任务提供，任务完成后清理临时登录信息。

配置文件和完整脚本都保存在 [JFred 的 deploy 目录](https://github.com/PengJiang23/JFred/tree/master/deploy) 中。
