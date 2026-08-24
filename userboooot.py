#BY tonyxGOD 
#TG @TEAM_tony
# ────────────────────────────────────────────────
#     ▄︻デ 𝒮𝒯𝒜𝒩𝒟𝒜𝑅𝒟 𝐿𝐼𝐵 ═━一
# ────────────────────────────────────────────────
import asyncio
import os
import time
import json
import random
import logging
import traceback
import re
from typing import Dict, Set, Optional
from io import BytesIO

# ────────────────────────────────────────────────
#      ▄︻デ 𝒯𝐻𝐼𝑅𝒟 𝒫𝒜𝑅𝒯𝒴 ═━一
# ────────────────────────────────────────────────
import requests
import qrcode
from gtts import gTTS
import yt_dlp

# ────────────────────────────────────────────────
#     ▄︻デ 𝒯𝐸𝐿𝐸𝒯𝐻𝒪𝒩 ═━一
# ────────────────────────────────────────────────
from telethon import TelegramClient, events, functions, types
from telethon.errors import FloodWaitError, RPCError

# ────────────────────────────────────────────────
# ▄︻デ 𝐵𝒜𝒮𝐼𝒞 𝒫𝒜𝒯𝐻 𝒮𝐸𝒯𝒰𝒫 ═━一
# ────────────────────────────────────────────────
BASE_DIR = os.getcwd()

DOWNLOAD_PATH = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

TEMP_PATH = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_PATH, exist_ok=True)

# ────────────────────────────────────────────────
#    ▄︻デ 𝒰𝒮𝐸𝑅𝐵𝒪𝒯 𝒞𝒪𝒩𝐹𝐼𝒢 ═━一
# ────────────────────────────────────────────────
API_ID = 34846638
API_HASH = "47e4d3cf24bcbe6c79af2a5fdc62b281"

OWNER_ID =8996032103
SESSION = "tony_userbot"

bot = TelegramClient(
    SESSION,
    API_ID,
    API_HASH,
    auto_reconnect=True,
    connection_retries=10,
    retry_delay=3
)

# ────────────────────────────────────────────────
#        ꧁❀ 𝘚𝘛𝘖𝘙𝘈𝘎𝘌 𝘍𝘐𝘓𝘌𝘚 ❀꧂
# ────────────────────────────────────────────────
ADMINS_FILE = "admins.json"
NOTES_FILE = "notes.json"
BANNER_FILE = "banner_msg_id.txt"
SPAM_TEXTS_FILE = "spam_texts.json"

# ────────────────────────────────────────────────
#    ꧁❀𝘊𝘓𝘖𝘕𝘌 𝘌𝘕𝘎𝘐𝘕𝘌 𝘚𝘛𝘈𝘛𝘌❀꧂
# ────────────────────────────────────────────────
CLONE_ACTIVE: bool = False
LAST_CLONE_ID: Optional[int] = None

CLONE_DATA: Dict[str, Optional[object]] = {
    "name": None,
    "username": None,
    "bio": None,
    "photo_bytes": None,
}

# ────────────────────────────────────────────────
#       ꧁❀ 𝘙𝘜𝘕𝘛𝘐𝘔𝘌 𝘚𝘛𝘈𝘛𝘌 ❀꧂
# ────────────────────────────────────────────────
admins: Set[int] = set()
notes: Dict[int, str] = {}

menu_banner_msg: Optional[tuple] = None
auto_react_emoji: Optional[str] = None

muted_users: Set[int] = set()
global_muted: Set[int] = set()

reply_users: Set[int] = set()
rr_users: Set[int] = set()
flag_users: Set[int] = set()
hrr_users: Set[int] = set()
replygod_users: Set[int] = set()

replytony_users: Dict[int, Dict[str, object]] = {}

spray_tasks: Dict[int, asyncio.Task] = {}
spam_texts: list = []

# watchspam: { (chat_id, user_id): {"limit": int, "seconds": float, "times": [timestamps]} }
watch_spam: Dict[tuple, Dict] = {}

# antidel: cache own messages to resend if deleted
antidel_enabled: bool = False
antidel_cache: Dict[int, Dict] = {}   # msg_id -> {chat_id, text, time}

group_locks: Set[int] = set()

START_TIME = time.time()

SPRAY_DELAY = 0.5

# ────────────────────────────────────────────────
#     ꧁✧ 𝘉𝘖𝘛 𝘈𝘋𝘋 𝘌𝘕𝘎𝘐𝘕𝘌 ࿐
# ────────────────────────────────────────────────
ADD_BOTS_LIST = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10"
    "11",
]

# ────────────────────────────────────────────────
#  ꧁❀ 𝘍𝘈𝘚𝘛𝘎𝘊 𝘌𝘕𝘎𝘐𝘕𝘌 𝘚𝘛𝘈𝘛𝘌 ❀꧂
# ────────────────────────────────────────────────
FASTGC_STATE: Dict[str, Optional[object]] = {
    "active": False,
    "template": None,
    "task": None,
    "chat_id": None,
}

GC_FAST_INTERVAL = 1

GC_FAST_EMOJIS = [
    "❤️","🧡","💛","💚","💙","💜",
    "🖤","🤍","🤎","🩷","🩵","🩶",
    "💖","💘","💝","💗","💓","💞",
    "💕","💟","❣️","❤️‍🔥","❤️‍🩹"
]

# ────────────────────────────────────────────────
#        ▄︻デ 𝐻𝐸𝐿𝒫𝐸𝑅𝒮 ═━一
# ────────────────────────────────────────────────
# ================= ADMIN STORAGE =================

def load_admins():
    global admins
    try:
        if not os.path.isfile(ADMINS_FILE):
            admins = set()
            return

        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        clean = set()

        if isinstance(data, list):
            for x in data:
                try:
                    clean.add(int(x))
                except:
                    continue

        admins = clean

    except Exception as e:
        print(f"[LOAD ADMINS ERROR] {str(e)[:80]}")
        admins = set()


def save_admins():
    try:
        tmp = sorted(set(int(x) for x in admins))
        with open(ADMINS_FILE, "w", encoding="utf-8") as f:
            json.dump(tmp, f, indent=2)
    except Exception as e:
        print(f"[SAVE ADMINS ERROR] {str(e)[:80]}")


def is_admin(uid: int) -> bool:
    if not uid:
        return False
    return uid == OWNER_ID or uid in admins


# ================= SAFE EDIT =================

async def safe_edit(event, text: str):

    if not text:
        return

    try:
        return await event.edit(text)

    except Exception:

        try:
            msg = await event.reply(text)
        except:
            return

        try:
            if event.out:
                await event.delete()
        except:
            pass

        return msg


# ================= NOTES STORAGE =================

def load_notes():
    global notes
    try:
        if not os.path.isfile(NOTES_FILE):
            notes = {}
            return

        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)

        clean = {}

        if isinstance(raw, dict):
            for k, v in raw.items():
                try:
                    clean[int(k)] = str(v)
                except:
                    continue

        notes = clean

    except Exception as e:
        print(f"[LOAD NOTES ERROR] {str(e)[:80]}")
        notes = {}


def save_notes():
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[SAVE NOTES ERROR] {str(e)[:80]}")


# ================= MENU BANNER STORAGE =================

def load_banner():
    global menu_banner_msg
    try:
        if not os.path.isfile(BANNER_FILE):
            menu_banner_msg = None
            return

        with open(BANNER_FILE, "r", encoding="utf-8") as f:
            raw = f.read().strip()

        if ":" not in raw:
            menu_banner_msg = None
            return

        chat, msg = raw.split(":", 1)

        menu_banner_msg = (int(chat), int(msg))

    except Exception as e:
        print(f"[LOAD BANNER ERROR] {str(e)[:80]}")
        menu_banner_msg = None


def save_banner():
    try:
        if not menu_banner_msg:
            if os.path.isfile(BANNER_FILE):
                os.remove(BANNER_FILE)
            return

        with open(BANNER_FILE, "w", encoding="utf-8") as f:
            f.write(f"{menu_banner_msg[0]}:{menu_banner_msg[1]}")

    except Exception as e:
        print(f"[SAVE BANNER ERROR] {str(e)[:80]}")


# ───── UNIVERSAL TARGET RESOLVER ─────
async def get_targets(event, arg: str = "") -> Set[int]:

    targets: Set[int] = set()

    # ⭐ reply resolver
    if event.is_reply:
        try:
            reply = await event.get_reply_message()
            if reply and reply.sender_id:
                targets.add(int(reply.sender_id))
        except:
            pass

    # ⭐ argument resolver
    if arg:
        for part in arg.strip().split():

            if not part:
                continue

            if part.isdigit():
                try:
                    targets.add(int(part))
                    continue
                except:
                    pass

            try:
                ent = await bot.get_entity(part)
                if ent and getattr(ent, "id", None):
                    targets.add(int(ent.id))
            except:
                pass

    # ⭐ self protection
    try:
        me = await bot.get_me()
        targets.discard(me.id)
    except:
        pass

    return targets


# ================= SPAM TEXTS STORAGE =================

