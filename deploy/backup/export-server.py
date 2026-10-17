#!/usr/bin/env python3
"""Consistent daily exports, app recovery bundles and content-addressed Docker images."""
import datetime,fcntl,gzip,hashlib,json,os,pathlib,re,shlex,shutil,sqlite3,subprocess,sys,tarfile,tempfile,time
os.umask(0o077)
ROOT=pathlib.Path('/opt/backups/jfred');ROOT.mkdir(parents=True,exist_ok=True)
lock=open('/run/lock/jfred-backup.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
STAMP=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d_%H%M%S_CST')
WORK=pathlib.Path(tempfile.mkdtemp(prefix='.daily-',dir=ROOT));OUT=WORK/'daily';OUT.mkdir()
MANIFEST={'created':STAMP,'timezone':'Asia/Shanghai','databases':[],'applications':[],'images':[],'excluded':[]}

def run(args,**kw):return subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kw).stdout
def log(s):print(s,flush=True)
def inspect():
 ids=run(['docker','ps','-aq']).decode().split()
 return json.loads(run(['docker','inspect',*ids])) if ids else []
CS=[c for c in inspect() if (c['Config'].get('Labels') or {}).get('io.jfred.backup.exclude')!='true' and not c['Name'].lstrip('/').startswith('jfred-restore-')]
def env(c):return dict(x.split('=',1) for x in c['Config'].get('Env',[]) if '=' in x)
def name(c):return c['Name'].lstrip('/')
def family(c):
 image=c['Config']['Image'].split('/')[-1].split(':')[0]
 return image if image in ['mysql','mariadb','postgres','mongo','redis'] else None

def output_stream(args,target):
 tmp=target.with_suffix(target.suffix+'.tmp')
 with tmp.open('wb') as f:
  p=subprocess.run(args,stdout=f,stderr=subprocess.PIPE)
 if p.returncode:
  tmp.unlink(missing_ok=True);raise RuntimeError('Backup command failed for '+target.name+'; exit '+str(p.returncode))
 tmp.replace(target)

def gzip_stream(args,target):
 tmp=target.with_suffix(target.suffix+'.tmp')
 with tempfile.TemporaryFile() as err, tmp.open('wb') as f:
  p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=err)
  with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0,compresslevel=3) as zipped:shutil.copyfileobj(p.stdout,zipped,1024*1024)
  if p.wait():tmp.unlink(missing_ok=True);raise RuntimeError('Export failed: '+target.name)
 tmp.replace(target)

# SQLite backup API, including files without a .db suffix, avoids copying live WAL data.
def add_snapshot(tar,path,arc,excluded):
 p=pathlib.Path(path)
 if not p.exists() and not p.is_symlink():return
 if any(p==x or x in p.parents for x in excluded):return
 if p.name.endswith(('-wal','-shm','-journal','.tmp')):return
 info=tar.gettarinfo(str(p),arcname=arc)
 if info is None:
  MANIFEST['excluded'].append({'path':str(p),'reason':'runtime socket / unsupported special file'});return
 if info.isdir():
  tar.addfile(info)
  for child in sorted(p.iterdir()):add_snapshot(tar,child,arc+'/'+child.name,excluded)
 elif info.isfile():
  try:
   with p.open('rb') as f:is_sqlite=f.read(16)==b'SQLite format 3\x00'
   if is_sqlite:
    with tempfile.TemporaryDirectory(dir=WORK) as d:
     dest=pathlib.Path(d)/'snapshot.db'
     with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True,timeout=30) as source,sqlite3.connect(dest) as target:
      source.backup(target);assert target.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
     info.size=dest.stat().st_size
     with dest.open('rb') as f:tar.addfile(info,f)
   else:
    with p.open('rb') as f:tar.addfile(info,f)
  except FileNotFoundError:
   # Only volatile runtime files may disappear; application data must not silently vanish.
   raise RuntimeError('Source changed while exporting '+str(p))
 else:tar.addfile(info)

def archive(label,paths,excluded=()):
 target=OUT/(label+'-'+STAMP+'.tar.gz');seen=set();excluded=[pathlib.Path(p) for p in excluded]
 with tarfile.open(target,'w:gz',compresslevel=3,dereference=False) as tar:
  for value in paths:
   p=pathlib.Path(value)
   if not p.exists() and not p.is_symlink():continue
   if any(p==old or old in p.parents for old in seen):continue
   add_snapshot(tar,p,str(p).lstrip('/'),excluded);seen.add(p)
 return target.name

