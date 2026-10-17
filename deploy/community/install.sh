#!/usr/bin/env bash
set -Eeuo pipefail
[[ $EUID -eq 0 ]] || exit 2
src=$(cd "$(dirname "$0")" && pwd)
stack=/opt/stacks/jfred-community
umask 077
install -d -m 700 "$stack" "$stack/artalk" "$stack/duplicati" "$stack/openlist" /opt/backups/jfred /opt/backups/jfred-duplicati
chown 1001:1001 "$stack/openlist"
for file in compose.yaml admin-access.yaml bootstrap.py openresty.conf backup.sh configure-backups.py; do
    install -o root -g root -m 600 "$src/$file" "$stack/$file"
done
if [[ ! -f "$stack/.env" ]]; then
    {
        printf 'POSTGRES_PASSWORD=%s\n' "$(openssl rand -hex 24)"
        printf 'APP_SECRET=%s\n' "$(openssl rand -hex 32)"
        printf 'TWO_FACTOR_ENCRYPTION_KEY=%s\n' "$(openssl rand -hex 32)"
        printf 'DUPLICATI_SETTINGS_KEY=%s\n' "$(openssl rand -hex 32)"
        printf 'OPENLIST_PASSWORD=%s\n' "$(openssl rand -hex 18)"
        printf 'DUPLICATI_PASSWORD=%s\n' "$(openssl rand -hex 18)"
    } > "$stack/.env"
fi
if ! grep -q '^OPENLIST_PASSWORD=' "$stack/.env"; then printf 'OPENLIST_PASSWORD=%s\n' "$(openssl rand -hex 18)" >> "$stack/.env"; fi
if [[ ! -f "$stack/artalk/artalk.yml" ]]; then
    cat > "$stack/artalk/artalk.yml" <<CONFIG
host: 0.0.0.0
port: 23366
app_key: $(openssl rand -hex 32)
locale: zh-CN
timezone: Asia/Shanghai
site_default: JFred
site_url: http://192.168.0.108/blog/
db:
  type: sqlite
  file: /data/artalk.db
http:
  proxy_header: X-Real-IP
trusted_domains:
  - http://192.168.0.108
moderator:
  pending_default: true
captcha:
  enabled: true
  always: false
  captcha_type: image
  action_limit: 3
  action_reset: 60
img_upload:
  enabled: false
frontend:
  darkMode: false
  locale: zh-CN
  pvAdd: false
  req: email
CONFIG
fi
cd "$stack"
docker compose up -d db artalk umami duplicati openlist
python3 "$stack/bootstrap.py"
if [[ ! -f "$stack/.artalk-admin-ready" ]]; then
    python3 - <<'PY'
import json, subprocess
s=json.load(open('/opt/stacks/jfred-community/access.json'))
subprocess.run(['docker','compose','exec','-T','artalk','artalk','admin','--name',s['artalk_name'],'--email',s['artalk_email'],'--password',s['artalk_password']],check=True)
PY
    touch "$stack/.artalk-admin-ready"
fi
# Admin listeners are enabled only after the initial passwords have been replaced.
docker compose -f compose.yaml -f admin-access.yaml up -d
site=/opt/1panel/www/conf.d/192.168.0.108jfred.conf
cp -n "$site" "$stack/openresty-site.before" || true
install -m 644 "$stack/openresty.conf" /opt/1panel/www/conf.d/jfred-community.include
python3 - "$site" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); s=p.read_text()
line='    include /usr/local/openresty/nginx/conf/conf.d/jfred-community.include;'
# Actual host/container include path is derived from existing conf path below if needed.
if 'jfred-community.include' not in s:
 s=s.replace('server {','server {\n'+line,1)
 p.write_text(s)
PY
if ! docker exec 1Panel-openresty-7mXZ nginx -t; then
    cp "$stack/openresty-site.before" "$site"
    exit 1
fi
docker exec 1Panel-openresty-7mXZ nginx -s reload
install -m 700 "$stack/backup.sh" /usr/local/sbin/backup-jfred
cat > /etc/systemd/system/jfred-backup.service <<'UNIT'
[Unit]
Description=Consistent JFred comment and analytics backup
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/backup-jfred
UNIT
cat > /etc/systemd/system/jfred-backup.timer <<'UNIT'
[Unit]
Description=Daily JFred local export at 02:30 Asia/Shanghai
[Timer]
OnCalendar=*-*-* 02:30:00 Asia/Shanghai
Persistent=true
RandomizedDelaySec=300
[Install]
WantedBy=timers.target
UNIT
systemctl daemon-reload
systemctl enable --now jfred-backup.timer
/usr/local/sbin/backup-jfred
python3 - <<'PY'
import json, pathlib, os
p=pathlib.Path('/opt/stacks/jfred-community'); s=json.loads((p/'access.json').read_text())
e=dict(l.split('=',1) for l in (p/'.env').read_text().splitlines())
t='JFred service access (keep private)\n\n'
t+=f"Artalk: http://192.168.0.108:18081/\nName: {s['artalk_name']}\nEmail: {s['artalk_email']}\nPassword: {s['artalk_password']}\n\n"
t+=f"Umami: http://192.168.0.108:18082/\nUsername: {s['umami_username']}\nPassword: {s['umami_password']}\n\n"
t+=f"Duplicati: http://192.168.0.108:18083/\nPassword: {e['DUPLICATI_PASSWORD']}\n\nCloud backup: Aliyun Drive via OpenList WebDAV (authorization pending).\nWebDAV URL inside Docker: http://openlist:5244/dav/aliyun/jfred-backups\nOSS bucket backup-data-j (Hangzhou) is reserved for blog media; no OSS backup job is enabled.\n"
t+=f"OpenList: http://192.168.0.108:18084/\nUsername: admin\nPassword: {e['OPENLIST_PASSWORD']}\nCloud drive: authorize Aliyun Drive yourself; no refresh token configured.\n"
recovery=pathlib.Path('/home/jiangpeng/services/jfred-backup-recovery.json')
if recovery.exists() and json.loads(recovery.read_text()).get('cloud_enabled'):
 t=t.replace('Cloud backup: Aliyun Drive via OpenList WebDAV (authorization pending).','Cloud backup: Aliyun Drive via restricted OpenList WebDAV; verified and scheduled daily at 03:30 Asia/Shanghai.').replace('Cloud drive: authorize Aliyun Drive yourself; no refresh token configured.','Cloud drive connected at /aliyun. Backup folder: /aliyun/jfred-backups.').replace('http://openlist:5244/dav/aliyun/jfred-backups','http://openlist:5244/dav/')
f=pathlib.Path('/home/jiangpeng/services/jfred-service-access.txt'); f.write_text(t); f.chmod(0o600); os.chown(f,1000,1000)
PY
runuser -u jiangpeng -- python3 "$src/configure-backups.py"
echo 'Community services configured. Check the private access file for current cloud authorization status.'
