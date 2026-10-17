#!/usr/bin/env python3
"""Private Feishu incident cards: outbound WS callbacks, loopback ingest, SQLite journal."""
import datetime, hashlib, hmac, http.server, json, logging, os, pathlib, queue, re, sqlite3, threading, time, urllib.request, uuid
import lark_oapi as lark
from lark_oapi.event.callback.model.p2_card_action_trigger import P2CardActionTriggerResponse

BASE=pathlib.Path(os.environ.get('STATE_DIRECTORY','/var/lib/jfred-alerts'))
CREDS=pathlib.Path(os.environ.get('CREDENTIALS_DIRECTORY','/etc/jfred-monitor'))
CONFIG=json.loads((CREDS/'app.json').read_text())
INGEST=(CREDS/'ingest-token').read_text().strip()
BESZEL=json.loads((CREDS/'beszel.json').read_text())
LOCK=threading.RLock(); JOBS=queue.Queue(); TOKEN={}; API_TOKEN={}
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
log=logging.getLogger('jfred-cards')
BASE.mkdir(parents=True,exist_ok=True)
DB=sqlite3.connect(BASE/'incidents.db',check_same_thread=False)
DB.row_factory=sqlite3.Row
DB.executescript('''PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS incidents(id TEXT PRIMARY KEY, source TEXT, alert_key TEXT, title TEXT, detail TEXT, severity TEXT, active INTEGER, status TEXT, actor TEXT DEFAULT '', created REAL, updated REAL, mute REAL DEFAULT 0, message_id TEXT DEFAULT '', dirty INTEGER DEFAULT 1, sent REAL DEFAULT 0, reminder INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS messages(message_id TEXT PRIMARY KEY,incident TEXT);
CREATE TABLE IF NOT EXISTS actions(event_id TEXT PRIMARY KEY, incident TEXT, actor TEXT, action TEXT, at REAL);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
CREATE INDEX IF NOT EXISTS incident_key ON incidents(source,alert_key,active);
''');
if 'closed_sent' not in [r[1] for r in DB.execute('PRAGMA table_info(incidents)')]:DB.execute('ALTER TABLE incidents ADD COLUMN closed_sent INTEGER DEFAULT 0')
DB.commit()

def nowstr(stamp):
 return datetime.datetime.fromtimestamp(stamp,datetime.timezone(datetime.timedelta(hours=8))).strftime('%m-%d %H:%M')
def setting(key,default='0'):
 row=DB.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone();return row[0] if row else default
def put(key,value):
 DB.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',(key,str(value)));DB.commit()
def get(i):return DB.execute('SELECT * FROM incidents WHERE id=?',(i,)).fetchone()
def paused(row):return max(float(setting('pause')),row['mute'])>time.time()
def card(row,mention=False):
 owner='<at id='+row['actor']+'></at>' if row['actor'] else '尚未接管'
 status={'open':'待接管','claimed':'已接管','handled':'人工已处理，等待监测恢复','resolved':'已解决','recovered':'监测已恢复'}[row['status']]
 if paused(row):status+=' · 通知已暂停至 '+nowstr(max(float(setting('pause')),row['mute']))
 color='green' if not row['active'] else ('red' if row['severity']=='critical' else 'orange')
 lines=['**服务器**：联想 · 10.144.144.66','**状态**：'+status,'**接管人**：'+owner,'**首次发现**：'+nowstr(row['created']),'**最近更新**：'+nowstr(row['updated']),row['detail'][:1800]]
 if mention:lines.insert(0,'<at id=all></at> 需要核对此项异常')
 elements=[{'tag':'markdown','content':'\n'.join(lines)}]
 def button(label,action,kind='default'):
  return {'tag':'button','text':{'tag':'plain_text','content':label},'type':kind,'value':{'incident':row['id'],'action':action}}
 if row['active']:
  elements.append({'tag':'action','actions':[button('我来接管','claim','primary'),button('标记已处理','resolve'),button('静默30分钟','mute30'),button('静默2小时','mute120')]})
 elements.append({'tag':'action','actions':[button('暂停全部2小时','pause120'),button('恢复全部提醒','resume'),{'tag':'button','text':{'tag':'plain_text','content':'打开监控'},'url':'http://10.144.144.66:18086/'}]})
 elements.append({'tag':'note','elements':[{'tag':'plain_text','content':'静默仅暂停通知，继续采集；指标恢复后自动更新。仅重要首次异常及未接管升级提醒 @全体。编号 '+row['id'][:8]}]})
 return {'config':{'wide_screen_mode':True,'update_multi':True},'header':{'template':color,'title':{'tag':'plain_text','content':('演练 · ' if row['source']=='test' else '')+row['title']}},'elements':elements}

