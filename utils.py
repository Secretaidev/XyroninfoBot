import html as _html, re, base64, struct, time
from config import bot

menu_msg = {}

DC_MAP = {
    1: "MIA, Miami 🇺🇸", 2: "AMS, Amsterdam 🇳🇱", 3: "MIA, Miami 🇺🇸",
    4: "AMS, Amsterdam 🇳🇱", 5: "SIN, Singapore 🇸🇬",
}

LANG_MAP = {
    "en": "English 🇬🇧", "hi": "Hindi 🇮🇳", "ru": "Russian 🇷🇺", "ar": "Arabic 🇸🇦",
    "es": "Spanish 🇪🇸", "fr": "French 🇫🇷", "de": "German 🇩🇪", "it": "Italian 🇮🇹",
    "pt": "Portuguese 🇵🇹", "pt-br": "Portuguese 🇧🇷", "ja": "Japanese 🇯🇵",
    "ko": "Korean 🇰🇷", "zh": "Chinese 🇨🇳", "tr": "Turkish 🇹🇷", "uk": "Ukrainian 🇺🇦",
    "id": "Indonesian 🇮🇩", "ms": "Malay 🇲🇾", "th": "Thai 🇹🇭", "vi": "Vietnamese 🇻🇳",
    "pl": "Polish 🇵🇱", "nl": "Dutch 🇳🇱", "fa": "Persian 🇮🇷", "uz": "Uzbek 🇺🇿",
    "bn": "Bengali 🇧🇩", "ta": "Tamil 🇮🇳", "te": "Telugu 🇮🇳", "mr": "Marathi 🇮🇳",
    "gu": "Gujarati 🇮🇳", "kn": "Kannada 🇮🇳", "ml": "Malayalam 🇮🇳", "pa": "Punjabi 🇮🇳",
    "ur": "Urdu 🇵🇰", "sv": "Swedish 🇸🇪", "fi": "Finnish 🇫🇮", "da": "Danish 🇩🇰",
    "nb": "Norwegian 🇳🇴", "el": "Greek 🇬🇷", "cs": "Czech 🇨🇿", "ro": "Romanian 🇷🇴",
    "hu": "Hungarian 🇭🇺", "he": "Hebrew 🇮🇱", "bg": "Bulgarian 🇧🇬", "sk": "Slovak 🇸🇰",
    "hr": "Croatian 🇭🇷", "sr": "Serbian 🇷🇸", "ca": "Catalan 🇪🇸", "et": "Estonian 🇪🇪",
    "lv": "Latvian 🇱🇻", "lt": "Lithuanian 🇱🇹", "sl": "Slovenian 🇸🇮",
}

def _strip_tg(text):
    text = re.sub(r'<tg-emoji[^>]*>', '', str(text))
    return re.sub(r'</tg-emoji>', '', text)

def safe_send(cid, text, markup=None, reply_to=None):
    try:
        msg = bot.send_message(cid, _strip_tg(text), parse_mode="HTML", reply_markup=markup,
                               reply_to_message_id=reply_to, disable_web_page_preview=True)
        if msg:
            menu_msg[cid] = msg.message_id
        return msg
    except Exception:
        return None

def safe_edit(cid, text, markup=None, message_id=None):
    mid = message_id or menu_msg.get(cid)
    if mid:
        try:
            return bot.edit_message_text(_strip_tg(text), chat_id=cid, message_id=mid,
                                        parse_mode="HTML", reply_markup=markup,
                                        disable_web_page_preview=True)
        except Exception as e:
            if "not modified" in str(e).lower():
                return None
    return safe_send(cid, text, markup)

def get_dc(file_id):
    try:
        pad = 4 - len(file_id) % 4
        if pad != 4:
            file_id += "=" * pad
        raw = base64.urlsafe_b64decode(file_id)
        if len(raw) >= 8:
            dc = struct.unpack_from('<i', raw, 4)[0]
            if 1 <= dc <= 5:
                return dc, DC_MAP.get(dc, f"DC{dc}")
        for off in (0, 1):
            if len(raw) > off and 1 <= raw[off] <= 5:
                return raw[off], DC_MAP.get(raw[off], f"DC{raw[off]}")
    except Exception:
        pass
    return None, "Unknown"

def esc(text):
    return _html.escape(str(text)) if text else "N/A"

def plink(uid, name="Link"):
    return f"<a href='tg://user?id={uid}'>{esc(name)}</a>"

def lang_name(code):
    if not code:
        return "—"
    return LANG_MAP.get(code.lower(), code.upper())

def ch_username(url):
    if not url:
        return ""
    if str(url).startswith("@"):
        return str(url).lstrip("@")
    if "t.me/" in str(url):
        part = str(url).split("t.me/")[-1].split("/")[0].split("?")[0]
        return part.lstrip("@")
    return ""

def get_wm():
    from database import load_data
    return load_data()["settings"].get("watermark", "Xyron Info")

def get_support():
    from database import load_data
    return load_data()["settings"].get("support_link", "https://t.me/its_Xyron")

def del_msg(cid, mid):
    try:
        bot.delete_message(cid, mid)
    except Exception:
        pass

def del_prev(cid):
    mid = menu_msg.pop(cid, None)
    if mid:
        del_msg(cid, mid)

def fmt_num(n):
    try:
        return f"{int(n):,}"
    except Exception:
        return str(n)

def ping_ms():
    start = time.time()
    try:
        bot.get_me()
    except Exception:
        pass
    return round((time.time() - start) * 1000)
