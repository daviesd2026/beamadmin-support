#!/usr/bin/env python3
import hashlib
import json
import os
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 8091
PUBLIC_IP = "YOUR_VPS_PUBLIC_IP"

USERS = {
    "admin": hashlib.sha256(b"CHANGE_ME_ADMIN_PASSWORD").hexdigest(),
    "superadmin": hashlib.sha256(b"CHANGE_ME_SUPERADMIN_PASSWORD").hexdigest(),
}

SERVERS = [
    {"id": "offroad", "name": "Str1x3vo Offroad", "path": "/opt/beammp-offroad", "port": 30816, "map": "Reshjemheia", "maxPlayers": 16, "maxCars": 3, "tags": ["Offroad", "Freeroam"], "note": "Public stock offroad server"},
    {"id": "offroad-plus", "name": "Str1x3vo Offroad+", "path": "/opt/beammp-offroad-plus", "port": 30817, "map": "Johnson Valley", "maxPlayers": 16, "maxCars": 3, "tags": ["Offroad", "Freeroam"], "note": "Offroad plus with resource pack"},
    {"id": "vanilla", "name": "Str1x3vo Vanilla", "path": "/opt/beammp-vanilla", "port": 30814, "map": "Italy", "maxPlayers": 16, "maxCars": 2, "tags": ["Freeroam"], "note": "Public stock freeroam server"},
    {"id": "vanilla-plus", "name": "Str1x3vo Vanilla+", "path": "/opt/beammp-vanilla-plus", "port": 30815, "map": "West Coast USA", "maxPlayers": 16, "maxCars": 2, "tags": ["Freeroam"], "note": "Freeroam plus with Str1x3vo resources"},
    {"id": "highforce", "name": "Str1x3vo Highforce Custom BackRoadDriving UK", "path": "/opt/beammp-highforce", "port": 30818, "map": "High Force", "maxPlayers": 16, "maxCars": 6, "tags": ["Backroads", "UK", "Custom"], "note": "Custom UK back road driving server"},
    {"id": "freeroam-old", "name": "Str1x3vo Public Freeroam", "path": "/opt/beammp-server", "port": 30814, "map": "West Coast USA", "maxPlayers": 16, "maxCars": 5, "tags": ["Freeroam"], "note": "Stopped; shares port 30814 with Vanilla"},
]

SESSIONS = {}
SESSION_TTL = 12 * 60 * 60


def bridge_dir(server):
    return Path(server["path"]) / "Resources" / "Server" / "beamadmin_bridge"


def read_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return fallback


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    os.chmod(tmp, 0o664)
    os.replace(tmp, path)
    os.chmod(path, 0o664)


def server_by_id(server_id):
    for server in SERVERS:
        if server["id"] == server_id:
            return server
    return None


def safe_text(value, fallback):
    text = str(value or "").replace("\r", " ").replace("\n", " ").strip()
    return text[:180] if text else fallback


def authed(handler):
    auth = handler.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth.split(" ", 1)[1].strip()
    expires = SESSIONS.get(token)
    if not expires or expires < time.time():
        SESSIONS.pop(token, None)
        return False
    SESSIONS[token] = time.time() + SESSION_TTL
    return True


class Handler(BaseHTTPRequestHandler):
    server_version = "BeamAdminAPI/1.0"

    def log_message(self, fmt, *args):
        return

    def send_json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def require_auth(self):
        if authed(self):
            return True
        self.send_json(401, {"error": "unauthorized"})
        return False

    def do_POST(self):
        path = urlparse(self.path).path
        body = self.read_body()

        if path == "/api/login":
            username = str(body.get("username", "")).strip()
            password = str(body.get("password", ""))
            expected = USERS.get(username)
            digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
            if expected and secrets.compare_digest(expected, digest):
                token = secrets.token_urlsafe(32)
                SESSIONS[token] = time.time() + SESSION_TTL
                self.send_json(200, {"token": token, "username": username})
            else:
                self.send_json(403, {"error": "bad credentials"})
            return

        if not self.require_auth():
            return

        parts = path.strip("/").split("/")
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "servers" and parts[3] in ("kick", "ban", "unban"):
            server = server_by_id(parts[2])
            if not server:
                self.send_json(404, {"error": "server not found"})
                return

            action = parts[3]
            command = {
                "id": secrets.token_hex(12),
                "action": action,
                "playerId": safe_text(body.get("playerId"), ""),
                "playerName": safe_text(body.get("playerName"), ""),
                "reason": safe_text(body.get("reason"), "Admin action from BeamAdmin"),
                "createdAt": int(time.time()),
            }
            if action in ("kick", "ban") and not command["playerId"] and not command["playerName"]:
                self.send_json(400, {"error": "playerId or playerName required"})
                return

            queue_file = bridge_dir(server) / "queue.json"
            queue = read_json(queue_file, [])
            if not isinstance(queue, list):
                queue = []
            queue.append(command)
            write_json(queue_file, queue[-50:])
            self.send_json(202, {"ok": True, "command": command})
            return

        self.send_json(404, {"error": "not found"})

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/health":
            self.send_json(200, {"ok": True})
            return

        if not self.require_auth():
            return

        if path == "/api/servers":
            payload = []
            for server in SERVERS:
                status = read_json(bridge_dir(server) / "status.json", {})
                item = dict(server)
                item["address"] = f"{PUBLIC_IP}:{server['port']}"
                item["bridge"] = status if isinstance(status, dict) else {}
                item["online"] = bool(item["bridge"].get("seenAt") and time.time() - int(item["bridge"].get("seenAt", 0)) < 20)
                payload.append(item)
            self.send_json(200, {"publicIp": PUBLIC_IP, "servers": payload})
            return

        parts = path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "servers":
            server = server_by_id(parts[2])
            if not server:
                self.send_json(404, {"error": "server not found"})
                return
            status = read_json(bridge_dir(server) / "status.json", {})
            item = dict(server)
            item["address"] = f"{PUBLIC_IP}:{server['port']}"
            item["bridge"] = status if isinstance(status, dict) else {}
            item["online"] = bool(item["bridge"].get("seenAt") and time.time() - int(item["bridge"].get("seenAt", 0)) < 20)
            self.send_json(200, item)
            return

        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
