#!/usr/bin/env python3
"""Small local security supplement to Beszel; no remote shell, blocking or killing."""
import base64,collections,datetime,hashlib,hmac,ipaddress,json,os,pathlib,re,subprocess,sys,time,urllib.request
ROOT=pathlib.Path('/var/lib/jfred-security');CONFIG=pathlib.Path('/etc/jfred-monitor')
def command(args):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=25,text=True)
 if p.returncode:raise RuntimeError('Collector failed: '+args[0])
 return p.stdout

def signed_send(text,config=None):
 c=config or json.loads((CONFIG/'feishu.json').read_text());stamp=str(int(time.time()))
 sign=base64.b64encode(hmac.new((stamp+'\n'+c['secret']).encode(),b'',hashlib.sha256).digest()).decode()
 body={'timestamp':stamp,'sign':sign,'msg_type':'text','content':{'text':text}}
 q=urllib.request.Request(c['webhook'],data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(q,timeout=15) as r:result=json.load(r)
 if result.get('code',result.get('StatusCode',0))!=0:raise RuntimeError('Feishu rejected notification')

class Alerts:
 def __init__(self,state,now):self.state=state;self.now=now;self.messages=[]
 def check(self,key,bad,description,delay=0):
  a=self.state.setdefault(key,{})
  if bad:
   a.setdefault('since',self.now)
   if self.now-a['since']>=delay and (not a.get('active') or self.now-a.get('sent',0)>=21600):
    self.messages.append('异常：'+description);a.update(active=True,sent=self.now)
  else:
   if a.get('active'):self.messages.append('恢复：'+description)
   self.state.pop(key,None)
 def event(self,key,fingerprint,description):
  a=self.state.setdefault(key,{})
  if fingerprint!=a.get('fingerprint'):
   self.messages.append('安全事件：'+description);a.update(fingerprint=fingerprint,sent=self.now)

def check(state,now):
 a=Alerts(state.setdefault('alerts',{}),now);since=max(state.get('journal_time',now),now-600)
 # Do not notify on every normal sudo or every failed login. Aggregate short bursts.
 try:
  lines=command(['journalctl','--since=@'+str(since),'--until=@'+str(now),'-o','json','--no-pager','SYSLOG_IDENTIFIER=sshd','+','SYSLOG_IDENTIFIER=sudo','+','_TRANSPORT=kernel']).splitlines()
  events=state.setdefault('auth_events',[]);oom=[]
  for line in lines:
   v=json.loads(line);m=v.get('MESSAGE','');stamp=int(v.get('__REALTIME_TIMESTAMP',int(now*1e6)))/1e6
   if stamp<=since:continue
   if re.search(r'Failed password|Invalid user|authentication failure',m,re.I):events.append([stamp,v.get('SYSLOG_IDENTIFIER','unknown')])
   if re.search(r'Accepted .* for root from ',m):a.event('root-login',hashlib.sha256(m.encode()).hexdigest(),'检测到 root SSH 登录；请核对是否本人操作。')
   if re.search(r'Out of memory: Killed process|oom-kill:',m):oom.append(stamp)
  events[:]=[e for e in events if e[0]>now-600]
  ssh=sum(e[1]=='sshd' for e in events);sudo=sum(e[1]=='sudo' for e in events)
  a.check('ssh-failures',ssh>=20,'SSH 认证失败在 10 分钟内达到 20 次（当前 '+str(ssh)+' 次）')
  a.check('sudo-failures',sudo>=5,'sudo 认证失败在 10 分钟内达到 5 次（当前 '+str(sudo)+' 次）')
  if oom:a.event('oom',str(max(oom)),'内核触发 OOM，进程因内存不足被终止。')
  state['journal_time']=now;a.check('journal-collector',False,'安全日志采集不可用',300)
 except Exception:a.check('journal-collector',True,'安全日志采集不可用',300)
 # auditd records writes even if a sensitive file is subsequently reverted.
 try:
  p=pathlib.Path('/var/log/audit/audit.log');st=p.stat();old=state.get('audit',{})
  offset=old.get('offset',st.st_size) if old.get('inode')==st.st_ino else 0
  # First invocation establishes a baseline; do not report historical maintenance.
  if not old:offset=st.st_size
  if offset>st.st_size:offset=0
  with p.open() as f:f.seek(offset);data=f.read(2_000_000);position=f.tell()
  state['audit']={'inode':st.st_ino,'offset':position}
  changed=collections.Counter(re.findall(r'type=SYSCALL[^\n]*\bsuccess=yes[^\n]*\bkey="?(jfred_[a-z_]+)',data))
  labels={'jfred_identity':'系统账号/权限组','jfred_privilege':'sudo 提权规则','jfred_ssh':'SSH 配置或登录公钥','jfred_persistence':'系统自启动或定时任务'}
  if changed:a.event('audit-write',str(st.st_ino)+':'+str(position),'敏感配置发生写入：'+'、'.join(labels.get(k,k) for k in changed)+'。这可能是管理操作，请核对；不等同于已确认入侵。')
  a.check('audit-collector',False,'auditd 安全审计不可用',300)
 except Exception:a.check('audit-collector',True,'auditd 安全审计不可用',300)
 uid0=[l.split(':')[0] for l in pathlib.Path('/etc/passwd').read_text().splitlines() if l.split(':')[2]=='0']
 if 'uid0' in state and uid0!=state['uid0']:a.event('uid0',json.dumps(uid0),'UID 0 账号列表发生变化：'+', '.join(uid0))
 state['uid0']=uid0
 # Watch root processes executing writable temporary files or deleted executables.
 previous=state.get('processes',{});current={};suspect=[]
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   raw=(p/'stat').read_text();fields=raw[raw.rfind(')')+2:].split();ticks=int(fields[11])+int(fields[12]);identity=p.name+':'+fields[19]
   exe=os.readlink(p/'exe');uid=int(re.search(r'^Uid:\s+(\d+)',(p/'status').read_text(),re.M)[1]);old=previous.get(identity)
   cpu=(ticks-old['ticks'])/os.sysconf('SC_CLK_TCK')/max(now-state.get('process_time',now),1)*100 if old else 0
   current[identity]={'ticks':ticks};bad=uid==0 and (exe.startswith(('/tmp/','/var/tmp/','/dev/shm/')) or exe.endswith(' (deleted)')) and cpu>20
   if bad:suspect.append((identity,exe))
  except (OSError,ValueError,IndexError,TypeError):continue
 active={i for i,_ in suspect}
 for i,exe in suspect:a.check('process:'+i,True,'root 进程 PID '+i.split(':')[0]+' 持续从临时/已删除程序运行且占用 CPU：'+exe[:120],300)
 for k in list(a.state):
  if k.startswith('process:') and k[8:] not in active:a.check(k,False,'此前可疑临时程序进程已结束或不再持续占用 CPU')
 state['processes']=current;state['process_time']=now
 try:
  values=command(['nvidia-smi','--query-gpu=temperature.gpu','--format=csv,noheader,nounits']).splitlines()
  temperature=max(float(x.strip()) for x in values)
  a.check('gpu-temperature',temperature>=85,'GPU 温度持续达到 85°C（当前 '+str(int(temperature))+'°C）',300)
  a.check('gpu-collector',False,'NVIDIA 显卡状态无法读取',300)
 except Exception:a.check('gpu-collector',True,'NVIDIA 显卡状态无法读取',300)
 policy=json.loads((CONFIG/'policy.json').read_text())
 for unit in policy['units']:
  bad=subprocess.run(['systemctl','is-active','--quiet',unit]).returncode!=0
  a.check('unit:'+unit,bad,'关键服务 '+unit+' 不处于运行状态',180)
 try:
  rows=[json.loads(l) for l in command(['docker','ps','-a','--format','{{json .}}']).splitlines()]
  containers={x['Names']:x for x in rows}
  for name in policy['containers']:
   value=containers.get(name,{});bad=value.get('State')!='running' or '(unhealthy)' in value.get('Status','')
   a.check('container:'+name,bad,'关键容器 '+name+' 停止或健康检查失败',180)
  a.check('docker-collector',False,'Docker 容器状态无法采集',300)
 except Exception:a.check('docker-collector',True,'Docker 容器状态无法采集',300)
 exports=list(pathlib.Path('/opt/backups/jfred').glob('jfred-*.tar.gz'));age=now-max((x.stat().st_mtime for x in exports),default=0)
 a.check('backup-age',age>36*3600,'最近一次数据库导出已超过 36 小时',300)
 # Check both encrypted jobs, so a healthy local export cannot hide a broken cloud job.
 try:
  access=pathlib.Path('/home/jiangpeng/services/jfred-service-access.txt').read_text();password=re.search(r'Duplicati:.*?Password: ([^\n]+)',access,re.S)[1]
  base='http://127.0.0.1:18083/api/v1'
  def api(path,body=None,token=None):
   headers={'Content-Type':'application/json'}
   if token:headers['Authorization']='Bearer '+token
   q=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
   with urllib.request.urlopen(q,timeout=10) as v:return json.load(v)
  token=api('/auth/login',{'Password':password,'RememberMe':False})['AccessToken']
  for job in api('/backups',token=token):
   metadata=job['Backup'].get('Metadata',{});stamp=metadata.get('LastBackupFinished','')
   finished=datetime.datetime.strptime(stamp,'%Y%m%dT%H%M%SZ').replace(tzinfo=datetime.timezone.utc).timestamp() if stamp else 0
   name=job['Backup']['Name'];a.check('encrypted-backup:'+str(job['Backup']['ID']),now-finished>36*3600,'加密备份 '+name+' 已超过 36 小时未完成',300)
  a.check('duplicati-collector',False,'无法核对加密备份任务结果',300)
 except Exception:a.check('duplicati-collector',True,'无法核对加密备份任务结果',300)
 # Failed oneshot tasks can be inactive normally; only the failed state is exceptional.
 failed=command(['systemctl','show','jfred-backup.service','--property=Result','--value']).strip()
 a.check('backup-failed',failed not in ['','success'],'数据库一致性导出任务失败',180)
 return a.messages

def main():
 ROOT.mkdir(mode=0o700,parents=True,exist_ok=True);f=ROOT/'state.json';state=json.loads(f.read_text()) if f.exists() else {};now=time.time()
 if '--test' in sys.argv:
  signed_send('【联想服务器告警 · 安全监控演练】\n签名验证与通知链路正常。正式告警仅在持续故障、认证失败聚集、敏感配置写入或可疑 root 进程触发时发送；不会自动终止进程或封禁地址。');print('Signed security test delivered.');return
 messages=check(state,now)
 if messages:
  signed_send('【联想服务器告警】\n'+'\n'.join(messages[:12])+('\n其余 '+str(len(messages)-12)+' 项请登录监控面板查看。' if len(messages)>12 else '')+'\n监控：http://10.144.144.66:18086/')
  print('Security notification delivered:',len(messages),'items')
 temp=f.with_suffix('.tmp');temp.write_text(json.dumps(state));temp.chmod(0o600);temp.replace(f)
 print('Security checks complete; events:',len(messages))
if __name__=='__main__':main()
