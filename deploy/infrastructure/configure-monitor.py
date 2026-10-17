#!/usr/bin/env python3
"""Configure Beszel through its authenticated local API; never print credentials."""
import json,pathlib,re,urllib.parse,urllib.request
r=pathlib.Path('/home/jiangpeng/services');text=(r/'jfred-service-access.txt').read_text();password=re.search(r'Beszel:.*?Password: ([^\n]+)',text,re.S)[1]
b='http://127.0.0.1:18086'
def api(path,body=None,t=None,method=None):
 h={'Content-Type':'application/json'}
 if t:h['Authorization']=t
 q=urllib.request.Request(b+path,data=json.dumps(body).encode() if body is not None else None,headers=h,method=method)
 with urllib.request.urlopen(q,timeout=30) as v:return json.load(v)
auth=api('/api/collections/users/auth-with-password',{'identity':'admin@jfred.local','password':password});t=auth['token'];uid=auth['record']['id']
key=api('/api/beszel/info',t=t)['key'];registration=api('/api/beszel/universal-token',t=t)
if not (registration.get('active') and registration.get('permanent')):registration=api('/api/beszel/universal-token?enable=1&permanent=1&token='+urllib.parse.quote(registration['token']),t=t)
token=registration['token']
p=r/'beszel-agent.env';p.write_text('KEY="'+key+'"\nTOKEN='+token+'\nHUB_URL=http://127.0.0.1:18086\nDISABLE_SSH=true\nGPU_COLLECTOR=nvidia-smi\nDOCKER_IMAGE_CHECK=false\nDATA_DIR=/var/lib/beszel-agent\n');p.chmod(0o600)
# Use the permanent registration token: the local agent registers and reconnects itself.
feishu=json.loads((r/'jfred-feishu.json').read_text());webhook=urllib.parse.urlparse(feishu['webhook']);url='lark://'+webhook.hostname+'/'+webhook.path.rsplit('/',1)[-1]+'?'+urllib.parse.urlencode({'secret':feishu['secret']})
settings=api('/api/collections/user_settings/records?perPage=10',t=t)['items'];existing=next((x for x in settings if x['user']==uid),None);value=(existing or {}).get('settings',{});value.update({'emails':[],'webhooks':[url]})
if existing:api('/api/collections/user_settings/records/'+existing['id'],{'settings':value},t,'PATCH')
else:api('/api/collections/user_settings/records',{'user':uid,'settings':value},t)
# Store no webhook in console output; test result is reduced to success/failure.
if '--test' in __import__('sys').argv:
 result=api('/api/beszel/test-notification',{'url':url},t)
 assert result.get('err') is False,'Feishu test notification failed; inspect privately'
print('Beszel account, signed Feishu notification, and local agent configuration prepared.')
