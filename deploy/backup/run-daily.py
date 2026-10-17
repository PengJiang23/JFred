#!/usr/bin/env python3
"""One scheduled cycle: consistent exports, then encrypted local and cloud copies."""
import fcntl,json,pathlib,re,subprocess,time,urllib.request
cycle=open("/run/lock/jfred-backup-cycle.lock","w")
try:fcntl.flock(cycle,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:
 print("Daily backup cycle already running; no duplicate job started.");raise SystemExit(0)
ROOT=pathlib.Path('/home/jiangpeng/services');state=json.loads((ROOT/'jfred-backup-recovery.json').read_text());access=(ROOT/'jfred-service-access.txt').read_text();password=re.search(r'Duplicati:.*?Password: ([^\n]+)',access,re.S)[1]
base='http://127.0.0.1:18083/api/v1'
def api(path,body=None,token=None):
 h={'Content-Type':'application/json'}
 if token:h['Authorization']='Bearer '+token
 q=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=h)
 with urllib.request.urlopen(q,timeout=30) as f:return json.load(f)
def token():return api('/auth/login',{'Password':password,'RememberMe':False})['AccessToken']
subprocess.run(['/usr/bin/python3','/opt/jfred-backup/export-server.py'],check=True)
tasks={}
for label in ['local','cloud']:
 t=token();i=api('/backup/'+str(state[label+'_backup_id'])+'/run',{},t)['ID'];deadline=time.time()+5*3600;tasks[label]=i
 while time.time()<deadline:
  status=api('/task/'+str(i),token=token())['Status']
  if status=='Completed':break
  if status not in ['Running','Waiting','Pending','Queued','Created']:raise RuntimeError(label+' encrypted backup status '+status)
  time.sleep(10)
 else:raise RuntimeError(label+' encrypted backup exceeded 5 hours')
 print(label+' encrypted daily backup completed',flush=True)
p=pathlib.Path('/opt/backups/jfred/last-cycle.json');p.write_text(json.dumps({'completed_at':time.time(),'tasks':tasks}));p.chmod(0o600)
