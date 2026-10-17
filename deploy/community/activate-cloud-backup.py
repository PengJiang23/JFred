#!/usr/bin/env python3
"""Enable daily cloud scheduling only after a verified encrypted cloud restore."""
import pathlib,sys
if pathlib.Path('/opt/jfred-backup/run-daily.py').exists():
 print('Complete daily server backup is configured; manage it through jfred-backup.timer. Legacy schedules remain disabled.')
 sys.exit(0)

import datetime,json,pathlib,re,urllib.parse,urllib.request
from zoneinfo import ZoneInfo
root=pathlib.Path('/home/jiangpeng/services')
f=root/'jfred-backup-recovery.json';state=json.loads(f.read_text())
assert state.get('cloud_restore_task_id'),'Perform an encrypted cloud restore first'
log=pathlib.Path('/home/jiangpeng/jfred-encrypted-restore.log').read_text()
assert 'jfred-cloud-restore-verification : restored archive SHA256 matches original' in log
access=(root/'jfred-service-access.txt').read_text()
password=re.search(r'Duplicati:.*?Password: ([^\n]+)',access,re.S)[1]
b='http://127.0.0.1:18083/api/v1'
def api(path,body=None,token=None,method=None):
    headers={'Content-Type':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    req=urllib.request.Request(b+path,data=json.dumps(body).encode() if body is not None else None,headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=30) as response:
        data=response.read();return json.loads(data) if data else {}
t=api('/auth/login',{'Password':password,'RememberMe':False})['AccessToken']
assert api('/task/'+str(state['cloud_restore_task_id']),token=t)['Status']=='Completed'
backup=api('/backup/'+state['cloud_backup_id'],token=t)['Backup']
backup['Name']='JFred - Aliyun Drive'
backup['TargetURL']='webdav://openlist:5244/dav/?'+urllib.parse.urlencode({'auth-username':state['webdav_username'],'auth-password':state['webdav_password']})
for setting in backup['Settings']:
    if setting['Name']=='passphrase':setting['Value']=state['encryption_passphrase']
next_run=(datetime.datetime.now(ZoneInfo('Asia/Shanghai'))+datetime.timedelta(days=1)).replace(hour=3,minute=30,second=0,microsecond=0)
schedule={'Time':next_run.astimezone(datetime.timezone.utc).isoformat(),'Repeat':'1D','Rule':'','AllowedDays':[],'Tags':[]}
api('/backup/'+state['cloud_backup_id'],{'Backup':backup,'Schedule':schedule},t,method='PUT')
actual=api('/backup/'+state['cloud_backup_id'],token=t)
assert actual['Schedule']['Repeat']=='1D'
state['cloud_enabled']=True;state['cloud_schedule']='03:30 Asia/Shanghai';state['cloud_retention']='30 days';f.write_text(json.dumps(state,indent=2));f.chmod(0o600)
p=root/'jfred-service-access.txt'
s=p.read_text();s=s.replace('Cloud backup: Aliyun Drive via OpenList WebDAV (authorization pending).','Cloud backup: Aliyun Drive via restricted OpenList WebDAV; verified and scheduled daily at 03:30 Asia/Shanghai.').replace('Cloud drive: authorize Aliyun Drive yourself; no refresh token configured.','Cloud drive connected at /aliyun. Backup folder: /aliyun/jfred-backups.').replace('http://openlist:5244/dav/aliyun/jfred-backups','http://openlist:5244/dav/')
p.write_text(s);p.chmod(0o600)
print('Cloud backup schedule active: daily 03:30 Asia/Shanghai; encrypted; 30-day retention.')
