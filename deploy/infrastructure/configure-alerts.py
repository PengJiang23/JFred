#!/usr/bin/env python3
import json,pathlib,re,urllib.request
p=re.search(r'Beszel:.*?Password: ([^\n]+)',pathlib.Path('/home/jiangpeng/services/jfred-service-access.txt').read_text(),re.S)[1];b='http://127.0.0.1:18086'
def api(path,body=None,t=None,method=None):
 h={'Content-Type':'application/json'}
 if t:h['Authorization']=t
 q=urllib.request.Request(b+path,data=json.dumps(body).encode() if body is not None else None,headers=h,method=method)
 with urllib.request.urlopen(q,timeout=20) as r:return json.load(r)
t=api('/api/collections/users/auth-with-password',{'identity':'admin@jfred.local','password':p})['token']
items=api('/api/collections/systems/records',t=t)['items'];assert len(items)==1,'Select a system explicitly if monitoring multiple servers';sid=items[0]['id']
api('/api/collections/systems/records/'+sid,{'name':'联想服务器'},t,'PATCH')
for name,value,minutes in [('CPU',90,10),('Memory',90,10),('Disk',90,15),('GPU',98,30),('Temperature',90,5),('Status',0,3)]:
 api('/api/beszel/user-alerts',{'name':name,'value':value,'min':minutes,'systems':[sid],'overwrite':True},t)
print('Six sustained resource and agent alerts configured.')
