# 联想服务器恢复说明

备份入口：Duplicati → 恢复 → 选择“每日分类备份”的数据库或应用数据与配置任务 → 选择日期 → `/source/grouped/对应分类/`。原完整备份和旧 Docker镜像备份仍保留，只用于历史恢复，不再自动运行。恢复口令保持不变，在 Mac `~/.ssh/lianxiang-all-service-accounts.txt` 的“备份恢复”部分。另存此文件，不要只存在被备份的服务器上。

本机和云盘各有两个自动运行的独立 AES 备份集：

```text
/aliyun/jfred-backups/
├── 数据库/
└── 应用数据与配置/
```

本机对应 `/opt/backups/jfred-duplicati/` 下同名目录。每个分类内的 `BACKUP-分类说明.json` 标明所属分类、导出时间和原始文件清单；新任务保留30天历史。云盘中的 AES 分块仍由 Duplicati 管理，不能按单块判断某个数据库或应用。原完整备份的数据保持原位，旧任务不再自动运行或清理。

`daily/` 内的文件名区分用途，时间为北京时间：

- `database-mysql-all-日期.sql.gz`：MySQL 所有库、账号、触发器、事件和存储过程。
- `database-postgresql-all-日期.sql.gz`：PostgreSQL 所有库与角色。每个库的逻辑快照一致；各引擎之间不是跨库事务快照。
- `database-mongodb-offline-physical-日期.tar.gz`：MongoDB 停止时的冷备份（包含认证数据）。运行后自动改成 `database-mongodb-all-日期.archive.gz`。
- `database-redis-all-日期.rdb`：Redis 所有逻辑库的 RDB 一致性快照。
- `application-项目名-日期.tar.gz`：该 Compose 项目的配置、持久目录和卷。SQLite 已用在线 backup API 快照，物理 MySQL/PG/Redis 目录不重复打包。
- `application-1panel-manager-日期.tar.gz`：1Panel 程序、管理数据库与配置。
- `application-host-and-native-services-日期.tar.gz`：v2rayA、EasyTier、监控与飞书告警、系统服务配置、服务器账号及 SSH/部署凭据、GitHub runner 程序（排除工作缓存/日志）、飞书 SDK 安装包缓存。
- `application-container-inventory-日期.json`：完整容器配置、环境、挂载、网络、镜像ID，含私密信息。
- `recovery-manifest-日期.json`：本次导出清单；`SHA256SUMS.txt` 校验导出文件完整性。
- 镜像只记录名称、版本、镜像ID与可用的 RepoDigest，保存在容器清单及恢复清单中，不再导出 Docker 镜像压缩包。历史 `Docker镜像/` 备份仍可恢复。

## 整机恢复顺序

1. 安装兼容 Ubuntu、Docker 和 Compose，确认数据盘挂载（当前 Docker 数据根目录在 `/disk512/docker`）。只在隔离的新机器演练，避免覆盖正在运行的服务。
2. 安装 Duplicati，使用本机备份目录或阿里云盘 WebDAV 下载备份并输入 AES 恢复口令。如果原 OpenList 不可用，先从云盘取回完整 Duplicati 加密备份集，恢复到本地文件夹。
3. 分别恢复同一批导出时间的数据库和应用配置两个分类目录；每个分类内运行 `sha256sum -c SHA256SUMS.txt`。跨午夜备份以清单的导出时间对齐。
4. 根据恢复清单 `container_images` 的 RepoDigest、镜像标签和 Compose 配置重新拉取镜像，再执行 `docker compose up -d`。今后的备份不包含镜像层，恢复时需要能访问镜像仓库。若恢复历史镜像备份，可逐个执行 `gzip -dc application-image-镜像名-ID.docker.tar.gz | docker load`。
5. 选择性解包 `application-*.tar.gz` 到新机器对应路径；档案内路径是相对 `/` 的 `opt/...`、`etc/...` 等。保留原 UID/GID 和权限。不要把旧机器的 `/etc/passwd`、`shadow`、网络、fstab 或 machine-id 不加检查地覆盖到新系统。
6. 先恢复数据库。MySQL 使用同版本镜像，在空实例中导入 SQL；PostgreSQL 先用独立临时超级用户（如 `jfred_restore_admin`）初始化空实例，再用这个用户执行 `psql -X -v ON_ERROR_STOP=1 -d postgres` 导入解压后的 SQL；导入后按恢复配置重新连接原账号。不要以备份中将被重建的原角色导入。SQL 包含 DROP/CREATE 数据库和角色，只能在隔离实例中操作。MongoDB 冷备只在停止的同版本 MongoDB 容器恢复；Redis 停止后恢复 RDB 到数据目录，并确保新实例不会优先加载旧 AOF。
7. 创建 Compose 依赖网络 `1panel-network`，按清单恢复网络/卷，先数据库，再 OpenList、Duplicati、Umami、Beszel、博客、导航、OpenResty和EasyTier。OpenResty、云盘、SQLite 数据与密钥一并恢复；SQLite 恢复前停止对应服务，移除不匹配的 WAL/SHM 后再启动。
8. 恢复原生服务的 systemd 单元与程序；飞书通道重建 Python venv（`requirements.txt`；也可从恢复出的 `jfred-lark-wheels` 离线安装）再启动。GitHub runner 优先重新注册，不要让两台机器同时使用同一 runner 身份。迁移机器时检查原有 SSH 与 EasyTier 身份是否仍适用。
9. 先核对应用登录、文章/访客统计、代理、EasyTier连接、飞书告警及下一次备份，再切换用户访问。

## 备份边界

备份覆盖当前所有 Docker 应用的可恢复配置/持久数据、共享数据库及上述原生管理服务；只保留镜像引用信息，不备份镜像层。数据库按自身导出机制获取一致性；普通应用文件应避免在导出窗口做大规模写入。不是包含分区表、引导器和所有个人文件的整盘镜像。Docker 运行层临时文件、日志、构建缓存、可重新下载的依赖不作为业务数据；应用应把重要内容写入挂载卷。新增应用将按容器挂载与 Compose 项目自动纳入，下次检查恢复清单即可确认。

本机 `/opt/backups/jfred` 是 root 可读的明文导出区。Duplicati 的本机副本 `/opt/backups/jfred-duplicati` 及阿里云盘 `/aliyun/jfred-backups` 内文件为 AES 密文；Duplicati 的物理分块名由软件管理，不要手动改名或删除单块。按用途命名的文件在“恢复”列表中可见。口令丢失无法解密，不应把恢复口令只保存在备份自身。

## 日常查看与手动触发

```sh
sudo systemctl list-timers jfred-backup.timer
sudo systemctl start --no-block jfred-backup.service
sudo journalctl -u jfred-backup.service -n 50 --no-pager
```

Duplicati 内四项当前任务由同一个系统定时器每天北京时间02:30触发一次，统一导出完成后顺序执行本机两类、云端两类；没有单独的内置计划时间属于正常状态。原完整备份和旧镜像备份不再自动触发，原数据暂不自动清理。阿里云盘经 WebDAV，空闲传输超时为5分钟；分类备份集使用10MiB分块，旧完整备份集的50MiB分块保持不变。不要手工重命名或删除 `.aes` 分块。

分类导出目录通过硬链接引用同一批导出文件，避免再占用一份明文空间。每批导出会核对数据库与应用分类清单，发现未分类文件或校验值不匹配会停止执行。已有镜像导出缓存及加密备份暂时保留，不再新增；恢复旧备份的口令不变。
