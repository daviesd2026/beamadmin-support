#!/usr/bin/env python3
import hashlib
import json
import os
import re
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
AUTH_FILE = Path("/opt/beamadmin/auth.json")
if AUTH_FILE.exists():
    try:
        loaded_users = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
        if isinstance(loaded_users, dict):
            USERS.update({str(k): str(v) for k, v in loaded_users.items()})
    except Exception:
        pass

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
MAPS = ["Italy", "West Coast USA", "Reshjemheia", "Johnson Valley", "High Force", "GridMap", "Small Island", "Industrial Site", "East Coast USA"]
MAP_PATHS = {
    "Italy": "/levels/italy/info.json",
    "West Coast USA": "/levels/west_coast_usa/info.json",
    "Reshjemheia": "/levels/Reshjemheia/info.json",
    "Johnson Valley": "/levels/johnson_valley/info.json",
    "High Force": "/levels/highforce/info.json",
    "GridMap": "/levels/gridmap_v2/info.json",
    "Small Island": "/levels/small_island/info.json",
    "Industrial Site": "/levels/industrial/info.json",
    "East Coast USA": "/levels/east_coast_usa/info.json",
}


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


def normalize_status(status):
    if not isinstance(status, dict):
        return {}
    players = status.get("players")
    if isinstance(players, dict):
        status["players"] = list(players.values())
    elif not isinstance(players, list):
        status["players"] = []
    status["playerCount"] = len(status["players"])
    return status


def queue_command(server, command):
    queue_file = bridge_dir(server) / "queue.json"
    queue = read_json(queue_file, [])
    if not isinstance(queue, list):
        queue = []
    command["id"] = command.get("id") or secrets.token_hex(12)
    command["createdAt"] = int(time.time())
    queue.append(command)
    write_json(queue_file, queue[-100:])
    return command


def read_server_config(server):
    config_path = Path(server["path"]) / "ServerConfig.toml"
    text = ""
    try:
        text = config_path.read_text(encoding="utf-8")
    except Exception:
        pass

    def val(key, fallback=""):
        match = re.search(rf"^\s*{re.escape(key)}\s*=\s*(.+?)\s*$", text, re.M)
        if not match:
            return fallback
        raw = match.group(1).strip()
        if raw.startswith('"') and raw.endswith('"'):
            return raw[1:-1]
        if raw.lower() in ("true", "false"):
            return raw.lower() == "true"
        try:
            return int(raw)
        except Exception:
            return raw

    map_path = val("Map", server.get("map", ""))
    current_map = next((name for name, path in MAP_PATHS.items() if path == map_path), server.get("map", map_path))
    return {
        "name": val("Name", server["name"]),
        "maxPlayers": val("MaxPlayers", server.get("maxPlayers", 16)),
        "password": val("Password", ""),
        "private": val("Private", False),
        "map": current_map,
        "mapPath": map_path,
    }


def write_server_config(server, updates):
    config_path = Path(server["path"]) / "ServerConfig.toml"
    text = config_path.read_text(encoding="utf-8")
    replacements = {
        "Name": str(updates.get("name", "")).strip(),
        "MaxPlayers": str(int(updates.get("maxPlayers", 16))),
        "Password": str(updates.get("password", "")),
        "Private": "true" if bool(updates.get("private")) else "false",
    }

    for key, value in replacements.items():
        if key == "MaxPlayers" or key == "Private":
            rendered = value
        else:
            rendered = '"' + value.replace('"', '\\"') + '"'
        pattern = rf"^(\s*{re.escape(key)}\s*=\s*).*$"
        if re.search(pattern, text, re.M):
            text = re.sub(pattern, rf"\g<1>{rendered}", text, flags=re.M)
        else:
            text += f"\n{key} = {rendered}\n"

    config_path.write_text(text, encoding="utf-8")
    return read_server_config(server)


def tail_lines(path, limit=100):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            lines = handle.readlines()
        return [line.rstrip("\n") for line in lines[-limit:]]
    except Exception:
        return []


def read_bridge_results(server, limit=100):
    return tail_lines(bridge_dir(server) / "results.log", limit)


