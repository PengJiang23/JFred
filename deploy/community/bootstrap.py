#!/usr/bin/env python3
"""Create the one-site analytics setup without storing admin credentials in Git."""
import json, secrets, time, urllib.request, urllib.error
from pathlib import Path

root = Path('/opt/stacks/jfred-community')
state_file = root / 'access.json'
if state_file.exists():
    state = json.loads(state_file.read_text())
else:
    state = {'umami_username': 'admin', 'umami_password': secrets.token_urlsafe(24),
             'website_id': 'fa4e9f07-6328-46d1-ad63-16ab7ec3682a', 'share_slug': 'jfred-public'}
    state_file.write_text(json.dumps(state, indent=2))
    state_file.chmod(0o600)

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def api(path, body=None, token=None, method=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request('http://127.0.0.1:18082/api' + path,
        data=json.dumps(body).encode() if body is not None else None, headers=headers, method=method)
    with opener.open(request, timeout=30) as response:
        text = response.read()
        return json.loads(text) if text else {}

for attempt in range(120):
    try:
        api('/heartbeat')
        break
    except Exception:
        time.sleep(3)
else:
    raise SystemExit('Umami did not become ready')

try:
    login = api('/auth/login', {'username': state['umami_username'], 'password': state['umami_password']})
except urllib.error.HTTPError as error:
    if error.code != 401:
        raise
    login = api('/auth/login', {'username': 'admin', 'password': 'umami'})
    api('/users/' + login['user']['id'], {'password': state['umami_password']}, login['token'])
    login = api('/auth/login', {'username': state['umami_username'], 'password': state['umami_password']})

token = login['token']
try:
    website = api('/websites/' + state['website_id'], token=token)
except urllib.error.HTTPError as error:
    if error.code != 404:
        raise
    website = None
if not website:
    api('/websites', {'id': state['website_id'], 'name': 'JFred', 'domain': '192.168.0.108'}, token)

# Public aggregate-only access. No visitor/session lists, events, replay or identity data.
try:
    api('/share/' + state['share_slug'])
except urllib.error.HTTPError as error:
    if error.code != 404:
        raise
    api('/share', {'entityId': state['website_id'], 'shareType': 1, 'name': 'JFred public counts',
                  'slug': state['share_slug'], 'parameters': {'overview': True, 'events': False,
                  'sessions': False, 'realtime': False, 'performance': False, 'compare': False,
                  'breakdown': False, 'allowFilter': True}}, token)
print('Umami admin secured; website and aggregate-only share configured.')
