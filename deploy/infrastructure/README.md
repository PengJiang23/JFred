# Lenovo server navigation, shared data and monitoring

## Entry points

Open `http://10.144.144.66/` over EasyTier, or `http://192.168.0.108/` at home.
The SUI2 start page has both groups of links. It is built from official
`reorx/sui2` commit `a1631c4f46e28352f13727601f9fe22f94f63fcf` and served as
static files through Compose/nginx and existing OpenResty. No Node build server
or unauthenticated live editor runs on the server. Navigation container memory
was about 7.5 MiB at verification.

Edit `navigation.json` to add a service. Run `bash build-navigation.sh /path/to/sui2`
on an administration computer, copy the built dist contents into
`/opt/stacks/jfred-infrastructure/navigation/`, then reload the page. Do not put
passwords, tokens or signed URLs in navigation.json. The server's private copy is
backed up. The static site and blog still require their own login where applicable.

EasyTier was already connected: the Mac peer is 10.144.144.32 and the Lenovo peer
is 10.144.144.66. Blog requests failed because OpenResty server_name included only
the LAN address. Admin requests failed because Docker ports bound only that LAN
address and loopback. The blog now matches both addresses. Administrative Docker
ports are IPv4-published with the persistent `jfred-private-ports.service` guard,
which allows only LAN/EasyTier/loopback sources. Restart Docker only during an
appropriate maintenance window; no reboot was required for these fixes.

## Shared databases in 1Panel

- Existing MySQL: retained unchanged, suitable when applications support MySQL.
- PostgreSQL 15.19-alpine: installed from the 1Panel app store; 2 CPU / 512 MiB
  limit, private port. Umami now uses this shared instance through `1panel-network`.
  Each application's database and login must remain separate. Migration dump,
  per-table count verification and retained old data provide a rollback path.
- MongoDB 8.0.15: app-store installation; 2 CPU / 768 MiB limit, authenticated,
  private port. Authenticated ping passed. Currently unused, so intentionally
  stopped with `unless-stopped`. Start in 1Panel before a document-store application
  needs it. Add a least-privilege application user and backup export at that time.
- OpenList, Duplicati and Beszel retain supported SQLite storage, avoiding
  unnecessary migrations and database connections.

`db-1` was Compose's name for the old dedicated Umami PostgreSQL container. It was
not MySQL. It has been removed after the successful migration; the old data
folder is retained temporarily. Future services should reuse these databases,
not install additional MySQL/PostgreSQL/MongoDB instances in their own stacks.

## Beszel and alerts

Beszel 0.21.0 hub is containerized at port 18086. The official checksum-verified
host binary collects CPU, RAM, disks, GPU, temperature and Docker metrics.
The agent connects outbound over WebSocket; its SSH listener is disabled.
Container log/inspect UI is disabled. No Docker socket is mounted into the hub.
The host agent can read Docker through its local socket and therefore remains a
trusted, privileged component. Systemd restricts filesystem writes and privilege
changes; do not expose its credentials or replace the binary with an untrusted one.

Measured steady memory at setup: hub about 14.7 MiB, agent about 16.8 MiB, auditd
about 2.4 MiB. The minute security check is short-lived; measured unit peak was
about 24 MiB. These are point-in-time measurements, not fixed limits or promises.

| Alert | Threshold | Sustained time |
|---|---|---|
| CPU | >90% | 10 min |
| RAM | >90% | 10 min |
| Disk | >90% | 15 min |
| GPU | >98% | 30 min |
| CPU / system temperature | >90°C | 5 min |
| NVIDIA GPU temperature | ≥85°C | 5 min |
| Agent offline | down | 3 min |

No routine bandwidth, individual successful sudo, or single failed-login alerts
are enabled. Beszel provides resource alerts; `security-watch.py` supplements it:

- 20 SSH authentication failures / 10 min or 5 sudo failures / 10 min.
- Root SSH login; UID 0 account changes.
- auditd watches writes to system accounts, sudo rules, SSH configuration/keys,
  system startup units and cron. A write is a reason to check, not proof of intrusion.
- A root process executing a temporary/deleted program and using >20% of one CPU
  continuously for 5 min. Known-path interpreters and low-resource attacks can
  evade this heuristic; this is not a complete endpoint protection system.
- Required services/containers unhealthy for 3 min, OOM events, and missing local
  or encrypted backups for 36 h. MongoDB's intentional stopped state is excluded.
- Events are batched. Persistent conditions notify once, then at most every 6 h;
  recovery is sent once. Sensitive-file writes remain separate audit events.

The Feishu group is **联想服务器告警**, with signed bot **联想服务器监控**.
The local private `~/.ssh/jfred-feishu.json` and server
`/etc/jfred-monitor/feishu.json` contain credentials; neither belongs in Git.
Notifications include condition summaries and selected process metadata, not full
command lines, passwords, or raw logs. Nothing automatically kills processes,
blocks IPs or changes permissions.

`configure-monitor.py` prepares the existing account/notification configuration
and host agent env file; it preserves an existing permanent registration token.
Use `--test` only when a test message is intended. Install the prepared agent env
with mode 600 in `/etc/jfred-monitor/beszel-agent.env`, the checksum-verified
official binary as `/usr/local/bin/beszel-agent`, and `beszel-agent.service` into
`/etc/systemd/system/`. Enable the unit, then run
`configure-alerts.py`. `install-security.sh` installs official Ubuntu auditd,
persistent audit rules and the minute systemd timer.