def bans_for_server(server):
    bridge = read_json(bridge_dir(server) / "status.json", {})
    bridge_bans = normalize_status(bridge).get("bans", {})
    rows = []
    for name, reason in (bridge_bans.get("names") or {}).items():
        rows.append({"playerName": name, "beammpId": "", "reason": reason, "bannedOn": "", "serverId": server["id"], "serverName": server["name"], "playerId": name})
    for ip, reason in (bridge_bans.get("ips") or {}).items():
        rows.append({"playerName": ip, "beammpId": "", "reason": reason, "bannedOn": "", "serverId": server["id"], "serverName": server["name"], "playerId": ip})
    return rows


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
            command = queue_command(server, {
                "action": action,
                "playerId": safe_text(body.get("playerId"), ""),
                "playerName": safe_text(body.get("playerName"), ""),
                "reason": safe_text(body.get("reason"), "Admin action from BeamAdmin"),
            })
            if action in ("kick", "ban") and not command["playerId"] and not command["playerName"]:
                self.send_json(400, {"error": "playerId or playerName required"})
                return

            self.send_json(202, {"ok": True, "command": command})
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "servers" and parts[3] in ("deletevehicle", "changemap", "console"):
            server = server_by_id(parts[2])
            if not server:
                self.send_json(404, {"error": "server not found"})
                return
            action = parts[3]
            if action == "deletevehicle":
                command = queue_command(server, {"action": "deletevehicle", "playerId": safe_text(body.get("playerId"), ""), "vehicleId": safe_text(body.get("vehicleId"), "")})
            elif action == "changemap":
                map_name = safe_text(body.get("map"), "")
                if map_name not in MAP_PATHS:
                    self.send_json(400, {"error": "unknown map"})
                    return
                command = queue_command(server, {"action": "changemap", "map": map_name, "mapPath": MAP_PATHS[map_name]})
            else:
                command = queue_command(server, {"action": "console", "command": safe_text(body.get("command"), "")})
            self.send_json(202, {"ok": True, "command": command})
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "servers" and parts[3] == "settings":
            server = server_by_id(parts[2])
            if not server:
                self.send_json(404, {"error": "server not found"})
                return
            try:
                settings = write_server_config(server, body)
                self.send_json(200, {"ok": True, "settings": settings})
            except Exception as exc:
                self.send_json(500, {"error": str(exc)})
            return

        if path == "/api/auth/changepassword":
            old_password = str(body.get("oldPassword", ""))
            new_password = str(body.get("newPassword", ""))
            username = str(body.get("username", "admin"))
            expected = USERS.get(username)
            digest = hashlib.sha256(old_password.encode("utf-8")).hexdigest()
            if not expected or not secrets.compare_digest(expected, digest):
                self.send_json(403, {"error": "old password is incorrect"})
                return
            USERS[username] = hashlib.sha256(new_password.encode("utf-8")).hexdigest()
            write_json(Path("/opt/beamadmin/auth.json"), USERS)
            self.send_json(200, {"ok": True})
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
                item["bridge"] = normalize_status(status)
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
            item["bridge"] = normalize_status(status)
            item["online"] = bool(item["bridge"].get("seenAt") and time.time() - int(item["bridge"].get("seenAt", 0)) < 20)
            self.send_json(200, item)
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "servers":
            server = server_by_id(parts[2])
            if not server:
                self.send_json(404, {"error": "server not found"})
                return
            route = parts[3]
            status = normalize_status(read_json(bridge_dir(server) / "status.json", {}))
            if route == "status":
                item = dict(server)
                item["address"] = f"{PUBLIC_IP}:{server['port']}"
                item["bridge"] = status
                item["settings"] = read_server_config(server)
                item["online"] = bool(status.get("seenAt") and time.time() - int(status.get("seenAt", 0)) < 20)
                self.send_json(200, item)
                return
            if route == "bans":
                self.send_json(200, {"bans": bans_for_server(server)})
                return
            if route == "settings":
                self.send_json(200, {"settings": read_server_config(server), "maps": MAPS})
                return
            if route == "consolelog":
                self.send_json(200, {"lines": read_bridge_results(server, 100)})
                return
            if route == "log":
                self.send_json(200, {"lines": tail_lines(Path(server["path"]) / "Server.log", 300)})
                return

        self.send_json(404, {"error": "not found"})

    def do_DELETE(self):
        path = urlparse(self.path).path
        if not self.require_auth():
            return
        parts = path.strip("/").split("/")
        if len(parts) == 5 and parts[0] == "api" and parts[1] == "servers" and parts[3] == "ban":
            server = server_by_id(parts[2])
            if not server:
                self.send_json(404, {"error": "server not found"})
                return
            player_id = safe_text(parts[4], "")
            command = queue_command(server, {"action": "unban", "playerName": player_id, "playerId": player_id})
            self.send_json(202, {"ok": True, "command": command})
            return

        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
