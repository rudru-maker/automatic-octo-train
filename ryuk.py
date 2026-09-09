import asyncio
import random
import time
import json
import sqlite3
import os
import psutil
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

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

# === CONFIG ===
BOT_TOKENS = [
    "8817990041:AAHO8Pl6mpe-8HAm5caVKCzX47772jGxRS0",                                    
    "8844625791:AAHvdHIK1Qp_FOsTTJgvZGQ-V-fdSliAkfA",                                                                                  
    "8890606582:AAHq_Xa9e801jDH_H_NMlhLx8NDFnL2RhY0",                                                                      
    "8934529784:AAHKaXATwSjUxI7gcNW277Qbm3-zCSylafo",                                                                      
    "8976613089:AAHV7Dvfl9cVNjrKA9l4xoM8PI0dYVk6g1Q",                                                                        
    "8904628926:AAF2KGLovmYcswQA1uUKSOMUzfCxjjYYn44",                                                                     
    "8293294399:AAEFra8RfVjym81m6iWt_oZGleSFTz5bCFs",                                                                          
    "8515468943:AAGg_xamts80w1NNPwMGH9365MdZGo3jM-w",                                                                         
    "8843363442:AAFFaN4uzc3W5xVECIvPnI-0uma46MKGKhs",                                                                  
    "8765836494:AAFowURaxfhLA8YZaw22ncLz92aPdPEX3iY",
]

OWNER_ID = 8996032103

class Controller:
    def __init__(self):
        self.admins = db.get_admins()
        self.master = db.get_setting("master", OWNER_ID)
        self.prefix = "》"
        self.menu_video = db.get_setting("menu_video", None)
        self.menu_image = db.get_setting("menu_image", None)
        self.secret_password = db.get_setting("secret_password", "slay")
        self.cluster_active = db.get_setting("cluster_active", True)
        self.admins.add(OWNER_ID)
        db.save_admin(OWNER_ID)
        db.save_authorized(OWNER_ID)

controller = Controller()

# Sudo users list
sudo_users = []

# Custom roast
CUSTOM_REPLIES = {
    "R1": "😂🍎 **LIGHT YAGAMI:** 'Kira's domain is sealed. Know your place, human.' 📓",
    "R2": "🖤 **RYUK:** *Laughs eating an apple* 'You really thought you could bypass Kira without the notebook?' 🍎",
    "R3": "⚡ **DEATH NOTE:** 'Unauthorized soul detected. Write your name in the sand instead.' 💀"
}
selected_roast = "R1"

# Individual NC flags
nc_flags = {
    "smallnc": False, "customnc": False, "hugenc": False, "hugenc2": False,
    "midnc": False, "italicnc": False, "angrync": False, "flowernc": False,
    "lovenc": False, "cursivenc": False, "jdnc": False
}
nc_tasks = {}
nc_content = {}

# Spam flags
spam_active = False
spam_task = None
current_spam_text = None
spam_chat_id = None
spam_mode = "normal"
spam_target = None

# Picture flags
pic_spam_active = False
pic_spam_task = None
pic_spam_chat_id = None

pic_changer_active = False
pic_changer_task = None
pic_changer_chat_id = None
pic_changer_delay = 0.0001
pic_changer_mode = "together"

# Multi-GC flags
multi_gc_groups = []
grpspam_active = False
grpspam_task = None

# Slide tracking
slide_active = {}

# Store all bot applications
bot_apps = []

# Wave delay set to ultra-fast 0.0001s as requested
wave_delay = 0.0001

# Start time
START_TIME = time.time()

# Picture storage
saved_pictures = []

HEART_EMOJIS = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔", "❤️‍🔥", "❤️‍🩹", "💖", "💗", "💓", "💕", "💞", "💘", "💝"]

# ============================================================
# ==================== SPAM LINES SECTION ====================
# ============================================================

BIGSPAM_LINES = [
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________",
    "{text} 𝐓ᴇʀ𝐈 𝐑🔺ɴᴅ𝐈 𝐌ᴀ𝐀 𝐊ɪ 𝐂ʜᴜ𝐓 𝐁ᴀᴊᴀ𝐔 🥁🔥🥁🔥🥁🔥  : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. 3'
]

AAYUSPAM_LINES = [
    "<{text}> Oʏᴇ Rɴᴅʏᴋ Tᴇʀɪ Mᴀᴀ Bᴇʜᴇɴ Cʜᴏᴅ Dᴇɴɢᴇ !🩷>ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ<{text}> Oʏᴇ Rɴᴅʏᴋ Tᴇʀɪ Mᴀᴀ Bᴇʜᴇɴ Cʜᴏᴅ Dᴇɴɢᴇ !🩷",
    "<{text}> Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ !🎀>ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ<{text}> Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ !🎀",
    "<{text}> TᴇʀI MᴀA Kɪ CʜᴜT Pᴇ MᴜᴋᴋE MᴀʀᴜɴɢA !🩵>ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ<{text}> TᴇʀI MᴀA Kɪ CʜᴜT Pᴇ MᴜᴋᴋE MᴀʀᴜɴɢA !🩵",
    "{text} 𑁍ࠬܓ<💛> ᴛᴇʀɪ ᴍᴀ 𝜗𝜚⋆₊𝘛𝘰𝘯y ᴋɪ ꜰᴀɴɢɪʀʟ ˚₊· ‌➳❥ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  {text} 𑁍ࠬܓ<💛> ᴛᴇʀɪ ᴍᴀ 𝜗𝜚⋆₊𝘛𝘰𝘯y ᴋɪ ꜰᴀɴɢɪʀʟ ˚₊· ‌"
]

MULTI_GC_SPAM_LINES = [
    "✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ?? 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {text} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀ"
]

MULTI_GC_NC_TEMPLATES = [
    "(🎀) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(🔥) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(⚡) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(❄) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(🪐) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(☄️) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(☀) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(☁️) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(🌊) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(🌙) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(🦚) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(🍀) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(🚀) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(🦋) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(✈️) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(🎸) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(🎏) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(🎗) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 ",
    "(😂) {Text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑 "
]

SMALL_ABUSES = [
    "{text} Hᴇʏ Mғ I'ʟʟ Fᴜᴄᴋ Yᴏᴜʀ Mᴏᴍ Sᴏ Hᴀʀᴅ Tʜᴀᴛ Sʜᴇ Cᴀɴᴛ Eᴠᴇɴ Wᴀᴋᴇ Uᴘ ❕❔",
    "{text} Sʟᴜᴛ Gᴏ Asᴋ Uʀ Mᴏᴍ Wʜᴏ Is Yᴏᴜʀ Rᴇᴀʟ Dᴀᴅ❕❔",
    "{text} Yᴏᴜʀ Mᴏᴍᴍᴀ Gᴏᴛ A Gᴏᴏғʏ Gɪᴀɴᴛ Ass Lᴍᴀᴏ❕❔",
    "{text} Iᴍ Sᴏʀʀʏ Bᴜᴛ Yᴏᴜʀ Mᴏᴍ Dɪᴇᴅ Wʜɪʟᴇ Fᴜᴄᴋɪɴɢ Wɪᴛʜ Mᴇ❕❔",
    "{text} Hᴇʏ Sᴏɴ Oғ A Bɪᴛᴄʜ Gᴏ Cᴀʟʟ Yᴏᴜʀ Sɪs I Wᴀɴᴛ Tᴏ Fᴜᴄᴋ Hᴇʀ Bᴀᴅʟʏ❕❔"
]

HUGE_ABUSES = [
    "{text} RΛɴᴅʏᴋᴇ LΛᴅҡᴇ 🥴 𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫 ({time_loop})"
]

HUGE_ABUSES2 = [
    "{text} ᑕʜꪊD ꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅ ({heart})"
]

MID_ABUSES = [
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(🤍)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(🩵)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(🎀)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(🚠)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(🚀)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(☁️)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(💗)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(❤️)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(🩷)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(👑)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(❤️‍🩹)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(😭)",
    "{text} ᑕʜᴜƿ RΛɴᴅʏᴋΣ𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯(❤️‍🔥)"
]

ITALIC_ABUSES = [
    "{text} 𝘛𝘌𝘙𝘐 𝘔𝘈𝘈 𝘓𝘖𝘋𝘌 𝘗𝘌 😹👎",
    "{text} 𝘈𝘉𝘌 𝘖𝘠 𝘈𝘞𝘈𝘡 𝘕𝘐𝘊𝘏𝘌 💋👙",
    "{text} 𝘛𝘌𝘙𝘐 𝘉𝘌𝘏𝘌𝘕 𝘒𝘐 𝘊𝘏𝘜𝘋𝘈𝘐 𝘒𝘙𝘋𝘜𝘕𝘎𝘈 🤪🫵",
    "{text} 𝘏𝘈𝘛 𝘛𝘌𝘙𝘐 𝘔𝘈𝘈 𝘒𝘈 𝘉𝘏𝘖𝘚𝘋𝘈 🐐🚠",
    "{text} 𝘊𝘏𝘈𝘓 𝘛𝘌𝘙𝘐 𝘔𝘈𝘈 𝘙𝘈𝘕𝘋𝘠 𝘕𝘐𝘒𝘓𝘐 🌲🍂",
    "{text} 𝘛𝘌𝘙𝘐 𝘔𝘈𝘈 𝘒𝘌 𝘊𝘏𝘜𝘛 𝘗𝘙 𝘊𝘜𝘔 🐄🔥"
]

