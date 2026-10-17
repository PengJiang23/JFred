#!/bin/bash
set -Eeuo pipefail
umask 077
src=/home/jiangpeng/services
DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::http::Proxy=http://127.0.0.1:20172 -o Acquire::https::Proxy=http://127.0.0.1:20172 install -y --no-install-recommends auditd
install -d -m 700 /etc/jfred-monitor /var/lib/jfred-security
install -m 750 "$src/security-watch.py" /usr/local/sbin/jfred-security-watch
python3 - <<'PY'
import json,pathlib,subprocess
p=pathlib.Path('/etc/jfred-monitor/policy.json')
# MongoDB is provisioned for future use and intentionally stopped; not a monitored outage.
names=subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).splitlines()
names=[n for n in names if not n.startswith('1Panel-mongodb-')]
policy={'containers':names,'units':['docker.service','v2raya.service','beszel-agent.service','auditd.service','jfred-backup.timer','jfred-private-ports.service','actions.runner.PengJiang23-JFred.lianxiang-jfred.service']}
p.write_text(json.dumps(policy,indent=2));p.chmod(0o600)
rules=[]
for p,key in [('/etc/passwd','identity'),('/etc/group','identity'),('/etc/sudoers','privilege'),('/etc/sudoers.d','privilege'),('/etc/ssh/sshd_config','ssh'),('/etc/ssh/sshd_config.d','ssh'),('/root/.ssh','ssh'),('/home/jiangpeng/.ssh','ssh'),('/etc/systemd/system','persistence'),('/etc/crontab','persistence'),('/etc/cron.d','persistence'),('/var/spool/cron','persistence')]:
 if pathlib.Path(p).exists():rules.append(f'-w {p} -p wa -k jfred_{key}')
pathlib.Path('/etc/audit/rules.d/70-jfred.rules').write_text('\n'.join(rules)+'\n')
PY
systemctl enable --now auditd
augenrules --load
cat > /etc/systemd/system/jfred-security.service <<'UNIT'
[Unit]
Description=Low-noise local security and critical-service checks
After=network-online.target docker.service auditd.service
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/jfred-security-watch
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/var/lib/jfred-security
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
MemoryMax=96M
TimeoutStartSec=90
UNIT
cat > /etc/systemd/system/jfred-security.timer <<'UNIT'
[Unit]
Description=Check security and critical services every minute
[Timer]
OnBootSec=3min
OnUnitActiveSec=60s
AccuracySec=5s
[Install]
WantedBy=timers.target
UNIT
systemctl daemon-reload
/usr/local/sbin/jfred-security-watch
systemctl enable --now jfred-security.timer
/usr/local/sbin/jfred-security-watch --test
