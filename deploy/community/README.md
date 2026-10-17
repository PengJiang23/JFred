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
not themselves encrypted. Duplicati should encrypt them before cloud upload.

No Docker socket or entire host filesystem is mounted into Duplicati. Its source
is the export directory, read-only. Its own config directory persists separately.

## Aliyun Drive connection (user authorization required)

1. Sign into OpenList; add **Aliyundrive Open** storage at `/aliyun` and complete its
   official account authorization flow yourself. Do not paste a refresh token into
   source control or chat. Select the drive/folder you intend to use for backups.
2. In Duplicati create an encrypted backup. Source: `/source/`. Destination: WebDAV,
   server `openlist`, port `5244`, path `/dav/aliyun/jfred-backups`. These names use
   the private Compose network, not a public endpoint. Enter OpenList credentials
   privately. Prefer a dedicated restricted WebDAV user for this path after mounting.
3. Choose and separately save the backup encryption passphrase. Run at 03:30, after
   local exports. Keep at least 30 days of cloud versions; local retention is separate.
4. Test connection, run a backup, and restore files into a new directory. Check
   SHA256 and restore the databases in an isolated instance before calling it ready.

Cloud upload remains pending until authorization, encryption and restore testing
are complete. If the WebDAV connection cannot reliably upload/list/delete backup
volumes, use a supported alternative destination rather than silently losing backups.

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
