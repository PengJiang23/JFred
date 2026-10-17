#!/usr/bin/env python3
"""Create independent category backup sets; never move or run the legacy sets."""
import base64,datetime,fcntl,json,os,pathlib,re,urllib.error,urllib.parse,urllib.request,xml.etree.ElementTree as ET
os.umask(0o077)
lock=open('/run/lock/jfred-backup-cycle.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
root=pathlib.Path('/home/jiangpeng/services');path=root/'jfred-backup-recovery.json';state=json.loads(path.read_text())
password=re.search(r'Duplicati:.*?Password: ([^\n]+)',(root/'jfred-service-access.txt').read_text(),re.S)[1]
base='http://127.0.0.1:18083/api/v1'
def api(endpoint,body=None,token=None):
    headers={'Content-Type':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    request=urllib.request.Request(base+endpoint,data=json.dumps(body).encode() if body is not None else None,headers=headers)
    with urllib.request.urlopen(request,timeout=30) as response:
        data=response.read();return json.loads(data) if data else {}
token=api('/auth/login',{'Password':password,'RememberMe':False})['AccessToken']
assert not api('/serverstate',token=token).get('ActiveTask'),'Wait for running Duplicati tasks first'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
snapshot=pathlib.Path('/opt/jfred-backup')/('before-grouping-'+stamp);snapshot.mkdir(mode=0o700)
(snapshot/'recovery-state.json').write_text(json.dumps(state,indent=2))
legacy=state.get('legacy_backup_ids') or {label:state[label+'_backup_id'] for label in ['local','cloud']}
legacy_local=None
for label,backup_id in legacy.items():
    original=api('/backup/'+str(backup_id),token=token)
    assert not original.get('Schedule'),'Legacy schedules must already be disabled'
    (snapshot/(label+'-original-job.json')).write_text(json.dumps(original,indent=2))
    if label=='local':
        backend=urllib.parse.unquote(urllib.parse.urlsplit(original['Backup']['TargetURL']).path)
        assert backend.startswith('/backups/')
        legacy_local=pathlib.Path('/opt/backups/jfred-duplicati')/backend.removeprefix('/backups/')
def local_inventory():
    return {str(p.relative_to(legacy_local)):[p.stat().st_size,p.stat().st_mtime_ns] for p in legacy_local.rglob('*') if p.is_file()}
local_before=local_inventory();assert local_before,'Expected existing encrypted local backup files'
(snapshot/'legacy-local-files.json').write_text(json.dumps(local_before,indent=2))
existing=api('/backups',token=token);groups={}
webdav_auth='Basic '+base64.b64encode((state['webdav_username']+':'+state['webdav_password']).encode()).decode()
def legacy_cloud_files():
    request=urllib.request.Request('http://127.0.0.1:18084/dav/',method='PROPFIND',headers={'Authorization':webdav_auth,'Depth':'1'})
    with urllib.request.urlopen(request,timeout=60) as response:tree=ET.fromstring(response.read())
    result={}
    for item in tree.findall('{DAV:}response'):
        href=urllib.parse.unquote(item.findtext('{DAV:}href',''))
        if not href.endswith('.aes'):continue
        result[href]={'size':item.findtext('.//{DAV:}getcontentlength'),'etag':item.findtext('.//{DAV:}getetag')}
    return result
cloud_before=legacy_cloud_files();assert cloud_before,'Expected existing encrypted cloud backup files'
(snapshot/'legacy-cloud-files.json').write_text(json.dumps(cloud_before,ensure_ascii=False,indent=2))
for category,label in [('databases','数据库'),('applications','应用数据与配置')]:
    group={'name':label,'source':'/source/grouped/'+label+'/'}
    for destination in ['local','cloud']:
        name='每日分类备份 · '+label+' · '+('本机' if destination=='local' else '阿里云盘')
        tags=['jfred-category-'+category,'jfred-destination-'+destination]
        if destination=='local':
            pathlib.Path('/opt/backups/jfred-duplicati',label).mkdir(mode=0o700,exist_ok=True)
            target='file:///backups/'+urllib.parse.quote(label)+'/'
        else:
            request=urllib.request.Request('http://127.0.0.1:18084/dav/'+urllib.parse.quote(label)+'/',method='MKCOL',headers={'Authorization':webdav_auth})
            try:
                with urllib.request.urlopen(request,timeout=60) as response:assert response.status in [200,201,204]
            except urllib.error.HTTPError as error:
                if error.code!=405:raise
            query=urllib.parse.urlencode({'auth-username':state['webdav_username'],'auth-password':state['webdav_password']})
            target='webdav://openlist:5244/dav/'+urllib.parse.quote(label)+'/?'+query
        found=[x['Backup'] for x in existing if all(tag in x['Backup'].get('Tags',[]) for tag in tags)]
        assert len(found)<=1,'Duplicate category jobs'
        if found:
            backup_id=str(found[0]['ID'])
        else:
            values={'encryption-module':'aes','compression-module':'zip','passphrase':state['encryption_passphrase'],
                    'dblock-size':'10mb','keep-time':'30D','backup-test-samples':'1','prefix':'lianxiang_'+category}
            if destination=='cloud':values.update({'read-write-timeout':'5m','short-timeout':'5m','list-timeout':'15m','asynchronous-concurrent-upload-limit':'2'})
            body={'Backup':{'Name':name,'Description':'北京时间02:30统一导出后顺序执行；AES加密，保留30天；原完整备份独立保留。',
                            'TargetURL':target,'Sources':[group['source']],'Settings':[{'Name':k,'Value':v} for k,v in values.items()],
                            'Filters':[],'Tags':tags,'Metadata':{}},'Schedule':None}
            backup_id=str(api('/backups',body,token)['ID'])
        actual=api('/backup/'+backup_id,token=token);backup=actual['Backup'];settings={x['Name']:x['Value'] for x in backup['Settings']}
        assert not actual.get('Schedule') and backup['Sources']==[group['source']]
        assert settings['encryption-module']=='aes' and settings['keep-time']=='30D'
        assert urllib.parse.unquote(urllib.parse.urlsplit(backup['TargetURL']).path)==urllib.parse.unquote(urllib.parse.urlsplit(target).path)
        group[destination+'_backup_id']=backup_id
        group[destination+'_directory']=('/opt/backups/jfred-duplicati/' if destination=='local' else '/aliyun/jfred-backups/')+label
        print('Configured '+destination+'/'+category+' (ID '+backup_id+')',flush=True)
    groups[category]=group
assert legacy_cloud_files()==cloud_before,'Existing cloud backup inventory changed unexpectedly'
assert local_inventory()==local_before,'Existing local backup inventory changed unexpectedly'
retired=state.get('retired_grouped_backups',{})
retired.update({key:value for key,value in state.get('grouped_backups',{}).items() if key not in groups})
state.update(grouped_backups=groups,retired_grouped_backups=retired,legacy_backup_ids=legacy,grouped_migration_utc=stamp,
             local_schedule='02:30 Asia/Shanghai, two category jobs after export',
             cloud_schedule='02:30 Asia/Shanghai cycle, after local category copies',
             legacy_policy='Original full-backup sets preserved in place; no scheduled runs or pruning',
             scope='databases, application data/configuration, image references (no image archives) in independent AES backup sets')
owner=path.stat();temp=path.with_suffix('.json.new');temp.write_text(json.dumps(state,ensure_ascii=False,indent=2));temp.chmod(0o600);os.chown(temp,owner.st_uid,owner.st_gid);temp.replace(path)
p=root/'lianxiang-all-service-accounts.txt';text=p.read_text()
text=text.replace('三类本机AES副本','两类本机AES副本').replace('三类阿里云盘AES副本','两类阿里云盘AES副本')
text=text.replace('每天北京时间02:30一次：数据库/应用一致性导出 → 本机AES副本 → 阿里云盘AES副本；历史版本30天。','每天北京时间02:30一次：一致性导出 → 两类本机AES副本 → 两类阿里云盘AES副本；新任务历史版本30天。')
marker='\n=== 分类备份目录（当前） ===\n';end_marker='=== 分类备份目录结束 ===\n'
section=marker+'每天北京时间02:30统一执行一次；数据库、应用数据与配置分别为独立的本机/云端AES任务，恢复口令保持不变。\n'
for group in groups.values():section+=group['name']+'：云盘 '+group['cloud_directory']+'；本机 '+group['local_directory']+'\n'
section+='Docker镜像不再导出或自动备份；已有镜像备份保留，恢复时可重新拉取镜像。\n'
section+='原完整备份任务ID '+str(legacy)+' 不再自动运行，原文件原位保留，不自动清理。恢复旧日期请选择原完整备份任务。\n'
section+='恢复新备份：选择对应分类和日期，/source/grouped/对应分类/；包含分类说明和SHA256SUMS.txt。云盘物理分块仍由Duplicati管理。\n'+end_marker
text=re.sub(re.escape(marker)+'.*?'+re.escape(end_marker),'',text,flags=re.S)+section
p.write_text(text);p.chmod(0o600)
print('Four AES jobs configured; original backup sets untouched; recovery state activated.',flush=True)
