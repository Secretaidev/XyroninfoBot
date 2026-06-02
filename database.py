import json, os, threading, time

DATA_FILE = "userinfo_bot_data.json"
_lock = threading.RLock()
_cache = {"data": None, "ts": 0}
CACHE_TTL = 2

DEFAULT_SETTINGS = {
    "watermark": "Xyron Info",
    "maintenance_mode": False,
    "maintenance_message": "🔧 Bot is under maintenance. Please try again later.",
    "welcome_message": "",
    "support_link": "https://t.me/its_Xyron",
    "force_join_enabled": False,
    "force_join_channels": [],
}

def _defaults():
    return {
        "users": [],
        "banned_users": [],
        "extra_admins": [],
        "settings": dict(DEFAULT_SETTINGS),
        "lookup_stats": {},
        "total_lookups": 0,
    }

def _read():
    if not os.path.exists(DATA_FILE):
        return _defaults()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return _defaults()
    base = _defaults()
    for k in base:
        data.setdefault(k, base[k])
    for k in DEFAULT_SETTINGS:
        data["settings"].setdefault(k, DEFAULT_SETTINGS[k])
    return data

def _write(data):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, DATA_FILE)

def load_data():
    with _lock:
        now = time.time()
        if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
            return _cache["data"]
        data = _read()
        _cache["data"] = data
        _cache["ts"] = now
        return data

def save_data(data):
    with _lock:
        _write(data)
        _cache["data"] = data
        _cache["ts"] = time.time()

def add_user(user_id):
    with _lock:
        data = load_data()
        uid = int(user_id)
        if uid not in data["users"]:
            data["users"].append(uid)
            save_data(data)

def increment_lookup(user_id):
    with _lock:
        data = load_data()
        k = str(user_id)
        data["lookup_stats"][k] = data["lookup_stats"].get(k, 0) + 1
        data["total_lookups"] = data.get("total_lookups", 0) + 1
        save_data(data)

def is_banned(user_id):
    return int(user_id) in load_data().get("banned_users", [])

def is_admin(user_id):
    from config import OWNER_ID
    uid = int(user_id)
    if uid == OWNER_ID:
        return True
    return uid in load_data().get("extra_admins", [])

def is_owner(user_id):
    from config import OWNER_ID
    return int(user_id) == OWNER_ID

def get_stats():
    d = load_data()
    return {
        "total_users": len(d.get("users", [])),
        "banned_users": len(d.get("banned_users", [])),
        "total_admins": len(d.get("extra_admins", [])),
        "total_lookups": d.get("total_lookups", 0),
    }
