import time, json, os, threading

_lock = threading.RLock()
_cache = {"data": None, "ts": 0}
_TTL = 2
_mongo_ok = False
_col = None
_FILE = "bot_data.json"

_DEFAULT = {
    "users": [],
    "settings": {
        "watermark": "Xyron Info",
        "support_link": "https://t.me/its_Xyron",
        "welcome_message": "",
        "maintenance_mode": False,
        "maintenance_message": "🔧 Bot is under maintenance. Please try again later.",
        "force_join_enabled": False,
        "force_join_channels": [],
    },
    "banned_users": [],
    "extra_admins": [],
    "lookup_stats": {},
    "total_lookups": 0,
}

def _try_mongo():
    global _mongo_ok, _col
    try:
        from config import MONGO_URI
        if not MONGO_URI or MONGO_URI == "mongodb://localhost:27017":
            return
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        db = client["xyron_info_bot"]
        _col = db["bot_data"]
        _mongo_ok = True
        print("💾 MongoDB connected!")
    except Exception as e:
        _mongo_ok = False
        _col = None
        print(f"⚠️ MongoDB unavailable, using JSON file. ({e})")

_try_mongo()


def _load_file():
    if os.path.exists(_FILE):
        try:
            with open(_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def _save_file(data):
    try:
        clean = {k: v for k, v in data.items() if k != "_id"}
        tmp = _FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(clean, f, ensure_ascii=False, indent=2)
        os.replace(tmp, _FILE)
    except Exception:
        pass


def load_data():
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < _TTL:
        return _cache["data"]

    doc = None
    if _mongo_ok and _col is not None:
        try:
            doc = _col.find_one({"_id": "main"})
        except Exception:
            pass

    if not doc:
        doc = _load_file()

    if not doc:
        doc = _DEFAULT.copy()
        doc["settings"] = _DEFAULT["settings"].copy()

    for key in _DEFAULT:
        if key not in doc:
            doc[key] = _DEFAULT[key] if not isinstance(_DEFAULT[key], dict) else _DEFAULT[key].copy()

    if "settings" in doc:
        for key in _DEFAULT["settings"]:
            if key not in doc["settings"]:
                doc["settings"][key] = _DEFAULT["settings"][key]

    _cache["data"] = doc
    _cache["ts"] = now
    return doc


def save_data(data):
    with _lock:
        _cache["data"] = None
        _cache["ts"] = 0

        clean = {k: v for k, v in data.items() if k != "_id"}

        _save_file(clean)

        if _mongo_ok and _col is not None:
            try:
                data["_id"] = "main"
                _col.replace_one({"_id": "main"}, data, upsert=True)
            except Exception:
                pass


def add_user(uid):
    uid = int(uid)
    with _lock:
        if _mongo_ok and _col is not None:
            try:
                _col.update_one({"_id": "main"}, {"$addToSet": {"users": uid}}, upsert=True)
            except Exception:
                pass

        data = load_data()
        users = data.setdefault("users", [])
        if uid not in users:
            users.append(uid)
            _save_file(data)

        _cache["data"] = None
        _cache["ts"] = 0


def increment_lookup(uid):
    uid_str = str(uid)
    with _lock:
        if _mongo_ok and _col is not None:
            try:
                _col.update_one(
                    {"_id": "main"},
                    {"$inc": {"total_lookups": 1, f"lookup_stats.{uid_str}": 1}},
                    upsert=True
                )
            except Exception:
                pass

        data = load_data()
        data["total_lookups"] = data.get("total_lookups", 0) + 1
        stats = data.setdefault("lookup_stats", {})
        stats[uid_str] = stats.get(uid_str, 0) + 1
        _save_file(data)

        _cache["data"] = None
        _cache["ts"] = 0


def is_banned(uid):
    return int(uid) in load_data().get("banned_users", [])


def is_admin(uid):
    from config import OWNER_ID
    uid = int(uid)
    if uid == OWNER_ID:
        return True
    return uid in load_data().get("extra_admins", [])


def is_owner(uid):
    from config import OWNER_ID
    return int(uid) == OWNER_ID


def get_stats():
    doc = load_data()
    return {
        "total_users": len(doc.get("users", [])),
        "total_lookups": doc.get("total_lookups", 0),
        "total_admins": len(doc.get("extra_admins", [])),
        "banned_users": len(doc.get("banned_users", [])),
    }