try:
 # Databases: logical exports for running engines; a stopped MongoDB is copied cold.
 db_sources=[]
 for c in CS:
  kind=family(c)
  if not kind:continue
  n=name(c);running=c['State']['Running'];mounts=c['Mounts'];db_sources.extend(m['Source'] for m in mounts if m['Destination'] in ['/var/lib/mysql','/var/lib/postgresql/data','/data/db','/data/configdb','/data'])
  if kind in ['mysql','mariadb']:
   if not running:raise RuntimeError('SQL service stopped: '+n)
   tables_raw=run(['docker','exec',n,'sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N -B -e "SELECT JSON_ARRAYAGG(JSON_OBJECT(\'schema\',table_schema,\'table\',table_name,\'engine\',engine)) FROM information_schema.tables WHERE table_schema NOT IN (\'mysql\',\'sys\',\'information_schema\',\'performance_schema\')"']).decode().strip()
   tables=json.loads(tables_raw) if tables_raw not in ['', 'NULL', 'null'] else []
   nontransactional=any(t['engine'] not in ['InnoDB',None] for t in tables)
   args=['docker','exec',n,'sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysqldump -uroot --all-databases --routines --events --triggers --hex-blob --set-gtid-purged=OFF '+('--lock-all-tables' if nontransactional else '--single-transaction')]
   filename='database-mysql-all-'+STAMP+'.sql.gz';gzip_stream(args,OUT/filename)
   MANIFEST['databases'].append({'engine':kind,'container':n,'file':filename,'consistency':'global-lock' if nontransactional else 'single-transaction','tables':tables})
  elif kind=='postgres':
   if not running:raise RuntimeError('PostgreSQL service stopped: '+n)
   filename='database-postgresql-all-'+STAMP+'.sql.gz'
   gzip_stream(['docker','exec',n,'sh','-c','exec pg_dumpall -U "$POSTGRES_USER" --clean --if-exists'],OUT/filename)
   MANIFEST['databases'].append({'engine':kind,'container':n,'file':filename,'consistency':'per-database logical snapshot, includes roles'})
  elif kind=='mongo':
   if running:
    credentials=env(c);pw=credentials.get('MONGO_INITDB_ROOT_PASSWORD','');user=credentials.get('MONGO_INITDB_ROOT_USERNAME','root');config='/tmp/jfred-mongodump-config.yml'
    # Password goes through stdin into a root-only temporary file, never a process argument.
    run(['docker','exec','-i',n,'sh','-c','umask 077; cat > '+config],input=('password: '+json.dumps(pw)+'\n').encode())
    filename='database-mongodb-all-'+STAMP+'.archive.gz'
    try:output_stream(['docker','exec',n,'mongodump','--config='+config,'--username='+user,'--authenticationDatabase=admin','--archive','--gzip'],OUT/filename)
    finally:run(['docker','exec',n,'rm','-f',config])
   else:filename=archive('database-mongodb-offline-physical',[m['Source'] for m in mounts if m['Destination'] in ['/data/db','/data/configdb']])
   MANIFEST['databases'].append({'engine':kind,'container':n,'file':filename,'consistency':'logical dump' if running else 'cold physical snapshot; restore same MongoDB image first'})
  elif kind=='redis':
   if not running:raise RuntimeError('Redis service stopped: '+n)
   credentials=env(c);password=credentials.get('REDIS_PASSWORD') or credentials.get('PANEL_REDIS_ROOT_PASSWORD')
   args=c['Config'].get('Cmd') or []
   if '--requirepass' in args:password=args[args.index('--requirepass')+1]
   if not password:
    config=next((m['Source'] for m in mounts if m['Destination'].endswith('redis.conf')),None)
    if config:
     match=re.search(r'^\s*requirepass\s+(.*)',pathlib.Path(config).read_text(),re.M);password=shlex.split(match[1])[0] if match else ''
   cfg='/tmp/jfred-redis-auth'
   run(['docker','exec','-i',n,'sh','-c','umask 077; cat > '+cfg],input=(password or '').encode())
   filename='database-redis-all-'+STAMP+'.rdb'
   try:
    run(['docker','exec',n,'sh','-c','REDISCLI_AUTH="$(cat '+cfg+')" redis-cli --rdb /tmp/jfred-backup.rdb'])
    output_stream(['docker','exec',n,'cat','/tmp/jfred-backup.rdb'],OUT/filename)
    run(['docker','exec',n,'redis-check-rdb','/tmp/jfred-backup.rdb'])
   finally:run(['docker','exec',n,'rm','-f',cfg,'/tmp/jfred-backup.rdb'])
   MANIFEST['databases'].append({'engine':kind,'container':n,'file':filename,'consistency':'replication RDB snapshot; all logical databases'})
  log('Database exported: '+kind)
 # Compose recovery bundles include config and all bind/volume application data.
 projects={}
 for c in CS:
  if 'artalk' in name(c):continue
  labels=c['Config'].get('Labels') or {};project=labels.get('com.docker.compose.project') or name(c)
  group=projects.setdefault(project,[]);wd=labels.get('com.docker.compose.project.working_dir')
  if wd:group.append(wd)
  for mount in c['Mounts']:
   source=mount['Source']
   if source in ['/etc/localtime','/etc/timezone','/etc/machine-id'] or source.startswith('/opt/backups/'):continue
   group.append(source)
 for project,paths in projects.items():
  excludes=list(db_sources)
  for p in paths:
   for part in ['log','logs','cache','tmp']:
    if (pathlib.Path(p)/part).is_dir():excludes.append(str(pathlib.Path(p)/part))
  filename=archive('application-'+re.sub('[^a-zA-Z0-9_.-]','-',project),sorted(set(paths),key=lambda p:(len(p),p)),excludes)
  MANIFEST['applications'].append({'name':project,'file':filename,'paths':sorted(set(paths))})
 # Native applications, OS service configuration, deployment keys and 1Panel manager.
 native=['/etc/1panel','/opt/1panel/db','/opt/1panel/conf','/opt/1panel/cache/ssl','/opt/1panel/runtime','/opt/1panel/ai','/opt/1panel/geo','/opt/1panel/firewall','/opt/1panel/mcp','/opt/1panel/docker','/usr/local/bin/1panel-core','/usr/local/bin/1panel-agent','/usr/local/bin/1panel-kvm','/usr/local/bin/1pctl','/usr/local/bin/1panel','/usr/local/bin/1panel.tmp']
 MANIFEST['applications'].append({'name':'1panel-manager','file':archive('application-1panel-manager',native)})
 native=['/etc/v2raya','/usr/local/bin/v2raya','/usr/local/bin/v2raya_core','/usr/local/share/v2raya','/etc/easytier','/etc/jfred-monitor','/var/lib/private/jfred-alerts','/var/lib/jfred-security','/var/lib/beszel-agent','/usr/local/bin/beszel-agent','/opt/jfred-alerts/feishu-cards.py','/opt/jfred-alerts/requirements.txt','/opt/jfred-backup','/usr/local/sbin','/etc/systemd/system','/etc/audit','/etc/ssh','/etc/cron.d','/etc/crontab','/etc/fstab','/etc/docker','/etc/machine-id','/etc/passwd','/etc/group','/etc/shadow','/etc/gshadow','/etc/sudoers','/etc/sudoers.d','/root/.ssh','/home/jiangpeng/.ssh','/home/jiangpeng/services','/home/jiangpeng/actions-runner','/home/jiangpeng/jfred-lark-wheels']
 MANIFEST['applications'].append({'name':'host-and-native-services','file':archive('application-host-and-native-services',native,['/home/jiangpeng/services/umami-pre-migration','/home/jiangpeng/services/artalk','/home/jiangpeng/actions-runner/_diag','/home/jiangpeng/actions-runner/_work','/home/jiangpeng/actions-runner/_update','/home/jiangpeng/actions-runner/_temp'])})
 # Container metadata contains environment secrets; only encrypted destinations receive it.
 (OUT/('application-container-inventory-'+STAMP+'.json')).write_text(json.dumps(CS,indent=2))
 (OUT/('application-os-packages-'+STAMP+'.txt')).write_bytes(run(['dpkg-query','-W','-f=${binary:Package}\t${Version}\n']))
 image_dir=ROOT/'application-images';image_dir.mkdir(exist_ok=True)
 refs={}
 for c in CS:
  if 'artalk' in name(c):continue
  refs.setdefault(c['Image'],[]).append(c['Config']['Image'])
 for image_id,image_refs in refs.items():
  short=image_id.split(':')[-1][:16];label=re.sub('[^a-zA-Z0-9_.-]','-',image_refs[0].split('@')[0]);filename='application-image-'+label+'-'+short+'.docker.tar.gz';target=image_dir/filename
  if not target.exists():
   # Keep original repository tags/digests where possible for Compose recovery.
   gzip_stream(['docker','image','save',*sorted(set(image_refs))],target);log('Image saved: '+image_refs[0])
  MANIFEST['images'].append({'id':image_id,'references':image_refs,'file':'application-images/'+filename,'sha256':hashlib.file_digest(target.open('rb'),'sha256').hexdigest()})
 (OUT/('recovery-manifest-'+STAMP+'.json')).write_text(json.dumps(MANIFEST,ensure_ascii=False,indent=2))
 shutil.copy2('/opt/jfred-backup/RESTORE.md',OUT/'RESTORE-恢复说明.md')
 # Complete named exports remain private; Duplicati encrypts them before upload.
 with (OUT/'SHA256SUMS.txt').open('w') as hashes:
  for f in sorted(OUT.iterdir()):
   if not f.is_file() or f.name=='SHA256SUMS.txt':continue
   digest=hashlib.file_digest(f.open('rb'),'sha256').hexdigest();hashes.write(digest+'  '+f.name+'\n')
 latest=ROOT/'daily';previous=ROOT/'.daily-previous'
 if previous.exists():shutil.rmtree(previous)
 if latest.exists():latest.rename(previous)
 OUT.rename(latest)
 if previous.exists():shutil.rmtree(previous)
 # Retain seven days of image versions in local source; Duplicati retains 30-day historical versions.
 wanted={x['file'].split('/')[-1] for x in MANIFEST['images']}
 for f in image_dir.glob('application-image-*.docker.tar.gz'):
  if f.name not in wanted and time.time()-f.stat().st_mtime>7*86400:f.unlink()
 summary={'completed_at':time.time(),'stamp':STAMP,'database_count':len(MANIFEST['databases']),'application_count':len(MANIFEST['applications']),'image_count':len(MANIFEST['images'])}
 (ROOT/'last-export.json').write_text(json.dumps(summary));log('Daily server export complete: '+json.dumps(summary))
finally:shutil.rmtree(WORK,ignore_errors=True)
