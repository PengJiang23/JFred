#!/bin/bash
set -Eeuo pipefail
umask 077
src=${1:-/home/jiangpeng}
install -d -m 700 /opt/jfred-backup
install -m 700 "$src/export-server.py" "$src/run-daily.py" "$src/group-exports.py" "$src/configure-groups.py" "$src/verify-encrypted-copy.py" "$src/verify-grouping.py" /opt/jfred-backup/
install -m 600 "$src/RESTORE.md" /opt/jfred-backup/
cat > /usr/local/sbin/backup-jfred <<'RUN'
#!/bin/bash
set -Eeuo pipefail
exec /usr/bin/python3 /opt/jfred-backup/run-daily.py
RUN
chmod 700 /usr/local/sbin/backup-jfred
cat > /etc/systemd/system/jfred-backup.service <<'UNIT'
[Unit]
Description=Daily server database, applications and encrypted recovery backups
After=docker.service network-online.target
Wants=network-online.target
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/backup-jfred
TimeoutStartSec=12h
UMask=0077
Nice=10
IOSchedulingClass=idle
[Install]
WantedBy=multi-user.target
UNIT
cat > /etc/systemd/system/jfred-backup.timer <<'UNIT'
[Unit]
Description=One daily complete server backup at 02:30 Asia/Shanghai
[Timer]
OnCalendar=*-*-* 02:30:00 Asia/Shanghai
Persistent=true
[Install]
WantedBy=timers.target
UNIT
# Create two independent categories per destination; legacy sets remain untouched.
/usr/bin/python3 /opt/jfred-backup/configure-groups.py
systemctl daemon-reload
systemctl enable --now jfred-backup.timer
