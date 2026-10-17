#!/usr/bin/env bash
# Compatibility entry point; the complete daily pipeline is maintained in deploy/backup.
set -Eeuo pipefail
[[ -f /opt/jfred-backup/run-daily.py ]] || { echo 'Install deploy/backup/install.sh first.'; exit 1; }
exec /usr/bin/python3 /opt/jfred-backup/run-daily.py
