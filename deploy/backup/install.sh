#!/bin/bash
set -Eeuo pipefail
umask 077
src=${1:-/home/jiangpeng}
install -d -m 700 /opt/jfred-backup
install -m 700 "$src/export-server.py" "$src/run-daily.py" /opt/jfred-backup/
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
# Disable independent schedules: this service runs each destination only after export succeeds.
python3 - <<'PY'
import json,pathlib,re,urllib.request,datetime
root=pathlib.Path('/home/jiangpeng/services');state=json.loads((root/'jfred-backup-recovery.json').read_text());access=(root/'jfred-service-access.txt').read_text();password=re.search(r'Duplicati:.*?Password: ([^\n]+)',access,re.S)[1];base='http://127.0.0.1:18083/api/v1'
def api(path,body=None,token=None,method=None):
 h={'Content-Type':'application/json'}
 if token:h['Authorization']='Bearer '+token
 q=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=h,method=method)
 with urllib.request.urlopen(q,timeout=30) as f:
  raw=f.read();return json.loads(raw) if raw else {}
t=api('/auth/login',{'Password':password,'RememberMe':False})['AccessToken']
for label in ['local','cloud']:
 path='/backup/'+str(state[label+'_backup_id']);backup=api(path,token=t)['Backup'];settings={s['Name']:s['Value'] for s in backup['Settings']};assert settings['encryption-module']=='aes'
 # The API masks secret fields; explicitly preserve the already-tested recovery passphrase.
 for item in backup['Settings']:
  if item['Name']=='passphrase':item['Value']=state['encryption_passphrase']
 backup['Name']='服务器每日完整备份 · '+('本机加密副本' if label=='local' else '阿里云盘加密副本')
 backup['Description']='数据库独立导出、全部已安装容器应用、镜像离线副本、1Panel和原生服务；每天02:30导出后执行。'
 # Retire old source tarballs from future versions while retaining their existing encrypted history.
 backup['Sources']=['/source/daily/','/source/application-images/']
 if label=='cloud':
  for k,v in {'dblock-size':'10mb','read-write-timeout':'5m','short-timeout':'5m','list-timeout':'15m','asynchronous-concurrent-upload-limit':'2'}.items():
   match=next((x for x in backup['Settings'] if x['Name']==k),None)
   if match:match['Value']=v
   else:backup['Settings'].append({'Name':k,'Value':v})
 api(path,{'Backup':backup,'Schedule':None},t,'PUT')
 actual=api(path,token=t);assert not actual.get('Schedule')
state.update(local_schedule='After daily 02:30 Asia/Shanghai export',cloud_schedule='After local encrypted copy, once daily',scope='all current server applications, Docker images and shared databases',encryption='AES',export_directory='/opt/backups/jfred/daily')
(root/'jfred-backup-recovery.json').write_text(json.dumps(state,indent=2));(root/'jfred-backup-recovery.json').chmod(0o600)
# Record both independent encryption secrets without printing either one.
env=dict(l.split('=',1) for l in pathlib.Path('/opt/stacks/jfred-community/.env').read_text().splitlines() if '=' in l)
p=root/'lianxiang-all-service-accounts.txt';s=p.read_text();s=re.sub(r'Artalk:.*?(?=Umami:)', 'GitHub 评论：giscus / GitHub Discussions，使用自己的 GitHub 账号，无独立密码。\n\n',s,flags=re.S)
marker='\n=== 备份加密与恢复（最新配置） ===\n';s=s.split(marker)[0]+marker
s+='备份解密口令（Duplicati AES 备份恢复时填写）：'+state['encryption_passphrase']+'\n'
s+='Duplicati 配置加密密钥（SETTINGS_ENCRYPTION_KEY，恢复管理配置用，与备份解密口令不同）：'+env['DUPLICATI_SETTINGS_KEY']+'\n'
s+='每天北京时间02:30一次：数据库/应用一致性导出 → 本机AES副本 → 阿里云盘AES副本；历史版本30天。\n'
s+='本机加密目录：/opt/backups/jfred-duplicati；云盘：/aliyun/jfred-backups；原始导出：/opt/backups/jfred/daily（仅root可读，明文）。\n'
s+='恢复说明：Duplicati恢复列表 /source/daily/RESTORE-恢复说明.md；Mac本机也保存独立恢复说明。请在服务器以外保管此账号文件。\n'
p.write_text(s);p.chmod(0o600)
print('Two AES backup jobs verified; independent schedules disabled; private recovery credentials recorded.')
PY
systemctl daemon-reload
systemctl enable --now jfred-backup.timer
