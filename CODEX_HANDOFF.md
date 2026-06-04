# Codex Handoff - BeamAdmin / BeamMP

This file is for the next Codex session so work can resume without rediscovering the whole setup.

## Current Project

- GitHub repo: `daviesd2026/beamadmin-support`
- Live VPS has a BeamNG / BeamMP admin panel.
- Admin panel lives on the VPS at `/opt/beamadmin/`.
- Static UI files: `/opt/beamadmin/index.html`, `/opt/beamadmin/style.css`, `/opt/beamadmin/app.js`
- Backend API: `/opt/beamadmin/server.py`
- Lua bridge source: `/opt/beamadmin/beamadmin_bridge.lua`
- Nginx serves the panel on port `8080`.
- Python API runs on `127.0.0.1:8091`.
- Nginx proxies `/api/` to the Python API.

## Access

- SSH key on local PC: `C:\Users\Str1x3v0\.ssh\codex_vps_minecraft_ed25519`
- SSH user used in this work: `ubuntu`
- Do not write live VPS IPs or real admin passwords into GitHub notes or committed files.
- Scrub any committed support copy:
  - Replace live VPS IP with `YOUR_VPS_PUBLIC_IP`
  - Replace real admin passwords with placeholders.

## Important Owner Rule

Every time the server is edited, create a new GitHub repo release.

Existing recent releases:

- `v0.3.3` - Mod research list
- `v0.3.4` - Mod download report
- `v0.3.5` - Mods moved to `/opt/beamadmin/mods`
- `v0.3.6` - Mods moved back live to Vanilla+
- `v0.3.7` - Per-server restart controls
- `v0.3.8` - Daily work log

Next release should normally be `v0.3.9` unless a newer tag exists.

## Local Repo Copy

Local support repo path:

`C:\Users\Str1x3v0\beamadmin-support-upload`

Use explicit Git/GitHub CLI paths if PowerShell cannot find them:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' status --short
& 'C:\Program Files\GitHub CLI\gh.exe' release list --repo daviesd2026/beamadmin-support --limit 5
```

Before commits, scan for secrets:

```powershell
Get-ChildItem -File -Recurse | Select-String -Pattern 'LIVE_VPS_IP_PATTERN|REAL_ADMIN_PASSWORD|REAL_SUPERADMIN_PASSWORD'
```

## Live BeamMP Server Paths

- `/opt/beammp-offroad/`
- `/opt/beammp-offroad-plus/`
- `/opt/beammp-vanilla/`
- `/opt/beammp-vanilla-plus/`
- `/opt/beammp-highforce/`
- `/opt/beammp-server/` is an older/offline server path.

Known active services:

- `beammp-offroad`
- `beammp-offroad-plus`
- `beammp-vanilla`
- `beammp-vanilla-plus`
- `beammp-highforce`
- `beamadmin`
- `nginx`

## Current Admin Panel Features

- Login/auth token stored in browser `localStorage` as `beam_token`.
- Dashboard shows server cards, live players, server IDs, player identifiers, and kick/ban actions.
- Kick/ban reason templates include the Discord link.
- Discord link: `https://discord.gg/2WEntWFeQs`
- Management pages are built:
  - Vehicles
  - Maps
  - Ban list
  - Settings
  - Console
  - Logs
  - Mods
- Per-server restart button exists on dashboard cards.
- Restart endpoint:
  `POST /api/servers/{id}/restart`

## Bridge Details

Lua plugin install path per server:

`/opt/beammp-<id>/Resources/Server/beamadmin_bridge/beamadmin_bridge.lua`

Bridge files per server:

- `status.json`
- `queue.json`

Bridge status is considered online when `seenAt` is recent.

## Vanilla+ Mods Current State

Final requested state from owner:

- The downloaded mod batch is live in:
  `/opt/beammp-vanilla-plus/Resources/Client/`
- At last check this folder had `50` zip files and was about `5.1G`.
- `/opt/beamadmin/mods` exists but was empty after moving the batch live.
- Mod research list on VPS:
  `/opt/beamadmin/mod_list.txt`
- Download/install report on VPS:
  `/opt/beamadmin/mod_download_report.txt`

Important mod correction:

- CK Tire Pack resource URL was corrected to:
  `https://www.beamng.com/resources/ck-tire-pack.36096/`
- Wrong accidental file `legran_hd_towing.zip` was removed.
- Correct file `ck_tires_repo.zip` was installed.

## Useful Commands

SSH:

```powershell
ssh -i 'C:\Users\Str1x3v0\.ssh\codex_vps_minecraft_ed25519' ubuntu@YOUR_VPS_PUBLIC_IP 'systemctl is-active beamadmin'
```

SCP:

```powershell
scp -i 'C:\Users\Str1x3v0\.ssh\codex_vps_minecraft_ed25519' .\app.js ubuntu@YOUR_VPS_PUBLIC_IP:/tmp/app.js
```

Deploy app/API files:

```bash
sudo install -m 0644 /tmp/app.js /opt/beamadmin/app.js
sudo install -m 0644 /tmp/server.py /opt/beamadmin/server.py
sudo systemctl restart beamadmin
sudo systemctl reload nginx
curl -s http://127.0.0.1:8091/api/health
```

Check Vanilla+ mods:

```bash
find /opt/beammp-vanilla-plus/Resources/Client -maxdepth 1 -type f -name '*.zip' | wc -l
du -sh /opt/beammp-vanilla-plus/Resources/Client
systemctl is-active beammp-vanilla-plus
```

## Where To Start Next Time

1. Check the newest user request first.
2. If it involves server edits, pull the live files from `/opt/beamadmin/` before patching.
3. Make the smallest targeted change.
4. Deploy via SCP to `/tmp`, then `sudo install` into `/opt/beamadmin/`.
5. Restart only the service that needs it.
6. Verify health with `curl -s http://127.0.0.1:8091/api/health`.
7. Copy sanitized files into `C:\Users\Str1x3v0\beamadmin-support-upload`.
8. Scan for secrets.
9. Commit, push, and create a new GitHub release.

## Safety Notes

- Do not delete existing BeamMP server files unless the owner explicitly asks.
- When moving mods, only move known zip files from the specific requested source/destination.
- Do not commit mod zips to GitHub.
- Keep GitHub notes free of live IPs and real passwords.
- The owner may ask for fast automation; still verify what folder/path they mean before moving large mod batches.
