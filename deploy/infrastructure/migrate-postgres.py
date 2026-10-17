#!/usr/bin/env python3
"""One-time Umami move to the PostgreSQL instance managed by 1Panel."""
import json,pathlib,subprocess,time,urllib.request,re,shutil,os
os.umask(0o077)
r=pathlib.Path('/opt/stacks/jfred-community');out=pathlib.Path('/opt/backups/jfred-migration');out.mkdir(mode=0o700,parents=True,exist_ok=True)
def run(args,data=None):return subprocess.check_output(args,input=data,stderr=subprocess.PIPE)
containers=json.loads(run(['docker','inspect','1Panel-postgresql-AOpK']))
pg=containers[0]['Name'].lstrip('/');env=dict(x.split('=',1) for x in containers[0]['Config']['Env']);admin=env['POSTGRES_USER'];assert '1panel-network' in containers[0]['NetworkSettings']['Networks']
appenv=dict(x.split('=',1) for x in (r/'.env').read_text().splitlines() if '=' in x)
def sql(container,user,db,text):return run(['docker','exec','-i',container,'psql','-X','-v','ON_ERROR_STOP=1','-At','-U',user,'-d',db],text.encode()).decode()
def counts(container,user):
 tables=sql(container,user,'umami',"select tablename from pg_tables where schemaname='public' order by tablename;").splitlines()
 return {t:int(sql(container,user,'umami','SELECT count(*) FROM public."'+t.replace('"','""')+'";').strip()) for t in tables}
backup=r/'compose.before-shared-postgres.yaml';shutil.copy2(r/'compose.yaml',backup)
run(['/usr/local/sbin/backup-jfred'])
run(['docker','stop','jfred-community-umami-1'])
try:
 original=counts('jfred-community-db-1','umami')
 dump=run(['docker','exec','jfred-community-db-1','pg_dump','-U','umami','-d','umami','-Fc']);(out/'umami-before-migration.pgdump').write_bytes(dump)
 existing=sql(pg,admin,'postgres',"SELECT datname FROM pg_database WHERE datname='umami';").strip();assert not existing,'Target umami database already exists; do not overwrite it'
 password=appenv['POSTGRES_PASSWORD'].replace("'","''")
 sql(pg,admin,'postgres',"CREATE ROLE umami LOGIN PASSWORD '"+password+"';\nCREATE DATABASE umami OWNER umami;")
 run(['docker','exec','-i',pg,'pg_restore','-U',admin,'-d','umami','--no-owner','--role=umami','--exit-on-error'],dump)
 assert original==counts(pg,admin),'Restored database table counts differ'
 (out/'verification.json').write_text(json.dumps({'tables':original,'matched':True,'postgres_container':pg},indent=2))
 s=(r/'compose.yaml').read_text();a=s.index('  db:\n');b=s.index('  umami:\n',a);s=s[:a]+s[b:]
 s=s.replace('    depends_on:\n      db: { condition: service_healthy }\n','    networks: [default, database]\n')
 s=s.replace('@db:5432/umami','@${POSTGRES_CONTAINER:?Required}:5432/umami')
 s+='\nnetworks:\n  database:\n    external: true\n    name: 1panel-network\n';(r/'compose.yaml').write_text(s)
 with (r/'.env').open('a') as f:f.write('\nPOSTGRES_CONTAINER='+pg+'\n')
 subprocess.run(['docker','compose','-f',str(r/'compose.yaml'),'-f',str(r/'admin-access.yaml'),'up','-d','--no-deps','umami'],cwd=r,check=True,stdout=subprocess.DEVNULL)
 access=pathlib.Path('/home/jiangpeng/services/jfred-service-access.txt').read_text();p=re.search(r'Umami:.*?Password: ([^\n]+)',access,re.S)[1]
 for n in range(60):
  try:
   req=urllib.request.Request('http://127.0.0.1:18082/api/auth/login',data=json.dumps({'username':'admin','password':p}).encode(),headers={'Content-Type':'application/json'})
   with urllib.request.urlopen(req,timeout=3) as v:assert json.load(v).get('token')
   break
  except Exception:
   if n==59:raise RuntimeError('Umami did not recover after database migration')
   time.sleep(2)
 run(['docker','stop','jfred-community-db-1']);run(['docker','rm','jfred-community-db-1'])
 print('Shared PostgreSQL migration verified; all table counts match; Umami login passed; old container removed, old data retained.')
except Exception:
 shutil.copy2(backup,r/'compose.yaml')
 subprocess.run(['docker','start','jfred-community-db-1'],stdout=subprocess.DEVNULL)
 subprocess.run(['docker','compose','-f',str(r/'compose.yaml'),'-f',str(r/'admin-access.yaml'),'up','-d','umami'],cwd=r,stdout=subprocess.DEVNULL)
 print('Migration stopped; restored original database connection. Inspect root-only migration diagnostics.')
 raise