ANGRY_ABUSES = [
    "{text} अबे तेरी माँ की चूत 💢",
    "{text} तेरी बहन की चुदाई करुंगा 💢",
    "{text} तेरी बहन की चूत 💢",
    "{text} तेरा बाप टकला 💢",
    "{text} तू हिज्दा 💢",
    "{text} रंडी माँ का लड़का 💢"
]

FLOWER_ABUSES = [
    "×🌸×{text} CHUD×🌸×",
    "×🌼×{text} CHUD×🌼×",
    "×🌹×{text} CHUD×🌹×",
    "×🥀×{text} CHUD×🥀×",
    "×🌺×{text} CHUD×🌺×",
    "×🌻×{text} CHUD×🌻×",
    "×🌷×{text} CHUD×🌷×",
    "×🌹×{text} CHUD×🌹×",
    "×🏵×{text} CHUD×🏵×",
    "×💮×{text} CHUD×💮×",
    "×💐×{text} CHUD×💐×"
]

LOVE_ABUSES = [
    "x💋x {text} ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴅᴇᴋʜ ᴋʀ ᴍᴜᴛʜɪ ᴍʀʟɪʏᴀ x💋x",
    "x👄x {text} ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴅᴇᴋʜ ᴋʀ ᴍᴜᴛʜɪ ᴍʀʟɪʏᴀ x👄x",
    "x💓x {text} ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴅᴇᴋʜ ᴋʀ ᴍᴜᴛʜɪ ᴍʀʟɪʏᴀ x💓x",
    "x❤x {text} ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴅᴇᴋʜ ᴋʀ ᴍᴜᴛʜɪ ᴍʀʟɪʏᴀ x❤x",
    "x💕x {text} ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴅᴇᴋʜ ᴋʀ ᴍᴜᴛʜɪ ᴍʀʟɪʏᴀ x💕x",
    "x💗x {text} ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴅᴇᴋʜ ᴋʀ ᴍᴜᴛʜɪ ᴍʀʟɪʏᴀ x💗x",
    "x💖x {text} ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴅᴇᴋʜ ᴋʀ ᴍᴜᴛʜɪ ᴍʀʟɪʏᴀ x💖x",
    "x💝x {text} ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴅᴇᴋʜ ᴋʀ ᴍᴜᴛʜɪ ᴍʀʟɪʏᴀ x💝x"
]

CURSIVE_ABUSES = [
    "❤️ {text} 𝒯𝑒𝓇𝒾 𝓂𝒶𝒶 𝓇𝒶𝓃𝒹𝒾 ❤️",
    "💖 {text} 𝐵𝑒𝒽𝓃 𝒸𝒽𝑜𝒹 𝒸𝒽𝓊𝓉𝒾𝓎𝒶 💖",
    "💗 {text} 𝐿𝒶𝓃𝒹 𝓅𝑒 𝓃𝒶𝒸𝒽 𝓉𝑒𝓇𝒾 𝓂𝒶𝒶 💗",
    "💕 {text} 𝒞𝒽𝓊𝓅 𝒽𝑜 𝒿𝒶 𝒷𝑒𝓋𝓀𝓊𝒻 💕",
    "💓 {text} 𝒯𝑒𝓇𝒾 𝒷𝑒𝒽𝓃 𝓀𝒾 𝒸𝒽𝓊𝓉 𝓂𝑒𝓇𝒾 𝓁𝒶𝓃𝒹 𝒷𝑒 💓",
    "💘 {text} 𝑀𝒶𝒹𝒶𝓇𝒸𝒽𝑜𝒹 𝓈𝒶𝓁𝒶 𝓉𝓊 𝒽𝒾 𝒽𝒶𝒾 💘",
    "❤️‍🔥 {text} 𝒮𝒶𝓁𝑒 𝓉𝑒𝓇𝒾 𝓂𝒶𝒶 𝓀𝑜 𝒸𝒽𝑜𝒹𝓊𝓃𝑔𝒶 ❤️‍🔥",
    "💋 {text} 𝐵𝑒𝒽𝓃𝒸𝒽𝑜𝒹 𝓀𝒾 𝓃𝒶𝓊𝓀𝒶𝓁 𝒸𝒽𝓊𝓉𝒾𝓎𝒶 💋"
]

ANIMAL_EMOJIS = [
    "🐈‍⬛", "🦬", "🦣", "🦫", "🐻‍❄️", "🦤", "🦭", "🪲", "🪳", "🪰", "🦧", "🦮", "🐕‍🦺", 
    "🦥", "🦦", "🦨", "🦩", "🐒", "🦍", "🐶", "🐕", "🐩", "🐺", "🦊", "🦁", "🐯", "🐅", 
    "🐆", "🐎", "🦌", "🦄", "🐮", "🐂", "🐃", "🐄", "🐖", "🐗", "🐏", "🐑", "🐪", "🐘"
]

JDNC_TEMPLATES = [
    "~// {text} Bһᴀɢᴡᴀꪀ है ~//~ {animal_loop}"
]

SMALL_EMOJIS = ["🫣", "😭", "😮‍💨", "😋", "🥲", "🤬", "😂", "🤗", "😈", "🎃", "💀", "🔥", "💢", "👺"]
TIME_EMOJIS = ["🕐", "🕒", "🕕", "🕘", "⏳", "⌛", "🕛", "🕥", "🕞", "🕟", "🕦"]

SWIPE_TEXTS = [
    "{target} चुदाई Kha 😂❤️", 
    "{target} उठक बैठक लगा 😏🔥", 
    "{target} तेरी माँ चोदू 😍😍", 
    "{target} ओय कमजोर 🤢🤢", 
    "{target} लंड चूस 🥱🤍➿", 
    "{target} पिल्लै 🐕‍",
    "{target} 😱 arey 😉 ye 🤡 kaise 😋 kiya 😏 re 😁 teri 😊 maa 😍 randy 😭100% 😂",
    "कमजोर टट्टा",
    "👈🏻👆🏻🖖🏻👇🏻🤲🏻👉🏻🤏🏻 Idr Udr Jidr Bhi Dekhega Teri Randi Maa Dikhegi",
    "{target} 𝘽𝙀𝙏𝘼 🤢᭄᭄᭄᭄ 🌟 𝙇𝙐𝙉𝘿 𝘾𝙃𝙐𝗦 🤪᭄᭄",
    "{target} मदरचोद 🤮🤮", 
    "{target} ro 🤣🤣", 
    "{target} रंडी", 
    "{target} चुप tmr 😒😂",
    "{target} Acha Beta ? Koi Na Mai Teri Maa Coduga 😹💥💯", 
    "{target} चुदकड़", 
    "{target} कमजोर पिल्ले 🤮👞", 
    "{target} Chup Rndyce ⁉", 
    "{target} Tmkc Mein Mist Breathing ☁",
    "{target} Teri माँ Dead 😂😂😂", 
    "{target} Teri Maa Chodu If Yes Then Reply To My Message 😂😂💯💯",
    "{target} चल तेरी माँ की चुत 🥵🥵", 
    "{target} Tera बाप • ⚡𝓣𝓸𝓷𝔂⚡ ~ 💗...!!?"
]