def request(url,body=None,token=None,method=None):
 headers={'Content-Type':'application/json'}
 if token:headers['Authorization']='Bearer '+token
 q=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,headers=headers,method=method)
 with urllib.request.urlopen(q,timeout=12) as f:return json.load(f)
def appapi(path,body,method='POST'):
 if TOKEN.get('until',0)<time.time():
  r=request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',{'app_id':CONFIG['app_id'],'app_secret':CONFIG['app_secret']})
  if r.get('code')!=0:raise RuntimeError('App token rejected code '+str(r.get('code')))
  TOKEN.update(value=r['tenant_access_token'],until=time.time()+r['expire']-120)
 r=request('https://open.feishu.cn/open-apis/'+path,body,TOKEN['value'],method)
 if r.get('code')!=0:raise RuntimeError('Feishu API code '+str(r.get('code')))
 return r

def ingest(source,key,title,detail,severity='warning',active=True):
 with LOCK:
  row=DB.execute('SELECT * FROM incidents WHERE source=? AND alert_key=? AND active=1 ORDER BY created DESC LIMIT 1',(source,key)).fetchone();now=time.time()
  if row:
   status=row['status'] if active else 'recovered'
   # Polling an unchanged metric must not update cards every 30 seconds.
   if row['active']==int(active) and row['detail']==detail and row['status']==status:return row['id']
   DB.execute('UPDATE incidents SET detail=?,active=?,status=?,updated=?,dirty=1 WHERE id=?',(detail,int(active),status,now,row['id']));i=row['id']
  elif active:
   i=uuid.uuid4().hex
   DB.execute('INSERT INTO incidents(id,source,alert_key,title,detail,severity,active,status,created,updated) VALUES(?,?,?,?,?,?,1,\'open\',?,?)',(i,source,key,title,detail,severity,now,now))
  else:return None
  DB.commit();return i

