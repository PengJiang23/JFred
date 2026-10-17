#!/usr/bin/env python3
"""Restore small files from each encrypted destination and compare with exported SHA256."""
import hashlib,json,pathlib,re,shutil,time,urllib.request,uuid
r=pathlib.Path('/home/jiangpeng/services');s=json.loads((r/'jfred-backup-recovery.json').read_text());p=re.search(r'Duplicati:.*?Password: ([^\n]+)',(r/'jfred-service-access.txt').read_text(),re.S)[1];b='http://127.0.0.1:18083/api/v1'
def api(path,body=None,t=None):
 h={'Content-Type':'application/json'}
 if t:h['Authorization']='Bearer '+t
 q=urllib.request.Request(b+path,data=json.dumps(body).encode() if body is not None else None,headers=h)
 with urllib.request.urlopen(q,timeout=30) as f:
  raw=f.read();return json.loads(raw) if raw else {}
def login():return api('/auth/login',{'Password':p,'RememberMe':False})['AccessToken']
root=pathlib.Path('/opt/backups/jfred/daily');chosen=[next(root.glob('database-mysql-all-*.sql.gz')),next(root.glob('recovery-manifest-*.json'))];proof=[]
for label in ['local','cloud']:
 key='restore-validation-'+uuid.uuid4().hex;host=pathlib.Path('/opt/stacks/jfred-community/duplicati')/key
 data={'paths':['/source/daily/'+f.name for f in chosen],'passphrase':s['encryption_passphrase'],'time':'now','restore_path':'/data/'+key,'overwrite':False,'permissions':False,'skip_metadata':True,'options':{'restore-with-local-blocks':'false','restore-from-local-blocks':'false'}}
 task=api('/backup/'+str(s[label+'_backup_id'])+'/restore',data,login())['ID'];deadline=time.time()+1200
 try:
  while time.time()<deadline:
   v=api('/task/'+str(task),t=login())
   if v['Status']=='Completed':break
   if v['Status'] not in ['Running','Waiting','Pending','Queued','Created']:raise RuntimeError(label+' encrypted restore: '+v['Status'])
   time.sleep(5)
  else:raise RuntimeError('Encrypted restore timed out')
  for f in chosen:
   matches=list(host.rglob(f.name));assert len(matches)==1
   assert hashlib.file_digest(matches[0].open('rb'),'sha256').hexdigest()==hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
  proof.append({'destination':label,'restore_task':task,'files_verified':[f.name for f in chosen],'sha256_matches':True})
 finally:
  if host.exists():shutil.rmtree(host)
path=pathlib.Path('/home/jiangpeng/jfred-encrypted-copy-proof.json');path.write_text(json.dumps(proof,indent=2));path.chmod(0o644)
print('PASS: local and cloud AES restores match original exported files.')