SLIDE_TEXTS = [
    "पिल्ले Lᴜɴᴅ pe उछल ?🧡",
    "Jd baap hai rndyke",
    "_✍🏻 𝐘ᴇ 𝐃ᴇᴋʜ ˢᶜʳⁱᵖᵗ ˡⁱᵏʰ ʳᵃʰᵃ ʰᵘ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐁ʜᴏsᴅᴇ 𝐌ᴇɪɴ 😂😂😂",
    "Sᴜᴀʀ Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ 😌😌💤💤",
    "𝐓ᴜ 𝐈ᴅ𝐑 ??ᴏᴍᴇʙᴀᴄ𝐊 𝐃ᴇᴛ𝐀 𝐑ᴇ𝐇 𝐆ʏ𝐀 𝐔ᴅʜ𝐑 Jd 𝐓ᴇʀ𝐈 𝐌ᴀ𝐀 𝐂ʜᴏᴅ 𝐆ʏ𝐀 🩷🩶🩵",
    "Choding ho rhi hai teri maa ki 😬👨🏻‍💻🔥",
    "Teri Maa Ki Chut Mein Loda Daluga Beta 🥵💯",
    "🧐 Teri maa ka bh🤪sda dikh rha hai 😎",
    "😉🔥 Cya 😉🔥 re 😉 🔥 sapri 😉🔥 try 😉🔥 maa 😉🔥 tujh 😉🔥 nehlati 😉🔥 ny 😉🔥 ey 😉🔥 Cya 😉🔥",
    "Oye Madarchod Uth 😤😡🥵 Teri Maa Ka Choding Tem 😈👻🦶🏻",
    "Teri Maa Ko Football ⚽ bnake uske 𝗕??😈𝗦𝗗𝗘 pe laat 🦶🏻 marunga 🤩🔥",
    "इस मंगलवार को ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴋᴀ ʙʜᴀɴᴅᴀʀᴀ ʜᴏɢᴀ 😈😘👌🏻",
    "TᗴᖇI ᗰᗩᗩ Kᗩ ᗷOOᖇ ᗷᗴTᗩ 🤣🤮🔥😏🔥😂💞🌧️",
    "𝙈𝘼𝘼 𝙆𝙀 𝙇ODЕ 🤮",
    "𝗣ᴇʜʟ𝗘 𝗧ᴇʀ𝗜 𝗕ᴇʜᴇ𝗻 𝗖ʜოდᴜɢ𝗔 𝗙ɪ𝗥 𝗧ᴇʀ𝗜 𝗠ᴀ𝗔 😆😂😆🔥🤢😂🤍😤",
    "ƇӇƲƤ ƬЄƦƖ Mƛƛ Ƙƛ ƁӇƠƧƊƛ ♻️",
    "𝘚𝘱𝘢𝘮𝘮𝘦𝘳 𝘣𝘢𝘯𝘦𝘨𝘢 𝘳𝘢𝘯𝘥𝘪𝘬𝘦 🤢🔥",
    "𝐀ᴊ𝐀 𝐌ᴄ 𝐁ᴀɴᴀ𝐔 𝐓ᴜﺝʜ𝐄 𝐒ᴘᴀᴍᴍᴇ𝐑 👻💥🤍😹👑",
    "𝘣𝘰𝘭 #Jd 𝘉𝘢𝘢𝘱 👑",
    "😍 Teri 😡 Randi 🤪 Maa 😤 Ko 😎 Pel 😭 Dunga 😍",
    "Idhar Aa Beta 🤪💔 Teri Maa Chodu 😂😘",
    "Oye bihari kaam pe ja 🔥⛏️🔥⛏️🔥⛏️🔥⛏️💞💞🔥💞⛏️🔥💞⛏️⛏️",
    "Sᴄʀɪᴩᴛꜱ Kᴇɴɢ <> 𝓣𝓸𝓷𝔂🌸👑 !!",
    "Teri Maa Bio Mein #Proudrandi 💔🥀 likhti hai 🤩🔥🩷",
    "Rndyk lund se utr 😩👏🏻",
    "bot by nationmafias",
    "Tu hasta reh gya yaaro mein 😁💯💔 Teri maa chudgyi baazaro mein 😂🌹",
    "Teri Maa Chudwa denge re 🪖🔥⛏️🥴🤪💔🩷🩷💯😁😩💞",
    "🩷 Gud ❤️ nyt 🧡 rndyk 💛 kal 🩵 Aaunga 💙 Teri 🖤 Maa 🩶 Chodne 🤍",
    "🥶 Are 😱 Mc 😩 Ye 🤔 Kaise 🤪 Kiya 😏 Teri 😎 Maa 😬 Randi 🙄 Hai 🤮 100% 😂",
    "🩷🩵🤍🩶🖤❤️💚 Ye sare dill teri maa k naam beta 😂😜🔥",
    "Hat peche hat tera AAYU baap aya 😂😂🥴😹🤲🏻💪🏻",
    "Leave le rndyk psnd nai aya tu meko 🤢👎🏻",
    "Teri maa chodu 💯 if yes then reply to my message 💀💀💀💪🏻🔥💯👆🏻💔😂😂💔💔💔",
    "#𝓣𝓸𝓷𝔂 𝐁ᴀᴀᴘ 𝐊ᴏ 𝐃ʙᴀ ɴʜɪ 𝐏ᴀʀᴇ ᴄʏᴀ?? 🥶🥱😂",
    "😹 Tᴇʀɪ 🤪 Rᴀɴᴅɪ 😫 Mᴀᴀ 🤗 Kᴇ 🤢 Bᴜʀ 🤣 Pᴇ 😤 Lᴀᴀᴛ 🙄 Mᴀʀ 😆 Kᴇ 😍 Tᴇʀɪ 😍 Bᴇʜᴇɴ 😈 Cʜᴏᴅ 😅 Dᴜɢᴀ 🤩",
    "Gᴀʀᴇᴇʙ Ghar Ke Ladke Baap Log Ke Gc Mein Kya Krr Rha 🤢👞",
    "🔮 𝐘ᴇ 𝐃ᴇᴋʜ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ʜೋದ 𝐃ɪʏᴀ 😂🪄😂🪄",
    "Teri Maa Ko बाहुबली style mein chodunga 🥶💔🤪😹",
    "Tumhare Pitashree AAYU  💯🔥🗿🌙"
]

# === Helper Functions ===
def is_authorized(user_id):
    return user_id == OWNER_ID or user_id in sudo_users or db.is_authorized(user_id)

def get_unauthorized_msg():
    return CUSTOM_REPLIES.get(selected_roast, CUSTOM_REPLIES["R1"])

def generate_nc_name(nc_type: str, content: str) -> str:
    text = content
    if nc_type == "smallnc":
        template = random.choice(SMALL_ABUSES)
        emoji = random.choice(SMALL_EMOJIS)
        return template.format(text=text) + f" {emoji}"
    elif nc_type == "customnc":
        return text
    elif nc_type == "hugenc":
        time_loop = " ".join(random.choices(TIME_EMOJIS, k=1))
        template = random.choice(HUGE_ABUSES)
        return template.format(text=text, time_loop=time_loop)
    elif nc_type == "hugenc2":
        heart = random.choice(HEART_EMOJIS)
        template = random.choice(HUGE_ABUSES2)
        return template.format(text=text, heart=heart)
    elif nc_type == "midnc":
        template = random.choice(MID_ABUSES)
        return template.format(text=text)
    elif nc_type == "italicnc":
        template = random.choice(ITALIC_ABUSES)
        return template.format(text=text)
    elif nc_type == "angrync":
        template = random.choice(ANGRY_ABUSES)
        return template.format(text=text)
    elif nc_type == "flowernc":
        template = random.choice(FLOWER_ABUSES)
        return template.format(text=text)
    elif nc_type == "lovenc":
        template = random.choice(LOVE_ABUSES)
        return template.format(text=text.upper())
    elif nc_type == "cursivenc":
        template = random.choice(CURSIVE_ABUSES)
        return template.format(text=text)
    elif nc_type == "jdnc":
        animal_loop = " ".join(random.choices(ANIMAL_EMOJIS, k=10))
        template = random.choice(JDNC_TEMPLATES)
        return template.format(text=text, animal_loop=animal_loop)
    return text

# === PASSWORD GATE COMMANDS ===
async def eyefordeath_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text(f"💡 **Usage:** `》eyefordeath <password>`", parse_mode="Markdown")
        return
    
    entered_pass = context.args[0]
    if entered_pass == controller.secret_password:
        db.save_authorized(user_id)
        success_panel = (
            "┌──( 🍎📓 𝙆𝙸𝚁𝙰'𝚂 𝐆𝐀𝐓𝐄 𝐔𝐍𝐋𝐎𝐂𝐊𝐄𝐃 )──┐\n"
            "🖤 **Status:** `SOUL VERIFIED BY RYUK`\n"
            "✨ **Light Yagami:** `Welcome to the new world, human.`\n"
            f"🚀 **Action:** `Type 》start to enter Kira's domain.`\n"
            "└──────────────────────────────────────┘"
        )
        await update.message.reply_text(success_panel, parse_mode="Markdown")
    else:
        fail_panel = (
            "┌──( ❌🍎 𝐀𝐂𝐂𝐄𝐒𝐒 𝐑𝐄𝐉𝐄𝐂𝐓𝐄𝐃 )──┐\n"
            "🖤 **Status:** `INVALID INCANTATION`\n"
            "⚠️ **Ryuk:** `Wrong password! Try again if you dare.`\n"
            "└──────────────────────────────┘"
        )
        await update.message.reply_text(fail_panel, parse_mode="Markdown")

async def changearmy_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        denied_panel = (
            "┌──( ❌🍎 𝐒𝐎𝐕𝐄𝐑𝐄𝐈𝐆𝐍 𝐎𝐍𝐋𝐘 )──┐\n"
            "🖤 **Status:** `PERMISSION DENIED`\n"
            "⚠️ **Ryuk:** `Only the absolute Sovereign Owner can change the password!`\n"
            "└────────────────────────────────┘"
        )
        await update.message.reply_text(denied_panel, parse_mode="Markdown")
        return
    
    if not context.args:
        await update.message.reply_text(f"💡 **Usage:** `》changearmy <new_password>`", parse_mode="Markdown")
        return
    
    new_pass = context.args[0]
    controller.secret_password = new_pass
    db.save_setting("secret_password", new_pass)
    
    change_panel = (
        "┌──( 🔑🍎 𝐏𝐀𝐒𝐒𝐖𝐎𝐑𝐃 𝐔𝐏𝐃𝐀𝐓𝐄𝐃 )──┐\n"
        "🖤 **Status:** `NEW INCANTATION FORGED`\n"
        f"✨ **Ryuk:** `The gate password has been changed to: {new_pass}`\n"
        "└────────────────────────────────┘"
    )
    await update.message.reply_text(change_panel, parse_mode="Markdown")