def load_spam_texts():
    global spam_texts
    try:
        if not os.path.isfile(SPAM_TEXTS_FILE):
            spam_texts = []
            return
        with open(SPAM_TEXTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        spam_texts = [str(x) for x in data] if isinstance(data, list) else []
    except Exception as e:
        print(f"[LOAD SPAM TEXTS ERROR] {str(e)[:80]}")
        spam_texts = []


def save_spam_texts():
    try:
        with open(SPAM_TEXTS_FILE, "w", encoding="utf-8") as f:
            json.dump(spam_texts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[SAVE SPAM TEXTS ERROR] {str(e)[:80]}")


# ⭐ INITIAL LOAD
load_admins()
load_notes()
load_banner()
load_spam_texts()
# ────────────────────────────────────────────────
#                   TEXT LISTS (Unchanged)
# ────────────────────────────────────────────────
reply_list = ["𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ ",
    "𝚃𝙴𝚁𝙸 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ 𝚃𝙾𝙽𝚈 ! 🌙",
    "acha beta 😂🔥👊🏻 koi na me toh TUJHE Choduga 😹💔🔥😆👊🏻💥",
    "chudke bhaga kaise 😂💥🤣🤘🏻",
    "ne toh 𝚃𝙾𝙽𝚈 ka lun muh me lelia 😂🙏🏻😂🙏🏻",
    "try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
    "mkl lun te vaj 😂✊🏻💦",
    "𝗧ᴍᴋ𝗕 pe 𝚃𝙾𝙽𝚈 ka hamla 😂⚔🔥💥",
    "𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
    "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
    "chl rndyce chud ke dikha 😂💥🤣🔥",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
    "tera baap bass 𝚃𝙾𝙽𝚈 hai 😂🎀",
    " try maa hagte hue paad mari -#😹🔥🥀",
    "  𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ 𝚃𝙾𝙽𝚈 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜","𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ 𝚃𝙾𝙽𝚈 𝐒ᴇ - 🦢💘",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ 𝚃𝙾𝙽𝚈 ! 🌙",
    "acha beta 😂🔥👊🏻 koi na me toh TUJHE Choduga 😹💔🔥😆👊🏻💥",
    "chudke bhaga kaise 😂💥🤣🤘🏻",
    "ne toh 𝚃𝙾𝙽𝚈 ka lun muh me lelia 😂🙏🏻😂🙏🏻",
    "try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
    "mkl lun te vaj 😂✊🏻💦",
    "𝗧ᴍᴋ𝗕 pe 𝚃𝙾𝙽𝚈 ka hamla 😂⚔🔥💥",
    "𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
    "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
    "chl rndyce chud ke dikha 😂💥🤣🔥",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
    "tera baap bass 𝚃𝙾𝙽𝚈 hai 😂🎀",
    " T 𝒦𝐼 𝑀𝒜𝒜 𝐵𝐻𝐸𝒩 𝒦♡ 𝑅𝒜𝒩𝒟𝐼 𝐵𝒜𝒩𝒜 𝒦𝒜  𝒞𝐻♡𝒟𝒰𝒰😹🥀",
    "  𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ 𝚃𝙾𝙽𝚈 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜"]

reply_texts = ["⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝚃𝙾𝙽𝚈 बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝚃𝙾𝙽𝚈 बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को 𝚃𝙾𝙽𝚈 बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? SAAS aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝚃𝙾𝙽𝚈 /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝚃𝙾𝙽𝚈 बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SHAMBHOG करती है ! 🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝚃𝙾𝙽𝚈 बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝚃𝙾𝙽𝚈 बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को 𝚃𝙾𝙽𝚈 बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Saas aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝚃𝙾𝙽𝚈 /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝚃𝙾𝙽𝚈 बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝚃𝙾𝙽𝚈 बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝚃𝙾𝙽𝚈 बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को 𝚃𝙾𝙽𝚈 बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? saas aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝚃𝙾𝙽𝚈 /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝚃𝙾𝙽𝚈 बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝚃𝙾𝙽𝚈 बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝚃𝙾𝙽𝚈 बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को 𝚃𝙾𝙽𝚈 बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? SAAS aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝚃𝙾𝙽𝚈 /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝚃𝙾𝙽𝚈 बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐"]

fun_texts = ["तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭","तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭","तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭","तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭" ]

flag_texts = [" ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚",
" ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆. " ,
" ₊⁺🇺🇸 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇺🇸 ₊⁺⋆.˚",
" ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.˚", 
" ོ༘₊⁺🇰🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚",
" ོ༘₊⁺🇫🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐅ʀᴀɴᴄᴇ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇫🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇮🇹 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ᴛᴀʟʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇹 ₊⁺⋆.˚",
" ོ༘₊⁺🇧🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐁ʀᴀᴢɪʟ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇧🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇨🇦 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐂ᴀɴᴀᴅᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇨🇦 ₊⁺⋆.˚"," ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚",
" ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆. " ,
" ₊⁺🇺🇸 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇺🇸 ₊⁺⋆.˚",
" ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.˚", 
" ོ༘₊⁺🇰🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚",
" ོ༘₊⁺🇫🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐅ʀᴀɴᴄᴇ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇫🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇮🇹 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ᴛᴀʟʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇹 ₊⁺⋆.˚",
" ོ༘₊⁺🇧🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐁ʀᴀᴢɪʟ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇧🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇨🇦 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝚃𝙾𝙽𝚈 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐂ᴀɴᴀᴅᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇨🇦 ₊⁺⋆.˚"]

heart_replies = ["𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💛 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💚 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💙 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💜͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💜 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🖤͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🖤 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🤍͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🤍 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🤎͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🤎 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💖͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💖 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💗͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💗 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💓͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💓 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💞͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💞 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💕͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💕 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💘͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💘 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💝͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💝 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💟͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💟 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❣️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❣️ ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❤️‍🔥͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❤️‍🔥 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❤️‍🩹͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❤️‍🩹 ݁˖⭑.ᐟ","𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💛 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💚 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💙 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💜͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💜 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🖤͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🖤 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🤍͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🤍 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🤎͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🤎 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💖͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💖 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💗͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💗 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💓͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💓 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💞͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💞 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💕͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💕 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💘͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💘 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💝͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💝 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💟͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💟 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❣️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❣️ ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❤️‍🔥͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❤️‍🔥 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❤️‍🩹͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❤️‍🩹 ݁˖⭑.ᐟ"]

# ────────────────────────────────────────────────
#                   DECORATOR
# ────────────────────────────────────────────────
# ================= COMMAND REGISTRY =================

commands = {}

def register_cmd(name: str, needs_reply: bool = False, group_only: bool = False):

    def decorator(func):

        key = (name or "").lower().strip()

        if not key:
            raise ValueError("Command name cannot be empty")

        if key in commands:
            raise ValueError(f"Duplicate command registered: {key}")

        commands[key] = {
            "func": func,
            "needs_reply": bool(needs_reply),
            "group_only": bool(group_only),
        }

        return func

    return decorator


# ================= FASTGC ENGINE =================

async def fast_title_edit(chat_id, title):

    safe_title = (title or "").strip()[:255]

    if not safe_title:
        return False

    try:
        await bot(functions.channels.EditTitleRequest(
            channel=chat_id,
            title=safe_title
        ))
        return True

    except Exception:

        try:
            await bot(functions.messages.EditChatTitleRequest(
                chat_id=chat_id,
                title=safe_title
            ))
            return True

        except Exception as e:
            print(f"[FastGC] Title edit failed → {str(e)[:80]}")
            return False


async def gc_fast_loop(chat_id):

    try:

        while True:

            # ⭐ state validation
            if not FASTGC_STATE.get("active"):
                break

            template = FASTGC_STATE.get("template")
            if not template:
                break

            try:
                emoji = random.choice(GC_FAST_EMOJIS)
            except:
                emoji = "⚡"

            try:
                new_title = template.replace("{emoji}", emoji)
            except:
                await asyncio.sleep(2)
                continue

            ok = await fast_title_edit(chat_id, new_title)

            # ⭐ adaptive delay engine
            try:
                if ok:
                    await asyncio.sleep(max(1, GC_FAST_INTERVAL))
                else:
                    await asyncio.sleep(5)
            except:
                await asyncio.sleep(3)

    except asyncio.CancelledError:
        # ⭐ silent cancel safe
        return

    except Exception as e:
        print(f"[FastGC Loop Crash] → {str(e)[:80]}")

# ────────────────────────────────────────────────
#                   MENU (STYLISH) - UNCHANGED
# ────────────────────────────────────────────────
@register_cmd("menu")
async def cmd_menu(event, _):
    global menu_banner_msg
    menu = (
"╔══❰ ⚡ 𝐓𝐎𝐍𝐘𝐱𝐆𝐎𝐃 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 ⚡ ❱══╗\n"
"║                                    ║\n"
"║   👑 𝐎ᴡɴᴇʀ  :  𝐓𝐎𝐍𝐘𝐱𝐆𝐎𝐃        ║\n"
"║   📦 𝐂ᴏᴍᴍᴀɴᴅs :  50+              ║\n"
"║   🔥 𝐏ʀᴇғɪx  :  . (𝐃ᴏᴛ)           ║\n"
"║                                    ║\n"
"╠══❰ 📖 𝐌𝐄𝐍𝐔 𝐏𝐀𝐆𝐄𝐒 ❱══╣\n"
"║                                    ║\n"
"║  .menu1  ➜  👑 𝐀ᴅᴍɪɴ              ║\n"
"║             🔇 𝐌ᴜᴛᴇ & 𝐆ʀᴏᴜᴘ        ║\n"
"║                                    ║\n"
"║  .menu2  ➜  ⚔️ 𝐑ᴀɪᴅ 𝐄ɴɢɪɴᴇ        ║\n"
"║                                    ║\n"
"║  .menu3  ➜  💣 𝐒ᴘᴀᴍ 𝐄ɴɢɪɴᴇ        ║\n"
"║             📝 𝐓ᴇxᴛ 𝐌ᴀɴᴀɢᴇʀ        ║\n"
"║                                    ║\n"
"║  .menu4  ➜  🛡️ 𝐏ʀᴏᴛᴇᴄᴛɪᴏɴ         ║\n"
"║             🖼️ 𝐆ʀᴏᴜᴘ 𝐏𝐅𝐏           ║\n"
"║             ❤️ 𝐀ᴜᴛᴏ 𝐒ʏsᴛᴇᴍ          ║\n"
"║                                    ║\n"
"║  .menu5  ➜  🛠️ 𝐓ᴏᴏʟs              ║\n"
"║             🎵 𝐌ᴜsɪᴄ               ║\n"
"║             🧠 𝐍ᴏᴛᴇs               ║\n"
"║             🎮 𝐅ᴜɴ                 ║\n"
"║             👤 𝐏ʀᴏғɪʟᴇ              ║\n"
"║             🖼️ 𝐁ᴀɴɴᴇʀ              ║\n"
"║                                    ║\n"
"╚════════════════════════════════════╝\n"
"    🔥 𝐏ᴏᴡᴇʀᴇᴅ ʙʏ 𝐓𝐎𝐍𝐘𝐱𝐆𝐎𝐃 🔥"
    )
    await safe_edit(event, menu)
    if menu_banner_msg:
        chat_id, msg_id = menu_banner_msg
        try:
            msg = await bot.get_messages(chat_id, ids=msg_id)
            await bot.send_file(
                event.chat_id,
                file=msg.media,
                caption="⚡ 𝐓𝐎𝐍𝐘𝐱𝐆𝐎𝐃 𝐄ɴᴛᴇʀs ❤️‍🔥"
            )
        except:
            pass


@register_cmd("menu1")
async def cmd_menu1(event, _):
    menu = (
"╔══❰ 👑 𝐀𝐃𝐌𝐈𝐍 & 🔇 𝐌𝐔𝐓𝐄 & 🧹 𝐆𝐑𝐎𝐔𝐏 ❱══╗\n"
"\n"
"┌─❰ 👑 𝐀𝐃𝐌𝐈𝐍 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ❱\n"
"│\n"
"│ ➤ .admins\n"
"│    └ Saare admins ki list dekho\n"
"│\n"
"│ ➤ .addadmin @user / reply\n"
"│    └ Kisi ko admin banao\n"
"│\n"
"│ ➤ .deladmin @user / reply\n"
"│    └ Admin se hatao\n"
"│\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 🔇 𝐌𝐔𝐓𝐄 & 𝐑𝐄𝐒𝐓𝐑𝐈𝐂𝐓 ❱\n"
"│\n"
"│ ➤ .mute @user     → Local mute\n"
"│ ➤ .unmute @user   → Local unmute\n"
"│ ➤ .gmute @user    → Global mute\n"
"│ ➤ .gunmute @user  → Global unmute\n"
"│ ➤ .mutelist       → Mute status dekho\n"
"│\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 🧹 𝐆𝐑𝐎𝐔𝐏 𝐌𝐎𝐃 ❱\n"
"│\n"
"│ ➤ .lock           → Group messages band\n"
"│ ➤ .unlock         → Group messages kholo\n"
"│ ➤ .purge <count>  → Itne msgs delete karo\n"
"│ ➤ .throw @user    → User ko kick karo\n"
"│ ➤ .addbots <n>    → Bots add karo\n"
"│\n"
"└─────────────────────────\n"
"\n"
"📌 .menu → Main menu"
    )
    await safe_edit(event, menu)


@register_cmd("menu2")
async def cmd_menu2(event, _):
    menu = (
"╔══❰ ⚔️ 𝐑𝐀𝐈𝐃 𝐄𝐍𝐆𝐈𝐍𝐄 ❱══╗\n"
"\n"
"┌─❰ 💬 𝐑𝐄𝐏𝐋𝐘 𝐑𝐀𝐈𝐃 ❱\n"
"│ ➤ .reply @user   → Reply raid shuru\n"
"│ ➤ .sreply @user  → Reply raid band\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 🤣 𝐑𝐑 𝐑𝐀𝐈𝐃 ❱\n"
"│ ➤ .rr @user      → RR + React raid\n"
"│ ➤ .srr @user     → RR raid band\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 🚩 𝐅𝐋𝐀𝐆 𝐑𝐀𝐈𝐃 ❱\n"
"│ ➤ .flag @user    → Flag raid shuru\n"
"│ ➤ .sflag @user   → Flag raid band\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 💗 𝐇𝐄𝐀𝐑𝐓 𝐑𝐀𝐈𝐃 ❱\n"
"│ ➤ .hrr @user     → Heart raid shuru\n"
"│ ➤ .shrr @user    → Heart raid band\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 😈 𝐆𝐎𝐃 𝐑𝐀𝐈𝐃 ❱\n"
"│ ➤ .replygod @user  → God raid shuru\n"
"│ ➤ .sgod @user      → God raid band\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 🎯 𝐋𝐈𝐌𝐈𝐓 𝐑𝐀𝐈𝐃 ❱\n"
"│ ➤ .replytony <text> <count>\n"
"│    └ Exactly N baar reply karo\n"
"│ ➤ .sstop @user  → Band karo\n"
"└─────────────────────────\n"
"\n"
"📌 .menu → Main menu"
    )
    await safe_edit(event, menu)


@register_cmd("menu3")
async def cmd_menu3(event, _):
    menu = (
"╔══❰ 💣 𝐒𝐏𝐀𝐌 𝐄𝐍𝐆𝐈𝐍𝐄 & 📝 𝐓𝐄𝐗𝐓 𝐌𝐀𝐍𝐀𝐆𝐄𝐑 ❱══╗\n"
"\n"
"┌─❰ 💣 𝐒𝐏𝐀𝐌 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ❱\n"
"│\n"
"│ ➤ .spray <text>       → Nonstop spam shuru\n"
"│ ➤ .dspray             → Koi bhi spam band\n"
"│ ➤ .tspray <num>       → Saved text se spam\n"
"│ ➤ .rspray             → Random text spam\n"
"│ ➤ .multispray         → Saare texts rotate\n"
"│ ➤ .countspray <n> <text>\n"
"│    └ Exactly N baar spam → auto stop\n"
"│ ➤ .spraydelay <sec>   → Speed change karo\n"
"│    └ Ex: .spraydelay 0.3\n"
"│\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 📝 𝐓𝐄𝐗𝐓 𝐌𝐀𝐍𝐀𝐆𝐄𝐑 ❱\n"
"│\n"
"│ ➤ .addtext <text>       → Text save karo\n"
"│ ➤ .listtexts            → Saare texts dekho\n"
"│ ➤ .edittext <num> <new> → Text edit karo\n"
"│ ➤ .deltext <num>        → Text delete karo\n"
"│ ➤ .cleartext confirm    → Saare clear karo\n"
"│\n"
"│ 💡 Workflow:\n"
"│   1. .addtext Tera baap aaya!\n"
"│   2. .addtext Kya re randi!\n"
"│   3. .listtexts  (check numbers)\n"
"│   4. .tspray 1  (slot 1 se spam)\n"
"│\n"
"└─────────────────────────\n"
"\n"
"┌─❰ ⚡ 𝐅𝐀𝐒𝐓 𝐆𝐂 ❱\n"
"│ ➤ .fastgc set {emoji} <template>\n"
"│    └ Ex: .fastgc set {emoji} God {emoji}\n"
"│ ➤ .fastgc stop  → Band karo\n"
"└─────────────────────────\n"
"\n"
"📌 .menu → Main menu"
    )
    await safe_edit(event, menu)


@register_cmd("menu4")
async def cmd_menu4(event, _):
    menu = (
"╔══❰ 🛡️ 𝐏𝐑𝐎𝐓𝐄𝐂𝐓𝐈𝐎𝐍 & 🖼️ 𝐆𝐑𝐎𝐔𝐏 𝐏𝐅𝐏 & ❤️ 𝐀𝐔𝐓𝐎 ❱══╗\n"
"\n"
"┌─❰ 🛡️ 𝐀𝐍𝐓𝐈-𝐃𝐄𝐋𝐄𝐓𝐄 ❱\n"
"│\n"
"│ ➤ .antidel on    → Protect shuru\n"
"│    └ Koi tumhara msg delete kare\n"
"│      → Bot turant wapas bhej dega!\n"
"│ ➤ .antidel off   → Band karo\n"
"│ ➤ .antidel       → Status dekho\n"
"│\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 👁️ 𝐖𝐀𝐓𝐂𝐇𝐒𝐏𝐀𝐌 ❱\n"
"│\n"
"│ ➤ .watchspam @user <limit> <sec>\n"
"│    └ Ex: .watchspam @ritik 3 5\n"
"│      → 5 sec mein 3+ msg → delete!\n"
"│ ➤ .unwatchspam @user  → Hatao\n"
"│ ➤ .unwatchspam        → Sabko hatao\n"
"│ ➤ .watchlist          → Active list\n"
"│\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 🖼️ 𝐆𝐑𝐎𝐔𝐏 𝐏𝐅𝐏 𝐂𝐇𝐀𝐍𝐆𝐄𝐑 ❱\n"
"│\n"
"│ ➤ .setgpfp       → Image reply → PFP set\n"
"│ ➤ .addgpfp       → Image pool mein add\n"
"│ ➤ .listgpfp      → Pool dekho\n"
"│ ➤ .autogpfp <sec> → Auto rotate\n"
"│    └ Ex: .autogpfp 30\n"
"│ ➤ .stopgpfp      → Rotation band\n"
"│\n"
"└─────────────────────────\n"
"\n"
"┌─❰ ❤️ 𝐀𝐔𝐓𝐎 𝐒𝐘𝐒𝐓𝐄𝐌 ❱\n"
"│\n"
"│ ➤ .ar <emoji>    → Apne msgs pe auto react\n"
"│    └ Ex: .ar ❤️\n"
"│ ➤ .sar           → Auto react band\n"
"│\n"
"└─────────────────────────\n"
"\n"
"📌 .menu → Main menu"
    )
    await safe_edit(event, menu)


@register_cmd("menu5")
async def cmd_menu5(event, _):
    menu = (
"╔══❰ 🛠️ 𝐓𝐎𝐎𝐋𝐒 & 🎵 𝐌𝐔𝐒𝐈𝐂 & 🎮 𝐅𝐔𝐍 ❱══╗\n"
"\n"
"┌─❰ 🛠️ 𝐓𝐎𝐎𝐋𝐒 ❱\n"
"│\n"
"│ ➤ .tts <text>      → Voice message banao\n"
"│ ➤ .qrcode <text>   → QR code banao\n"
"│ ➤ .fancy <text>    → Fancy style text\n"
"│ ➤ .style <text>    → Text format change\n"
"│ ➤ .emoji <text>    → Emoji style\n"
"│ ➤ .calc <expr>     → Calculator\n"
"│    └ Ex: .calc 5*9+2\n"
"│ ➤ .weather <city>  → Weather report\n"
"│    └ Ex: .weather Mumbai\n"
"│ ➤ .ip <ip>         → IP location\n"
"│ ➤ .short <url>     → URL short karo\n"
"│ ➤ .info @user      → User info dekho\n"
"│\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 🎵 𝐌𝐔𝐒𝐈𝐂 ❱\n"
"│\n"
"│ ➤ .music <song>    → Voice note bhejo\n"
"│    └ Ex: .music Kesariya\n"
"│ ➤ .dmusic <song>   → MP3 file download\n"
"│    └ 320kbps quality, save kar sako\n"
"│\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 🧠 𝐍𝐎𝐓𝐄𝐒 ❱\n"
"│\n"
"│ ➤ .notesadd <text>    → Note save karo\n"
"│ ➤ .noteslist          → Saare notes\n"
"│ ➤ .notesdelete <id>   → Note delete\n"
"│\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 🎮 𝐅𝐔𝐍 & 𝐒𝐓𝐀𝐓𝐔𝐒 ❱\n"
"│\n"
"│ ➤ .ping    → Latency check\n"
"│ ➤ .status  → Bot uptime & stats\n"
"│ ➤ .flip    → Coin flip\n"
"│ ➤ .dice    → Dice roll\n"
"│\n"
"└─────────────────────────\n"
"\n"
"┌─❰ 👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄 & 🖼️ 𝐁𝐀𝐍𝐍𝐄𝐑 ❱\n"
"│\n"
"│ ➤ .copy @user   → Kisi ka profile clone\n"
"│ ➤ .normal       → Apna profile wapas\n"
"│ ➤ .banner       → Image reply → menu banner\n"
"│ ➤ .rembanner    → Banner hatao\n"
"│\n"
"└─────────────────────────\n"
"\n"
"╔══════════════════════════════╗\n"
"║  🔥 𝐓𝐎𝐍𝐘𝐱𝐆𝐎𝐃 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 🔥  ║\n"
"╚══════════════════════════════╝"
    )
    await safe_edit(event, menu)


@register_cmd("cmds")
async def cmd_cmds(event, _):
    cmds = (
"⚡ 𝐓𝐎𝐍𝐘𝐱𝐆𝐎𝐃 — 𝐅𝐔𝐋𝐋 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 𝐋𝐈𝐒𝐓 ⚡\n"
"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
"\n"
"👑 𝐀𝐃𝐌𝐈𝐍\n"
"  .admins  .addadmin  .deladmin\n"
"\n"
"🔇 𝐌𝐔𝐓𝐄\n"
"  .mute  .unmute  .gmute  .gunmute  .mutelist\n"
"\n"
"🧹 𝐆𝐑𝐎𝐔𝐏 𝐌𝐎𝐃\n"
"  .lock  .unlock  .purge  .throw  .addbots\n"
"\n"
"⚔️ 𝐑𝐀𝐈𝐃 𝐄𝐍𝐆𝐈𝐍𝐄\n"
"  .reply    .sreply\n"
"  .rr       .srr\n"
"  .flag     .sflag\n"
"  .hrr      .shrr\n"
"  .replygod .sgod\n"
"  .replytony  .stony\n"
"\n"
"💣 𝐒𝐏𝐀𝐌\n"
"  .spray  .dspray  .tspray  .rspray\n"
"  .multispray  .countspray  .spraydelay\n"
"\n"
"📝 𝐓𝐄𝐗𝐓 𝐌𝐀𝐍𝐀𝐆𝐄𝐑\n"
"  .addtext  .listtexts  .edittext\n"
"  .deltext  .cleartext\n"
"\n"
"🛡️ 𝐏𝐑𝐎𝐓𝐄𝐂𝐓𝐈𝐎𝐍\n"
"  .antidel  .watchspam  .unwatchspam  .watchlist\n"
"\n"
"🖼️ 𝐆𝐑𝐎𝐔𝐏 𝐏𝐅𝐏\n"
"  .setgpfp  .addgpfp  .listgpfp\n"
"  .autogpfp  .stopgpfp\n"
"\n"
"❤️ 𝐀𝐔𝐓𝐎 𝐒𝐘𝐒𝐓𝐄𝐌\n"
"  .ar  .sar  .fastgc\n"
"\n"
"🛠️ 𝐓𝐎𝐎𝐋𝐒\n"
"  .tts  .qrcode  .fancy  .style  .emoji\n"
"  .calc  .weather  .ip  .short  .info\n"
"\n"
"🎵 𝐌𝐔𝐒𝐈𝐂\n"
"  .music  .dmusic\n"
"\n"
"🧠 𝐍𝐎𝐓𝐄𝐒\n"
"  .notesadd  .noteslist  .notesdelete\n"
"\n"
"🎮 𝐅𝐔𝐍\n"
"  .ping  .status  .flip  .dice\n"
"\n"
"👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄\n"
"  .copy  .normal\n"
"\n"
"🖼️ 𝐁𝐀𝐍𝐍𝐄𝐑\n"
"  .banner  .rembanner\n"
"\n"
"📖 𝐌𝐄𝐍𝐔\n"
"  .menu  .menu1  .menu2  .menu3  .menu4  .menu5\n"
"  .cmds  (this page)\n"
"\n"
"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
"🔥 𝐓𝐨𝐭𝐚𝐥: 54 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 | 𝐏𝐫𝐞𝐟𝐢𝐱: .\n"
"💡 Details: .menu1 to .menu5"
    )
    await safe_edit(event, cmds)


# ────────────────────────────────────────────────
#                   COMMANDS
# ────────────────────────────────────────────────

# Banner
@register_cmd("banner", needs_reply=True)
async def cmd_banner(event, _):
    global menu_banner_msg

    reply = await event.get_reply_message()

    # ─── MEDIA VALIDATION ENGINE ───
    if not reply:
        return await safe_edit(
            event,
            "❌ 𝐍ᴏ 𝐑ᴇᴘʟʏ\n👉 𝐑ᴇᴘʟʏ 𝐓ᴏ 𝐏ʜᴏᴛᴏ / 𝐕ɪᴅᴇᴏ"
        )

    if not reply.media:
        return await safe_edit(
            event,
            "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐌ᴇᴅɪᴀ\n👉 𝐎ɴʟʏ 𝐏ʜᴏᴛᴏ / 𝐕ɪᴅᴇᴏ"
        )

    await safe_edit(
        event,
        "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐁ᴀɴɴᴇʀ...\n━━━━━━━━━━━━━━━"
    )

    try:
        # ─── FORWARD TRY FIRST (FAST PATH) ───
        try:
            saved = await reply.forward_to("me")
        except Exception:
            # ⭐ FORWARD RESTRICTED FALLBACK
            file = await reply.download_media(file=bytes)
            if not file:
                return await safe_edit(event,
                    "❌ 𝐌ᴇᴅɪᴀ 𝐃ᴏᴡɴʟᴏᴀᴅ 𝐅ᴀɪʟ"
                )

            bio = BytesIO(file)
            bio.name = "banner"
            saved = await bot.send_file("me", bio)

        menu_banner_msg = (saved.chat_id, saved.id)
        save_banner()

        text = (
            "🖼️ 𝐁ᴀɴɴᴇʀ 𝐒ᴇᴛ\n"
            "━━━━━━━━━━━━━━━\n"
            f"📌 𝐒ᴀᴠᴇᴅ 𝐈ᴅ → `{saved.id}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except FloodWaitError as fw:
        await safe_edit(event,
            f"⏳ 𝐅ʟᴏᴏᴅ 𝐖ᴀɪᴛ → {fw.seconds}s"
        )

    except RPCError as e:
        await safe_edit(event,
            f"❌ 𝐓ɢ 𝐄ʀʀ → `{str(e)[:40]}`"
        )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐁ᴀɴɴᴇʀ 𝐄ʀʀ → `{str(e)[:50]}`"
        )


@register_cmd("rembanner")
async def cmd_rembanner(event, _):
    global menu_banner_msg

    if not menu_banner_msg:
        return await safe_edit(event,
            "⚠️ 𝐍ᴏ 𝐁ᴀɴɴᴇʀ 𝐒ᴇᴛ"
        )

    await safe_edit(
        event,
        "⚡ 𝐑ᴇᴍᴏᴠɪɴɢ 𝐁ᴀɴɴᴇʀ...\n━━━━━━━━━━━━━━━"
    )

    try:
        chat_id, msg_id = menu_banner_msg

        try:
            await bot.delete_messages(chat_id, [msg_id])
        except Exception:
            # ⭐ banner already manually deleted
            pass

        menu_banner_msg = None
        save_banner()

        text = (
            "🗑️ 𝐁ᴀɴɴᴇʀ 𝐑ᴇᴍᴏᴠᴇᴅ\n"
            "━━━━━━━━━━━━━━━"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except FloodWaitError as fw:
        await safe_edit(event,
            f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s"
        )

    except RPCError as e:
        await safe_edit(event,
            f"❌ 𝐓ɢ 𝐄ʀʀ → `{str(e)[:40]}`"
        )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐑ᴇᴍᴏᴠᴇ 𝐄ʀʀ → `{str(e)[:50]}`"
        )
        
# Admin Commands (Updated)
@register_cmd("addadmin", needs_reply=True)
async def cmd_addadmin(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ\n👉 𝐑ᴇᴘʟʏ / @username / ID"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅ...\n━━━━━━━━━━━━━━━"
        )

        added = []
        already = []
        skipped_owner = []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid == OWNER_ID:
                skipped_owner.append(str(uid))
                continue

            if uid in admins:
                already.append(str(uid))
            else:
                admins.add(uid)
                added.append(str(uid))

        try:
            save_admins()
        except Exception:
            pass

        parts = []

        if added:
            parts.append(
                f"✅ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅᴇᴅ → `{', '.join(added)}`"
            )

        if already:
            parts.append(
                f"⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴅᴍɪɴ → `{', '.join(already)}`"
            )

        if skipped_owner:
            parts.append(
                f"👑 𝐎ᴡɴᴇʀ 𝐒ᴋɪᴘᴘᴇᴅ → `{', '.join(skipped_owner)}`"
            )

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇs 𝐌ᴀᴅᴇ")

        text = "\n".join(parts)

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except FloodWaitError as fw:
        await safe_edit(event,
            f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s"
        )
    except RPCError as e:
        await safe_edit(event,
            f"❌ 𝐓ɢ 𝐄ʀʀ → `{str(e)[:40]}`"
        )
    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅ 𝐄ʀʀ → `{str(e)[:50]}`"
        )


@register_cmd("deladmin", needs_reply=True)
async def cmd_deladmin(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ\n👉 𝐑ᴇᴘʟʏ / @username / ID"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇ...\n━━━━━━━━━━━━━━━"
        )

        removed = []
        not_admin = []
        skipped_owner = []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid == OWNER_ID:
                skipped_owner.append(str(uid))
                continue

            if uid in admins:
                admins.remove(uid)
                removed.append(str(uid))
            else:
                not_admin.append(str(uid))

        try:
            save_admins()
        except Exception:
            pass

        parts = []

        if removed:
            parts.append(
                f"🗑️ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇᴅ → `{', '.join(removed)}`"
            )

        if not_admin:
            parts.append(
                f"⚠️ 𝐍ᴏᴛ 𝐀ᴅᴍɪɴ → `{', '.join(not_admin)}`"
            )

        if skipped_owner:
            parts.append(
                f"👑 𝐎ᴡɴᴇʀ 𝐏ʀᴏᴛᴇᴄᴛᴇᴅ → `{', '.join(skipped_owner)}`"
            )

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇs 𝐌ᴀᴅᴇ")

        text = "\n".join(parts)

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except FloodWaitError as fw:
        await safe_edit(event,
            f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s"
        )
    except RPCError as e:
        await safe_edit(event,
            f"❌ 𝐓ɢ 𝐄ʀʀ → `{str(e)[:40]}`"
        )
    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇ 𝐄ʀʀ → `{str(e)[:50]}`"
        )


