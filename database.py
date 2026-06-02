import time
from pymongo import MongoClient
from config import OWNER_ID, MONGO_URI

_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
_db = _client["xyron_info_bot"]
_col = _db["bot_data"]

_cache = {"data": None, "ts": 0}
_TTL = 2

_DEFAULT = {
    "_id": "main",
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


def _init():
    doc = _col.find_one({"_id": "main"})
    if not doc:
        _col.insert_one(_DEFAULT.copy())
        return _DEFAULT.copy()
    return doc


def load_data():
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < _TTL:
        return _cache["data"]
    doc = _col.find_one({"_id": "main"})
    if not doc:
        doc = _init()
    for key in _DEFAULT:
        if key not in doc and key != "_id":
            doc[key] = _DEFAULT[key]
    _cache["data"] = doc
    _cache["ts"] = now
    return doc


def save_data(data):
    data["_id"] = "main"
    _col.replace_one({"_id": "main"}, data, upsert=True)
    _cache["data"] = None
    _cache["ts"] = 0


def add_user(uid):
    uid = int(uid)
    _col.update_one(
        {"_id": "main"},
        {"$addToSet": {"users": uid}},
        upsert=True
    )
    _cache["data"] = None
    _cache["ts"] = 0


def increment_lookup(uid):
    uid_str = str(uid)
    _col.update_one(
        {"_id": "main"},
        {"$inc": {"total_lookups": 1, f"lookup_stats.{uid_str}": 1}},
        upsert=True
    )
    _cache["data"] = None
    _cache["ts"] = 0


def is_banned(uid):
    doc = load_data()
    return int(uid) in doc.get("banned_users", [])


def is_admin(uid):
    uid = int(uid)
    if uid == OWNER_ID:
        return True
    doc = load_data()
    return uid in doc.get("extra_admins", [])


def is_owner(uid):
    return int(uid) == OWNER_ID


def get_stats():
    doc = load_data()
    return {
        "total_users": len(doc.get("users", [])),
        "total_lookups": doc.get("total_lookups", 0),
        "total_admins": len(doc.get("extra_admins", [])),
        "banned_users": len(doc.get("banned_users", [])),
    }
