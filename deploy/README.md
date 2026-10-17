# Lenovo deployment

The existing GitHub Pages workflow keeps its `/JFred/` base path.
The separate `server.yml` workflow builds with `VITEPRESS_BASE=/blog/` and
publishes an amd64 image to `ghcr.io/pengjiang23/jfred`.

Only pushes to `master` and manual runs trigger server deployment. Builds run on
GitHub-hosted runners. The `lianxiang-jfred` self-hosted runner performs no source
checkout: it invokes the root-owned `/usr/local/sbin/deploy-jfred` command with an
immutable image digest. Pull requests do not run this workflow.

The helper accepts only images in this repository's GHCR namespace, serializes
deployments, keeps registry credentials temporarily in `/run`, and restores the
previous image if Compose health checks fail. It does not grant general Docker
socket access to the runner account. Host deployment files live in
`/opt/stacks/jfred` and are owned by root.

The container listens at `127.0.0.1:18080`. In 1Panel, create a website for
`192.168.0.108` and proxy `/blog/` to `http://127.0.0.1:18080/`. The trailing slash
strips the public prefix before forwarding to the container. Add `/blog` to
`/blog/` redirection. `openresty.conf` contains the equivalent standalone config;
do not install it alongside a 1Panel-generated server with the same server name.

One-time root installation, after the official GitHub runner package is verified,
extracted, and its registration token staged with mode 600:

```sh
bash /home/jiangpeng/services/jfred/source/deploy/install-server.sh
```

Check the deployment:

```sh
sudo docker compose -f /opt/stacks/jfred/compose.yaml ps
sudo docker compose -f /opt/stacks/jfred/compose.yaml logs --tail=100
curl --noproxy '*' -I http://192.168.0.108/blog/
```

To roll back without a new build, restore the previous digest and recreate the
service (previous images are not pruned automatically):

```sh
sudo cp /opt/stacks/jfred/.env.previous /opt/stacks/jfred/.env
sudo docker compose --project-directory /opt/stacks/jfred \
  -f /opt/stacks/jfred/compose.yaml up -d --no-build --wait
```

The dedicated `github-jfred` SSH alias and read-only deploy key are for manual
repository pulls. The CI deployment itself uses its short-lived `GITHUB_TOKEN`
to pull the private or public GHCR package; no permanent PAT is stored.
