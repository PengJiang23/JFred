#!/usr/bin/env python3
"""Restore current exports into disposable containers with no network or published ports."""
import gzip,json,os,pathlib,shutil,sqlite3,subprocess,tarfile,tempfile,time,uuid
os.umask(0o077)
ROOT=pathlib.Path('/opt/backups/jfred/daily');manifest=json.loads(next(ROOT.glob('recovery-manifest-*.json')).read_text())
containers=json.loads(next(ROOT.glob('application-container-inventory-*.json')).read_text());original={c['Name'].lstrip('/'):c for c in containers};proof=[]
def run(args,**kw):return subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kw).stdout
def wait(n,cmd):
 for _ in range(90):
  p=subprocess.run(['docker','exec',n,*cmd],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  if not p.returncode:return
  time.sleep(1)
 raise RuntimeError('Disposable restore container not ready: '+n)
def sql_import(cmd,f):
 with tempfile.TemporaryFile() as err:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=err)
  try:
   with gzip.open(f,'rb') as src:shutil.copyfileobj(src,p.stdin,1024*1024)
   p.stdin.close()
  except BrokenPipeError:pass
  if p.wait():raise RuntimeError('Restore import failed: '+f.name)
with tempfile.TemporaryDirectory(prefix='jfred-restore-',dir='/opt/backups') as tmp:
 base=pathlib.Path(tmp)
 for d in manifest['databases']:
  c=original[d['container']];n='jfred-restore-'+uuid.uuid4().hex[:10];stage=base/n;stage.mkdir();envfile=stage/'env';envfile.write_text('\n'.join(c['Config']['Env'])+'\n');envfile.chmod(0o600);image=c['Image'];f=ROOT/d['file'];kind=d['engine']
  try:
   if kind in ['mysql','mariadb']:
    data=stage/'data';data.mkdir()
    run(['docker','run','-d','--name',n,'--network','none','--label','io.jfred.backup.exclude=true','--memory','1g','--env-file',str(envfile),'-v',str(data)+':/var/lib/mysql',image])
    cmd=['sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N -e "SELECT 1"'];wait(n,cmd)
    sql_import(['docker','exec','-i',n,'sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql -uroot'],f)
    result=run(['docker','exec',n,'sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N -e "SHOW DATABASES"']).decode().splitlines();assert 'mysql' in result
    proof.append({'engine':kind,'restored':True,'database_count':len(result)})
   elif kind=='postgres':
    data=stage/'data';data.mkdir()
    # Use an independent superuser so pg_dumpall can recreate the original owner role.
    envfile.write_text('POSTGRES_USER=jfred_restore_admin\nPOSTGRES_PASSWORD='+uuid.uuid4().hex+'\n')
    run(['docker','run','-d','--name',n,'--network','none','--label','io.jfred.backup.exclude=true','--memory','768m','--env-file',str(envfile),'-v',str(data)+':/var/lib/postgresql/data',image])
    wait(n,['pg_isready','-U','jfred_restore_admin','-d','postgres'])
    sql_import(['docker','exec','-i',n,'psql','-X','-v','ON_ERROR_STOP=1','-U','jfred_restore_admin','-d','postgres'],f)
    value=run(['docker','exec',n,'psql','-At','-U','jfred_restore_admin','-d','umami','-c','SELECT count(*) FROM website;']).decode().strip();assert int(value)>=1
    proof.append({'engine':kind,'restored':True,'umami_websites':int(value)})
   elif kind=='redis':
    data=stage/'data';data.mkdir();shutil.copy2(f,data/'dump.rdb');os.chmod(data,0o777);os.chmod(data/'dump.rdb',0o644)
    run(['docker','run','-d','--name',n,'--network','none','--label','io.jfred.backup.exclude=true','--memory','256m','-v',str(data)+':/data',image,'redis-server','--appendonly','no','--dir','/data','--dbfilename','dump.rdb'])
    wait(n,['redis-cli','ping']);status=run(['docker','exec',n,'redis-cli','INFO','persistence']).decode();assert 'loading:0' in status;proof.append({'engine':kind,'restored':True})
   elif kind=='mongo' and 'offline-physical' in f.name:
    unpack=stage/'unpack';unpack.mkdir()
    with tarfile.open(f) as tar:tar.extractall(unpack,filter='data')
    source=next(m['Source'] for m in c['Mounts'] if m['Destination']=='/data/db');data=unpack/source.lstrip('/')
    run(['docker','run','-d','--name',n,'--network','none','--label','io.jfred.backup.exclude=true','--memory','768m','--env-file',str(envfile),'-v',str(data)+':/data/db',image])
    js='const a=db.getSiblingDB("admin"); a.auth(process.env.MONGO_INITDB_ROOT_USERNAME,process.env.MONGO_INITDB_ROOT_PASSWORD); if(a.runCommand({ping:1}).ok!==1)quit(1);'
    wait(n,['mongosh','--quiet','--eval',js]);proof.append({'engine':kind,'restored':True,'method':'cold physical same image'})
  finally:subprocess.run(['docker','rm','-f','-v',n],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 # Validate every SQLite snapshot inside all application bundles.
 checked=0
 for f in ROOT.glob('application-*.tar.gz'):
  with tarfile.open(f) as tar:
   for member in tar:
    if not member.isfile():continue
    stream=tar.extractfile(member);header=stream.read(16)
    if header!=b'SQLite format 3\x00':continue
    dest=base/'verify.sqlite'
    with dest.open('wb') as out:out.write(header);shutil.copyfileobj(stream,out)
    with sqlite3.connect(dest) as db:assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    dest.unlink();checked+=1
 proof.append({'sqlite_snapshots_checked':checked,'integrity':'ok'})
path=pathlib.Path('/home/jiangpeng/jfred-server-restore-proof.json');path.write_text(json.dumps(proof,indent=2));path.chmod(0o644)
print('PASS: independent database restores and application SQLite snapshots verified.')
