#!/usr/bin/env bash
set -Eeuo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run this installer as root.' >&2; exit 1; }
source_dir=/home/jiangpeng/services/jfred/source
runner=/home/jiangpeng/actions-runner
stack=/opt/stacks/jfred

# Only root owns the files used by the privileged deployment command.
install -d -m 755 "$stack"
install -m 644 "$source_dir/deploy/compose.yaml" "$stack/compose.yaml"
install -m 755 "$source_dir/deploy/deploy-jfred" /usr/local/sbin/deploy-jfred
printf 'jiangpeng ALL=(root) NOPASSWD: /usr/local/sbin/deploy-jfred\n' > /etc/sudoers.d/jfred-deploy
chmod 440 /etc/sudoers.d/jfred-deploy
visudo -cf /etc/sudoers.d/jfred-deploy

# The image is intentionally absent until the first successful CI build.
JFRED_IMAGE=ghcr.io/pengjiang23/jfred:pending docker compose -f "$stack/compose.yaml" config --quiet

if [[ ! -f "$runner/.runner" ]]; then
    [[ -s "$runner/.registration-token" ]] || { echo 'Runner registration token is missing.' >&2; exit 1; }
    registration_token=$(cat "$runner/.registration-token")
    cd "$runner"
    runuser -u jiangpeng -- env \
        https_proxy=http://127.0.0.1:20172 \
        http_proxy=http://127.0.0.1:20172 \
        no_proxy=localhost,127.0.0.1,192.168.0.108 \
        ./config.sh \
        --url https://github.com/PengJiang23/JFred \
        --token "$registration_token" \
        --name lianxiang-jfred \
        --labels jfred-deploy \
        --work _work \
        --unattended
    rm -f "$runner/.registration-token"
    unset registration_token
fi
cd "$runner"
python3 - <<'PY'
from pathlib import Path
p = Path('.env')
lines = p.read_text().splitlines() if p.exists() else []
keys = ('https_proxy=', 'http_proxy=', 'no_proxy=')
lines = [line for line in lines if not line.startswith(keys)]
lines += ['https_proxy=http://127.0.0.1:20172',
          'http_proxy=http://127.0.0.1:20172',
          'no_proxy=localhost,127.0.0.1,192.168.0.108']
p.write_text('\n'.join(lines) + '\n')
PY
chown jiangpeng:jiangpeng .env
chmod 600 .env
if [[ ! -f .service ]]; then
    ./svc.sh install jiangpeng
fi
./svc.sh start
./svc.sh status
echo 'JFred deployment runner installed. The queued GitHub workflow can now deploy the blog.'