def action(event):
 e=event.event;ctx=e.context;actor=e.operator.open_id;value=e.action.value or {};i=value.get('incident');act=value.get('action')
 # Trust only callbacks authenticated by the SDK from our own group/message.
 with LOCK:
  row=get(i)
  if not row or ctx.open_chat_id!=CONFIG['chat_id'] or not DB.execute('SELECT 1 FROM messages WHERE message_id=? AND incident=?',(ctx.open_message_id,i)).fetchone() or not re.fullmatch(r'ou_[A-Za-z0-9]+',actor or ''):return P2CardActionTriggerResponse({'toast':{'type':'error','content':'不属于当前告警群或卡片'}})
  eid=getattr(event.header,'event_id',None) or hashlib.sha256((str(e.token)+act+actor).encode()).hexdigest()
  if DB.execute('SELECT 1 FROM actions WHERE event_id=?',(eid,)).fetchone():return P2CardActionTriggerResponse({'toast':{'type':'info','content':'操作已记录'}})
  if act not in ['claim','resolve','mute30','mute120','pause120','resume']:return P2CardActionTriggerResponse({'toast':{'type':'error','content':'不支持的操作'}})
  now=time.time();notice='操作已记录'
  if act=='claim' and row['active']:
   if row['actor'] and row['actor']!=actor:notice='已有接管人，保留原接管记录'
   else:DB.execute('UPDATE incidents SET actor=?,status=\'claimed\' WHERE id=?',(actor,i));notice='已记录你为接管人'
  elif act=='resolve' and row['active']:
   DB.execute('UPDATE incidents SET actor=?,status=?,active=? WHERE id=?',(row['actor'] or actor,'resolved' if row['source'] in ['test','security-event'] else 'handled',0 if row['source'] in ['test','security-event'] else 1,i));notice='演练已解决' if row['source']=='test' else '已记录处理，指标恢复后自动关闭'
  elif act.startswith('mute'):
   DB.execute('UPDATE incidents SET mute=? WHERE id=?',(now+int(act[4:])*60,i));notice='此项通知已静默'
  elif act=='pause120':
   put('pause',now+7200);DB.execute('UPDATE incidents SET dirty=1 WHERE active=1');notice='所有告警通知暂停2小时，监测继续'
  elif act=='resume':
   put('pause',0);DB.execute('UPDATE incidents SET mute=0,dirty=1 WHERE active=1');notice='全部提醒已恢复'
  DB.execute('INSERT INTO actions VALUES(?,?,?,?,?)',(eid,i,actor,act,now))
  DB.execute('UPDATE incidents SET updated=?,dirty=1 WHERE id=?',(now,i));DB.commit()
  # Fast response; API updates happen in a separate worker, never block WS callbacks.
  return P2CardActionTriggerResponse({'toast':{'type':'success','content':notice},'card':{'type':'raw','data':card(get(i))}})

def deliver():
 with LOCK:
  rows=DB.execute('SELECT * FROM incidents WHERE dirty=1 OR (active=1 AND status=\'open\')').fetchall()
 for row in rows:
  with LOCK:
   row=get(row['id']);now=time.time();quiet=paused(row);new=not row['message_id']
   reminder=row['active'] and row['status']=='open' and row['sent'] and now-row['sent']>=(900 if not row['reminder'] else 21600)
   if not row['dirty'] and not reminder:continue
   if quiet and (new or reminder):continue
   # A never-notified fault that recovered while muted should not generate a late message.
   if new and not row['active']:DB.execute('UPDATE incidents SET dirty=0 WHERE id=?',(row['id'],));DB.commit();continue
   version=row['updated'];payload=card(row,mention=row['active'] and not quiet and (row['severity']=='critical' and new or reminder))
  try:
   closing=not row['active'] and not row['closed_sent'] and not quiet
   if new or reminder or closing:
    r=appapi('im/v1/messages?receive_id_type=chat_id',{'receive_id':CONFIG['chat_id'],'msg_type':'interactive','content':json.dumps(payload),'uuid':hashlib.sha256((row['id']+('first' if new else ('closed' if closing else str(row['reminder']+1)))).encode()).hexdigest()[:32]})
    message_id=r['data']['message_id']
    with LOCK:DB.execute('INSERT OR IGNORE INTO messages VALUES(?,?)',(message_id,row['id']));DB.commit()
    # Reminders point at current incident; update the original too, preserving its buttons.
    if reminder or closing:appapi('im/v1/messages/'+row['message_id'],{'content':json.dumps(payload)},'PATCH')
   else:
    appapi('im/v1/messages/'+row['message_id'],{'content':json.dumps(payload)},'PATCH');message_id=row['message_id']
   with LOCK:
    # Retain the first message for future updates; registered reminder cards can also receive callbacks.
    DB.execute('UPDATE incidents SET message_id=?,dirty=CASE WHEN updated=? THEN 0 ELSE 1 END,sent=?,reminder=?,closed_sent=? WHERE id=?',(row['message_id'] or message_id,version,now,row['reminder']+(1 if reminder else 0),1 if not row['active'] else row['closed_sent'],row['id']));DB.commit();put('delivery_failure_since',0)
  except Exception as exc:
   with LOCK:
    if not float(setting('delivery_failure_since')):put('delivery_failure_since',time.time())
   log.warning('Card delivery failed: %s',type(exc).__name__+': '+str(exc));time.sleep(5)

