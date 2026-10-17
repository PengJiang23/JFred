#!/usr/bin/env python3
"""Confirm grouped jobs succeeded and the legacy encrypted sets stayed unchanged."""
import base64,json,pathlib,re,urllib.parse,urllib.request,xml.etree.ElementTree as ET
root=pathlib.Path('/home/jiangpeng/services');state=json.loads((root/'jfred-backup-recovery.json').read_text())
password=re.search(r'Duplicati:.*?Password: ([^\n]+)',(root/'jfred-service-access.txt').read_text(),re.S)[1]
base='http://127.0.0.1:18083/api/v1'
request=urllib.request.Request(base+'/auth/login',data=json.dumps({'Password':password,'RememberMe':False}).encode(),headers={'Content-Type':'application/json'})
with urllib.request.urlopen(request,timeout=30) as response:token=json.load(response)['AccessToken']
def api(endpoint):
    request=urllib.request.Request(base+endpoint,headers={'Authorization':'Bearer '+token})
    with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
snapshot=pathlib.Path('/opt/jfred-backup')/('before-grouping-'+state['grouped_migration_utc'])
legacy_local=None
for label,backup_id in state['legacy_backup_ids'].items():
    before=json.loads((snapshot/(label+'-original-job.json')).read_text());after=api('/backup/'+str(backup_id))
    assert not before.get('Schedule') and not after.get('Schedule')
    for key in ['Name','Sources','TargetURL','Settings','Filters','Tags','DBPath']:
        assert before['Backup'].get(key)==after['Backup'].get(key),'Legacy job changed: '+label+'/'+key
    if label=='local':
        backend=urllib.parse.unquote(urllib.parse.urlsplit(before['Backup']['TargetURL']).path)
        legacy_local=pathlib.Path('/opt/backups/jfred-duplicati')/backend.removeprefix('/backups/')
local_before=json.loads((snapshot/'legacy-local-files.json').read_text())
local_after={str(p.relative_to(legacy_local)):[p.stat().st_size,p.stat().st_mtime_ns] for p in legacy_local.rglob('*') if p.is_file()}
assert local_before==local_after,'Legacy local files changed'
auth='Basic '+base64.b64encode((state['webdav_username']+':'+state['webdav_password']).encode()).decode()
def cloud_files(folder):
    request=urllib.request.Request('http://127.0.0.1:18084/dav/'+urllib.parse.quote(folder),method='PROPFIND',headers={'Authorization':auth,'Depth':'1'})
    with urllib.request.urlopen(request,timeout=60) as response:tree=ET.fromstring(response.read())
    files={}
    for item in tree.findall('{DAV:}response'):
        href=urllib.parse.unquote(item.findtext('{DAV:}href',''))
        if href.endswith('.aes'):files[href]={'size':item.findtext('.//{DAV:}getcontentlength'),'etag':item.findtext('.//{DAV:}getetag')}
    return files
cloud_before=json.loads((snapshot/'legacy-cloud-files.json').read_text());assert cloud_files('')==cloud_before,'Legacy cloud files changed'
cycle=json.loads(pathlib.Path('/opt/backups/jfred/last-cycle.json').read_text());assert len(cycle['tasks'])==2*len(state['grouped_backups'])
for task in cycle['tasks'].values():assert api('/task/'+str(task))['Status']=='Completed'
jobs=[]
for category,group in state['grouped_backups'].items():
    assert cloud_files(group['name']+'/'),'New cloud directory has no AES volumes'
    for destination in ['local','cloud']:
        value=api('/backup/'+str(group[destination+'_backup_id']));backup=value['Backup'];settings={x['Name']:x['Value'] for x in backup['Settings']}
        assert not value.get('Schedule') and settings['encryption-module']=='aes' and settings['keep-time']=='30D'
        assert backup['Sources']==[group['source']]
        if destination=='local':assert list(pathlib.Path(group['local_directory']).glob('*.aes')),'New local directory has no AES volumes'
        jobs.append({'category':group['name'],'destination':destination,'backup_id':backup['ID'],'directory':group[destination+'_directory'],'aes':True,'retention_days':30})
restores=json.loads(pathlib.Path('/home/jiangpeng/jfred-grouped-backup-proof.json').read_text())
assert len(restores)==2*len(state['grouped_backups']) and all(x['sha256_matches'] for x in restores)
proof={'jobs':jobs,'daily_schedule':'02:30 Asia/Shanghai','original_jobs_unchanged':True,
       'original_local_files_unchanged':len(local_before),'original_cloud_files_unchanged':len(cloud_before),
       'daily_cycle_tasks':cycle['tasks'],'all_active_encrypted_restores_verified':True}
path=pathlib.Path('/home/jiangpeng/jfred-grouped-backup-layout-proof.json');path.write_text(json.dumps(proof,ensure_ascii=False,indent=2));path.chmod(0o644)
print('PASS: all active category jobs and restores verified; original local/cloud files and jobs unchanged.',flush=True)