@register_cmd("admins")
async def cmd_admins(event, _):
    try:
        await safe_edit(
            event,
            "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ...\n━━━━━━━━━━━━━━━"
        )

        if admins:
            admin_list = "\n".join(
                f"• `{a}`" for a in sorted(admins)
            )
        else:
            admin_list = "⚠️ 𝐍ᴏ 𝐄xᴛʀᴀ 𝐀ᴅᴍɪɴs"

        txt = (
            "👑 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ\n"
            "━━━━━━━━━━━━━━━\n"
            f"👑 𝐎ᴡɴᴇʀ → `{OWNER_ID}`\n\n"
            f"{admin_list}\n\n"
            f"📊 𝐓ᴏᴛᴀʟ → `{len(admins)}`"
        )

        await safe_edit(event, txt)

    except FloodWaitError as fw:
        await safe_edit(event,
            f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s"
        )
    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ 𝐄ʀʀ → `{str(e)[:50]}`"
        )

# Basic Commands (Unchanged)
@register_cmd("ping")
async def cmd_ping(event, _):
    try:
        t0 = time.perf_counter()

        # ─── MESSAGE DISPATCH SAFE ───
        try:
            if event.out:
                msg = await event.edit("🏓 𝐏ɪɴɢ...")
            else:
                msg = await event.reply("🏓 𝐏ɪɴɢ...")
        except:
            msg = None

        t1 = time.perf_counter()
        ms = round((t1 - t0) * 1000)

        # ─── RESPONSE EDIT SAFE ───
        try:
            if msg:
                await msg.edit(f"🏓 𝐏ᴏɴɢ → `{ms} ms`")
            else:
                await event.reply(f"🏓 𝐏ᴏɴɢ → `{ms} ms`")
        except:
            pass

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐏ɪɴɢ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("status")
async def cmd_status(event, _):
    try:
        now = time.time()

        # ─── START TIME CORRUPTION SAFE ───
        try:
            uptime = int(now - START_TIME)
            if uptime < 0:
                uptime = 0
        except:
            uptime = 0

        # ─── ADMIN STORAGE SAFE ───
        try:
            admin_count = len(admins)
        except:
            admin_count = 0

        txt = (
            "✅ 𝐔sᴇʀʙᴏᴛ 𝐒ᴛᴀᴛᴜs\n"
            "━━━━━━━━━━━━━━━\n"
            f"⏱️ 𝐔ᴘᴛɪᴍᴇ → `{uptime}s`\n"
            f"👑 𝐀ᴅᴍɪɴs → `{admin_count}`\n"
            f"⚙️ 𝐌ᴏᴅᴇ → `Operational`"
        )

        try:
            if event.out:
                await safe_edit(event, txt)
            else:
                await event.reply(txt)
        except:
            pass

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐒ᴛᴀᴛᴜs 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("flip")
async def cmd_flip(event, _):
    try:
        # ─── RANDOM SAFE ───
        try:
            result = random.choice(["🪙 𝐇ᴇᴀᴅs", "🪙 𝐓ᴀɪʟs"])
        except:
            result = "🪙 𝐇ᴇᴀᴅs"

        text = (
            "🎲 𝐂ᴏɪɴ 𝐅ʟɪᴘ\n"
            "━━━━━━━━━━━━━━━\n"
            f"👉 𝐑ᴇsᴜʟᴛ → {result}"
        )

        try:
            if event.out:
                await safe_edit(event, text)
            else:
                await event.reply(text)
        except:
            pass

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐅ʟɪᴘ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("dice")
async def cmd_dice(event, _):
    try:
        # ─── RANDOM SAFE ───
        try:
            num = random.randint(1, 6)
        except:
            num = 1

        text = (
            "🎲 𝐃ɪᴄᴇ 𝐑ᴏʟʟ\n"
            "━━━━━━━━━━━━━━━\n"
            f"👉 𝐑ᴇsᴜʟᴛ → `{num}`"
        )

        try:
            if event.out:
                await safe_edit(event, text)
            else:
                await event.reply(text)
        except:
            pass

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐃ɪᴄᴇ 𝐄ʀʀ → `{str(e)[:40]}`")