# === ON/OFF CLUSTER COMMANDS (LIGHT = ON, DARK = OFF) ===
async def light_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    controller.cluster_active = True
    db.save_setting("cluster_active", True)
    panel = (
        "┌──( 🍎⚡ 𝙆𝙸𝚁𝙰'𝚂 𝐋𝐈𝐆𝐇𝐓 : 𝐀𝐖𝐀𝐊𝐄𝐍𝐄𝐃 )──┐\n"
        "🖤 **Status:** `SHINIGAMI CLUSTER ONLINE`\n"
        "✨ **Light Yagami:** `The divine judgement begins now. All systems operational.`\n"
        "└──────────────────────────────────────┘"
    )
    await update.message.reply_text(panel, parse_mode="Markdown")

async def dark_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    controller.cluster_active = False
    db.save_setting("cluster_active", False)
    
    for k in nc_flags: nc_flags[k] = False
    global spam_active, pic_spam_active, pic_changer_active, grpspam_active
    spam_active = False
    pic_spam_active = False
    pic_changer_active = False
    grpspam_active = False
    
    panel = (
        "┌──( 🌑📓 𝙆𝙸𝚁𝙰'𝚂 𝐃𝐀𝐑𝐊 : 𝐒𝐋𝐔𝐌𝐁𝐄𝐑 )──┐\n"
        "🖤 **Status:** `SHINIGAMI CLUSTER SLEEPING`\n"
        "🛑 **Ryuk:** `The notebook rests in darkness. All assaults halted.`\n"
        "└──────────────────────────────────────┘"
    )
    await update.message.reply_text(panel, parse_mode="Markdown")

# === INDIVIDUAL NC LOOPS ===
async def nc_loop(nc_type: str, chat_id: int, content: str):
    global nc_flags
    wave_count = 0
    while controller.cluster_active and nc_flags.get(nc_type, False):
        wave_count += 1
        new_name = generate_nc_name(nc_type, content)
        if len(new_name) > 128:
            new_name = new_name[:125] + "..."
        
        tasks = []
        for app in bot_apps:
            tasks.append(app.bot.set_chat_title(chat_id=chat_id, title=new_name))
        
        try:
            await asyncio.gather(*tasks)
            print(f"[{nc_type.upper()} WAVE {wave_count}] ALL {len(bot_apps)} BOTS changed name")
        except Exception as e:
            print(f"Name change error: {e}")
        
        if controller.cluster_active and nc_flags.get(nc_type, False):
            await asyncio.sleep(wave_delay)

async def start_nc(update: Update, context: ContextTypes.DEFAULT_TYPE, nc_type: str, content: str):
    global nc_flags, nc_tasks, nc_content
    if not controller.cluster_active:
        await update.message.reply_text("🌑 **Cluster is in DARK mode!** Type `》light` to awaken Kira's domain first.", parse_mode="Markdown")
        return
    if nc_flags.get(nc_type, False):
        await update.message.reply_text(f"⚠️ **{nc_type.upper()}** is already running!", parse_mode="Markdown")
        return
    nc_flags[nc_type] = True
    nc_content[nc_type] = content
    chat_id = update.effective_chat.id
    nc_tasks[nc_type] = asyncio.create_task(nc_loop(nc_type, chat_id, content))
    await update.message.reply_text(f"⚡ **{nc_type.upper()}** STARTED UNDER KIRA'S JUDGEMENT!", parse_mode="Markdown")

async def stop_nc(update: Update, context: ContextTypes.DEFAULT_TYPE, nc_type: str):
    global nc_flags, nc_tasks
    if nc_flags.get(nc_type, False):
        nc_flags[nc_type] = False
        if nc_type in nc_tasks and nc_tasks[nc_type] and not nc_tasks[nc_type].done():
            nc_tasks[nc_type].cancel()
        await update.message.reply_text(f"🛑 **{nc_type.upper()}** STOPPED!", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"⚠️ **{nc_type.upper()}** was not running!", parse_mode="Markdown")

# === SUDO COMMANDS (SUPPORT REPLY & ARGS) ===
async def add_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(get_unauthorized_msg())
        return
    
    user_id = None
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        target = context.args[0].replace('@', '')
        try:
            user_id = int(target)
        except:
            await update.message.reply_text("❌ Provide a valid numeric user ID or reply to a user's message!")
            return
    else:
        await update.message.reply_text("❌ Use: `》sudo <user_id>` or reply to someone's message with `》sudo`")
        return

    if user_id == OWNER_ID:
        await update.message.reply_text("❌ Sovereign Owner cannot be added as sudo!")
        return

    if user_id not in sudo_users:
        sudo_users.append(user_id)
        await update.message.reply_text(f"✅ User `{user_id}` successfully granted Shinigami Sudo power!", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"⚠️ User `{user_id}` is already a Sudo user!", parse_mode="Markdown")

async def remove_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(get_unauthorized_msg())
        return
    
    user_id = None
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        target = context.args[0].replace('@', '')
        try:
            user_id = int(target)
        except:
            await update.message.reply_text("❌ Provide a valid numeric user ID or reply to a user's message!")
            return
    else:
        await update.message.reply_text("❌ Use: `》-sudo <user_id>` or reply to someone's message with `》-sudo`")
        return

    if user_id in sudo_users:
        sudo_users.remove(user_id)
        await update.message.reply_text(f"✅ User `{user_id}` removed from sudo users!", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"⚠️ User `{user_id}` is not a sudo user!", parse_mode="Markdown")

async def list_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(get_unauthorized_msg())
        return
    await update.message.reply_text(f"📋 **Sudo Users:**\n`{sudo_users}`", parse_mode="Markdown")

# === SPAM FUNCTIONS ===
async def spam_wave_loop():
    global spam_active, current_spam_text, spam_chat_id, bot_apps, spam_mode, spam_target
    wave_count = 0
    while controller.cluster_active and spam_active:
        wave_count += 1
        if spam_mode == "normal":
            msg = current_spam_text
            tasks = [app.bot.send_message(chat_id=spam_chat_id, text=msg) for app in bot_apps]
            try:
                await asyncio.gather(*tasks)
            except Exception as e:
                print(f"Spam error: {e}")
        elif spam_mode == "bigspam":
            for template in BIGSPAM_LINES:
                if not controller.cluster_active or not spam_active: break
                msg = template.format(text=current_spam_text if current_spam_text else "")
                tasks = [app.bot.send_message(chat_id=spam_chat_id, text=msg) for app in bot_apps]
                try: await asyncio.gather(*tasks)
                except: pass
                if spam_active: await asyncio.sleep(wave_delay)
            continue
        elif spam_mode == "AAYUspam" and spam_target:
            for template in AAYUSPAM_LINES:
                if not controller.cluster_active or not spam_active: break
                msg = template.format(target=f"@{spam_target}", text=current_spam_text if current_spam_text else "")
                tasks = [app.bot.send_message(chat_id=spam_chat_id, text=msg) for app in bot_apps]
                try: await asyncio.gather(*tasks)
                except: pass
                if spam_active: await asyncio.sleep(wave_delay)
            return
        if controller.cluster_active and spam_active and spam_mode == "normal":
            await asyncio.sleep(wave_delay)