```sh
systemctl status beszel-agent jfred-security.timer auditd
journalctl -u jfred-security.service -n 20 --no-pager
sudo ausearch -k jfred_privilege -ts today -i
sudo /usr/local/sbin/jfred-security-watch --test
```

Self-monitoring cannot deliver an alert while the entire server, its power or
outbound network is down. Add a heartbeat watcher on a separate always-on device
if whole-server outage notifications are required. A resource alert alone cannot
confirm compromise; verify the process, login and audit evidence.

## Backups and credentials

The daily export now also captures consistent Beszel SQLite snapshots, monitoring
keys/configuration, navigation assets, shared database configuration and PostgreSQL
roles. Duplicati encrypts these exports locally and on Aliyun Drive. Current backup
scope remains JFred and this service stack; unrelated MySQL/Redis applications and
future MongoDB data require their own logical export before production use.

Keep `~/.ssh/jfred-service-access.txt`, `~/.ssh/jfred-databases.json` and
`~/.ssh/jfred-backup-recovery.json` private. Credentials are owner-readable only.
Never recover test data over the running databases. Provision 1Panel PostgreSQL,
restore app roles and database into an isolated target, check integrity, then
restore service configuration and reconnect applications.

### 飞书交互告警卡片（2026-10-17）

个人自建应用“联想服务器告警”只授予 `im:message:send_as_bot`，仅 Jumpen 可用，无对外共享。回调订阅 `card.action.trigger`，通过飞书官方 Python SDK 1.7.5 的出站长连接接收，不开放公网回调端口。`jfred-alerts.service` 使用 DynamicUser、只读系统及 LoadCredential；入口只监听宿主机 `127.0.0.1:18088`，需要随机 Bearer token。应用凭证在 `/etc/jfred-monitor/app.json`，不要提交到 Git。

Beszel 每 30 秒提供已满足持续时间的资源告警状态，安全 watcher 提供独立事件。SQLite `/var/lib/private/jfred-alerts/incidents.db` 记录事件、接管者、按钮操作及静默状态。告警首次通知去重；重要异常首次 @全体（当前群只有本人），未接管 15 分钟升级提醒，之后最多每 6 小时一次；接管后停止未接管升级。正常恢复更新原卡片，并发送一次不 @ 的恢复卡片。安全审计类事件可以人工关闭；持续指标人工处理后仍等待监测恢复，避免把“已处理”误当作指标正常。

按钮支持单项静默 30 分钟 / 2 小时、暂停全部 2 小时、立即恢复全部提醒。暂停只影响通知，仍采集并记录；期间恢复且从未推送的事件不会补发。暂停到期自动解除。已发送卡片在暂停期间仍可更新状态。备用签名机器人用于交互服务中断或连续投递失败；全局暂停也会抑制备用通知（使用最近采集的暂停期限）。

管理员命令：

```sh
sudo jfred-alertctl status
sudo jfred-alertctl pause 120  # 全部暂停 120 分钟；最长 1440 分钟
sudo jfred-alertctl resume
sudo jfred-alertctl test      # 发送明确标记的测试卡片
```

原 Beszel 通知设置私密备份在 `/etc/jfred-monitor/beszel-notifications-before-cards.json`，正式路由关闭 Beszel 的直接 Webhook，避免重复和绕过静默。签名机器人作为备用仍保留在群中。`configure-monitor.py` 检测交互服务后也会保留此路由。资源 / 安全采集持续运行，NVIDIA MX250 使用率 >98% 持续30分钟、温度≥85°C持续5分钟、显卡采集不可用持续5分钟均受监测。

已验证真实飞书 @全体、Jumpen 接管、原卡片更新、单项静默、全局暂停、恢复通知和演练关闭。持久化测试覆盖重复事件、异群回调拒绝、重复回调保护、异常恢复及复发；实测全局暂停期间事件入库但不推送，已恢复事件不会延后刷屏。SDK 通道实测额外内存约210 MiB（主监控 Beszel + agent 约30 MiB），上限384 MiB，无 Docker/socket/root 权限。

每日导出包含卡片 SQLite 一致性快照、应用配置、源代码、锁定依赖清单和 systemd 单元；恢复时先重建 venv 再恢复数据库。Mac 的账号总览：`~/.ssh/lianxiang-all-service-accounts.txt`，权限600；飞书应用凭证单独存放在 `~/.ssh/jfred-feishu-app.json`。

### Complete server backups (2026-10-17 update)

`deploy/backup` supersedes the initial blog-only exporter. Daily02:30 Asia/Shanghai runs four database exports (MySQL, PostgreSQL, Redis, offline MongoDB), per-project persistent-data/config bundles, native/1Panel recovery bundles and content-addressed Docker image archives. SQLite files are snapshotted online. Export names identify purpose and Beijing date; the recovery manifest and SHA256 list document coverage. Successful export then runs both AES destinations once, retaining30 days. See `deploy/backup/RESTORE.md` for ordering, consistency limits and restore guidance. All current applications are included; this is application recovery, not a bootable disk clone.

Artalk was removed; GitHub Discussions/giscus hosts comments without a server container. Navigation links point to the GitHub Discussions console.