def poll_beszel():
 base='http://127.0.0.1:18086'
 if API_TOKEN.get('until',0)<time.time():
  r=request(base+'/api/collections/users/auth-with-password',{'identity':BESZEL['username'],'password':BESZEL['password']});API_TOKEN.update(value=r['token'],until=time.time()+3600)
 q=urllib.request.Request(base+'/api/collections/alerts/records?perPage=100',headers={'Authorization':API_TOKEN['value']})
 with urllib.request.urlopen(q,timeout=10) as f:rows=json.load(f)['items']
 labels={'CPU':'CPU持续高负载','Memory':'内存持续高占用','Disk':'磁盘空间不足','GPU':'显卡持续高占用','Temperature':'系统温度过高','Status':'主机监控连接中断'}
 for r in rows:
  name=r['name'];detail=('监控连接中断持续 '+str(r.get('min'))+' 分钟' if name=='Status' else '阈值 '+str(r.get('value'))+('°C' if name=='Temperature' else '%')+'，持续 '+str(r.get('min'))+' 分钟')
  ingest('beszel',r['id'],labels.get(name,name),detail,'critical' if name in ['Status','Disk','Temperature'] else 'warning',r.get('triggered',False))
 with LOCK:put('last_poll',time.time())

class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  if not hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+INGEST):self.send_error(403);return
  try:
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<=16384:raise ValueError()
   data=json.loads(self.rfile.read(size))
   if self.path=='/event':
    source=data['source'];assert source in ['security','security-event','test'];i=ingest(source,str(data['key'])[:180],str(data['title'])[:120],str(data['detail'])[:2200],data.get('severity','warning'),data.get('active',True));result={'ok':True,'id':i}
   elif self.path=='/control':
    with LOCK:
     if data.get('action')=='pause':put('pause',time.time()+min(max(int(data.get('minutes',120)),1),1440)*60);DB.execute('UPDATE incidents SET dirty=1 WHERE active=1');DB.commit()
     elif data.get('action')=='resume':put('pause',0);DB.execute('UPDATE incidents SET mute=0,dirty=1 WHERE active=1');DB.commit()
     else:raise ValueError()
     result={'ok':True,'paused_until':float(setting('pause'))}
   elif self.path=='/status':
    with LOCK:result={'ok':True,'paused_until':float(setting('pause')),'delivery_failure_since':float(setting('delivery_failure_since')),'last_poll':float(setting('last_poll')),'active':DB.execute('SELECT count(*) FROM incidents WHERE active=1').fetchone()[0]}
   else:self.send_error(404);return
   body=json.dumps(result).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(body)
  except Exception:self.send_error(400)

def worker():
 last=0
 while True:
  try:
   with LOCK:
    now=time.time()
    if 0<float(setting('pause'))<=now:put('pause',0);DB.execute('UPDATE incidents SET dirty=1 WHERE active=1')
    DB.execute('UPDATE incidents SET mute=0,dirty=1 WHERE mute>0 AND mute<=?',(now,));DB.commit()
   if time.time()-last>=30:
    try:poll_beszel();last=time.time()
    except Exception as exc:API_TOKEN.clear();log.warning('Beszel polling unavailable: %s',type(exc).__name__);last=time.time()
   deliver()
  except Exception:log.exception('Incident worker failed')
  time.sleep(2)

def main():
 threading.Thread(target=http.server.ThreadingHTTPServer(('127.0.0.1',18088),Handler).serve_forever,daemon=True).start()
 threading.Thread(target=worker,daemon=True).start()
 handler=lark.EventDispatcherHandler.builder('','').register_p2_card_action_trigger(action).build()
 # WARNING avoids logging the authenticated WS URL, which contains credentials.
 lark.ws.Client(CONFIG['app_id'],CONFIG['app_secret'],event_handler=handler,log_level=lark.LogLevel.WARNING).start()
if __name__=='__main__':main()
