from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

_orig_inline = InlineKeyboardButton.to_dict
def _patched_inline(self):
    d = _orig_inline(self)
    if hasattr(self, "style"):
        d["style"] = self.style
    if hasattr(self, "_copy_text") and self._copy_text:
        d["copy_text"] = {"text": str(self._copy_text)}
        d.pop("callback_data", None)
    return d
InlineKeyboardButton.to_dict = _patched_inline

_orig_kb = KeyboardButton.to_dict
def _patched_kb(self):
    d = _orig_kb(self)
    if hasattr(self, "style"):
        d["style"] = self.style
    return d
KeyboardButton.to_dict = _patched_kb

def ibtn(text, callback_data=None, url=None, style=None, copy_text=None):
    kw = {"text": text}
    if copy_text:
        kw["callback_data"] = "noop"
    elif callback_data:
        kw["callback_data"] = callback_data
    if url:
        kw["url"] = url
    btn = InlineKeyboardButton(**kw)
    if style:
        btn.style = style
    if copy_text:
        btn._copy_text = copy_text
    return btn

def rbtn(text, style=None):
    btn = KeyboardButton(text=text)
    if style:
        btn.style = style
    return btn
