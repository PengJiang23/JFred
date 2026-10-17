#!/bin/bash
set -Eeuo pipefail
src=$(cd "$(dirname "$0")" && pwd)
checkout=${1:?Pass a local checkout of https://github.com/reorx/sui2}
cp "$src/navigation.json" "$checkout/data.json"
cd "$checkout"
npm install --ignore-scripts --no-audit --no-fund
NO_PWA=1 npm run build
printf 'Built navigation at %s/dist; copy to /opt/stacks/jfred-infrastructure/navigation/\n' "$checkout"