async def start_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global spam_active, spam_task, current_spam_text, spam_chat_id, spam_mode, spam_target
    if not controller.cluster_active:
        await update.message.reply_text("🌑 **Cluster is in DARK mode!** Type `》light` first.", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("❌ Use: `》spam <text>`")
        return
    if spam_active:
        await update.message.reply_text("⚠️ Spam already running!")
        return
    spam_active = True
    spam_mode = "normal"
    current_spam_text = ' '.join(context.args)
    spam_chat_id = update.effective_chat.id
    spam_target = None
    spam_task = asyncio.create_task(spam_wave_loop())
    await update.message.reply_text(f"⚡ **SPAM STARTED!**", parse_mode="Markdown")

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global spam_active, spam_task
    if spam_active:
        spam_active = False
        if spam_task and not spam_task.done(): spam_task.cancel()
        await update.message.reply_text("🛑 **SPAM STOPPED!**", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ **Spam was not running!**", parse_mode="Markdown")

async def start_bigspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global spam_active, spam_task, spam_chat_id, spam_mode, spam_target, current_spam_text
    if not controller.cluster_active:
        await update.message.reply_text("🌑 **Cluster is in DARK mode!** Type `》light` first.", parse_mode="Markdown")
        return
    if spam_active:
        await update.message.reply_text("⚠️ Spam already running!")
        return
    text = ' '.join(context.args) if context.args else ""
    spam_active = True
    spam_mode = "bigspam"
    current_spam_text = text
    spam_chat_id = update.effective_chat.id
    spam_target = None
    spam_task = asyncio.create_task(spam_wave_loop())
    await update.message.reply_text(f"⚡ **BIGSPAM STARTED!**", parse_mode="Markdown")

async def start_AAYUspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global spam_active, spam_task, spam_chat_id, spam_mode, spam_target, current_spam_text
    if not controller.cluster_active:
        await update.message.reply_text("🌑 **Cluster is in DARK mode!** Type `》light` first.", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("❌ Use: `》AAYUspam @username <text>`")
        return
    target = context.args[0].replace('@', '')
    text = ' '.join(context.args[1:]) if len(context.args) > 1 else ""
    if spam_active:
        await update.message.reply_text("⚠️ Spam already running!")
        return
    spam_active = True
    spam_mode = "AAYUspam"
    current_spam_text = text
    spam_chat_id = update.effective_chat.id
    spam_target = target
    spam_task = asyncio.create_task(spam_wave_loop())
    await update.message.reply_text(f"⚡ **TARGET SPAM STARTED!**", parse_mode="Markdown")

async def start_slide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: `》slide @username`")
        return
    target = context.args[0].replace('@', '')
    slide_active[update.effective_chat.id] = target.lower()
    await update.message.reply_text(f"✅ **SLIDE ACTIVATED** for @{target}", parse_mode="Markdown")

async def stop_slide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in slide_active:
        del slide_active[chat_id]
        await update.message.reply_text("🛑 **SLIDE STOPPED!**", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ **Slide was not active!**", parse_mode="Markdown")

async def start_swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: `》swipe @username`")
        return
    target = context.args[0].replace('@', '')
    text = random.choice(SWIPE_TEXTS).format(target=f"@{target}")
    await update.message.reply_text(text)

async def save_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global saved_pictures
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        saved_pictures.append(update.message.reply_to_message.photo[-1].file_id)
        await update.message.reply_text(f"✅ Picture saved! Total: {len(saved_pictures)}")
    elif update.message.photo:
        saved_pictures.append(update.message.photo[-1].file_id)
        await update.message.reply_text(f"✅ Picture saved! Total: {len(saved_pictures)}")
    else:
        await update.message.reply_text("❌ Reply to a picture with `》save`")

async def remove_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global saved_pictures
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    if saved_pictures:
        saved_pictures.pop()
        await update.message.reply_text(f"❌ Last picture removed! Remaining: {len(saved_pictures)}")
    else:
        await update.message.reply_text("❌ No saved pictures!")

async def start_picspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pic_spam_active, pic_spam_task, pic_spam_chat_id
    if not controller.cluster_active:
        await update.message.reply_text("🌑 **Cluster is in DARK mode!**", parse_mode="Markdown")
        return
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    if not saved_pictures:
        await update.message.reply_text("❌ No saved pictures!")
        return
    if pic_spam_active:
        await update.message.reply_text("⚠️ Already running!")
        return
    pic_spam_active = True
    pic_spam_chat_id = update.effective_chat.id
    
    async def picspam_wave_loop():
        global pic_spam_active, saved_pictures, pic_spam_chat_id, bot_apps
        while controller.cluster_active and pic_spam_active:
            for file_id in saved_pictures:
                if not controller.cluster_active or not pic_spam_active: break
                tasks = [app.bot.send_photo(chat_id=pic_spam_chat_id, photo=file_id) for app in bot_apps]
                try: await asyncio.gather(*tasks)
                except: pass
                if pic_spam_active: await asyncio.sleep(wave_delay)
    
    pic_spam_task = asyncio.create_task(picspam_wave_loop())
    await update.message.reply_text("🖼️ **PICTURE SPAM STARTED!**", parse_mode="Markdown")

async def stop_picspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pic_spam_active, pic_spam_task
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    if pic_spam_active:
        pic_spam_active = False
        if pic_spam_task and not pic_spam_task.done(): pic_spam_task.cancel()
        await update.message.reply_text("🛑 **PICTURE SPAM STOPPED!**", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ **Not running!**", parse_mode="Markdown")

async def start_pic_changer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pic_changer_active, pic_changer_task, pic_changer_chat_id, pic_changer_delay
    if not controller.cluster_active:
        await update.message.reply_text("🌑 **Cluster is in DARK mode!**", parse_mode="Markdown")
        return
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    if not saved_pictures:
        await update.message.reply_text("❌ No saved pictures!")
        return
    if pic_changer_active:
        await update.message.reply_text("⚠️ Already running!")
        return
    pic_changer_active = True
    pic_changer_chat_id = update.effective_chat.id
    
    async def pic_changer_loop():
        global pic_changer_active, saved_pictures, pic_changer_chat_id, bot_apps
        while controller.cluster_active and pic_changer_active:
            for file_id in saved_pictures:
                if not controller.cluster_active or not pic_changer_active: break
                for app in bot_apps:
                    try: await app.bot.set_chat_photo(chat_id=pic_changer_chat_id, photo=file_id)
                    except: pass
                    await asyncio.sleep(pic_changer_delay)
    
    pic_changer_task = asyncio.create_task(pic_changer_loop())
    await update.message.reply_text("🖼️ **PICTURE CHANGER STARTED!**", parse_mode="Markdown")

async def stop_pic_changer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pic_changer_active, pic_changer_task
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    if pic_changer_active:
        pic_changer_active = False
        if pic_changer_task and not pic_changer_task.done(): pic_changer_task.cancel()
        await update.message.reply_text("🛑 **PICTURE CHANGER STOPPED!**", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ **Not running!**", parse_mode="Markdown")

async def set_pic_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pic_changer_delay
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    try:
        pic_changer_delay = float(context.args[0])
        await update.message.reply_text(f"✅ Picture delay set to: `{pic_changer_delay}s`", parse_mode="Markdown")
    except:
        await update.message.reply_text(f"❌ Use: `》picdelay <seconds>`\nCurrent: `{pic_changer_delay}s`", parse_mode="Markdown")

async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global multi_gc_groups
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    chat_id = update.effective_chat.id
    if chat_id not in multi_gc_groups:
        multi_gc_groups.append(chat_id)
        await update.message.reply_text(f"✅ Group added! Total: {len(multi_gc_groups)}")
    else:
        await update.message.reply_text("⚠️ Already added!")

async def remove_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global multi_gc_groups
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    chat_id = update.effective_chat.id
    if chat_id in multi_gc_groups:
        multi_gc_groups.remove(chat_id)
        await update.message.reply_text(f"❌ Group removed! Total: {len(multi_gc_groups)}")
    else:
        await update.message.reply_text("⚠️ Not in list!")

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    await update.message.reply_text(f"📋 **Groups:** {len(multi_gc_groups)}\nIDs: {multi_gc_groups}", parse_mode="Markdown")

async def grpnc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not controller.cluster_active:
        await update.message.reply_text("🌑 **Cluster is in DARK mode!**", parse_mode="Markdown")
        return
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    if not multi_gc_groups:
        await update.message.reply_text("❌ No groups added!")
        return
    parts = update.message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        await update.message.reply_text("❌ Use: `》grpnc <text>`")
        return
    result = random.choice(MULTI_GC_NC_TEMPLATES).format(Text=parts[1].upper())
    for chat_id in multi_gc_groups:
        for app in bot_apps:
            try:
                await app.bot.send_message(chat_id=chat_id, text=result)
                break
            except: pass
    await update.message.reply_text("✅ Group NC broadcast sent!")

async def grpspam_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global grpspam_active, grpspam_task
    if not controller.cluster_active:
        await update.message.reply_text("🌑 **Cluster is in DARK mode!**", parse_mode="Markdown")
        return
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    if not multi_gc_groups:
        await update.message.reply_text("❌ No groups added!")
        return
    if grpspam_active:
        await update.message.reply_text("⚠️ Already running!")
        return
    grpspam_active = True
    
    async def grpspam_loop():
        while controller.cluster_active and grpspam_active:
            for template in MULTI_GC_SPAM_LINES:
                if not controller.cluster_active or not grpspam_active: break
                msg = template.format(text="")
                for chat_id in multi_gc_groups:
                    if not controller.cluster_active or not grpspam_active: break
                    for app in bot_apps:
                        try: await app.bot.send_message(chat_id=chat_id, text=msg); break
                        except: pass
                if grpspam_active: await asyncio.sleep(wave_delay)
    
    grpspam_task = asyncio.create_task(grpspam_loop())
    await update.message.reply_text("✅ Multi-GC Spam started!")

async def grpspam_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global grpspam_active, grpspam_task
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    if grpspam_active:
        grpspam_active = False
        if grpspam_task and not grpspam_task.done(): grpspam_task.cancel()
        await update.message.reply_text("🛑 Multi-GC Spam stopped!")
    else:
        await update.message.reply_text("⚠️ Not running!")

async def hard_stop_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global nc_flags, nc_tasks, spam_active, spam_task, pic_spam_active, pic_spam_task, pic_changer_active, pic_changer_task, grpspam_active, grpspam_task
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    for k in nc_flags: nc_flags[k] = False
    spam_active = False
    pic_spam_active = False
    pic_changer_active = False
    grpspam_active = False
    for t in [spam_task, pic_spam_task, pic_changer_task, grpspam_task]:
        if t and not t.done(): t.cancel()
    for task in nc_tasks.values():
        if task and not task.done(): task.cancel()
    
    watermark = (
        "╭▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰━╮\n"
        "┃ 𓆩🍎𓆪  ꉂ🗯.꩜‹—𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𝐋𝐢𝐠𝐡𝐭 𝐘𝐚𝐠𝐚𝐦𝐢 & 𝐑𝐲𝐮𝐤』𓆩📓𓆪\n"
        "╰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰╯"
    )
    await update.message.reply_text(f"🛑 **HARD STOP - ALL ACTIONS TERMINATED BY KIRA!**\n\n{watermark}", parse_mode="Markdown")

# === STEALTH RECON COMMAND ===
async def stealth_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    ram_used = memory.used // (1024**2)
    uptime_sec = time.time() - START_TIME
    h = int(uptime_sec // 3600)
    m = int((uptime_sec % 3600) // 60)

    stealth_panel = (
        f"┌──( 🛡️🍎 𝐊𝐈𝐑𝐀'𝐒 𝐒𝐓𝐄𝐀𝐋𝐓𝐇 𝐑𝐄𝐂𝐎𝐍 )──┐\n"
        f"🖤 **Shinigami Status:** `AT FULL POWER`\n"
        f"🟢 **Anti-Detection Shield:** `ACTIVE`\n"
        f"💻 **Core CPU Load:** `{cpu_usage}%`\n"
        f"💾 **Death RAM Usage:** `{ram_used}MB`\n"
        f"⏱️ **Realm Uptime:** `{h}h {m}m`\n"
        f"└────────────────────────────────┘"
    )
    await update.message.reply_text(stealth_panel, parse_mode="Markdown")

# === EYES COMMAND (SHINIGAMI EYES DOSSIER) ===
async def eyes_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    
    target_user = None
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        target_user = context.args[0]
    
    if not target_user and not update.message.reply_to_message:
        target_user = update.effective_user

    if isinstance(target_user, str):
        dossier = (
            f"┌──( 👁️🍎 𝐒𝐇𝐈𝐍𝐈𝙶𝙰𝙼𝙸 𝙴𝚈𝙴𝚂 : 𝙳𝙾𝚂𝚂𝙸𝙴𝚁 )──┐\n"
            f"🖤 **Target Handle:** `{target_user}`\n"
            f"📓 **Death Note Status:** `TARGET ACQUIRED IN REALM`\n"
            f"⚡ **Ryuk's Verdict:** `Marked for ultimate judgment.`\n"
            f"└──────────────────────────────────────┘"
        )
    else:
        name = target_user.full_name
        uid = target_user.id
        uname = f"@{target_user.username}" if target_user.username else "None"
        dossier = (
            f"┌──( 👁️🍎 𝐒𝐇𝐈𝐍𝐈𝙶𝙰𝙼𝙸 𝙴𝚈𝙴𝚂 : 𝙳𝙾𝚂𝚂𝙸𝙴𝚁 )──┐\n"
            f"🖤 **Subject Name:** `{name}`\n"
            f"🆔 **Soul ID:** `{uid}`\n"
            f"🌐 **Alias:** `{uname}`\n"
            f"📓 **Death Note Status:** `REGISTERED IN NOTEBOOK`\n"
            f"⚡ **Ryuk's Verdict:** `Lifespan visible. Ready for harvest.`\n"
            f"└──────────────────────────────────────┘"
        )
    await update.message.reply_text(dossier, parse_mode="Markdown")

# === PING COMMAND ===
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text(get_unauthorized_msg())
        return
    
    start_time = time.time()
    ping_msg = await update.message.reply_text("🍎 **Ryuk is calculating the speed of death...** 💀", parse_mode="Markdown")
    end_time = time.time()
    
    latency = round((end_time - start_time) * 1000, 2)
    cpu_usage = psutil.cpu_percent(interval=0.1)
    
    if latency < 200:
        speed_status = "⚡ 𝙆𝙸𝚁𝙰'𝚂 𝐄𝐘𝐄𝐒 : LIGHTNING FAST"
    elif latency < 500:
        speed_status = "🔥 𝑺𝑯𝑰𝑵𝑰𝑮𝑨𝑴𝑰 𝐖𝐈𝑵𝑮𝐒 : STABLE VELOCITY"
    else:
        speed_status = "⚠️ 𝐃𝐄𝐀𝐓𝐇 𝐍𝐎𝐓𝐄 : NETWORK CONGESTED"

    ping_panel = (
        f"┌──( ⚡🍎 𝙆𝙸𝚁𝙰'𝚂 𝙕𝙾𝙽𝙴 𝑷𝑰𝑵𝑮 )──┐\n"
        f"🖤 **Status:** `REALM SYNCHRONIZED`\n"
        f"⏱️ **Latency Speed:** `{latency} ms`\n"
        f"💻 **Core Load:** `{cpu_usage}%`\n"
        f"⚡ **Rating:** `{speed_status}`\n"
        f"🤖 **Active Bots:** `{len(bot_apps)}/10`\n"
        f"└────────────────────────────────┘\n\n"
        f"╭▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰━╮\n"
        f"┃ 𓆩🍎𓆪  ꉂ🗯.꩜‹—𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𝐋𝐢𝐠𝐡𝐭 𝐘𝐚𝐠𝐚𝐦𝐢 & 𝐑𝐲𝐮𝐤』𓆩📓𓆪\n"
        f"╰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰╯"
    )
    
    await ping_msg.edit_text(ping_panel, parse_mode="Markdown")

# === RYUK MENU IMAGE COMMAND ===
async def ryukmenuimg_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Sovereign Only!")
    
    watermark = (
        "╭▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰━╮\n"
        "┃ 𓆩🍎𓆪  ꉂ🗯.꩜‹—𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𝐋𝐢𝐠𝐡𝐭 𝐘𝐚𝐠𝐚𝐦𝐢 & 𝐑𝐲𝐮𝐤』𓆩📓𓆪\n"
        "╰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰╯"
    )
    
    target_msg = update.message.reply_to_message
    if target_msg and target_msg.photo:
        file_id = target_msg.photo[-1].file_id
        controller.menu_image = file_id
        db.save_setting("menu_image", file_id)
        await update.message.reply_text(f"✅ **Ryuk's Menu Photo Bound Successfully, My King!**\n\n{watermark}", parse_mode="Markdown")
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        controller.menu_image = file_id
        db.save_setting("menu_image", file_id)
        await update.message.reply_text(f"✅ **Ryuk's Menu Photo Bound Successfully, My King!**\n\n{watermark}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"💡 Usage: Send or reply to a photo with `》ryukmenuimg` to set images across menus!\n\n{watermark}", parse_mode="Markdown")

# === MENU COMMANDS WITH DYNAMIC WATERMARK WIDTH ===
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        locked_panel = (
            "┌──( 🔒🍎 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃 )──┐\n"
            "🖤 **Status:** `GATE SEALED BY LIGHT YAGAMI`\n"
            "⚠️ **Notice:** `You lack clearance to enter the Death Note domain.`\n"
            "💡 **Action:** `Type 》eyefordeath <password> to unlock.`\n"
            "└────────────────────────────────┘"
        )
        return await update.message.reply_text(locked_panel, parse_mode="Markdown")

    keyboard = [
        [InlineKeyboardButton("🍎 𝙆𝙸𝚁𝙰'𝚂 𝐀𝐑𝐌𝐘 𝐒𝐔𝐌𝐌𝐎𝐍", callback_data="summon_menu")],
        [InlineKeyboardButton("📓 𝙆𝙸𝚁𝙰'𝚂 𝖬𝙴𝙽𝚄𝚂", callback_data="main_menu"), InlineKeyboardButton("📊 𝚂𝙷𝙸𝙽𝙸𝙶𝙰𝙼𝙸 𝚂𝚃𝙰𝚃𝚂", callback_data="stats")],
        [InlineKeyboardButton("❌ 𝙲𝙻𝙾𝚂𝙴 𝙶𝙰𝚃𝙴", callback_data="close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Dynamic Watermark matching maximum text line width perfectly
    watermark_text = "𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𝐋𝐢𝐠𝐡𝐭 𝐘𝐚𝐠𝐚𝐦𝐢 & 𝐑𝐲𝐮𝐤』"
    border = "━" * (len(watermark_text) + 6)
    watermark = (
        f"╭{border}╮\n"
        f"┃ 𓆩🍎𓆪  ꉂ🗯.꩜‹—{watermark_text}𓆩📓𓆪 ┃\n"
        f"╰{border}╯"
    )

    cluster_state = "⚡ 𝙆𝙸𝚁𝙰'𝚂 𝐋𝐈𝐆𝐇𝐓 (ONLINE)" if controller.cluster_active else "🌑 𝙆𝙸𝚁𝙰'𝚂 𝐃𝐀𝐑𝐊 (OFFLINE)"

    menu_caption = (
        "🍎📓 **『 ᴅᴇᴀᴛʜ ɴᴏᴛᴇ : ʟɪɢʜᴛ ʏᴀɢᴀᴍɪ'ꜱ ᴅᴏᴍᴀɪℕ 』** 📓🍎\n\n"
        "🖤 `🔥 𝙆𝙸𝚁𝙰 𝙸𝚂 𝙹𝚄𝙳𝙶𝙸𝙽𝙶 𝚃𝙷𝙴 𝚆𝙾𝚁𝙻𝙳 🔥` 🖤\n"
        "┌──────────────────────────────────────┐\n"
        "│  👑 **ᴋɪʀ𝙰 — ꜱᴜᴘʀᴇᴍᴇ 𝙹𝚄𝙳𝙶𝙴**  │\n"
        "└──────────────────────────────────────┘\n\n"
        f"🤖 **Active Shinigami Bots:** `{len(bot_apps)}/10`\n"
        f"⚡ **Domain State:** `{cluster_state}`\n"
        f"⚡ **Assault Velocity:** `{wave_delay}s`\n"
        f"🔑 **Command Sigil:** `》`\n\n"
        f"📂 **KIRA'S CLUSTER MENUS:**\n"
        f"➤ `》menu1` : Core (Unlock, Summon, Light/Dark, Setvid, Rmvid, Stealth, Ping, Eyes)\n"
        f"➤ `》menu2` : NC (Name Changer Assault)\n"
        f"➤ `》menu3` : Spam (Legion Spam Engine)\n"
        f"➤ `》menu4` : Target (Soul Intel & Recon)\n"
        f"➤ `》menu5` : Auth & Stop (Sudo, Delay, Stop, Changearmy)\n\n"
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
        elif controller.menu_image:
            await update.message.reply_photo(
                photo=controller.menu_image,
                caption=menu_caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(menu_caption, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception:
        await update.message.reply_text(menu_caption, parse_mode="Markdown", reply_markup=reply_markup)

async def send_menu_with_image(update: Update, text: str):
    try:
        if controller.menu_image:
            await update.message.reply_photo(photo=controller.menu_image, caption=text, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(text, parse_mode="Markdown")

async def menu1_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    watermark_text = "𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𝐋𝐢𝐠𝐡𝐭 𝐘𝐚𝐠𝐚𝐦𝐢 & 𝐑𝐲𝐮𝐤』"
    border = "━" * (len(watermark_text) + 6)
    watermark = (
        f"╭{border}╮\n"
        f"┃ 𓆩🍎𓆪  ꉂ🗯.꩜‹—{watermark_text}𓆩📓𓆪 ┃\n"
        f"╰{border}╯"
    )
    text = (
        "┌──( 🍎📓 𝖬𝖤𝖭𝖴 1 : 𝖢𝖮𝖱𝖤 )──┐\n"
        f"➤ `》eyefordeath <pass>` - Unlock Gate\n"
        f"➤ `》light` / `》dark` - Shinigami Cluster ON / OFF\n"
        f"➤ `》ping` - Check Shinigami Latency Speed\n"
        f"➤ `》eyes` - Shinigami Eyes Dossier Scan\n"
        f"➤ `》setvid` - Bind Grimoire Video (Reply Video)\n"
        f"➤ `》rmvid` - Purge Grimoire Video\n"
        f"➤ `》ryukmenuimg` - Bind Menu Photo\n"
        f"➤ `》stealth` - Shinigami Stealth Recon\n"
        f"➤ `》clear` - Purge Realm Corruptions\n"
        f"└──────────────────────────┘\n\n{watermark}"
    )
    await send_menu_with_image(update, text)

async def menu2_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    watermark_text = "𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𝐋𝐢𝐠𝐡𝐭 𝐘𝐚𝐠𝐚𝐦𝐢 & 𝐑𝐲𝐮𝐤』"
    border = "━" * (len(watermark_text) + 6)
    watermark = (
        f"╭{border}╮\n"
        f"┃ 𓆩🍎𓆪  ꉂ🗯.꩜‹—{watermark_text}𓆩📓𓆪 ┃\n"
        f"╰{border}╯"
    )
    text = (
        "┌──( 🍎📓 𝖬𝖤𝖭𝖴 2 : 𝖭𝖢 & 𝖲𝖳𝖱𝖨𝖪𝖤 )──┐\n"
        f"➤ `》smallnc <text>` / `》-smallnc`\n"
        f"➤ `》hugenc <text>` / `》-hugenc`\n"
        f"➤ `》hugenc2 <text>` / `》-hugenc2`\n"
        f"➤ `》midnc <text>` / `》-midnc`\n"
        f"➤ `》italicnc <text>` / `》-italicnc`\n"
        f"➤ `》angrync <text>` / `》-angrync`\n"
        f"➤ `》flowernc <text>` / `》-flowernc`\n"
        f"➤ `》lovenc <text>` / `》-lovenc`\n"
        f"➤ `》cursivenc <text>` / `》-cursivenc`\n"
        f"└──────────────────────────────┘\n\n{watermark}"
    )
    await send_menu_with_image(update, text)

async def menu3_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    watermark_text = "𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𝐋𝐢𝐠𝐡𝐭 𝐘𝐚𝐠𝐚𝐦𝐢 & 𝐑𝐲𝐮𝐤』"
    border = "━" * (len(watermark_text) + 6)
    watermark = (
        f"╭{border}╮\n"
        f"┃ 𓆩🍎𓆪  ꉂ🗯.꩜‹—{watermark_text}𓆩📓𓆪 ┃\n"
        f"╰{border}╯"
    )
    text = (
        "┌──( 🍎📓 𝖬𝖤𝖭𝖴 3 : 𝖲𝖯𝖠𝖬 )──┐\n"
        f"➤ `》spam <text>` / `》-spam`\n"
        f"➤ `》bigspam <text>`\n"
        f"➤ `》AAYUspam @user <text>`\n"
        f"➤ `》slide @user` / `》-slide`\n"
        f"➤ `》swipe @user`\n"
        f"└────────────────────────────┘\n\n{watermark}"
    )
    await send_menu_with_image(update, text)

async def menu4_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    watermark_text = "𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𝐋𝐢𝐠𝐡𝐭 𝐘𝐚𝐠𝐚𝐦𝐢 & 𝐑𝐲𝐮𝐤』"
    border = "━" * (len(watermark_text) + 6)
    watermark = (
        f"╭{border}╮\n"
        f"┃ 𓆩🍎𓆪  ꉂ🗯.꩜‹—{watermark_text}𓆩📓𓆪 ┃\n"
        f"╰{border}╯"
    )
    text = (
        "┌──( 🍎📓 𝖬𝖤𝖭𝖴 4 : 𝖬𝚄𝙻𝚃𝙸-𝙶𝙲 & 𝙿𝙸𝙲𝚂 )──┐\n"
        f"➤ `》add` / `》-add` / `》listgroups`\n"
        f"➤ `》grpnc <text>`\n"
        f"➤ `》grpspam` / `》-grpspam`\n"
        f"➤ `》save` / `》-save`\n"
        f"➤ `》picspam` / `》-picspam`\n"
        f"➤ `》pic` / `》-pic`\n"
        f"└──────────────────────────┘\n\n{watermark}"
    )
    await send_menu_with_image(update, text)

async def menu5_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    watermark_text = "𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 『𝐋𝐢𝐠𝐡𝐭 𝐘𝐚𝐠𝐚𝐦𝐢 & 𝐑𝐲𝐮𝐤』"
    border = "━" * (len(watermark_text) + 6)
    watermark = (
        f"╭{border}╮\n"
        f"┃ 𓆩🍎𓆪  ꉂ🗯.꩜‹—{watermark_text}𓆩📓𓆪 ┃\n"
        f"╰{border}╯"
    )
    text = (
        "┌──( 🍎📓 𝖬𝖤𝖭𝖴 5 : 𝖠𝖴𝖳𝖧 & 𝖲𝖳𝖮𝖯 )──┐\n"
        f"➤ `》changearmy <pass>` - Change Gate Password\n"
        f"➤ `》sudo <id>` / `》-sudo <id>` / `》listsudo`\n"
        f"➤ `》delay <sec>` - Set Wave Velocity\n"
        f"➤ `》-all` - Hard Stop All Operations\n"
        f"➤ `》uptime` - Shinigami Uptime\n"
        f"└────────────────────────────────┘\n\n{watermark}"
    )
    await send_menu_with_image(update, text)

async def setvid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Sovereign Only!")
    target_msg = update.message.reply_to_message
    if target_msg and target_msg.video:
        file_id = target_msg.video.file_id
        controller.menu_video = file_id
        db.save_setting("menu_video", file_id)
        await update.message.reply_text("✅ **Death Note Grimoire Video Bound Successfully!**", parse_mode="Markdown")
    elif update.message.video:
        file_id = update.message.video.file_id
        controller.menu_video = file_id
        db.save_setting("menu_video", file_id)
        await update.message.reply_text("✅ **Death Note Grimoire Video Bound Successfully!**", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"💡 Usage: Send or reply to a video message with `》setvid`", parse_mode="Markdown")

async def rmvid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Sovereign Only!")
    db.delete_setting("menu_video")
    controller.menu_video = None
    await update.message.reply_text("✅ **Video Grimoire Purged!** Reverted to text mode.", parse_mode="Markdown")

async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return await update.message.reply_text(get_unauthorized_msg())
    try:
        subprocess.run("sync; echo 3 > /proc/sys/vm/drop_caches", shell=True, check=True)
        await update.message.reply_text("✅ **Realm Purged Successfully!** Cache cleared.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Purge error: {str(e)}")

async def uptime_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return await update.message.reply_text(get_unauthorized_msg())
    uptime_seconds = int(time.time() - START_TIME)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    await update.message.reply_text(
        f"🍎 **Kira Domain Uptime:** `{hours}h {minutes}m {seconds}s`\n"
        f"📊 **Active Shinigami Bots:** {len(bot_apps)}\n"
        f"⚡ **Wave Delay:** {wave_delay}s\n"
        f"👑 **Sudo Users:** {len(sudo_users)}",
        parse_mode="Markdown"
    )

async def set_wave_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global wave_delay
    if not is_authorized(update.effective_user.id):
        return await update.message.reply_text(get_unauthorized_msg())
    try:
        new_delay = float(context.args[0])
        wave_delay = new_delay
        await update.message.reply_text(f"✅ Wave delay set to: `{wave_delay}s`", parse_mode="Markdown")
    except:
        await update.message.reply_text(f"❌ Use: `》delay <seconds>`\nCurrent: `{wave_delay}s`", parse_mode="Markdown")

async def cr_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global selected_roast
    if not is_authorized(update.effective_user.id):
        return await update.message.reply_text(get_unauthorized_msg())
    try:
        roast_key = context.args[0].upper()
        if roast_key in CUSTOM_REPLIES:
            selected_roast = roast_key
            await update.message.reply_text(f"✅ Roast changed to: {CUSTOM_REPLIES[roast_key]}")
        else:
            await update.message.reply_text("❌ Invalid. Use: R1, R2, or R3")
    except:
        await update.message.reply_text(f"❌ Use: `》cr R1`\nCurrent: {selected_roast}")

async def leave_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return await update.message.reply_text(get_unauthorized_msg())
    await update.message.reply_text("🍎 Ryuk says goodbye!")
    await context.bot.leave_chat(update.effective_chat.id)

async def summon_portal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    row = []
    for idx, token in enumerate(BOT_TOKENS):
        row.append(InlineKeyboardButton(f"Shinigami #{idx+1}", url=f"https://t.me/{(await bot_apps[idx].bot.get_me()).username}?startgroup=true"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    await update.message.reply_text("🕳️🍎 **DEATH NOTE GATE SUMMON PORTAL** 🍎🕳️", reply_markup=InlineKeyboardMarkup(keyboard))

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📊 Active Operations: {len(db.get_active())}\n🤖 Online Shinigami Bots: {len(bot_apps)}")

# === BUTTON CALLBACK HANDLER ===
async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "close":
        await query.message.delete()
    elif query.data == "stats":
        await update.message.reply_text(f"📊 Active Ops: {len(db.get_active())} | 🤖 Bots: {len(bot_apps)}")
    elif query.data == "summon_menu":
        await summon_portal(update, context)
    elif query.data == "main_menu":
        await start_cmd(update, context)

# === MAIN MESSAGE HANDLER ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    message = update.message
    text = message.text.strip()
    user_id = update.effective_user.id
    
    if text.startswith("》eyefordeath"):
        parts = text.split(maxsplit=1)
        context.args = [parts[1]] if len(parts) > 1 else []
        await eyefordeath_cmd(update, context)
        return

    if text.startswith("》changearmy"):
        parts = text.split(maxsplit=1)
        context.args = [parts[1]] if len(parts) > 1 else []
        await changearmy_cmd(update, context)
        return

    if not is_authorized(user_id):
        if text.startswith("》") or text.startswith("/") or text.startswith("-"):
            await message.reply_text(get_unauthorized_msg())
        return
    
    if text.lower() == "》-all" or text.lower() == "-all":
        await hard_stop_all(update, context)
        return
    
    if text.startswith("》-"):
        cmd_part = text[2:].strip().split(maxsplit=1)
        cmd = cmd_part[0].lower()
        context.args = cmd_part[1:] if len(cmd_part) > 1 else []
        
        if cmd in ["smallnc", "customnc", "hugenc", "hugenc2", "midnc", "italicnc", "angrync", "flowernc", "lovenc", "cursivenc", "jdnc"]:
            await stop_nc(update, context, cmd)
            return
        if cmd == "spam": await stop_spam(update, context); return
        if cmd == "slide": await stop_slide(update, context); return
        if cmd == "picspam": await stop_picspam(update, context); return
        if cmd == "pic": await stop_pic_changer(update, context); return
        if cmd == "grpspam": await grpspam_stop(update, context); return
        if cmd == "add": await remove_group(update, context); return
        if cmd == "sudo": await remove_sudo(update, context); return
        if cmd == "save": await remove_picture(update, context); return
    
    if text.startswith("》"):
        actual_text = text[len("》"):]
        parts = actual_text.split(maxsplit=1)
        cmd = parts[0].lower()
        content = parts[1] if len(parts) > 1 else ""
        context.args = parts[1:]
        
        if cmd == "start": await start_cmd(update, context); return
        if cmd == "menu1": await menu1_cmd(update, context); return
        if cmd == "menu2": await menu2_cmd(update, context); return
        if cmd == "menu3": await menu3_cmd(update, context); return
        if cmd == "menu4": await menu4_cmd(update, context); return
        if cmd == "menu5": await menu5_cmd(update, context); return
        if cmd == "light": await light_cmd(update, context); return
        if cmd == "dark": await dark_cmd(update, context); return
        if cmd == "ping": await ping_cmd(update, context); return
        if cmd == "eyes": await eyes_cmd(update, context); return
        if cmd == "stealth": await stealth_cmd(update, context); return
        if cmd == "ryukmenuimg": await ryukmenuimg_cmd(update, context); return
        if cmd == "uptime": await uptime_cmd(update, context); return
        if cmd == "delay": await set_wave_delay(update, context); return
        if cmd == "picdelay": await set_pic_delay(update, context); return
        if cmd == "cr": await cr_cmd(update, context); return
        if cmd == "leave": await leave_cmd(update, context); return
        if cmd == "listgroups": await list_groups(update, context); return
        if cmd == "listsudo": await list_sudo(update, context); return
        if cmd == "setvid": await setvid_cmd(update, context); return
        if cmd == "rmvid": await rmvid_cmd(update, context); return
        if cmd == "clear": await clear_cmd(update, context); return
        
        if cmd in ["smallnc", "customnc", "hugenc", "hugenc2", "midnc", "italicnc", "angrync", "flowernc", "lovenc", "cursivenc", "AAYUnc", "jdnc"]:
            if content: await start_nc(update, context, cmd, content)
            else: await message.reply_text(f"❌ Use: `》{cmd} <text>`")
            return
        if cmd == "spam":
            if content: await start_spam(update, context)
            else: await message.reply_text(f"❌ Use: `》spam <text>`")
            return
        if cmd == "bigspam": await start_bigspam(update, context); return
        if cmd == "AAYUspam": await start_AAYUspam(update, context); return
        if cmd == "slide": await start_slide(update, context); return
        if cmd == "swipe": await start_swipe(update, context); return
        if cmd == "save": await save_picture(update, context); return
        if cmd == "picspam": await start_picspam(update, context); return
        if cmd == "pic": await start_pic_changer(update, context); return
        if cmd == "add": await add_group(update, context); return
        if cmd == "grpnc": await grpnc_start(update, context); return
        if cmd == "grpspam": await grpspam_start(update, context); return
        if cmd == "sudo": await add_sudo(update, context); return
        return
    
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user = message.reply_to_message.from_user
        if replied_user.username:
            await message.reply_text(random.choice(SWIPE_TEXTS).format(target=f"@{replied_user.username}"))
            return
    
    chat_id = update.effective_chat.id
    if chat_id in slide_active:
        if message.from_user.username and message.from_user.username.lower() == slide_active[chat_id]:
            await message.reply_text(random.choice(SLIDE_TEXTS))
            return

# === BOT RUNNER ===
async def run_bot(token, bot_index):
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("fullhelp", fullhelp_cmd))
    app.add_handler(CommandHandler("menu1", menu1_cmd))
    app.add_handler(CommandHandler("menu2", menu2_cmd))
    app.add_handler(CommandHandler("menu3", menu3_cmd))
    app.add_handler(CommandHandler("menu4", menu4_cmd))
    app.add_handler(CommandHandler("menu5", menu5_cmd))
    app.add_handler(CommandHandler("light", light_cmd))
    app.add_handler(CommandHandler("dark", dark_cmd))
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("eyes", eyes_cmd))
    app.add_handler(CommandHandler("stealth", stealth_cmd))
    app.add_handler(CommandHandler("ryukmenuimg", ryukmenuimg_cmd))
    app.add_handler(CommandHandler("uptime", uptime_cmd))
    app.add_handler(CommandHandler("delay", set_wave_delay))
    app.add_handler(CommandHandler("picdelay", set_pic_delay))
    app.add_handler(CommandHandler("cr", cr_cmd))
    app.add_handler(CommandHandler("leave", leave_cmd))
    app.add_handler(CommandHandler("listgroups", list_groups))
    app.add_handler(CommandHandler("listsudo", list_sudo))
    app.add_handler(CallbackQueryHandler(button_callback_handler))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print(f"🍎 Shinigami Bot {bot_index + 1} online: {token[:10]}...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    bot_apps.append(app)
    try: await asyncio.Event().wait()
    except: pass

async def main_async():
    print("=" * 60)
    print("🍎 LIGHT YAGAMI & RYUK - DEATH NOTE CLUSTER BOOTING 🍎")
    print("=" * 60)
    tasks = [asyncio.create_task(run_bot(token, i)) for i, token in enumerate(BOT_TOKENS)]
    await asyncio.gather(*tasks)

def main():
    try: asyncio.run(main_async())
    except KeyboardInterrupt: print("\n🛑 All Death Note bots stopped")

if __name__ == "__main__":
    main()
