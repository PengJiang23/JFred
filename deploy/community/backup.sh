#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
stack=/opt/stacks/jfred-community
base=/opt/backups/jfred
exec 8>/run/lock/jfred-backup.lock
flock -n 8 || exit 0
stamp=$(date -u +%Y%m%dT%H%M%SZ)
work=$(mktemp -d "$base/.export.XXXXXX")
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/config/community" "$work/config/blog" "$work/artalk"
cd "$stack"
docker compose exec -T db pg_dump -U umami -d umami -Fc > "$work/umami.pgdump"
# SQLite's backup API takes a consistent snapshot, including WAL content.
python3 - "$stack/artalk/artalk.db" "$work/artalk/artalk.db" <<'PY'
import sqlite3, sys
with sqlite3.connect(sys.argv[1]) as source, sqlite3.connect(sys.argv[2]) as dest:
 source.backup(dest)
 result=dest.execute('PRAGMA integrity_check').fetchone()[0]
 assert result == 'ok', result
PY
# Export bridge and backup-tool databases with the same SQLite snapshot API.
python3 - "$stack" "$work" <<'PYSQL'
from pathlib import Path
import sqlite3,sys,shutil
root,out=map(Path,sys.argv[1:])
for service in ['openlist','duplicati']:
 target=out/service; target.mkdir()
 for f in (root/service).rglob('*'):
  if not f.is_file():
   continue
  destination=target/f.relative_to(root/service)
  destination.parent.mkdir(parents=True,exist_ok=True)
  if f.is_file() and f.suffix.lower() in ['.db','.sqlite']:
   with sqlite3.connect('file:'+str(f)+'?mode=ro',uri=True) as source, sqlite3.connect(destination) as dest:
    source.backup(dest)
    assert dest.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
  elif f.suffix in ['.json','.txt']:
   shutil.copy2(f,destination)
PYSQL
cp -a "$stack/.env" "$stack/access.json" "$stack/compose.yaml" "$stack/admin-access.yaml" "$stack/artalk/artalk.yml" "$work/config/community/"
cp -a /opt/stacks/jfred/compose.yaml /opt/stacks/jfred/.env "$work/config/blog/" 2>/dev/null || true
cp "$stack/openresty.conf" "$work/config/community/"
if [[ -d "$stack/artalk/uploads" ]]; then cp -a "$stack/artalk/uploads" "$work/artalk/"; fi
cat > "$work/RESTORE.txt" <<'NOTE'
Contains secrets: keep this archive private and encrypt it before cloud upload.
Restore configuration into /opt/stacks/jfred-community (directory mode 700).
Start only the PostgreSQL service, then restore umami.pgdump with pg_restore.
Stop Artalk before restoring artalk/artalk.db; remove stale -wal/-shm only while stopped.
Restore app keys and restart services. Do a recovery test in a separate project first.
Website source is also versioned in GitHub; blog image digest is included in config.
NOTE
archive="$base/jfred-$stamp.tar.gz"
tar -C "$work" -czf "$archive.tmp" .
mv "$archive.tmp" "$archive"
sha256sum "$archive" > "$archive.sha256"
# Only prune this script's completed exports; preserve the newest seven.
python3 - "$base" <<'PY'
from pathlib import Path
import sys
files=sorted(Path(sys.argv[1]).glob('jfred-????????T??????Z.tar.gz'),reverse=True)
for f in files[7:]:
 f.unlink(); f.with_name(f.name+'.sha256').unlink(missing_ok=True)
PY
printf 'Backup complete: %s\n' "$archive"
