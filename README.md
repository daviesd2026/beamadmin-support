# BeamAdmin support copy

This is a support/debug copy of a BeamMP admin panel.

## Files

- `index.html`, `style.css`, `app.js`: browser UI
- `server.py`: Python API service that runs on the VPS
- `beamadmin_bridge.lua`: BeamMP server plugin for player list, kick, and ban commands

## Runtime layout

The live VPS uses:

```text
/opt/beamadmin/
/opt/beammp-*/Resources/Server/beamadmin_bridge/
```

Nginx serves the UI and proxies `/api/` to `server.py` on `127.0.0.1:8091`.

## Notes

GitHub Pages can host the static UI only. It cannot run `server.py`, so kick/ban requires the VPS backend.

Passwords and public IP values in this support copy were replaced with placeholders.
