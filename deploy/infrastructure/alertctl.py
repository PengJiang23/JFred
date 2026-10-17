#!/usr/bin/env python3
"""Root-only notification controls; monitoring remains enabled."""
import json,pathlib,sys,urllib.request
args=sys.argv[1:];action=args[0] if args else 'status'
if action=='test':
 path='/event';data={'source':'test','key':'operator-test','title':'联想服务器告警流程演练','detail':'这是测试卡片。请尝试接管、静默、暂停全部及恢复提醒；最后标记已处理。不会触发真实故障。','severity':'critical'}
elif action=='status':path='/status';data={}
elif action in ['pause','resume']:
 path='/control';data={'action':action,'minutes':int(args[1]) if len(args)>1 else 120}
else:raise SystemExit('Usage: jfred-alertctl [status | test | pause MINUTES | resume]')
token=pathlib.Path('/etc/jfred-monitor/ingest-token').read_text().strip()
q=urllib.request.Request('http://127.0.0.1:18088'+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+token})
with urllib.request.urlopen(q,timeout=10) as f:print(json.dumps(json.load(f),ensure_ascii=False))
