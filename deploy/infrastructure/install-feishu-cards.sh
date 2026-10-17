#!/bin/bash
set -euo pipefail
umask 077
# Requires python3-venv. Override PIP_INDEX_URL for a trusted local package mirror.
install -d -m 755 /opt/jfred-alerts
if [[ ! -x /opt/jfred-alerts/venv/bin/python ]]; then python3 -m venv /opt/jfred-alerts/venv; fi
/opt/jfred-alerts/venv/bin/pip install lark-oapi==1.7.5
/opt/jfred-alerts/venv/bin/pip freeze > /opt/jfred-alerts/requirements.txt
install -m 600 /home/jiangpeng/services/jfred-feishu-app.json /etc/jfred-monitor/app.json
python3 - <<'PY'
import pathlib,secrets,json,re
root=pathlib.Path('/etc/jfred-monitor')
f=root/'ingest-token'
if not f.exists():f.write_text(secrets.token_urlsafe(32));f.chmod(0o600)
s=pathlib.Path('/home/jiangpeng/services/jfred-service-access.txt').read_text()
p=re.search(r'Beszel:.*?Password: ([^\n]+)',s,re.S)[1]
(root/'beszel.json').write_text(json.dumps({'username':'admin@jfred.local','password':p}));(root/'beszel.json').chmod(0o600)
PY
install -m 755 /home/jiangpeng/feishu-cards.py /opt/jfred-alerts/feishu-cards.py
cat > /etc/systemd/system/jfred-alerts.service <<'UNIT'
[Unit]
Description=Feishu incident cards and outbound callback connection
After=network-online.target docker.service
Wants=network-online.target
[Service]
DynamicUser=yes
StateDirectory=jfred-alerts
StateDirectoryMode=0700
LoadCredential=app.json:/etc/jfred-monitor/app.json
LoadCredential=beszel.json:/etc/jfred-monitor/beszel.json
LoadCredential=ingest-token:/etc/jfred-monitor/ingest-token
ExecStart=/opt/jfred-alerts/venv/bin/python /opt/jfred-alerts/feishu-cards.py
Restart=on-failure
RestartSec=15
UMask=0077
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictSUIDSGID=yes
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
MemoryMax=384M
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now jfred-alerts.service
printf 'Incident service installed.\n'
