#!/usr/bin/env python3
"""Integration check using a disposable analytics website and an unpublished comment."""
import json, re, time, uuid, urllib.request, urllib.error
from pathlib import Path

access = Path('/home/jiangpeng/services/jfred-service-access.txt').read_text()
password = re.search(r'Umami:.*?Password: ([^\n]+)', access, re.S)[1]
base = 'http://127.0.0.1:18082/api'
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def api(url, body=None, token=None, method=None, extra=None):
    headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36'}
    if token: headers['Authorization'] = 'Bearer ' + token
    if extra: headers.update(extra)
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, headers=headers, method=method)
    with opener.open(req, timeout=30) as response:
        text=response.read()
        return json.loads(text) if text else {}

auth=api(base+'/auth/login',{'username':'admin','password':password})['token']
website=str(uuid.uuid4())
api(base+'/websites',{'id':website,'name':'JFred disposable verification','domain':'192.168.0.108'},auth)
try:
    data={'type':'event','payload':{'website':website,'hostname':'192.168.0.108','url':'/blog/__jfred_qa__','title':'Disposable verification','language':'zh-CN','screen':'1440x900'}}
    endpoint='http://192.168.0.108/blog/metrics/api/send'
    api(endpoint,data,extra={'x-umami-website-id':website,'x-umami-hostname':'192.168.0.108','X-Forwarded-For':'203.0.113.11'})
    params='?startAt=1791129600000&endAt='+str(int(time.time()*1000)+1000)
    first=api(base+'/websites/'+website+'/stats'+params,token=auth)
    api(endpoint,data,extra={'x-umami-website-id':website,'x-umami-hostname':'192.168.0.108','X-Forwarded-For':'203.0.113.22'})
    params='?startAt=1791129600000&endAt='+str(int(time.time()*1000)+1000)
    second=api(base+'/websites/'+website+'/stats'+params,token=auth)
    assert first['pageviews']==1 and first['visitors']==1,first
    assert second['pageviews']==2 and second['visitors']==1,second
    print('PASS: repeated views 1 -> 2; unique daily visitor stays 1; spoofed forwarded IP is ignored.')
finally:
    api(base+'/websites/'+website,token=auth,method='DELETE')

public='http://192.168.0.108/blog/metrics/api'
share=api(public+'/share/jfred-public')
headers={'x-umami-share-token':share['token'],'x-umami-share-context':'website'}
params='?startAt=1791129600000&endAt='+str(int(time.time()*1000))
api(public+'/websites/'+share['websiteId']+'/stats'+params,extra=headers)
try:
    api(public+'/websites/'+share['websiteId']+'/sessions'+params,extra=headers)
    raise AssertionError('Private session endpoint was publicly exposed')
except urllib.error.HTTPError as error:
    assert error.code==404,error.code
print('PASS: public aggregate API works; session details are blocked by the proxy.')

comment=api('http://192.168.0.108/blog/comments/api/v2/comments',{
    'name':'JFred verification','email':'verification@example.invalid','content':'Temporary unpublished integration test.',
    'page_key':'/blog/__jfred_qa__','page_title':'Disposable verification','site_name':'JFred'})
assert comment.get('is_pending') is True or comment.get('is_pending')==1,comment
Path('/home/jiangpeng/jfred-qa-comment.json').write_text(json.dumps({'id':comment['id'],'page_key':'/blog/__jfred_qa__'}))
print('PASS: new comments enter the moderation queue, not the public stream.')