# Raid Commands
@register_cmd("reply", needs_reply=True)
async def cmd_reply(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐄ɴᴀʙʟɪɴɢ 𝐑ᴇᴘʟʏ 𝐑ᴀɪᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in reply_users:
                already.append(str(uid))
            else:
                reply_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"🔥 𝐑ᴇᴘʟʏ 𝐑ᴀɪᴅ 𝐎ɴ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐑ᴇᴘʟʏ 𝐑ᴀɪᴅ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("rr", needs_reply=True)
async def cmd_rr(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐄ɴᴀʙʟɪɴɢ 𝐑𝐑 𝐑ᴀɪᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in rr_users:
                already.append(str(uid))
            else:
                rr_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"⚡ 𝐑𝐑 𝐎ɴ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("flag", needs_reply=True)
async def cmd_flag(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐄ɴᴀʙʟɪɴɢ 𝐅ʟᴀɢ 𝐑ᴀɪᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in flag_users:
                already.append(str(uid))
            else:
                flag_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"🌊 𝐅ʟᴀɢ 𝐎ɴ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐅ʟᴀɢ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("hrr", needs_reply=True)
async def cmd_hrr(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐄ɴᴀʙʟɪɴɢ 𝐇ᴇᴀʀᴛ 𝐑ᴀɪᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in hrr_users:
                already.append(str(uid))
            else:
                hrr_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"💜 𝐇ᴇᴀʀᴛ 𝐑ᴀɪᴅ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐇𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("replygod", needs_reply=True)
async def cmd_replygod(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐄ɴᴀʙʟɪɴɢ 𝐑ᴇᴘʟʏ𝐆ᴏᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in replygod_users:
                already.append(str(uid))
            else:
                replygod_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"💥 𝐑ᴇᴘʟʏ𝐆ᴏᴅ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐑𝐆 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("replytony", needs_reply=True)
async def cmd_replytony(event, arg):
    try:
        if not arg or len(arg.split()) < 2:
            return await safe_edit(event,
                "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐅ᴏʀᴍᴀᴛ\n👉 `.replytony <text> <count>`"
            )

        text, count = arg.rsplit(" ", 1)

        try:
            count = int(count)
        except:
            return await safe_edit(event,
                "❌ 𝐂ᴏᴜɴᴛ 𝐌ᴜsᴛ 𝐁ᴇ 𝐍ᴜᴍʙᴇʀ"
            )

        if count <= 0:
            count = 1
        if count > 100:
            count = 100

        targets = await get_targets(event, "")

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐒ᴇᴛᴛɪɴɢ 𝐑ᴇᴘʟʏtony (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, overridden = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in replytony_users:
                overridden.append(str(uid))

            replytony_users[uid] = {
                "text": text,
                "count": count
            }
            added.append(str(uid))

        parts = []

        if added:
            parts.append(f"☄️ 𝐑𝐘 → `{', '.join(added)}` × `{count}`")

        if overridden:
            parts.append(f"⚠️ 𝐎ᴠᴇʀʀɪᴅᴇ → `{', '.join(overridden)}`")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐑𝐘 𝐄ʀʀ → `{str(e)[:40]}`")

@register_cmd("spray")
async def cmd_spray(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ 𝐆ɪᴠᴇɴ\n"
                "👉 𝐔sᴀɢᴇ: `.spray <text>`"
            )

        chat = event.chat_id

        # ─── HUGE TEXT GUARD ───
        if len(arg) > 4000:
            arg = arg[:4000]

        # ─── ALREADY ACTIVE GUARD ───
        if chat in spray_tasks and not spray_tasks[chat].done():
            msg = "⚠️ 𝐒ᴘʀᴀʏ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴄᴛɪᴠᴇ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐈ɴɪᴛɪᴀʟɪᴢɪɴɢ 𝐒ᴘʀᴀʏ...\n━━━━━━━━━━━━━━━"
        )

        async def spray_loop():
            try:
                while True:
                    # stop condition
                    if chat not in spray_tasks:
                        break

                    try:
                        await bot.send_message(chat, arg)
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except RPCError:
                        # permission lost / banned / readonly
                        spray_tasks.pop(chat, None)
                        break
                    except Exception:
                        # network / msg send fail
                        await asyncio.sleep(2)

                    await asyncio.sleep(SPRAY_DELAY)

            except asyncio.CancelledError:
                pass
            finally:
                spray_tasks.pop(chat, None)

        spray_tasks[chat] = asyncio.create_task(spray_loop())

        text = (
            "💣 𝐒ᴘʀᴀʏ 𝐒ᴛᴀʀᴛᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            f"📢 𝐓ᴇxᴛ → `{arg[:40]}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒ᴘʀᴀʏ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("dspray")
async def cmd_dspray(event, _):
    try:
        chat = event.chat_id

        if chat not in spray_tasks:
            msg = "⚠️ 𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐒ᴘʀᴀʏ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐒ᴛᴏᴘᴘɪɴɢ 𝐒ᴘʀᴀʏ...\n━━━━━━━━━━━━━━━"
        )

        try:
            spray_tasks[chat].cancel()
        except:
            pass

        spray_tasks.pop(chat, None)

        text = (
            "🛑 𝐒ᴘʀᴀʏ 𝐒ᴛᴏᴘᴘᴇᴅ\n"
            "━━━━━━━━━━━━━━━"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐃𝐒ᴘʀᴀʏ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


# ────────────────────────────────────────────────
#              CUSTOM SPAM TEXT COMMANDS
# ────────────────────────────────────────────────

@register_cmd("addtext")
async def cmd_addtext(event, arg):
    try:
        if not arg:
            return await safe_edit(event,
                "❌ 𝐔sᴀɢᴇ → `.addtext <your text>`"
            )
        arg = arg.strip()
        if len(arg) > 4000:
            arg = arg[:4000]
        spam_texts.append(arg)
        save_spam_texts()
        idx = len(spam_texts)
        await safe_edit(event,
            f"✅ 𝐓ᴇxᴛ 𝐒ᴀᴠᴇᴅ!\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📌 𝐍ᴜᴍʙᴇʀ → `{idx}`\n"
            f"📝 𝐓ᴇxᴛ → `{arg[:60]}`\n\n"
            f"💡 𝐔sᴇ → `.tspray {idx}` ᴛᴏ sᴘʀᴀʏ ɪᴛ"
        )
    except Exception as e:
        await safe_edit(event, f"❌ 𝐀ᴅᴅᴛᴇxᴛ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("listtexts")
async def cmd_listtexts(event, _):
    try:
        if not spam_texts:
            return await safe_edit(event,
                "📭 𝐍ᴏ 𝐓ᴇxᴛs 𝐒ᴀᴠᴇᴅ\n"
                "💡 𝐔sᴇ `.addtext <text>` ᴛᴏ ᴀᴅᴅ ᴏɴᴇ"
            )
        lines = ["📋 𝐒ᴀᴠᴇᴅ 𝐒ᴘᴀᴍ 𝐓ᴇxᴛs\n━━━━━━━━━━━━━━━"]
        for i, t in enumerate(spam_texts, 1):
            preview = t[:50].replace("`", "'")
            lines.append(f"**{i}.** `{preview}`{'…' if len(t) > 50 else ''}")
        lines.append(f"\n💡 `.tspray <number>` ᴛᴏ sᴘʀᴀʏ | `.deltext <number>` ᴛᴏ ᴅᴇʟᴇᴛᴇ")
        await safe_edit(event, "\n".join(lines))
    except Exception as e:
        await safe_edit(event, f"❌ 𝐋ɪsᴛᴛᴇxᴛs 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("deltext")
async def cmd_deltext(event, arg):
    try:
        if not arg or not arg.strip().isdigit():
            return await safe_edit(event,
                "❌ 𝐔sᴀɢᴇ → `.deltext <number>`\n"
                "💡 𝐔sᴇ `.listtexts` ᴛᴏ sᴇᴇ ɴᴜᴍʙᴇʀs"
            )
        idx = int(arg.strip()) - 1
        if idx < 0 or idx >= len(spam_texts):
            return await safe_edit(event,
                f"❌ 𝐈ɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ. 𝐓ᴏᴛᴀʟ ᴛᴇxᴛs: `{len(spam_texts)}`"
            )
        removed = spam_texts.pop(idx)
        save_spam_texts()
        await safe_edit(event,
            f"🗑️ 𝐃ᴇʟᴇᴛᴇᴅ!\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📝 `{removed[:60]}`"
        )
    except Exception as e:
        await safe_edit(event, f"❌ 𝐃ᴇʟᴛᴇxᴛ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("tspray")
async def cmd_tspray(event, arg):
    try:
        if not arg or not arg.strip().isdigit():
            return await safe_edit(event,
                "❌ 𝐔sᴀɢᴇ → `.tspray <number>`\n"
                "💡 𝐔sᴇ `.listtexts` ᴛᴏ sᴇᴇ ɴᴜᴍʙᴇʀs"
            )
        idx = int(arg.strip()) - 1
        if idx < 0 or idx >= len(spam_texts):
            return await safe_edit(event,
                f"❌ 𝐈ɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ. 𝐓ᴏᴛᴀʟ ᴛᴇxᴛs: `{len(spam_texts)}`"
            )
        text_to_spray = spam_texts[idx]
        chat = event.chat_id

        if chat in spray_tasks and not spray_tasks[chat].done():
            msg = "⚠️ 𝐒ᴘʀᴀʏ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴄᴛɪᴠᴇ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(event,
            f"⚡ 𝐒ᴛᴀʀᴛɪɴɢ 𝐓𝐒ᴘʀᴀʏ...\n━━━━━━━━━━━━━━━"
        )

        async def tspray_loop():
            try:
                while True:
                    if chat not in spray_tasks:
                        break
                    try:
                        await bot.send_message(chat, text_to_spray)
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except RPCError:
                        spray_tasks.pop(chat, None)
                        break
                    except Exception:
                        await asyncio.sleep(2)
                    await asyncio.sleep(SPRAY_DELAY)
            except asyncio.CancelledError:
                pass
            finally:
                spray_tasks.pop(chat, None)

        spray_tasks[chat] = asyncio.create_task(tspray_loop())

        preview = text_to_spray[:40].replace("`", "'")
        result = (
            f"💣 𝐓𝐒ᴘʀᴀʏ 𝐒ᴛᴀʀᴛᴇᴅ\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📌 𝐒ʟᴏᴛ → `{idx + 1}`\n"
            f"📢 𝐓ᴇxᴛ → `{preview}`\n\n"
            f"🛑 𝐒ᴛᴏᴘ ᴡɪᴛʜ `.dspray`"
        )
        if event.out:
            await safe_edit(event, result)
        else:
            await event.reply(result)

    except Exception as e:
        await safe_edit(event, f"❌ 𝐓𝐒ᴘʀᴀʏ 𝐄ʀʀ → `{str(e)[:40]}`")


# ────────────────────────────────────────────────
#           ADVANCED SPAM ENGINE COMMANDS
# ────────────────────────────────────────────────

@register_cmd("rspray")
async def cmd_rspray(event, _):
    try:
        if not spam_texts:
            return await safe_edit(event,
                "📭 𝐍ᴏ 𝐓ᴇxᴛs 𝐒ᴀᴠᴇᴅ\n"
                "💡 𝐔sᴇ `.addtext <text>` ᴛᴏ ᴀᴅᴅ ᴛᴇxᴛs ғɪʀsᴛ"
            )
        chat = event.chat_id
        if chat in spray_tasks and not spray_tasks[chat].done():
            return await safe_edit(event, "⚠️ 𝐒ᴘʀᴀʏ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴄᴛɪᴠᴇ")

        await safe_edit(event, "🎲 𝐑𝐒ᴘʀᴀʏ 𝐒ᴛᴀʀᴛɪɴɢ...\n━━━━━━━━━━━━━━━")

        import random as _random

        async def rspray_loop():
            try:
                while True:
                    if chat not in spray_tasks:
                        break
                    txt = _random.choice(spam_texts)
                    try:
                        await bot.send_message(chat, txt)
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except RPCError:
                        spray_tasks.pop(chat, None)
                        break
                    except Exception:
                        await asyncio.sleep(2)
                    await asyncio.sleep(SPRAY_DELAY)
            except asyncio.CancelledError:
                pass
            finally:
                spray_tasks.pop(chat, None)

        spray_tasks[chat] = asyncio.create_task(rspray_loop())
        result = (
            "🎲 𝐑𝐒ᴘʀᴀʏ 𝐒ᴛᴀʀᴛᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            f"📦 𝐏ᴏᴏʟ → `{len(spam_texts)} ᴛᴇxᴛs`\n"
            "🔀 𝐌ᴏᴅᴇ → 𝐑ᴀɴᴅᴏᴍ\n\n"
            "🛑 𝐒ᴛᴏᴘ ᴡɪᴛʜ `.dspray`"
        )
        if event.out:
            await safe_edit(event, result)
        else:
            await event.reply(result)
    except Exception as e:
        await safe_edit(event, f"❌ 𝐑𝐒ᴘʀᴀʏ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("multispray")
async def cmd_multispray(event, _):
    try:
        if not spam_texts:
            return await safe_edit(event,
                "📭 𝐍ᴏ 𝐓ᴇxᴛs 𝐒ᴀᴠᴇᴅ\n"
                "💡 𝐔sᴇ `.addtext <text>` ᴛᴏ ᴀᴅᴅ ᴛᴇxᴛs ғɪʀsᴛ"
            )
        chat = event.chat_id
        if chat in spray_tasks and not spray_tasks[chat].done():
            return await safe_edit(event, "⚠️ 𝐒ᴘʀᴀʏ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴄᴛɪᴠᴇ")

        await safe_edit(event, "🔄 𝐌ᴜʟᴛɪ𝐒ᴘʀᴀʏ 𝐒ᴛᴀʀᴛɪɴɢ...\n━━━━━━━━━━━━━━━")

        async def multispray_loop():
            try:
                i = 0
                while True:
                    if chat not in spray_tasks:
                        break
                    txt = spam_texts[i % len(spam_texts)]
                    i += 1
                    try:
                        await bot.send_message(chat, txt)
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except RPCError:
                        spray_tasks.pop(chat, None)
                        break
                    except Exception:
                        await asyncio.sleep(2)
                    await asyncio.sleep(SPRAY_DELAY)
            except asyncio.CancelledError:
                pass
            finally:
                spray_tasks.pop(chat, None)

        spray_tasks[chat] = asyncio.create_task(multispray_loop())
        result = (
            "🔄 𝐌ᴜʟᴛɪ𝐒ᴘʀᴀʏ 𝐒ᴛᴀʀᴛᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            f"📦 𝐓ᴇxᴛs → `{len(spam_texts)}`\n"
            "🔁 𝐌ᴏᴅᴇ → 𝐑ᴏᴛᴀᴛɪɴɢ\n\n"
            "🛑 𝐒ᴛᴏᴘ ᴡɪᴛʜ `.dspray`"
        )
        if event.out:
            await safe_edit(event, result)
        else:
            await event.reply(result)
    except Exception as e:
        await safe_edit(event, f"❌ 𝐌ᴜʟᴛɪ𝐒ᴘʀᴀʏ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("countspray")
async def cmd_countspray(event, arg):
    try:
        parts = arg.strip().split(None, 1) if arg else []
        if len(parts) < 2 or not parts[0].isdigit():
            return await safe_edit(event,
                "❌ 𝐔sᴀɢᴇ → `.countspray <count> <text>`\n"
                "📌 𝐄x → `.countspray 20 Hello!`"
            )
        count = int(parts[0])
        if count < 1 or count > 500:
            return await safe_edit(event, "❌ 𝐂ᴏᴜɴᴛ ᴍᴜsᴛ ʙᴇ 1–500")
        text_to_send = parts[1][:4000]
        chat = event.chat_id

        if chat in spray_tasks and not spray_tasks[chat].done():
            return await safe_edit(event, "⚠️ 𝐒ᴘʀᴀʏ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴄᴛɪᴠᴇ")

        await safe_edit(event,
            f"🎯 𝐂𝐨𝐮𝐧𝐭𝐒ᴘʀᴀʏ 𝐒ᴛᴀʀᴛɪɴɢ...\n━━━━━━━━━━━━━━━\n"
            f"📊 𝐓ᴀʀɢᴇᴛ → `{count}` ᴍsɢs"
        )

        async def countspray_loop():
            try:
                sent = 0
                while sent < count:
                    if chat not in spray_tasks:
                        break
                    try:
                        await bot.send_message(chat, text_to_send)
                        sent += 1
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except RPCError:
                        spray_tasks.pop(chat, None)
                        break
                    except Exception:
                        await asyncio.sleep(2)
                    await asyncio.sleep(SPRAY_DELAY)
                spray_tasks.pop(chat, None)
                try:
                    await bot.send_message(chat,
                        f"✅ 𝐃ᴏɴᴇ! `{sent}` 𝐌ᴇssᴀɢᴇs 𝐒ᴇɴᴛ"
                    )
                except:
                    pass
            except asyncio.CancelledError:
                pass
            finally:
                spray_tasks.pop(chat, None)

        spray_tasks[chat] = asyncio.create_task(countspray_loop())
        result = (
            f"🎯 𝐂𝐨𝐮𝐧𝐭𝐒ᴘʀᴀʏ 𝐒ᴛᴀʀᴛᴇᴅ\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📊 𝐂ᴏᴜɴᴛ → `{count}`\n"
            f"📢 𝐓ᴇxᴛ → `{text_to_send[:40]}`\n\n"
            f"🛑 𝐄ᴀʀʟʏ sᴛᴏᴘ: `.dspray`"
        )
        if event.out:
            await safe_edit(event, result)
        else:
            await event.reply(result)
    except Exception as e:
        await safe_edit(event, f"❌ 𝐂𝐨𝐮𝐧𝐭𝐒ᴘʀᴀʏ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("spraydelay")
async def cmd_spraydelay(event, arg):
    global SPRAY_DELAY
    try:
        if not arg:
            return await safe_edit(event,
                f"⏱ 𝐂ᴜʀʀᴇɴᴛ 𝐃ᴇʟᴀʏ → `{SPRAY_DELAY}s`\n"
                "❌ 𝐔sᴀɢᴇ → `.spraydelay <seconds>`\n"
                "📌 𝐄x → `.spraydelay 0.3`"
            )
        try:
            val = float(arg.strip())
        except ValueError:
            return await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ")
        if val < 0.1:
            val = 0.1
        if val > 60:
            val = 60
        old = SPRAY_DELAY
        SPRAY_DELAY = val
        await safe_edit(event,
            f"⚡ 𝐒ᴘʀᴀʏ 𝐃ᴇʟᴀʏ 𝐔ᴘᴅᴀᴛᴇᴅ!\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔴 𝐎ʟᴅ → `{old}s`\n"
            f"🟢 𝐍ᴇᴡ → `{val}s`"
        )
    except Exception as e:
        await safe_edit(event, f"❌ 𝐒ᴘʀᴀʏᴅᴇʟᴀʏ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("edittext")
async def cmd_edittext(event, arg):
    try:
        parts = arg.strip().split(None, 1) if arg else []
        if len(parts) < 2 or not parts[0].isdigit():
            return await safe_edit(event,
                "❌ 𝐔sᴀɢᴇ → `.edittext <number> <new text>`\n"
                "📌 𝐄x → `.edittext 2 New spam text here`"
            )
        idx = int(parts[0]) - 1
        if idx < 0 or idx >= len(spam_texts):
            return await safe_edit(event,
                f"❌ 𝐈ɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ. 𝐓ᴏᴛᴀʟ: `{len(spam_texts)}`"
            )
        new_text = parts[1][:4000]
        old_text = spam_texts[idx]
        spam_texts[idx] = new_text
        save_spam_texts()
        await safe_edit(event,
            f"✏️ 𝐓ᴇxᴛ 𝐔ᴘᴅᴀᴛᴇᴅ!\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📌 𝐒ʟᴏᴛ → `{idx + 1}`\n"
            f"🔴 𝐎ʟᴅ → `{old_text[:50]}`\n"
            f"🟢 𝐍ᴇᴡ → `{new_text[:50]}`"
        )
    except Exception as e:
        await safe_edit(event, f"❌ 𝐄ᴅɪᴛᴛᴇxᴛ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("cleartext")
async def cmd_cleartext(event, arg):
    try:
        if arg.strip().lower() != "confirm":
            return await safe_edit(event,
                f"⚠️ 𝐓ʜɪs ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ 𝐀𝐋𝐋 `{len(spam_texts)}` ᴛᴇxᴛs!\n"
                "━━━━━━━━━━━━━━━\n"
                "✅ 𝐓ʏᴘᴇ `.cleartext confirm` ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ"
            )
        count = len(spam_texts)
        spam_texts.clear()
        save_spam_texts()
        await safe_edit(event,
            f"🗑️ 𝐂ʟᴇᴀʀᴇᴅ! `{count}` ᴛᴇxᴛs ᴅᴇʟᴇᴛᴇᴅ."
        )
    except Exception as e:
        await safe_edit(event, f"❌ 𝐂ʟᴇᴀʀᴛᴇxᴛ 𝐄ʀʀ → `{str(e)[:40]}`")


# ────────────────────────────────────────────────
#            WATCHSPAM — OPPONENT SPAM CONTROLLER
# ────────────────────────────────────────────────

@register_cmd("watchspam")
async def cmd_watchspam(event, arg):
    try:
        parts = arg.strip().split() if arg else []
        # Usage: .watchspam @user <limit> <seconds>
        # Example: .watchspam @ritik 3 5  → delete if >3 msgs in 5s
        if len(parts) < 1:
            return await safe_edit(event,
                "❌ 𝐔sᴀɢᴇ → `.watchspam @user <limit> <seconds>`\n"
                "📌 𝐄x → `.watchspam @tony 3 5`\n"
                "💡 Agar 5 sec mein 3 se zyada msg bheje → auto-delete"
            )

        limit = 3
        seconds = 5.0

        try:
            if len(parts) >= 2:
                limit = int(parts[1])
            if len(parts) >= 3:
                seconds = float(parts[2])
        except:
            pass

        limit = max(1, min(limit, 20))
        seconds = max(1.0, min(seconds, 60.0))

        # Resolve target user
        target_arg = parts[0].lstrip("@")
        try:
            entity = await bot.get_entity(target_arg)
            uid = int(entity.id)
            uname = getattr(entity, "first_name", target_arg) or target_arg
        except:
            if event.is_reply:
                reply = await event.get_reply_message()
                uid = reply.sender_id
                uname = str(uid)
            else:
                return await safe_edit(event,
                    "❌ 𝐔sᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ. 𝐑ᴇᴘʟʏ ᴛᴏ ᴛʜᴇɪʀ ᴍsɢ ᴏʀ ᴜsᴇ @ᴜsᴇʀɴᴀᴍᴇ"
                )

        chat = event.chat_id
        ws_key = (chat, uid)
        watch_spam[ws_key] = {"limit": limit, "seconds": seconds, "times": [], "name": uname}

        await safe_edit(event,
            f"👁️ 𝐖ᴀᴛᴄʜ𝐒ᴘᴀᴍ 𝐀ᴄᴛɪᴠᴇ!\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 𝐔sᴇʀ → `{uname}`\n"
            f"⚡ 𝐋ɪᴍɪᴛ → `{limit}` ᴍsɢ / `{seconds}s`\n"
            f"🗑️ 𝐀ᴄᴛɪᴏɴ → 𝐀ᴜᴛᴏ-𝐃ᴇʟᴇᴛᴇ ɪꜰ ᴇxᴄᴇᴇᴅᴇᴅ\n\n"
            f"🛑 𝐒ᴛᴏᴘ → `.unwatchspam {parts[0]}`"
        )
    except Exception as e:
        await safe_edit(event, f"❌ 𝐖ᴀᴛᴄʜ𝐒ᴘᴀᴍ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("unwatchspam")
async def cmd_unwatchspam(event, arg):
    try:
        chat = event.chat_id
        removed = []

        if arg:
            target_arg = arg.strip().lstrip("@")
            try:
                entity = await bot.get_entity(target_arg)
                uid = int(entity.id)
            except:
                if event.is_reply:
                    reply = await event.get_reply_message()
                    uid = reply.sender_id
                else:
                    return await safe_edit(event, "❌ 𝐔sᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ")
            ws_key = (chat, uid)
            if ws_key in watch_spam:
                name = watch_spam[ws_key].get("name", str(uid))
                del watch_spam[ws_key]
                removed.append(name)
        else:
            # Remove all watches in this chat
            keys = [k for k in watch_spam if k[0] == chat]
            for k in keys:
                removed.append(watch_spam[k].get("name", str(k[1])))
                del watch_spam[k]

        if removed:
            await safe_edit(event,
                f"✅ 𝐖ᴀᴛᴄʜ𝐒ᴘᴀᴍ 𝐑ᴇᴍᴏᴠᴇᴅ\n"
                f"━━━━━━━━━━━━━━━\n"
                f"👤 `{'`, `'.join(removed)}`"
            )
        else:
            await safe_edit(event, "⚠️ 𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐖ᴀᴛᴄʜ ɪɴ 𝐓ʜɪs 𝐂ʜᴀᴛ")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐔ɴ𝐖ᴀᴛᴄʜ𝐒ᴘᴀᴍ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("watchlist")
async def cmd_watchlist(event, _):
    try:
        chat = event.chat_id
        entries = {k: v for k, v in watch_spam.items() if k[0] == chat}

        if not entries:
            return await safe_edit(event,
                "📭 𝐍ᴏ 𝐖ᴀᴛᴄʜᴇs 𝐀ᴄᴛɪᴠᴇ\n"
                "💡 𝐔sᴇ `.watchspam @user <limit> <sec>` ᴛᴏ ᴀᴅᴅ"
            )

        lines = [f"👁️ 𝐖ᴀᴛᴄʜ𝐒ᴘᴀᴍ 𝐋ɪsᴛ\n━━━━━━━━━━━━━━━"]
        for (_, uid), v in entries.items():
            lines.append(
                f"👤 `{v.get('name', uid)}` → "
                f"𝐋ɪᴍɪᴛ `{v['limit']}` ᴍsɢ / `{v['seconds']}s`"
            )
        lines.append(f"\n🛑 `.unwatchspam @user` ᴛᴏ sᴛᴏᴘ")
        await safe_edit(event, "\n".join(lines))
    except Exception as e:
        await safe_edit(event, f"❌ 𝐖ᴀᴛᴄʜʟɪsᴛ 𝐄ʀʀ → `{str(e)[:40]}`")


# ────────────────────────────────────────────────
#               ANTI-DELETE PROTECTION
# ────────────────────────────────────────────────

@register_cmd("antidel")
async def cmd_antidel(event, arg):
    global antidel_enabled
    try:
        arg = arg.strip().lower() if arg else ""

        if arg in ("on", "start", "enable"):
            antidel_enabled = True
            antidel_cache.clear()
            await safe_edit(event,
                "🛡️ 𝐀ɴᴛɪ-𝐃ᴇʟᴇᴛᴇ 𝐎𝐍!\n"
                "━━━━━━━━━━━━━━━\n"
                "✅ 𝐀ʙ ᴀɢᴀʀ ᴋᴏɪ ᴛᴜᴍʜᴀʀᴀ ᴍsɢ\n"
                "   ᴅᴇʟᴇᴛᴇ ᴋᴀʀᴇ → ᴡᴀᴘᴀs ᴀ ᴊᴀʏᴇɢᴀ!\n\n"
                "🔴 𝐁ᴀɴᴅ ᴋᴀʀɴᴇ → `.antidel off`"
            )

        elif arg in ("off", "stop", "disable"):
            antidel_enabled = False
            antidel_cache.clear()
            await safe_edit(event,
                "🔓 𝐀ɴᴛɪ-𝐃ᴇʟᴇᴛᴇ 𝐎𝐅𝐅\n"
                "━━━━━━━━━━━━━━━\n"
                "💤 𝐏ʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴀɴᴅ ʜᴏ ɢᴀʏɪ"
            )

        else:
            status = "🟢 𝐎𝐍" if antidel_enabled else "🔴 𝐎𝐅𝐅"
            cached = len(antidel_cache)
            await safe_edit(event,
                f"🛡️ 𝐀ɴᴛɪ-𝐃ᴇʟᴇᴛᴇ 𝐒ᴛᴀᴛᴜs\n"
                f"━━━━━━━━━━━━━━━\n"
                f"⚡ 𝐒ᴛᴀᴛᴜs → {status}\n"
                f"💾 𝐂ᴀᴄʜᴇᴅ ᴍsɢs → `{cached}`\n\n"
                f"✅ 𝐔sᴀɢᴇ:\n"
                f"  `.antidel on` → 𝐒ʜᴜʀᴜ ᴋᴀʀᴏ\n"
                f"  `.antidel off` → 𝐁ᴀɴᴅ ᴋᴀʀᴏ"
            )

    except Exception as e:
        await safe_edit(event, f"❌ 𝐀ɴᴛɪ𝐃ᴇʟ 𝐄ʀʀ → `{str(e)[:40]}`")


# Mute Commands
@register_cmd("mute", needs_reply=True)
async def cmd_mute(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ\n👉 `.mute` (reply / @username / id)"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐌ᴜᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in muted_users:
                already.append(str(uid))
            else:
                muted_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"🔇 𝐌ᴜᴛᴇ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐌ᴜᴛᴇᴅ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐌ᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("unmute", needs_reply=True)
async def cmd_unmute(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ\n👉 `.unmute` (reply / @username / id)"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐔ɴᴍᴜᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        removed, not_muted = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in muted_users:
                muted_users.remove(uid)
                removed.append(str(uid))
            else:
                not_muted.append(str(uid))

        parts = []

        if removed:
            parts.append(f"🗣️ 𝐔ɴᴍᴜᴛᴇ → `{', '.join(removed)}`")

        if not_muted:
            parts.append(f"⚠️ 𝐍ᴏᴛ 𝐌ᴜᴛᴇᴅ → `{', '.join(not_muted)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐔ɴᴍᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("gmute", needs_reply=True)
async def cmd_gmute(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ\n👉 `.gmute` (reply / @username / id)"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐆ᴍᴜᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in global_muted:
                already.append(str(uid))
            else:
                global_muted.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"🔕 𝐆ᴍᴜᴛᴇ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐆ᴍᴜᴛᴇᴅ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐆ᴍᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("gunmute", needs_reply=True)
async def cmd_gunmute(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ\n👉 `.gunmute` (reply / @username / id)"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐆ᴜɴᴍᴜᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        removed, not_muted = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in global_muted:
                global_muted.remove(uid)
                removed.append(str(uid))
            else:
                not_muted.append(str(uid))

        parts = []

        if removed:
            parts.append(f"🔊 𝐆ᴜɴᴍᴜᴛᴇ → `{', '.join(removed)}`")

        if not_muted:
            parts.append(f"⚠️ 𝐍ᴏᴛ 𝐆ᴍᴜᴛᴇᴅ → `{', '.join(not_muted)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐆𝐔𝐍𝐌𝐔𝐓𝐄 𝐄ʀʀ → `{str(e)[:40]}`")

# Group Mod
@register_cmd("purge")
async def cmd_purge(event, arg):
    try:
        try:
            count = int(arg) if arg else 50
        except:
            count = 50

        # ─── HARD LIMIT ENGINE ───
        if count < 1:
            count = 1
        if count > 200:
            count = 200

        await safe_edit(
            event,
            "⚡ 𝐏ᴜʀɢɪɴɢ 𝐌ᴇssᴀɢᴇs...\n━━━━━━━━━━━━━━━"
        )

        msgs = []
        async for m in bot.iter_messages(event.chat_id, limit=count + 1):
            msgs.append(m.id)

        if not msgs:
            return await safe_edit(event,
                "⚠️ 𝐍ᴏ 𝐌ᴇssᴀɢᴇs 𝐅ᴏᴜɴᴅ"
            )

        # ─── SAFE DELETE BATCH ───
        try:
            await bot.delete_messages(event.chat_id, msgs)
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
            await bot.delete_messages(event.chat_id, msgs)
        except RPCError:
            # readonly / no rights / protected msgs
            pass

        text = (
            "🧹 𝐏ᴜʀɢᴇ 𝐂ᴏᴍᴘʟᴇᴛᴇ\n"
            "━━━━━━━━━━━━━━━\n"
            f"🗑️ 𝐃ᴇʟᴇᴛᴇᴅ → `{max(len(msgs)-1,0)}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐏ᴜʀɢᴇ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("throw", needs_reply=True, group_only=True)
async def cmd_throw(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ"
            )

        # ─── ADMIN CHECK SAFE ───
        try:
            perms = await bot.get_permissions(event.chat_id, 'me')
            if not perms.is_admin:
                return await safe_edit(event,
                    "❌ 𝐍ᴏ 𝐀ᴅᴍɪɴ 𝐑ɪɢʜᴛs"
                )
        except:
            return await safe_edit(event,
                "❌ 𝐏ᴇʀᴍ𝐢ssɪᴏɴ 𝐂ʜᴇᴄᴋ 𝐅ᴀɪʟ"
            )

        await safe_edit(
            event,
            "⚡ 𝐊ɪᴄᴋɪɴɢ 𝐓ᴀʀɢᴇᴛs...\n━━━━━━━━━━━━━━━"
        )

        kicked, failed, skipped = [], [], []

        me = await bot.get_me()

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid == me.id:
                skipped.append(str(uid))
                continue

            try:
                await bot.kick_participant(event.chat_id, uid)
                kicked.append(str(uid))
            except:
                failed.append(str(uid))

        parts = []

        if kicked:
            parts.append(f"👞 𝐊ɪᴄᴋᴇᴅ → `{', '.join(kicked)}`")

        if failed:
            parts.append(f"⚠️ 𝐅ᴀɪʟᴇᴅ → `{', '.join(failed)}`")

        if skipped:
            parts.append(f"👑 𝐒ᴇʟғ 𝐒ᴋɪᴘ → `{', '.join(skipped)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐀ᴄᴛɪᴏɴ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐓ʜʀᴏᴡ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("sreply")
async def cmd_sreply(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in reply_users:
                    reply_users.discard(uid)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(f"🛑 𝐑ᴇᴘʟʏ 𝐎ғғ → `{', '.join(stopped)}`")

            if not_active:
                parts.append(f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`")

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            reply_users.clear()
            text = (
                "🛑 𝐑ᴇᴘʟʏ 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐑𝐄𝐏𝐋𝐘 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("srr")
async def cmd_srr(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in rr_users:
                    rr_users.discard(uid)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(f"🛑 𝐑𝐑 𝐎ғғ → `{', '.join(stopped)}`")

            if not_active:
                parts.append(f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`")

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            rr_users.clear()

            text = (
                "🛑 𝐑𝐑 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("sflag")
async def cmd_sflag(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in flag_users:
                    flag_users.discard(uid)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(f"🛑 𝐅ʟᴀɢ 𝐎ғғ → `{', '.join(stopped)}`")

            if not_active:
                parts.append(f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`")

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            flag_users.clear()

            text = (
                "🛑 𝐅ʟᴀɢ 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐅𝐋𝐀𝐆 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("shrr")
async def cmd_shrr(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            await safe_edit(
                event,
                "⚡ 𝐃ɪsᴀʙʟɪɴɢ 𝐇ᴇᴀʀᴛ 𝐑ᴀɪᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
            )

            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in hrr_users:
                    hrr_users.discard(uid)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(
                    f"🛑 𝐇ᴇᴀʀᴛ 𝐎ғғ → `{', '.join(stopped)}`"
                )

            if not_active:
                parts.append(
                    f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`"
                )

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            hrr_users.clear()

            text = (
                "🛑 𝐇ᴇᴀʀᴛ 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐇𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("sgod")
async def cmd_sgod(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            await safe_edit(
                event,
                "⚡ 𝐃ɪsᴀʙʟɪɴɢ 𝐑ᴇᴘʟʏ𝐆ᴏᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
            )

            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in replygod_users:
                    replygod_users.discard(uid)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(
                    f"🛑 𝐑𝐆 𝐎ғғ → `{', '.join(stopped)}`"
                )

            if not_active:
                parts.append(
                    f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`"
                )

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            replygod_users.clear()

            text = (
                "🛑 𝐑𝐆 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐆𝐎𝐃 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("stony")
async def cmd_stony(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            await safe_edit(
                event,
                "⚡ 𝐃ɪsᴀʙʟɪɴɢ 𝐑𝐘 (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
            )

            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in replytony_users:
                    replytony_users.pop(uid, None)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(
                    f"🛑 𝐑𝐘 𝐎ғғ → `{', '.join(stopped)}`"
                )

            if not_active:
                parts.append(
                    f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`"
                )

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            replytony_users.clear()

            text = (
                "🛑 𝐑𝐘 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ Stony 𝐄ʀʀ → `{str(e)[:40]}`"
        )

# Lock / Unlock
@register_cmd("lock", group_only=True)
async def cmd_lock(event, _):
    try:
        chat = event.chat_id

        # ─── ADMIN CHECK ───
        try:
            perms = await bot.get_permissions(chat, 'me')
            if not perms.is_admin:
                return await safe_edit(event,
                    "❌ 𝐍ᴏ 𝐀ᴅᴍɪɴ 𝐑ɪɢʜᴛs"
                )
        except:
            pass

        if chat in group_locks:
            msg = "⚠️ 𝐆ʀᴏᴜᴘ 𝐀ʟʀᴇᴀᴅʏ 𝐋ᴏᴄᴋᴇᴅ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐀ᴘᴘʟʏɪɴɢ 𝐋ᴏᴄᴋ...\n━━━━━━━━━━━━━━━"
        )

        group_locks.add(chat)

        text = (
            "🔒 𝐆ʀᴏᴜᴘ 𝐋ᴏᴄᴋᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            "🚫 𝐍ᴏɴ-𝐀ᴅᴍɪɴ 𝐌ᴇssᴀɢᴇs 𝐁ʟᴏᴄᴋᴇᴅ"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐋ᴏᴄᴋ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("unlock", group_only=True)
async def cmd_unlock(event, _):
    try:
        chat = event.chat_id

        # ─── ADMIN CHECK ───
        try:
            perms = await bot.get_permissions(chat, 'me')
            if not perms.is_admin:
                return await safe_edit(event,
                    "❌ 𝐍ᴏ 𝐀ᴅᴍɪɴ 𝐑ɪɢʜᴛs"
                )
        except:
            pass

        if chat not in group_locks:
            msg = "⚠️ 𝐆ʀᴏᴜᴘ 𝐀ʟʀᴇᴀᴅʏ 𝐔ɴʟᴏᴄᴋᴇᴅ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐑ᴇᴍᴏᴠɪɴɢ 𝐋ᴏᴄᴋ...\n━━━━━━━━━━━━━━━"
        )

        group_locks.discard(chat)

        text = (
            "🔓 𝐆ʀᴏᴜᴘ 𝐔ɴʟᴏᴄᴋᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            "✅ 𝐌ᴇssᴀɢɪɴɢ 𝐑ᴇsᴛᴏʀᴇᴅ"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐔ɴʟᴏᴄᴋ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


# ───────── AUTO REACT ─────────

@register_cmd("ar")
async def cmd_ar(event, arg):
    global auto_react_emoji

    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐄ᴍᴏᴊɪ\n👉 `.ar <emoji>`"
            )

        emoji = arg.strip()

        # ─── EMOJI SANITY GUARD ───
        if len(emoji) > 8:
            return await safe_edit(event,
                "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐄ᴍᴏᴊɪ"
            )

        if auto_react_emoji == emoji:
            msg = f"⚠️ 𝐀ʀ 𝐀ʟʀᴇᴀᴅʏ → {emoji}"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐀ᴘᴘʟʏɪɴɢ 𝐀ᴜᴛᴏ-𝐑ᴇᴀᴄᴛ...\n━━━━━━━━━━━━━━━"
        )

        auto_react_emoji = emoji

        text = (
            "✅ 𝐀ᴜᴛᴏ 𝐑ᴇᴀᴄᴛ 𝐄ɴᴀʙʟᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            f"😀 𝐄ᴍᴏᴊɪ → {emoji}"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐀𝐑 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("sar")
async def cmd_sar(event, _):
    global auto_react_emoji

    try:
        if auto_react_emoji is None:
            msg = "⚠️ 𝐀𝐑 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐃ɪsᴀʙʟɪɴɢ 𝐀ᴜᴛᴏ-𝐑ᴇᴀᴄᴛ...\n━━━━━━━━━━━━━━━"
        )

        auto_react_emoji = None

        text = (
            "🛑 𝐀ᴜᴛᴏ 𝐑ᴇᴀᴄᴛ 𝐃ɪsᴀʙʟᴇᴅ\n"
            "━━━━━━━━━━━━━━━"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐀𝐑 𝐄ʀʀ → `{str(e)[:40]}`"
        )

# FastGC
@register_cmd("fastgc")
async def cmd_fastgc(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐔sᴀɢᴇ → `.fastgc set <template {emoji}>`"
            )

        arg = arg.strip()

        # ───── START ENGINE ─────
        if arg.startswith("set "):
            template = arg[4:].strip()

            if "{emoji}" not in template:
                return await safe_edit(
                    event,
                    "❌ 𝐔sᴇ `{emoji}` 𝐢ɴ 𝐭ᴇᴍᴘʟᴀᴛᴇ"
                )

            await safe_edit(
                event,
                "⚡ 𝐒ᴛᴀʀᴛɪɴɢ 𝐅ᴀsᴛ𝐆𝐂...\n━━━━━━━━━━━━━━━"
            )

            FASTGC_STATE["active"] = True
            FASTGC_STATE["template"] = template
            FASTGC_STATE["chat_id"] = event.chat_id

            try:
                if FASTGC_STATE.get("task") and not FASTGC_STATE["task"].done():
                    FASTGC_STATE["task"].cancel()
            except:
                pass

            FASTGC_STATE["task"] = asyncio.create_task(
                gc_fast_loop(event.chat_id)
            )

            return await safe_edit(event, "⚡ 𝐅ᴀsᴛ𝐆𝐂 𝐒ᴛᴀʀᴛᴇᴅ")

        # ───── STOP ENGINE ─────
        elif arg == "stop":
            await safe_edit(
                event,
                "⚡ 𝐒ᴛᴏᴘᴘɪɴɢ 𝐅ᴀsᴛ𝐆𝐂...\n━━━━━━━━━━━━━━━"
            )

            FASTGC_STATE["active"] = False
            FASTGC_STATE["template"] = None

            try:
                if FASTGC_STATE.get("task"):
                    FASTGC_STATE["task"].cancel()
            except:
                pass

            FASTGC_STATE["task"] = None

            return await safe_edit(event, "🛑 𝐅ᴀsᴛ𝐆𝐂 𝐒ᴛᴏᴘᴘᴇᴅ")

        else:
            return await safe_edit(
                event,
                "❌ 𝐈ɴᴠᴀʟɪᴅ\n👉 `.fastgc set <template {emoji}>`"
            )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐅𝐆𝐂 𝐄ʀʀ → `{str(e)[:40]}`"
        )


# ───────── NOTES ─────────

@register_cmd("notesadd")
async def notes_add(event, arg):
    try:
        if not arg:
            return await safe_edit(event,
                "❌ 𝐆ɪᴠᴇ 𝐍ᴏᴛᴇ 𝐓ᴇxᴛ"
            )

        await safe_edit(
            event,
            "⚡ 𝐒ᴀᴠɪɴɢ 𝐍ᴏᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        nid = max(notes.keys(), default=0) + 1
        notes[nid] = arg[:4000]

        try:
            save_notes()
        except:
            pass

        await safe_edit(
            event,
            f"📝 𝐍ᴏᴛᴇ 𝐒ᴀᴠᴇᴅ\n━━━━━━━━━━━━━━━\n🆔 `{nid}`"
        )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐍ᴏᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("noteslist")
async def notes_list(event, _):
    try:
        if not notes:
            return await safe_edit(event,
                "📭 𝐍ᴏ 𝐍ᴏᴛᴇs"
            )

        await safe_edit(
            event,
            "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐍ᴏᴛᴇs...\n━━━━━━━━━━━━━━━"
        )

        msg = "📝 𝐘ᴏᴜʀ 𝐍ᴏᴛᴇs\n━━━━━━━━━━━━━━━\n"

        for i, t in sorted(notes.items()):
            msg += f"🔹 `{i}` → {t[:100]}\n"

        await safe_edit(event, msg)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐍ᴏᴛᴇ𝐋𝐢sᴛ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("notesdelete")
async def notes_delete(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐆ɪᴠᴇ 𝐈𝐃"
            )

        try:
            nid = int(arg)
        except:
            return await safe_edit(event,
                "❌ 𝐈𝐃 𝐌ᴜsᴛ 𝐁ᴇ 𝐍ᴜᴍʙᴇʀ"
            )

        if nid not in notes:
            msg = "⚠️ 𝐍ᴏᴛᴇ 𝐍ᴏᴛ 𝐅ᴏᴜɴᴅ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐃ᴇʟᴇᴛɪɴɢ 𝐍ᴏᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        notes.pop(nid, None)

        try:
            save_notes()
        except:
            pass

        text = (
            "🗑️ 𝐍ᴏᴛᴇ 𝐃ᴇʟᴇᴛᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            f"🆔 `{nid}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐍ᴏᴛᴇ𝐃𝐞𝐥 𝐄ʀʀ → `{str(e)[:40]}`"
        )


# ───────── TTS ─────────

@register_cmd("tts")
async def cmd_tts(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ\n👉 `.tts <text>`"
            )

        await safe_edit(
            event,
            "⚡ 𝐆ᴇɴᴇʀᴀᴛɪɴɢ 𝐓𝐓𝐒...\n━━━━━━━━━━━━━━━"
        )

        fname = f"tts_{int(time.time())}.mp3"

        try:
            gTTS(text=arg[:5000], lang="hi", slow=False).save(fname)
        except Exception:
            return await safe_edit(event,
                "❌ 𝐓𝐓𝐒 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ"
            )

        try:
            if event.out:
                await event.delete()
                await bot.send_file(
                    event.chat_id,
                    fname,
                    caption="🎙️ 𝐓𝐓𝐒 𝐆ᴇɴ"
                )
            else:
                await event.reply(
                    file=fname,
                    message="🎙️ 𝐓𝐓𝐒 𝐆ᴇɴ"
                )
        finally:
            try:
                os.remove(fname)
            except:
                pass

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐓𝐓𝐒 𝐄ʀʀ → `{str(e)[:50]}`"
        )


@register_cmd("qrcode")
async def cmd_qrcode(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ / 𝐋ɪɴᴋ\n👉 `.qrcode <text>`"
            )

        await safe_edit(
            event,
            "⚡ 𝐆ᴇɴᴇʀᴀᴛɪɴɢ 𝐐𝐑...\n━━━━━━━━━━━━━━━"
        )

        file = f"qr_{int(time.time())}.png"
        qrcode.make(arg[:3000]).save(file)

        try:
            if event.out:
                await event.delete()
                await bot.send_file(
                    event.chat_id,
                    file,
                    caption="🔳 𝐐𝐑 𝐂ᴏᴅᴇ"
                )
            else:
                await event.reply(
                    file=file,
                    message="🔳 𝐐𝐑 𝐂ᴏᴅᴇ"
                )
        finally:
            try:
                os.remove(file)
            except:
                pass

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐐𝐑 𝐄ʀʀ → `{str(e)[:50]}`"
        )


@register_cmd("fancy")
async def cmd_fancy(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ\n👉 `.fancy <text>`"
            )

        t = arg[:2000]

        styles = [
            t.upper(),
            t.lower(),
            f"★彡 {t} 彡★",
            f"『 {t} 』",
            f"✦ {t} ✦",
            f"☾ {t} ☽",
            f"➳ {t} ➳",
            f"⚡ {t} ⚡",
            f"❖ {t} ❖",
            f"⫷ {t} ⫸",
            f"♛ {t} ♛",
            f"✧･ﾟ: *✧ {t} ✧*:･ﾟ✧",
            f"꧁ {t} ꧂",
            f"░▒▓ {t} ▓▒░",
            f"➶➶ {t} ➷➷",
            f"✿ {t} ✿",
            f"彡★ {t} ★彡",
            f"⧼ {t} ⧽",
            f"⟪ {t} ⟫",
            f"⌁ {t} ⌁"
        ]

        text = (
            "✨ 𝐅ᴀɴᴄʏ 𝐒ᴛʏʟᴇs\n"
            "━━━━━━━━━━━━━━━\n"
            + "\n".join(styles)
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐅ᴀɴᴄʏ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("style")
async def cmd_style(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ\n👉 `.style <text>`"
            )

        t = arg[:2000]

        fancy = (
            t.replace('a','𝒶').replace('b','𝒷')
             .replace('c','𝒸').replace('d','𝒹')
             .replace('e','𝑒').replace('f','𝒻')
             .replace('g','𝑔').replace('h','𝒽')
             .replace('i','𝒾').replace('j','𝒿')
             .replace('k','𝓀').replace('l','𝓁')
             .replace('m','𝓂').replace('n','𝓃')
             .replace('o','𝑜').replace('p','𝓅')
             .replace('q','𝓆').replace('r','𝓇')
             .replace('s','𝓈').replace('t','𝓉')
             .replace('u','𝓊').replace('v','𝓋')
             .replace('w','𝓌').replace('x','𝓍')
             .replace('y','𝓎').replace('z','𝓏')
        )

        text = (
            "🎨 𝐓ᴇxᴛ 𝐒ᴛʏʟᴇ\n"
            "━━━━━━━━━━━━━━━\n"
            f"𝒇𝒂𝒏𝒄ʏ → {fancy}\n"
            f"**Bold** → **{t}**\n"
            f"__Italic__ → __{t}__\n"
            f"`Mono` → `{t}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒ᴛʏʟᴇ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("emoji")
async def cmd_emoji(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ\n👉 `.emoji <text>`"
            )

        pool = [
            "🔥","❤️","✨","⚡","💥","🌟","💫","🎯",
            "💎","🦋","🌈","🧨","🎆","👑","🌸","🪄",
            "🌊","❄️","🍁","🌙","☀️","💣","🎵","🧿"
        ]

        emojis = "".join(random.choice(pool) for _ in range(8))

        text = (
            "😀 𝐄ᴍᴏᴊɪ 𝐒ᴛʏʟᴇ\n"
            "━━━━━━━━━━━━━━━\n"
            f"{arg[:2000]} {emojis}"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐄ᴍᴏᴊɪ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("calc")
async def cmd_calc(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐄xᴘʀᴇssɪᴏɴ\n👉 `.calc <math>`"
            )

        expr = arg.replace(" ", "")

        allowed = set("0123456789+-*/().%")

        if any(c not in allowed for c in expr):
            return await safe_edit(event,
                "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐂ʜᴀʀ"
            )

        await safe_edit(
            event,
            "⚡ 𝐂ᴀʟᴄᴜʟᴀᴛɪɴɢ...\n━━━━━━━━━━━━━━━"
        )

        res = eval(expr, {"__builtins__": None}, {})

        text = (
            "🧮 𝐂ᴀʟᴄ𝐮ʟᴀᴛᴏʀ\n"
            "━━━━━━━━━━━━━━━\n"
            f"📥 `{expr}`\n"
            f"📤 `{res}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception:
        await safe_edit(event,
            "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐄xᴘʀᴇssɪᴏɴ"
        )

@register_cmd("weather")
async def cmd_weather(event, arg):
    try:
        if not arg:
            return await safe_edit(event,
                "❌ 𝐆ɪᴠᴇ 𝐂ɪᴛʏ"
            )

        await safe_edit(
            event,
            "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐖ᴇᴀᴛʜᴇʀ...\n━━━━━━━━━━━━━━━"
        )

        try:
            geo = requests.get(
                f"https://geocoding-api.open-meteo.com/v1/search?name={arg}&count=1",
                timeout=8
            ).json()
        except:
            return await safe_edit(event,
                "❌ 𝐆ᴇᴏ 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ"
            )

        if not geo.get("results"):
            return await safe_edit(event,
                "❌ 𝐂ɪᴛʏ 𝐍ᴏᴛ 𝐅ᴏᴜɴᴅ"
            )

        res = geo["results"][0]

        lat = res.get("latitude")
        lon = res.get("longitude")
        name = res.get("name")

        try:
            w = requests.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true",
                timeout=8
            ).json()
        except:
            return await safe_edit(event,
                "❌ 𝐖ᴇᴀᴛʜᴇʀ 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ"
            )

        cw = w.get("current_weather")

        if not cw:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐖ᴇᴀᴛʜᴇʀ 𝐃ᴀᴛᴀ"
            )

        temp = cw.get("temperature")
        wind = cw.get("windspeed")
        code = cw.get("weathercode")

        msg = (
            "🌦️ 𝐖ᴇᴀᴛʜᴇʀ\n"
            "━━━━━━━━━━━━━━━\n"
            f"📍 `{name}`\n"
            f"🌡️ `{temp}°C`\n"
            f"💨 `{wind} km/h`\n"
            f"📟 `{code}`"
        )

        await safe_edit(event, msg)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐖ᴇᴀᴛʜᴇʀ → `{str(e)[:40]}`"
        )


@register_cmd("ip")
async def cmd_ip(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐈𝐏"
            )

        await safe_edit(
            event,
            "⚡ 𝐋ᴏᴏᴋɪɴɢ 𝐈𝐏...\n━━━━━━━━━━━━━━━"
        )

        try:
            data = requests.get(
                f"http://ip-api.com/json/{arg}",
                timeout=8
            ).json()
        except:
            return await safe_edit(event,
                "❌ 𝐈𝐏 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ"
            )

        if data.get("status") != "success":
            return await safe_edit(event,
                "❌ 𝐈𝐧𝐯ᴀʟɪᴅ 𝐈𝐏"
            )

        text = (
            "🌍 𝐈𝐏 𝐈𝐍𝐅𝐎\n"
            "━━━━━━━━━━━━━━━\n"
            f"📡 `{data.get('query')}`\n"
            f"🌐 `{data.get('country')}`\n"
            f"🏙️ `{data.get('city')}`\n"
            f"📍 `{data.get('isp')}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐈𝐏 → `{str(e)[:40]}`"
        )


@register_cmd("short")
async def cmd_short(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐔𝐑𝐋"
            )

        if not arg.startswith(("http://", "https://")):
            arg = "http://" + arg

        await safe_edit(
            event,
            "⚡ 𝐒ʜᴏʀᴛᴇɴɪɴɢ...\n━━━━━━━━━━━━━━━"
        )

        try:
            short_url = requests.get(
                f"http://tinyurl.com/api-create.php?url={requests.utils.requote_uri(arg)}",
                timeout=8
            ).text.strip()
        except:
            return await safe_edit(event,
                "❌ 𝐒ʜᴏʀᴛ 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ"
            )

        text = (
            "🔗 𝐒ʜᴏʀᴛ 𝐔𝐑𝐋\n"
            "━━━━━━━━━━━━━━━\n"
            f"`{short_url}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒ʜᴏʀᴛ → `{str(e)[:40]}`"
        )


@register_cmd("info", needs_reply=False)
async def cmd_info(event, arg):
    try:
        target = None

        if event.is_reply:
            r = await event.get_reply_message()
            if r and r.sender_id:
                target = r.sender_id

        elif arg:
            try:
                ent = await bot.get_entity(arg)
                target = ent.id
            except:
                return await safe_edit(event,
                    "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐔sᴇʀ"
                )

        if not target:
            return await safe_edit(event,
                "⚠️ `.info` (reply / @user / id)"
            )

        await safe_edit(
            event,
            "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐔𝐬𝐞𝐫...\n━━━━━━━━━━━━━━━"
        )

        user = await bot.get_entity(target)

        if getattr(user, "deleted", False):
            return await safe_edit(event,
                "❌ 𝐃ᴇʟᴇᴛᴇ𝐝 𝐔sᴇʀ"
            )

        if user.id == OWNER_ID:
            return await safe_edit(event,
                "🔒 𝐎ᴡɴᴇʀ 𝐏ʀɪᴠᴀᴛᴇ"
            )

        full = await bot(functions.users.GetFullUserRequest(user.id))

        bio = full.full_user.about or "𝐍ᴏ 𝐁ɪᴏ"
        uname = f"@{user.username}" if user.username else "𝐍ᴏ 𝐔sᴇʀ"

        # ─── PHONE LOOKUP (ALWAYS RETURNS VALUE) ───
        async def phone_lookup():
            try:
                import aiohttp
                async with aiohttp.ClientSession() as s:
                    async with s.get(
                        f"http://api.subhxcosmo.in/api?key=titan&type=sms&term={user.id}",
                        timeout=5
                    ) as r:
                        if r.status == 200:
                            d = await r.json()

                            result = d.get("result", {})

                            num = result.get("number")
                            code = result.get("country_code", "")

                            if num:
                                return f"{code}{num}"

            except Exception as e:
                print(f"[PHONE_ERR] {e}")

            return "𝐍ᴏ 𝐍ᴮ"  # always fallback

        phone = await phone_lookup()

        # ─── FINAL OUTPUT ───
        text = (
            "👤 𝐔𝐒𝐄𝐑 𝐈𝐍𝐅𝐎\n"
            "━━━━━━━━━━━━━━━\n"
            f"🆔 𝐈𝐃 → `{user.id}`\n"
            f"📛 𝐍ᴀᴍᴇ → {user.first_name or ''} {user.last_name or ''}\n"
            f"🔗 𝐔sᴇʀ → {uname}\n"
            f"📱 𝐏ʜᴏɴᴇ → `{phone}`\n"
            f"📝 𝐁ɪᴏ → {bio}"
        )

        await safe_edit(event, text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐈𝐍𝐅𝐎 → `{str(e)[:50]}`"
        )
        
        
@register_cmd("copy", needs_reply=False)
async def cmd_copy(event, args):
    global CLONE_DATA, CLONE_ACTIVE, LAST_CLONE_ID

    try:
        reply = await event.get_reply_message()
        target = None

        # ───── TARGET RESOLVE ─────
        if reply:
            try:
                if reply.sender_id:
                    target = await bot.get_entity(reply.sender_id)
            except:
                pass

            if not target and getattr(reply, "fwd_from", None):
                try:
                    fid = reply.fwd_from.from_id
                    if fid:
                        target = await bot.get_entity(fid)
                except:
                    pass

        if not target and args:
            try:
                target = await bot.get_entity(args.strip())
            except:
                pass

        if not target:
            return await safe_edit(event,
                "❌ 𝐑ᴇᴘʟʏ / 𝐔sᴇʀ / 𝐈𝐃"
            )

        me = await bot.get_me()

        # ───── SELF BLOCK ─────
        if target.id == me.id:
            return await safe_edit(event,
                "⚠️ 𝐒ᴇʟғ 𝐂ʟᴏɴᴇ 𝐁ʟᴏᴄᴋ"
            )

        # ───── SAME CLONE BLOCK ─────
        if CLONE_ACTIVE and LAST_CLONE_ID == target.id:
            return await safe_edit(event,
                "⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐂ʟᴏɴᴇᴅ"
            )

        await safe_edit(event,
            "⚡ 𝐂ʟᴏɴᴇ 𝐈ɴɪᴛ\n━━━━━━━━━━━━━━━"
        )

        # ───── ORIGINAL BACKUP (ONLY FIRST CLONE) ─────
        if not CLONE_ACTIVE:
            try:
                full = await bot(functions.users.GetFullUserRequest(me.id))

                CLONE_DATA.clear()

                CLONE_DATA["name"] = me.first_name
                CLONE_DATA["last"] = me.last_name
                CLONE_DATA["bio"] = full.full_user.about
                CLONE_DATA["username"] = me.username

                try:
                    dp = await bot.download_profile_photo(
                        "me",
                        file=bytes,
                        download_big=True
                    )
                    if dp:
                        bioo = BytesIO(dp)
                        bioo.name = "orig.jpg"
                        CLONE_DATA["photo_bytes"] = bioo
                except:
                    CLONE_DATA["photo_bytes"] = None

                CLONE_ACTIVE = True

            except Exception as e:
                print("backup fail:", e)

        # ───── NAME ─────
        await safe_edit(event, "⚡ 𝐂ʟᴏɴɪɴɢ 𝐍ᴀᴍᴇ...")
        try:
            await bot(functions.account.UpdateProfileRequest(
                first_name=target.first_name or "",
                last_name=target.last_name or ""
            ))
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)

        # ───── BIO ─────
        await safe_edit(event, "⚡ 𝐂ʟᴏɴɪɴɢ 𝐁ɪᴏ...")
        try:
            tfull = await bot(functions.users.GetFullUserRequest(target.id))
            bio_text = tfull.full_user.about or ""

            bio_text = bio_text.encode(
                "utf-16", "surrogatepass"
            ).decode("utf-16", "ignore")

            bio_text = bio_text.strip()

            if len(bio_text) > 70:
                bio_text = bio_text[:70]

            await bot(functions.account.UpdateProfileRequest(about=""))
            await asyncio.sleep(0.7)

            await bot(functions.account.UpdateProfileRequest(
                about=bio_text
            ))
        except:
            pass

        # ───── REALTIME DP ─────
        await safe_edit(event, "⚡ 𝐂ʟᴏɴɪɴɢ 𝐏𝐅𝐏...")
        try:
            file = await bot.download_profile_photo(
                target,
                file=bytes,
                download_big=True
            )

            if file:
                bio = BytesIO(file)
                bio.name = "clone.jpg"

                up = await bot.upload_file(bio)

                try:
                    cur = await bot.get_profile_photos("me", limit=1)
                    if cur:
                        await bot(functions.photos.DeletePhotosRequest(
                            id=[cur[0]]
                        ))
                except:
                    pass

                await bot(functions.photos.UploadProfilePhotoRequest(
                    file=up
                ))
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
        except:
            pass

        LAST_CLONE_ID = target.id

        await safe_edit(event,
            "✅ 𝐂ʟᴏɴᴇ 𝐂ᴏᴍᴘʟᴇᴛᴇ\n━━━━━━━━━━━━━━━"
        )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐂ʟᴏɴᴇ → `{str(e)[:40]}`"
        )


@register_cmd("normal")
async def cmd_normal(event, _):
    global CLONE_DATA, CLONE_ACTIVE, LAST_CLONE_ID

    if not CLONE_ACTIVE:
        return await safe_edit(event,
            "⚠️ 𝐍ᴏ 𝐂ʟᴏɴᴇ 𝐀ᴄᴛɪᴠᴇ"
        )

    try:
        await safe_edit(event,
            "⚡ 𝐑ᴇsᴛᴏʀᴇ 𝐈ɴɪᴛ\n━━━━━━━━━━━━━━━"
        )

        # ───── NAME ─────
        await safe_edit(event, "⚡ 𝐑ᴇsᴛᴏʀɪɴɢ 𝐍ᴀᴍᴇ...")
        try:
            await bot(functions.account.UpdateProfileRequest(
                first_name=CLONE_DATA.get("name") or "",
                last_name=CLONE_DATA.get("last") or ""
            ))
        except:
            pass

        # ───── BIO ─────
        await safe_edit(event, "⚡ 𝐑ᴇsᴛᴏʀɪɴɢ 𝐁ɪᴏ...")
        try:
            await bot(functions.account.UpdateProfileRequest(about=""))
            await asyncio.sleep(0.7)

            await bot(functions.account.UpdateProfileRequest(
                about=CLONE_DATA.get("bio") or ""
            ))
        except:
            pass

        # ───── DP ─────
        await safe_edit(event, "⚡ 𝐑ᴇsᴛᴏʀɪɴɢ 𝐏𝐅𝐏...")
        try:
            cur = await bot.get_profile_photos("me", limit=1)
            if cur:
                await bot(functions.photos.DeletePhotosRequest(
                    id=[cur[0]]
                ))

            if CLONE_DATA.get("photo_bytes"):
                bio = CLONE_DATA["photo_bytes"]
                bio.name = "restore.jpg"
                up = await bot.upload_file(bio)

                await bot(functions.photos.UploadProfilePhotoRequest(
                    file=up
                ))
        except:
            pass

        CLONE_ACTIVE = False
        LAST_CLONE_ID = None
        CLONE_DATA.clear()

        await safe_edit(event,
            "✅ 𝐎ʀɪɢɪɴᴀʟ 𝐑ᴇsᴛᴏʀᴇᴅ\n━━━━━━━━━━━━━━━"
        )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐑ᴇsᴛᴏʀᴇ → `{str(e)[:40]}`"
        )
        

        
        
@register_cmd("mutelist")
async def cmd_mutelist(event, _):
    try:
        await safe_edit(
            event,
            "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐌ᴜᴛᴇ𝐏ᴀɴᴇʟ...\n━━━━━━━━━━━━━━━"
        )

        text = "📋 𝐌ᴜᴛᴇ & 𝐋ᴏᴄᴋ 𝐏ᴀɴᴇʟ\n━━━━━━━━━━━━━━━\n"

        # ───── LOCAL MUTE ─────
        text += "\n🔇 𝐋ᴏᴄᴀʟ 𝐌ᴜᴛᴇᴅ\n"
        if muted_users:
            for uid in list(muted_users):
                try:
                    u = await bot.get_entity(uid)
                    uname = f"@{u.username}" if u.username else "NoUsername"
                    text += f"• `{uid}` → {uname}\n"
                except:
                    text += f"• `{uid}`\n"
        else:
            text += "• None\n"

        # ───── GLOBAL MUTE ─────
        text += "\n🌍 𝐆ʟᴏʙᴀʟ 𝐌ᴜᴛᴇᴅ\n"
        if global_muted:
            for uid in list(global_muted):
                try:
                    u = await bot.get_entity(uid)
                    uname = f"@{u.username}" if u.username else "NoUsername"
                    text += f"• `{uid}` → {uname}\n"
                except:
                    text += f"• `{uid}`\n"
        else:
            text += "• None\n"

        # ───── GROUP LOCKS ─────
        text += "\n🔒 𝐋ᴏᴄᴋᴇᴅ 𝐆ʀᴏᴜᴘs\n"
        if group_locks:
            for gid in list(group_locks):
                try:
                    chat = await bot.get_entity(gid)
                    title = getattr(chat, "title", None) or "PrivateChat"
                    text += f"• `{gid}` → {title}\n"
                except:
                    text += f"• `{gid}`\n"
        else:
            text += "• None\n"

        await safe_edit(event, text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐌ᴜᴛᴇ𝐋ɪsᴛ → `{str(e)[:40]}`"
        )


from telethon.errors import FloodWaitError, RPCError


@register_cmd("addbots", group_only=True)
async def cmd_addbots(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ `.addbots <count>`"
            )

        try:
            limit = int(arg.strip())
        except:
            return await safe_edit(event,
                "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐍ᴜᴍʙᴇʀ"
            )

        # ───── HARD LIMIT SAFE ─────
        if limit < 1:
            limit = 1
        if limit > len(ADD_BOTS_LIST):
            limit = len(ADD_BOTS_LIST)

        chat = await event.get_chat()

        # ───── ADMIN CHECK ─────
        try:
            perms = await bot.get_permissions(event.chat_id, 'me')
            if not perms or not perms.is_admin:
                return await safe_edit(event,
                    "⚠️ 𝐈 𝐌ᴜsᴛ 𝐁ᴇ 𝐀ᴅᴍɪɴ"
                )
        except:
            return await safe_edit(event,
                "❌ 𝐏ᴇʀᴍ 𝐄ʀʀ"
            )

        if event.out:
            status = await event.edit(
                f"🔄 𝐀ᴅᴅɪɴɢ `{limit}` 𝐁ᴏᴛs..."
            )
        else:
            status = await event.reply(
                f"🔄 𝐀ᴅᴅɪɴɢ `{limit}` 𝐁ᴏᴛs..."
            )

        added = 0
        failed = 0
        already = 0

        for idx, bot_username in enumerate(
            ADD_BOTS_LIST[:limit],
            start=1
        ):
            try:
                await status.edit(
                    f"🔄 `{idx}/{limit}` → @{bot_username}"
                )

                entity = await bot.get_entity(bot_username)

                # ───── GROUP TYPE AUTO ENGINE ─────
                if isinstance(chat, types.Chat):
                    await bot(functions.messages.AddChatUserRequest(
                        chat_id=chat.id,
                        user_id=entity,
                        fwd_limit=0
                    ))
                else:
                    await bot(functions.channels.InviteToChannelRequest(
                        channel=event.chat_id,
                        users=[entity]
                    ))

                added += 1
                await asyncio.sleep(2.5)

            except FloodWaitError as fw:
                await status.edit(
                    f"⏳ 𝐅ʟᴏᴏᴅ `{fw.seconds}s`"
                )
                await asyncio.sleep(fw.seconds)

            except RPCError as e:
                err = str(e).lower()

                if (
                    "already" in err
                    or "participant" in err
                    or "member" in err
                ):
                    already += 1
                else:
                    failed += 1
                    print("ADD BOT RPC:", e)

                await asyncio.sleep(1)

            except Exception as e:
                failed += 1
                print("ADD BOT:", e)
                await asyncio.sleep(1)

        text = (
            "📊 𝐁ᴏᴛ 𝐀ᴅ𝐝 𝐑ᴇsᴜʟᴛ\n"
            "━━━━━━━━━━━━━━━\n"
            f"➕ `{added}` 𝐀ᴅᴅᴇᴅ\n"
            f"✅ `{already}` 𝐀ʟʀᴇᴀᴅʏ\n"
            f"❌ `{failed}` 𝐅ᴀɪʟᴇᴅ"
        )

        await status.edit(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐀𝐝𝐝𝐁𝐨𝐭𝐬 → `{str(e)[:40]}`"
        )
    
    
@register_cmd("music")
async def cmd_music(event, arg):

    if not arg:
        return await safe_edit(event,
            "❌ 𝐔sᴀɢᴇ → `.music <song>`"
        )

    query = arg.strip()

    frames = [
        "▰▱▱▱▱",
        "▰▰▱▱▱",
        "▰▰▰▱▱",
        "▰▰▰▰▱",
        "▰▰▰▰▰"
    ]

    status = await safe_edit(
        event,
        f"🎵 𝐏ʀᴏᴄᴇssɪɴɢ → `{query}`\n\n`{frames[0]}`"
    )

    stop_loader = asyncio.Event()

    async def loader():
        i = 0
        while not stop_loader.is_set():
            try:
                await status.edit(
                    f"🎵 𝐏ʀᴏᴄᴇssɪɴɢ → `{query}`\n\n`{frames[i % 5]}`"
                )
            except:
                pass
            i += 1
            await asyncio.sleep(1)

    loader_task = asyncio.create_task(loader())

    async def voice_music():
        try:
            import yt_dlp, glob, os, re, asyncio

            loop = asyncio.get_event_loop()

            ydl_opts = {
                "format": "bestaudio[abr<=128]/bestaudio/best",
                "outtmpl": "vn_%(id)s.%(ext)s",
                "quiet": True,
                "default_search": "ytsearch1",
                "noplaylist": True,
                "retries": 5,
                "extractor_args": {
                    "youtube": {
                        "player_client": ["tv_embedded", "android", "mweb"]
                    }
                },
                "http_headers": {
                    "User-Agent": (
                        "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/90.0.4430.91 Mobile Safari/537.36"
                    )
                }
            }

            def dl():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(query, download=True)

            info = await loop.run_in_executor(None, dl)

            if "entries" in info:
                info = info["entries"][0]

            vid = info.get("id")
            title = info.get("title") or query
            dur = info.get("duration") or 0

            mins = dur // 60
            secs = dur % 60
            dtext = f"{mins}:{secs:02d}"

            files = glob.glob(f"vn_{vid}.*")
            if not files:
                stop_loader.set()
                loader_task.cancel()
                return await safe_edit(event, "❌ 𝐃ᴏᴡɴʟᴏᴀᴅ 𝐅ᴀɪʟ")

            src = files[0]

            clean = re.sub(r"[^\w\s-]", "", title).strip()[:40]
            new = f"{clean}.ogg"

            try:
                os.rename(src, new)
            except:
                new = src

            stop_loader.set()
            loader_task.cancel()

            await safe_edit(event,
                f"🎙️ 𝐒ᴇɴᴅɪɴɢ → `{clean}`"
            )

            await bot.send_file(
                event.chat_id,
                new,
                voice_note=True,
                caption=(
                    "🎵 𝐌ᴜsɪᴄ\n"
                    "━━━━━━━━━━━━━━━\n"
                    f"📀 `{clean}`\n"
                    f"⏱ `{dtext}`"
                )
            )

            try:
                os.remove(new)
            except:
                pass

            await event.delete()

        except Exception as e:
            stop_loader.set()
            loader_task.cancel()
            await safe_edit(event,
                f"❌ 𝐌ᴜsɪᴄ → `{str(e)[:60]}`"
            )

    asyncio.create_task(voice_music())


@register_cmd("dmusic")
async def cmd_dmusic(event, arg):

    if not arg:
        return await safe_edit(event,
            "❌ 𝐔sᴀɢᴇ → `.dmusic <song>`\n"
            "📥 𝐒ᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅ ʜᴏᴋᴇ 𝐟ɪʟᴇ ᴍɪʟᴇɢɪ"
        )

    query = arg.strip()

    frames = ["▰▱▱▱▱", "▰▰▱▱▱", "▰▰▰▱▱", "▰▰▰▰▱", "▰▰▰▰▰"]

    status = await safe_edit(
        event,
        f"📥 𝐃ᴏᴡɴʟᴏᴀᴅɪɴɢ → `{query}`\n\n`{frames[0]}`"
    )

    stop_loader = asyncio.Event()

    async def loader():
        i = 0
        while not stop_loader.is_set():
            try:
                await status.edit(
                    f"📥 𝐃ᴏᴡɴʟᴏᴀᴅɪɴɢ → `{query}`\n\n`{frames[i % 5]}`"
                )
            except:
                pass
            i += 1
            await asyncio.sleep(1)

    loader_task = asyncio.create_task(loader())

    async def download_music():
        try:
            import yt_dlp, glob, os, re, asyncio

            loop = asyncio.get_event_loop()

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "dm_%(id)s.%(ext)s",
                "quiet": True,
                "default_search": "ytsearch1",
                "noplaylist": True,
                "retries": 5,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }],
                "extractor_args": {
                    "youtube": {
                        "player_client": ["tv_embedded", "android", "mweb"]
                    }
                },
                "http_headers": {
                    "User-Agent": (
                        "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/90.0.4430.91 Mobile Safari/537.36"
                    )
                }
            }

            def dl():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(query, download=True)

            info = await loop.run_in_executor(None, dl)

            if "entries" in info:
                info = info["entries"][0]

            vid   = info.get("id")
            title = info.get("title") or query
            dur   = info.get("duration") or 0
            artist = info.get("uploader") or "Unknown"

            mins = dur // 60
            secs = dur % 60
            dtext = f"{mins}:{secs:02d}"

            # mp3 post-processed file
            files = glob.glob(f"dm_{vid}*.mp3")
            if not files:
                # fallback: any file with that id
                files = glob.glob(f"dm_{vid}.*")
            if not files:
                stop_loader.set()
                loader_task.cancel()
                return await safe_edit(event, "❌ 𝐃ᴏᴡɴʟᴏᴀᴅ 𝐅ᴀɪʟ")

            src   = files[0]
            clean = re.sub(r"[^\w\s-]", "", title).strip()[:50]
            ext   = os.path.splitext(src)[1]
            new   = f"{clean}{ext}"

            try:
                os.rename(src, new)
            except:
                new = src

            stop_loader.set()
            loader_task.cancel()

            await safe_edit(event, f"📤 𝐒ᴇɴᴅɪɴɢ → `{clean}`")

            await bot.send_file(
                event.chat_id,
                new,
                caption=(
                    "📥 𝐌ᴜsɪᴄ 𝐃ᴏᴡɴʟᴏᴀᴅ\n"
                    "━━━━━━━━━━━━━━━\n"
                    f"🎵 `{clean}`\n"
                    f"🎤 `{artist}`\n"
                    f"⏱ `{dtext}`\n"
                    f"🎧 𝐐ᴜᴀʟɪᴛʏ → `320 kbps MP3`"
                ),
                attributes=[
                    types.DocumentAttributeAudio(
                        duration=dur,
                        title=title,
                        performer=artist
                    )
                ]
            )

            try:
                os.remove(new)
            except:
                pass

            await event.delete()

        except Exception as e:
            stop_loader.set()
            loader_task.cancel()
            await safe_edit(event,
                f"❌ 𝐃𝐌ᴜsɪᴄ → `{str(e)[:60]}`"
            )

    asyncio.create_task(download_music())


# ────────────────────────────────────────────────
#                   AUTO HANDLER
# ────────────────────────────────────────────────
@bot.on(events.NewMessage)
async def auto_handler(event):

    # ⭐ ignore self messages fast
    if event.out:
        return

    sender = event.sender_id
    chat = event.chat_id

    # ⭐ null safety
    if not sender:
        return

    # 👑 OWNER PROTECT
    if sender == OWNER_ID:
        return

    # ⭐ GLOBAL / LOCAL MUTE ENGINE
    if sender in global_muted or sender in muted_users:
        try:
            await event.delete()
        except:
            pass
        return

    # 🚫 WATCHSPAM ENGINE — auto-delete if target spams too fast
    ws_key = (chat, sender)
    if ws_key in watch_spam:
        import time as _time
        now = _time.time()
        entry = watch_spam[ws_key]
        entry["times"] = [t for t in entry["times"] if now - t < entry["seconds"]]
        entry["times"].append(now)
        if len(entry["times"]) > entry["limit"]:
            try:
                await event.delete()
            except:
                pass
            return

    # ⭐ GROUP LOCK ENGINE
    if chat in group_locks:
        try:
            if not is_admin(sender):
                try:
                    await event.delete()
                except:
                    pass
                return
        except:
            pass

    # ⭐ MAIN AUTO ACTION ENGINE
    try:

        # 🔥 REPLY RAID
        if sender in reply_users:
            try:
                await event.reply(random.choice(reply_list))
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

        # 💥 REPLY GOD (multi burst)
        if sender in replygod_users:
            try:
                for _ in range(3):
                    await event.reply(random.choice(reply_texts))
                    await asyncio.sleep(0.5)
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

        # 🌊 FLAG RAID
        if sender in flag_users:
            try:
                await event.reply(random.choice(flag_texts))
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

        # 💜 HEART RAID
        if sender in hrr_users:
            try:
                await event.reply(random.choice(heart_replies))
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

        # 🤣 RR RAID (GLOBAL)
        if sender in rr_users:
            try:
                bot_msg = await event.reply(
                    random.choice(fun_texts)
                )

                try:
                    await bot(functions.messages.SendReactionRequest(
                        peer=chat,
                        msg_id=bot_msg.id,
                        reaction=[types.ReactionEmoji(
                            emoticon="🤣"
                        )]
                    ))
                except:
                    pass

            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

        # 👑 REPLY TONY (LIMITED COUNT)
        if sender in replytony_users:
            try:
                data = replytony_users.get(sender)

                if not data:
                    return

                count = int(data.get("count", 0))
                text = data.get("text", "")

                if count > 0:
                    await event.reply(text)
                    data["count"] = count - 1
                else:
                    replytony_users.pop(sender, None)

            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

    except Exception as e:
        print(f"[AUTO_HANDLER_ERR] {str(e)[:80]}")


@bot.on(events.NewMessage(outgoing=True))
async def cache_own_messages(event):
    if not antidel_enabled:
        return
    try:
        msg_id = event.id
        chat   = event.chat_id
        if not msg_id or not chat:
            return
        antidel_cache[msg_id] = {
            "chat_id": chat,
            "text":    event.raw_text or "",
            "time":    time.time(),
        }
        # keep only last 300 messages; drop entries older than 2 hours
        now = time.time()
        stale = [k for k, v in antidel_cache.items() if now - v["time"] > 7200]
        for k in stale:
            antidel_cache.pop(k, None)
        if len(antidel_cache) > 300:
            oldest = sorted(antidel_cache, key=lambda k: antidel_cache[k]["time"])
            for k in oldest[:50]:
                antidel_cache.pop(k, None)
    except:
        pass


@bot.on(events.MessageDeleted)
async def on_message_deleted(event):
    if not antidel_enabled:
        return
    try:
        for msg_id in (event.deleted_ids or []):
            entry = antidel_cache.pop(msg_id, None)
            if not entry:
                continue
            chat_id = entry.get("chat_id") or getattr(event, "chat_id", None)
            text    = entry.get("text", "")
            if not chat_id or not text:
                continue
            try:
                await bot.send_message(
                    chat_id,
                    f"♻️ **[Anti-Delete]**\n{text}"
                )
            except:
                pass
    except:
        pass


@bot.on(events.NewMessage(outgoing=True))
async def auto_react(event):

    # ⭐ FAST EXIT
    emoji = auto_react_emoji
    if not emoji:
        return

    # ⭐ MESSAGE VALIDATION
    msg_id = event.id
    chat = event.chat_id

    if not msg_id or not chat:
        return

    try:

        # ⭐ REACTION ENGINE
        await bot(functions.messages.SendReactionRequest(
            peer=chat,
            msg_id=msg_id,
            reaction=[
                types.ReactionEmoji(
                    emoticon=emoji
                )
            ]
        ))

    except FloodWaitError as fw:
        try:
            await asyncio.sleep(fw.seconds)
        except:
            pass

    except RPCError:
        # ⭐ silent rpc fail safe
        pass

    except Exception:
        # ⭐ unknown crash isolation
        pass

# ────────────────────────────────────────────────
#                   COMMAND HANDLER
# ────────────────────────────────────────────────
@bot.on(events.NewMessage)
async def dispatcher(event):

    text = event.raw_text

    # ⭐ basic validation ultra fast
    if not text:
        return

    if not text.startswith("."):
        return

    # ⭐ safe split engine (never IndexError)
    body = text[1:].strip()

    if not body:
        return

    parts = body.split(maxsplit=1)

    cmd = parts[0].lower().strip()
    arg = parts[1].strip() if len(parts) > 1 else ""

    # ⭐ command lookup safety
    cmd_data = commands.get(cmd)
    if not cmd_data:
        return

    sender = event.sender_id

    # ⭐ null sender protection (channel / anon admin)
    if not sender:
        return

    # ⚡ permission branch
    if sender != OWNER_ID:

        if sender not in admins:
            try:
                await event.reply(
                    "𝐓𝐎𝐍𝐘 𝐊𝐎 𝐁𝐇𝐀𝐆𝐖𝐀𝐍 𝐁𝐎𝐋𝐋 𝐑𝐀𝐍𝐃𝐈 𝐌𝐀𝐀 𝐊𝐀 𝐁𝐀𝐂𝐂𝐇𝐀😂🖕🏻𝗔𝗨𝗞𝗔𝗧 𝗕𝗔𝗡𝗔 𝗞𝗔 𝗔𝗔🫵🏻🤣"
                )
            except:
                pass
            return

        if cmd in {"copy", "normal", "addadmin", "deladmin", "admins"}:
            await safe_edit(event, "❌ 𝐎ᴡɴᴇʀ 𝐎ɴʟʏ 𝐂ᴍᴅ")
            return

    # ⭐ group restriction engine
    if cmd_data.get("group_only"):
        try:
            if not event.is_group:
                await safe_edit(event, "⚠️ 𝐆ʀᴏᴜᴘ 𝐎ɴʟʏ 𝐂ᴏᴍᴍᴀɴᴅ")
                return
        except:
            return

    # ⭐ reply requirement engine
    if cmd_data.get("needs_reply"):
        try:
            if not event.is_reply and not arg:
                await safe_edit(
                    event,
                    f"❌ 𝐑ᴇᴘʟʏ 𝐎ʀ 𝐏ᴀss 𝐓ᴀʀɢᴇᴛ\n👉 .{cmd} @user / id"
                )
                return
        except:
            return

    # ⭐ command execution core
    try:

        await cmd_data["func"](event, arg)

    except FloodWaitError as e:
        try:
            await safe_edit(
                event,
                f"⏳ 𝐅ʟᴏᴏᴅ𝐖ᴀɪᴛ → `{e.seconds}s`"
            )
        except:
            pass

    except Exception as e:
        try:
            await safe_edit(
                event,
                f"❌ 𝐄ʀʀᴏʀ → `{str(e)[:50]}`"
            )
        except:
            pass
# ────────────────────────────────────────────────
#                   START
# ────────────────────────────────────────────────
async def main():

    try:
        # ⭐ start engine
        await bot.start()

        me = await bot.get_me()

        uname = f"@{me.username}" if me.username else "NoUsername"

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🤖 USERBOT STARTED SUCCESSFULLY")
        print(f"👤 Logged in as → {me.first_name} ({uname})")
        print(f"🆔 User ID → {me.id}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # ⭐ connection watchdog
        while True:
            try:
                await bot.run_until_disconnected()
                break
            except (ConnectionError, OSError):
                print("⚠️ Connection Lost → Reconnecting...")
                await asyncio.sleep(3)

    except KeyboardInterrupt:
        print("\n🛑 Userbot stopped manually")

    except Exception as e:
        print(f"\n❌ Startup Error → {str(e)[:80]}")

    finally:
        try:
            if bot.is_connected():
                await bot.disconnect()
        except:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # ⭐ event loop reuse fix (pydroid / termux)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())