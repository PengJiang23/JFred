#!/usr/bin/env bash
set -Eeuo pipefail
[[ $EUID -eq 0 ]] || exit 2
src=$(cd "$(dirname "$0")" && pwd)
stack=/opt/stacks/jfred-community
umask 077
[[ -x /usr/local/sbin/jfred-private-ports ]] || { echo 'Install the private administration firewall rules first.'; exit 1; }
/usr/local/sbin/jfred-private-ports
install -d -m 700 "$stack" "$stack/duplicati" "$stack/openlist" /opt/backups/jfred /opt/backups/jfred-duplicati
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
cd "$stack"
# Provision the shared database in 1Panel first; never recreate a per-app database.
grep -q '^POSTGRES_CONTAINER=' "$stack/.env" || { echo 'Configure POSTGRES_CONTAINER in the private .env for the shared 1Panel PostgreSQL instance first.'; exit 1; }
docker compose up -d umami duplicati openlist
python3 "$stack/bootstrap.py"
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
# Complete backup scheduling is managed by deploy/backup/install.sh.
[[ -f /opt/jfred-backup/run-daily.py ]] || { echo 'Install the complete server backup pipeline first.'; exit 1; }
python3 - <<'PY'
import json, pathlib, os
p=pathlib.Path('/opt/stacks/jfred-community'); s=json.loads((p/'access.json').read_text())
e=dict(l.split('=',1) for l in (p/'.env').read_text().splitlines())
t='JFred service access (keep private)\n\n'
t+=f"Umami: http://192.168.0.108:18082/\nUsername: {s['umami_username']}\nPassword: {s['umami_password']}\n\n"
t+=f"Duplicati: http://192.168.0.108:18083/\nPassword: {e['DUPLICATI_PASSWORD']}\n\nCloud backup: Aliyun Drive via OpenList WebDAV (authorization pending).\nWebDAV URL inside Docker: http://openlist:5244/dav/aliyun/jfred-backups\nOSS bucket backup-data-j (Hangzhou) is reserved for blog media; no OSS backup job is enabled.\n"
t+=f"OpenList: http://192.168.0.108:18084/\nUsername: admin\nPassword: {e['OPENLIST_PASSWORD']}\nCloud drive: authorize Aliyun Drive yourself; no refresh token configured.\n"
recovery=pathlib.Path('/home/jiangpeng/services/jfred-backup-recovery.json')
if recovery.exists() and json.loads(recovery.read_text()).get('cloud_enabled'):
 t=t.replace('Cloud backup: Aliyun Drive via OpenList WebDAV (authorization pending).','Cloud backup: Aliyun Drive via restricted OpenList WebDAV; verified and scheduled daily at 03:30 Asia/Shanghai.').replace('Cloud drive: authorize Aliyun Drive yourself; no refresh token configured.','Cloud drive connected at /aliyun. Backup folder: /aliyun/jfred-backups.').replace('http://openlist:5244/dav/aliyun/jfred-backups','http://openlist:5244/dav/')
f=pathlib.Path('/home/jiangpeng/services/jfred-service-access.txt'); f.write_text(t); f.chmod(0o600); os.chown(f,1000,1000)
PY
echo 'Existing complete daily backup configuration preserved.'
echo 'Community services configured. Check the private access file for current cloud authorization status.'
