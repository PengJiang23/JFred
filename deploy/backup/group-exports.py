#!/usr/bin/env python3
"""Build three atomic, root-only backup views using hard links, not extra copies."""
import hashlib,json,os,pathlib,shutil,tempfile

GROUPS={'databases':'数据库','applications':'应用数据与配置','images':'Docker镜像'}

def group_exports(root):
    root=pathlib.Path(root);daily=root/'daily'
    manifests=list(daily.glob('recovery-manifest-*.json'))
    if len(manifests)!=1:raise RuntimeError('Expected one completed export manifest')
    manifest=json.loads(manifests[0].read_text())
    files={
        'databases':[daily/x['file'] for x in manifest['databases']],
        'applications':sorted(daily.glob('application-*')),
        'images':[root/x['file'] for x in manifest['images']],
    }
    expected={manifests[0].name,'RESTORE-恢复说明.md','SHA256SUMS.txt'}
    expected.update(p.name for k in ['databases','applications'] for p in files[k])
    if {p.name for p in daily.iterdir()}!=expected:
        raise RuntimeError('Unclassified export files; refusing an incomplete grouped backup')
    if any(not values for values in files.values()):raise RuntimeError('An export category is empty')
    checksums={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (daily/'SHA256SUMS.txt').read_text().splitlines()}
    image_hashes={pathlib.Path(x['file']).name:x['sha256'] for x in manifest['images']}
    stage=pathlib.Path(tempfile.mkdtemp(prefix='.grouped-',dir=root));stage.chmod(0o700)
    try:
        for key,label in GROUPS.items():
            dest=stage/label;dest.mkdir(mode=0o700);hashes=[]
            for source in files[key]+[manifests[0],daily/'RESTORE-恢复说明.md']:
                digest=hashlib.file_digest(source.open('rb'),'sha256').hexdigest()
                if digest!=(image_hashes if key=='images' and source.parent!=daily else checksums)[source.name]:
                    raise RuntimeError('Export checksum mismatch: '+source.name)
                os.link(source,dest/source.name);hashes.append(digest+'  '+source.name)
            info={'category':label,'export_created':manifest['created'],'timezone':'Asia/Shanghai',
                  'files':[p.name for p in files[key]],'encryption':'Duplicati AES',
                  'restore':'在 Duplicati 选择同名分类任务和日期恢复；目录中的分块不能单独作为压缩包解压。'}
            info_path=dest/'BACKUP-分类说明.json';info_path.write_text(json.dumps(info,ensure_ascii=False,indent=2));info_path.chmod(0o600)
            hashes.append(hashlib.file_digest(info_path.open('rb'),'sha256').hexdigest()+'  '+info_path.name)
            (dest/'SHA256SUMS.txt').write_text('\n'.join(hashes)+'\n')
        previous=root/'.grouped-previous';latest=root/'grouped'
        if previous.exists():shutil.rmtree(previous)
        if latest.exists():latest.rename(previous)
        stage.rename(latest)
        if previous.exists():shutil.rmtree(previous)
    finally:
        if stage.exists():shutil.rmtree(stage)
    print('Grouped exports verified: '+json.dumps({GROUPS[k]:len(v) for k,v in files.items()},ensure_ascii=False),flush=True)

if __name__=='__main__':
    os.umask(0o077)
    group_exports('/opt/backups/jfred')
