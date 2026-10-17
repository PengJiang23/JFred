# Statistics, cloud storage and backups

The community stack now runs Umami, Duplicati and OpenList. Comments use the official `@giscus/vue` component backed by GitHub Discussions in `PengJiang23/JFred`; there is no local comment service or database.

- Umami: port18082; shared 1Panel PostgreSQL, least-privilege application role.
- Duplicati: port18083; AES-encrypted local and Aliyun Drive copies, 30-day history.
- OpenList: port18084; Aliyun Drive Open mounted at `/aliyun`, restricted backup account maps WebDAV `/dav/` to `/aliyun/jfred-backups`.

Administration ports require the existing private network firewall. OpenResty only exposes aggregate analytics endpoints, never the admin UI/session lists. The blog's `/stats` page embeds public counts. IP+User-Agent with rotating daily salt counts anonymous daily readership; refreshes are not unique readers.

Full-server backup and recovery are maintained in [../backup/RESTORE.md](../backup/RESTORE.md). `jfred-backup.timer` starts once daily at02:30 Asia/Shanghai: consistent database/application exports → encrypted local copy → encrypted Aliyun Drive copy. Independent Duplicati schedules are disabled so large exports cannot race uploads. The root-only source directory contains readable purpose-named files; destination `.aes` chunks retain Duplicati's own names.

All live Artalk containers, image and data were removed2026-10-17 at the owner's request. Existing historical encrypted backup versions expire through normal retention; do not delete individual chunks belonging to mixed-service backup sets.
