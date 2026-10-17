#!/usr/bin/env python3
"""Prepare encrypted Duplicati jobs. Cloud scheduling waits for drive authorization."""
import pathlib,sys
if pathlib.Path('/opt/jfred-backup/run-daily.py').exists():
 print('Complete daily server backup is configured; manage it through jfred-backup.timer. Legacy schedules remain disabled.')
 sys.exit(0)

import datetime, json, pathlib, re, secrets, time, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

access=pathlib.Path('/home/jiangpeng/services/jfred-service-access.txt').read_text()
def password(service): return re.search(service+r':.*?Password: ([^\n]+)',access,re.S)[1]
state_file=pathlib.Path('/home/jiangpeng/services/jfred-backup-recovery.json')
if state_file.exists(): state=json.loads(state_file.read_text())
else:
    state={'encryption_passphrase':secrets.token_urlsafe(36),'webdav_username':'jfred-backup','webdav_password':secrets.token_urlsafe(24)}
    state_file.write_text(json.dumps(state,indent=2)); state_file.chmod(0o600)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def api(base,path,body=None,token=None,raw=False):
    headers={'Content-Type':'application/json'}
    if token:headers['Authorization']=token if raw else 'Bearer '+token
    req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
    with opener.open(req,timeout=30) as response:
        data=response.read();return json.loads(data) if data else {}

a='http://127.0.0.1:18084/api'
login=api(a,'/auth/login',{'username':'admin','password':password('OpenList')})
assert login['code']==200,login.get('message')
at=login['data']['token']
users=api(a,'/admin/user/list?page=1&per_page=100',token=at,raw=True)
assert users['code']==200,users.get('message')
if not any(u['username']==state['webdav_username'] for u in users['data']['content']):
    created=api(a,'/admin/user/create',{'username':state['webdav_username'],'password':state['webdav_password'],
        'base_path':'/aliyun/jfred-backups','role':0,'disabled':False,'permission':920},at,True)
    assert created['code']==200,created.get('message')
print('Restricted backup WebDAV user prepared for /aliyun/jfred-backups.')

b='http://127.0.0.1:18083/api/v1'
t=api(b,'/auth/login',{'Password':password('Duplicati'),'RememberMe':False})['AccessToken']
existing=api(b,'/backups',token=t)
settings=[{'Name':k,'Value':v} for k,v in {'encryption-module':'aes','compression-module':'zip',
    'passphrase':state['encryption_passphrase'],'dblock-size':'50mb','keep-time':'30D',
    'backup-test-samples':'1'}.items()]
def job(name,target,schedule,state_key):
    if state.get(state_key) and any(str(x["Backup"]["ID"])==str(state[state_key]) for x in existing):return state[state_key]
    found=next((x for x in existing if x['Backup']['Name']==name),None)
    if found:return str(found['Backup']['ID'])
    value=api(b,'/backups',{'Backup':{'Name':name,'Description':'Consistent JFred database exports; AES encrypted.',
        'TargetURL':target,'Sources':['/source/'],'Settings':settings,'Filters':[],'Tags':[],'Metadata':{}},'Schedule':schedule},t)
    return str(value['ID'])
next_run=(datetime.datetime.now(ZoneInfo('Asia/Shanghai'))+datetime.timedelta(days=1)).replace(hour=3,minute=0,second=0,microsecond=0)
schedule={'Time':next_run.astimezone(datetime.timezone.utc).isoformat(),'Repeat':'1D','Rule':'','AllowedDays':[],'Tags':[]}
state['local_backup_id']=job('JFred - Local encrypted','file:///backups/jfred/',schedule,'local_backup_id')
query=urllib.parse.urlencode({'auth-username':state['webdav_username'],'auth-password':state['webdav_password']})
state['cloud_backup_id']=job('JFred - Aliyun Drive (authorize before scheduling)','webdav://openlist:5244/dav/?'+query,None,'cloud_backup_id')
state_file.write_text(json.dumps(state,indent=2));state_file.chmod(0o600)
print('Encrypted local backup configured; existing cloud schedule preserved.' if state.get('cloud_enabled') else 'Encrypted local daily backup configured; cloud backup prepared without a schedule.')
run=api(b,'/backup/'+state['local_backup_id']+'/run',{},t)
state['local_task_id']=run['ID'];state_file.write_text(json.dumps(state,indent=2))
print('Local encrypted backup started; task',run['ID'])
