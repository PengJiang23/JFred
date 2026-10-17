# Community services and backups

Separate from the immutable static-site container, `/opt/stacks/jfred-community`
contains Artalk, Umami/PostgreSQL, Duplicati and OpenList. These services retain
state across blog updates. Image tags are pinned; review upgrades before applying.

## Administration

Admin listeners bind only to the server's LAN address and loopback. Default Umami
credentials are replaced before enabling LAN listeners. Access details are saved
at `/home/jiangpeng/services/jfred-service-access.txt` (owner-only, never committed).

- Artalk: `http://192.168.0.108:18081/` (login through Artalk sidebar/control center).
- Umami: `http://192.168.0.108:18082/`.
- Duplicati: `http://192.168.0.108:18083/`.
- OpenList: `http://192.168.0.108:18084/`.

OpenResty proxies comments and a strict allowlist of analytics endpoints under
`/blog/`. The true client address overwrites incoming forwarded-IP headers. Public
Umami tokens can read only this website's overview aggregates; session/replay/admin
APIs are not exposed through that prefix. Never put an admin token in frontend code.

## Counting

Umami `SALT_ROTATION=day`, `TZ=Asia/Shanghai`: IP + User-Agent + secret-derived
rotating salt identify a visitor for one calendar day. Page heat uses `visitors`,
not `pageviews`. The total accumulates distinct daily identifiers, not lifetime
unique people. DNT is respected, query strings are stripped, and `.html`/trailing
slash aliases are canonicalized before tracking. Artalk's own PV increment is off.

## Backup scope

`backup-jfred` uses `pg_dump -Fc` for analytics and SQLite's online backup API for
Artalk, OpenList and Duplicati. It includes service keys/config and deployed image
digest. Local tar archives have mode 600, retain seven exports, and run daily around
02:30 Asia/Shanghai using a persistent systemd timer. They contain secrets and are
not themselves encrypted. Duplicati encrypts them before cloud upload.

No Docker socket or entire host filesystem is mounted into Duplicati. Its source
is the export directory, read-only. Its own config directory persists separately.

## Aliyun Drive backups

OpenList mounts Aliyundrive Open at `/aliyun`. The dedicated `jfred-backup` user
is restricted to `/aliyun/jfred-backups`, with WebDAV read/write permissions and
no administration privileges. Its destination inside Compose is
`webdav://openlist:5244/dav/`; the user base path maps this DAV root to the backup
folder. Do not append `/aliyun/jfred-backups` again for this restricted user.

`configure-backups.py` prepares AES-encrypted local and cloud jobs. Local backups
run at 03:00 Asia/Shanghai; cloud scheduling is initially disabled. After cloud
authorization, successful upload and restore verification,
`activate-cloud-backup.py` enables the cloud job at 03:30. Both keep 30 days of
versions, independent of the seven unencrypted source exports.

On this server cloud authorization, WebDAV connection, encrypted upload and both
local/cloud restores were verified on 2026-10-17. Restored archive SHA256 matched
the original; all SQLite snapshots passed integrity checks and the PostgreSQL
export restored into a separate test database. Daily cloud scheduling is enabled.

Owner-only `/home/jiangpeng/services/jfred-backup-recovery.json` contains the AES
passphrase and restricted WebDAV credentials. Keep a separate protected copy,
along with `jfred-service-access.txt`; neither belongs in Git. Cloud authorization
can expire, so check Duplicati task results and periodically repeat restoration.

## OSS media

`backup-data-j` is private, Hangzhou (`oss-cn-hangzhou.aliyuncs.com`). It is reserved
for blog images/video; this setup neither uploads backups there nor changes bucket
ACL, lifecycle or billing settings. Use local `docs/public/media/` assets meanwhile.
Private OSS URLs need an authorized delivery design before embedding stable URLs:
short-lived signatures are not permanent article links. Never expose AccessKey in JS.

## Recovery check

```sh
sudo systemctl status jfred-backup.timer
sudo /usr/local/sbin/backup-jfred
sudo sha256sum -c /opt/backups/jfred/jfred-TIMESTAMP.tar.gz.sha256
```

Restore into a separate Compose project/network first. Stop services before replacing
SQLite databases; restore PostgreSQL with `pg_restore --clean --if-exists` only into
an empty test database. Keep app keys and Duplicati encryption/settings keys safely
outside the only server that they protect. Never test restoration over live data.
