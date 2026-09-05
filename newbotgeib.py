# 𝘳𝓲𝘴ꫝꪊ ꪖʙʙꪊ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ - ULTIMATE FIXED 🔥

import asyncio
import json
import os
import random
import time
import string
from datetime import datetime
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging

logging.basicConfig(level=logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# ==================== MASTER CONFIG ====================
MASTER_ID = 8996032103
MASTER_KEY = "c9eb5e70623b411af29c904fb17e1a11"

# ==================== TOKENS ====================
TOKENS = [ 
    "8670479769:AAGB4UUsyyhcPce1-qocLIyD4owJYRQn9n4",
    "8890606582:AAHq_Xa9e801jDH_H_NMlhLx8NDFnL2RhY0",
    "8904628926:AAEUCY0vl6HzYpamVx5EaVfEmNqXHXzuAJA",
    
"8976613089:AAHV7Dvfl9cVNjrKA9l4xoM8PI0dYVk6g1Q",

"8765836494:AAFowURaxfhLA8YZaw22ncLz92aPdPEX3iY",

"8817990041:AAHO8Pl6mpe-8HAm5caVKCzX47772jGxRS0",
    "8934529784:AAHKaXATwSjUxI7gcNW277Qbm3-zCSylafo",
    "8767383748:AAHC1v9IVqohAIXgHQ9cDFS5iG-uT4tNjDU",
    "8675374289:AAFU60_j3y6v2LpOBbYyxiNecyF0CMr2s8A",
    "8844625791:AAHvdHIK1Qp_FOsTTJgvZGQ-V-fdSliAkfA",
    
]

# ==================== NC LISTS ====================
NCEMO_WORDS = [
    "𝐓ᴍᴋᴄ ➰", "𝐓ᴍᴋʟ ➿", "𝐓ᴍʀ ✖", "𝐓ʀʏ 𝐌ᴀᴀ 𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ ᴋɪ ɢᴜʟᴀᴍ 🔱", "𝐓ʀʏ 𝐌ᴀᴀ 𝐒ᴜᴀʀ ✔",
    "𝐓ʀʏ 𝐌ᴀᴀ 𝐑ɴᴅʏ 🫨", "𝐓ʀʏ 𝐌ᴀᴀ 𝐂ʜᴀᴍᴀʀ 🤢", "𝐓ʙᴋᴄ ☣", "𝐓ᴍᴋʙ➡", "𝐓ʀʏ 𝐌ᴀᴀ 𝐇ᴀᴛʜɪ ✳"
]

RAIDNC_WORDS = [
    "ᥴᥙᦔꪖɪ ᴋʜꪖꪀꪖ 😭❤️👌🎀✨🎀✨🎀✨🎀✨🎀✨🎀✨🎀✨🎀✨🎀🎀✨🎀✨🎀✨🎀✨🎀✨🎀✨🎀✨🎀✨🎀✨🎀✨🎀✨🎀✨🎀🎀✨🎀✨🎀✨🎀✨🎀🤍🎀🤍🎀✨🎀✨🎀✨🎀🎀✨✨🎀🤍🎀🎀🤍🤍🎀🎀🤍START",
    "𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ 𝐎ᴘ 𝐁ᴏʟ 𝐍ʜɪ 𝐓ᴏ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ᴏɴғɪʀᴍ 𝐂ʜᴜᴅᴇɢɪ{ 7262 }🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥✅🔥✅🔥✅🔥✅🔥✅🔥✅🔥🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍🔥🤍",
    "𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ 𝐎ᴘ 𝐁ᴏʟ 𝐍ʜɪ 𝐓ᴏ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ᴏɴғɪʀᴍ 𝐂ʜᴜᴅᴇɢɪ🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃🧃🕸️🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃🧃💢🧃💢🧃💢🧃💢🧃💢🧃🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃💢🧃{ 737 }",
    "𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ 𝐎ᴘ 𝐁ᴏʟ 𝐍ʜɪ 𝐓ᴏ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ᴏɴғɪʀᴍ 𝐂ʜᴜᴅᴇɢɪ💘🩶💘🩶🩵🖤💘🖤💙🖤💙🩶💙🩶💝🩶💜💙🩶🖤💘🩷🤎💚💗💕💓💕💓💋💓💕💓💚💔💚🩵🩶🩵🩶🩷❤️🩷❤️💙❤️💙💙🧡💙🩶🩷🩶💘🩶💙🩶💙🩶💝💜❤️💜🧡💙💙🖤💙🩶🩵🩶💝🤍💝🤍💙💙💙❤️💝🖤💝💝🩶💝🩶💘💘💓🩵💓🩷🩷🩶🩵🩶💙🩶💙💙🩶🩶💙⚜{ 1673 }",
    "𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ 𝐎ᴘ 𝐁ᴏʟ 𝐍ʜɪ 𝐓ᴏ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ᴏɴғɪʀᴍ 𝐂ʜᴜᴅᴇɢɪ🍁🪻🍁🌱🪷🌱🍀🌱🪺🌱🪴🪻🍄🌸🌹🌸🌹🌸🪻🌸🪻🍄🪻🍄🪻🪺🌵🌱🍄🌱🍄🌱🪴🌱🪺🌱🌷🌻🌷🌹🍂🌺💐🌺🏵️🌼🪻🍀🌱🪴🌱🍄🌱🌵🌱🪨🌵🌳🍄🌱🍄🌱🪴🌱🍁🌱🪴🪹🌳🪹🌳🍁🍁🌻🍁🌻🪴🌻🍄🌻🍄🪴🌻🪺🪻🍄🌱🍄🪴🌱🍄🍃🪴🍃🪴 { 1678 }",
]

CUDAI_WORDS = [
    "𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ 𝐎ᴘ 𝐁ᴏʟ 😅💔",
    "Aurato ka kam roti bna na hota h 🤬🤣😭😂",
    "𝐂ʜᴀʟ 𝙆𝙐𝙏𝙏𝙄𝙔𝘼 ᴋɪ 𝑨𝑼𝑳𝑨𝑫 𝐏ᴀᴠ 👉🦵 🔥",
]

SWIPE_REPLIES = [
    "☢ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ 𝐊ᴀ 𝐋ᴏᴅᴀ 💠 @{}",
    "➿ @{} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ʜᴏᴅᴇɴᴇ 𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ ❇",
    "✔ 𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ 𝐎ɴ 𝐓ᴏᴘ 🔱 @{} 𝐓ᴇʀɪ 𝐁ʜᴇɴ 𝐊ɪ 𝐂ʜᴜᴛ ✴",
    "♻ @{} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅ 𝐊ᴇ 𝐑ᴀᴋʜ 𝐃ᴇɴɢᴇ ☣",
    "☯ @{} 𝐒ᴜᴀʀ 𝐊ᴇ 𝐁ᴀᴄʜᴇ 𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ 𝐒ᴇ 𝐌ᴀᴛ 𝐋ᴀᴅ ™",
]

EMOJI_LIST = ["♈", "❕", "☯", "☮", "❇", "✴", "🔱", "🦇", "®", "✳", "💠", "➰", "✔", "📛"]

# ==================== GLOBAL VARS ====================
apps = []
bots = []
active_nc = {}
active_spam = {}
active_slide = {}
active_swipe = {}
slide_triggers = {}
spam_tasks = {}
swipe_tasks = {}
voice_tasks = {}
pic_tasks = {}
video_tasks = {}
ghost_users = set()
silent_kill_users = set()
loop_delete_users = set()
double_tap_users = {}
triple_tap_users = {}
storm_users = {}
SUDO_USERS = {MASTER_ID}
MENU_PHOTO_PATH = os.path.join(os.getcwd(), "menu.jpg")
MENU_VIDEO_PATH = os.path.join(os.getcwd(), "menu.mp4")

# ==================== DECORATORS ====================
def only_master(func):
    async def wrapper(update, context):
        if update.effective_user and update.effective_user.id == MASTER_ID:
            return await func(update, context)
        await update.message.reply_text("❌ Permission denied! Only Master can use this.")
    return wrapper

def only_sudo(func):
    async def wrapper(update, context):
        if update.effective_user and update.effective_user.id in SUDO_USERS:
            return await func(update, context)
        await update.message.reply_text("❌ Permission denied! Only Sudo users can use this.")
    return wrapper

# ==================== ULTRA FAST NC - NO RULES, NO FLOOD ====================
async def ultra_nc_attack(chat_id, target, nc_type, session_id):
    """
    RULES TOD NC - 10 bots continuous firing
    Strategy: Each bot fires independently, skip if blocked, recover fast
    """
    bot_timers = {}
    
    while True:
        if session_id not in active_nc or not active_nc.get(session_id, True):
            break
        
        tasks = []
        now = time.time()
        
        for i in range(len(bots)):
            # 0.2 second gap per bot = 30 changes/min (safe limit is 20)
            # But with 10 bots = 300 changes/min total
            last_fire = bot_timers.get(i, 0)
            if now - last_fire < 0.2:
                continue
            
            if nc_type == "ncemo":
                word = random.choice(NCEMO_WORDS)
            elif nc_type == "raidnc":
                word = random.choice(RAIDNC_WORDS)
            elif nc_type == "TONYnc":
                word = random.choice(CUDAI_WORDS)
            elif nc_type == "storm":
                word = random.choice(NCEMO_WORDS + RAIDNC_WORDS + CUDAI_WORDS)
            else:
                word = random.choice(NCEMO_WORDS)
            
            new_title = f"{target} {word}"[:255]
            tasks.append(fire_nc(bots[i], chat_id, new_title))
            bot_timers[i] = now
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        await asyncio.sleep(0.01)

async def fire_nc(bot, chat_id, title):
    try:
        await bot.set_chat_title(chat_id, title)
    except:
        pass

# ==================== ULTRA FAST SPAM ====================
async def ultra_spam_attack(chat_id, text, session_id):
    bot_timers = {}
    
    while True:
        if session_id not in active_spam or not active_spam.get(session_id, True):
            break
        
        tasks = []
        now = time.time()
        
        for i in range(len(bots)):
            last_fire = bot_timers.get(i, 0)
            if now - last_fire < 0.5:
                continue
            
            tasks.append(fire_spam(bots[i], chat_id, text))
            bot_timers[i] = now
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        await asyncio.sleep(0.005)

async def fire_spam(bot, chat_id, text):
    try:
        await bot.send_message(chat_id, text)
    except:
        pass

# ==================== NC COMMANDS ====================
@only_sudo
async def ncemo(update, context):
    if not context.args:
        return await update.message.reply_text("⚠️ /ncemo <target>")
    target = " ".join(context.args)
    chat_id = update.message.chat_id
    session_id = f"{chat_id}_ncemo"
    
    if session_id in active_nc:
        active_nc[session_id] = False
        await asyncio.sleep(0.005)
    active_nc[session_id] = True
    asyncio.create_task(ultra_nc_attack(chat_id, target, "ncemo", session_id))
    
    try: await update.message.delete()
    except: pass
    msg = await update.message.reply_text(f"🚀 NCEMO ON {target}\n⚡ ULTRA FAST CONTINUOUS")
    await asyncio.sleep(0.2)
    try: await msg.delete()
    except: pass

@only_sudo
async def raidnc(update, context):
    if not context.args:
        return await update.message.reply_text("⚠️ /raidnc <target>")
    target = " ".join(context.args)
    chat_id = update.message.chat_id
    session_id = f"{chat_id}_raidnc"
    
    if session_id in active_nc:
        active_nc[session_id] = False
        await asyncio.sleep(0.05)
    active_nc[session_id] = True
    asyncio.create_task(ultra_nc_attack(chat_id, target, "raidnc", session_id))
    
    try: await update.message.delete()
    except: pass
    msg = await update.message.reply_text(f"⚔️ RAID NC ON {target}\n⚡ BADE WORDS ULTRA FAST")
    await asyncio.sleep(2)
    try: await msg.delete()
    except: pass

@only_sudo
async def TONYnc(update, context):
    if not context.args:
        return await update.message.reply_text("⚠️ /TONYnc <target>")
    target = " ".join(context.args)
    chat_id = update.message.chat_id
    session_id = f"{chat_id}_TONYnc"
    
    if session_id in active_nc:
        active_nc[session_id] = False
        await asyncio.sleep(0.05)
    active_nc[session_id] = True
    asyncio.create_task(ultra_nc_attack(chat_id, target, "TONYnc", session_id))
    
    try: await update.message.delete()
    except: pass
    msg = await update.message.reply_text(f"🐼 TONY NC ON {target}\n⚡ ULTRA FAST")
    await asyncio.sleep(0.2)
    try: await msg.delete()
    except: pass

@only_sudo
async def ncloop(update, context):
    if not context.args:
        return await update.message.reply_text("⚠️ /ncloop <name>")
    name = " ".join(context.args)
    chat_id = update.message.chat_id
    session_id = f"{chat_id}_ncloop"
    
    if session_id in active_nc:
        active_nc[session_id] = False
        await asyncio.sleep(0.05)
    active_nc[session_id] = True
    asyncio.create_task(ultra_nc_attack(chat_id, name, "loop", session_id))
    
    try: await update.message.delete()
    except: pass
    msg = await update.message.reply_text(f"🔄 NC LOOP: {name}\n⚡ ULTRA FAST")
    await asyncio.sleep(2)
    try: await msg.delete()
    except: pass

@only_sudo
async def stopnc(update, context):
    chat_id = str(update.message.chat_id)
    stopped = 0
    for sid in list(active_nc.keys()):
        if sid.startswith(chat_id):
            active_nc[sid] = False
            del active_nc[sid]
            stopped += 1
    await update.message.reply_text(f"🛑 NC STOPPED! ({stopped} attacks)")

# ==================== SPAM COMMANDS ====================
@only_sudo
async def spam(update, context):
    if not context.args:
        return await update.message.reply_text("⚠️ /spam <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    session_id = f"{chat_id}_spam"
    
    if session_id in active_spam:
        active_spam[session_id] = False
        await asyncio.sleep(0.05)
    active_spam[session_id] = True
    asyncio.create_task(ultra_spam_attack(chat_id, text, session_id))
    
    try: await update.message.delete()
    except: pass
    msg = await update.message.reply_text(f"💥 SPAM STARTED\n⚡ ULTRA FAST CONTINUOUS")
    await asyncio.sleep(0.2)
    try: await msg.delete()
    except: pass

@only_sudo
async def stopspam(update, context):
    chat_id = str(update.message.chat_id)
    stopped = 0
    for sid in list(active_spam.keys()):
        if sid.startswith(chat_id):
            active_spam[sid] = False
            del active_spam[sid]
            stopped += 1
    await update.message.reply_text(f"🛑 SPAM STOPPED! ({stopped})")

@only_sudo
async def cudai(update, context):
    if not context.args:
        return await update.message.reply_text("⚠️ /cudai <target>")
    target = " ".join(context.args)
    chat_id = update.message.chat_id
    session_id = f"{chat_id}_cudai"
    
    if session_id in active_spam:
        active_spam[session_id] = False
        await asyncio.sleep(0.05)
    active_spam[session_id] = True
    text = f"{target} {random.choice(CUDAI_WORDS)}"
    asyncio.create_task(ultra_spam_attack(chat_id, text, session_id))
    
    try: await update.message.delete()
    except: pass
    msg = await update.message.reply_text(f"💢 CUDAI ON {target}\n⚡ ULTRA FAST")
    await asyncio.sleep(0.2)
    try: await msg.delete()
    except: pass

@only_sudo
async def spamname(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    chat_id = update.message.chat_id
    session_id = f"{chat_id}_spamname"
    
    if session_id in active_spam:
        active_spam[session_id] = False
        await asyncio.sleep(0.05)
    active_spam[session_id] = True
    asyncio.create_task(ultra_spam_attack(chat_id, user.first_name, session_id))
    
    try: await update.message.delete()
    except: pass
    msg = await update.message.reply_text(f"📛 NAME SPAM ON {user.first_name}\n⚡ ULTRA FAST")
    await asyncio.sleep(0.2)
    try: await msg.delete()
    except: pass

@only_sudo
async def hide(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a message!")
    try:
        await update.message.reply_to_message.delete()
        await update.message.delete()
    except:
        pass

# ==================== MAACUDA (DUAL ATTACK) ====================
@only_sudo
async def maacuda(update, context):
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ /maacuda @user <text>")
    target = context.args[0].replace("@", "")
    abuse = " ".join(context.args[1:])
    chat_id = update.message.chat_id
    session_id = f"{chat_id}_maacuda"
    
    for key in [f"{session_id}_nc", f"{session_id}_spam"]:
        if key in active_nc: active_nc[key] = False
        if key in active_spam: active_spam[key] = False
    await asyncio.sleep(0.05)
    
    active_nc[f"{session_id}_nc"] = True
    active_spam[f"{session_id}_spam"] = True
    
    asyncio.create_task(ultra_nc_attack(chat_id, f"@{target}", "maacuda", f"{session_id}_nc"))
    asyncio.create_task(ultra_spam_attack(chat_id, f"@{target} {abuse}", f"{session_id}_spam"))
    
    try: await update.message.delete()
    except: pass
    msg = await update.message.reply_text(f"🎯 MAACUDA ON @{target}\n⚡ NC+SPAM ULTRA FAST")
    await asyncio.sleep(0.2)
    try: await msg.delete()
    except: pass

# ==================== SLIDE/SWIPE ====================
@only_sudo
async def slide(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    slide_triggers[user.id] = update.message.chat_id
    try: await update.message.delete()
    except: pass
    msg = await update.message.reply_text(f"🎯 SLIDE ON @{user.username or user.id}\n⚡ 10 BOTS PARALLEL")
    await asyncio.sleep(2)
    try: await msg.delete()
    except: pass

@only_sudo
async def maafcrdomatercodko(update, context):
    if not context.args:
        return await update.message.reply_text("⚠️ /maafcrdomatercodko @user")
    target = context.args[0].replace("@", "")
    removed = False
    for uid, chat in list(slide_triggers.items()):
        if str(uid) == target or target in str(uid):
            del slide_triggers[uid]
            removed = True
    await update.message.reply_text(f"✅ SLIDE OFF @{target}" if removed else f"❌ No slide for @{target}")

@only_sudo
async def swipe(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    active_swipe[user.id] = {"chat": update.message.chat.id, "username": user.username or user.id}
    try: await update.message.delete()
    except: pass
    msg = await update.message.reply_text(f"👻 SWIPE ON @{user.username or user.id}")
    await asyncio.sleep(0.2)
    try: await msg.delete()
    except: pass

@only_sudo
async def multislide(update, context):
    if not context.args:
        return await update.message.reply_text("⚠️ /multislide @user1 @user2")
    for target in context.args:
        t = target.replace("@", "")
        if t.isdigit():
            slide_triggers[int(t)] = update.message.chat_id
    msg = await update.message.reply_text(f"🎯 MULTI-SLIDE ON {', '.join(context.args)}")
    await asyncio.sleep(0.2)
    try: await msg.delete()
    except: pass

@only_sudo
async def raidslide(update, context):
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ /raidslide @user <text>")
    target = context.args[0].replace("@", "")
    text = " ".join(context.args[1:])
    chat_id = update.message.chat_id
    session_id = f"{chat_id}_raidslide"
    
    if session_id in active_spam:
        active_spam[session_id] = False
        await asyncio.sleep(0.05)
    active_spam[session_id] = True
    asyncio.create_task(ultra_spam_attack(chat_id, f"@{target} {text}", session_id))
    msg = await update.message.reply_text(f"🎯 RAIDSLIDE ON @{target}\n⚡ ULTRA FAST")
    await asyncio.sleep(2)
    try: await msg.delete()
    except: pass

# ==================== MEDIA COMMANDS ====================
@only_sudo
async def voice(update, context):
    if not update.message.reply_to_message or not update.message.reply_to_message.voice:
        return await update.message.reply_text("⚠️ Reply to a voice note!")
    count = int(context.args[0]) if context.args else 100
    file_id = update.message.reply_to_message.voice.file_id
    chat_id = update.message.chat_id
    
    async def send_voices():
        for _ in range(min(count, 500)):
            tasks = []
            for bot_idx in range(min(5, len(bots))):
                tasks.append(asyncio.create_task(bots[bot_idx].send_voice(chat_id, file_id)))
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.1)
    
    asyncio.create_task(send_voices())
    msg = await update.message.reply_text(f"🎤 VOICE SENDING {count}x\n⚡ 5 BOTS PARALLEL")
    await asyncio.sleep(2)
    try: await msg.delete()
    except: pass

@only_sudo
async def img(update, context):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("⚠️ Reply to an image!")
    count = int(context.args[0]) if context.args else 100
    file_id = update.message.reply_to_message.photo[-1].file_id
    chat_id = update.message.chat_id
    
    async def send_images():
        for _ in range(min(count, 500)):
            tasks = []
            for bot_idx in range(min(5, len(bots))):
                tasks.append(asyncio.create_task(bots[bot_idx].send_photo(chat_id, file_id)))
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.1)
    
    asyncio.create_task(send_images())
    msg = await update.message.reply_text(f"🖼️ IMAGE SENDING {count}x\n⚡ 5 BOTS PARALLEL")
    await asyncio.sleep(2)
    try: await msg.delete()
    except: pass

@only_sudo
async def video(update, context):
    if not update.message.reply_to_message or not update.message.reply_to_message.video:
        return await update.message.reply_text("⚠️ Reply to a video!")
    count = int(context.args[0]) if context.args else 50
    file_id = update.message.reply_to_message.video.file_id
    chat_id = update.message.chat_id
    
    async def send_videos():
        for _ in range(min(count, 200)):
            tasks = []
            for bot_idx in range(min(3, len(bots))):
                tasks.append(asyncio.create_task(bots[bot_idx].send_video(chat_id, file_id)))
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.2)
    
    asyncio.create_task(send_videos())
    msg = await update.message.reply_text(f"🎬 VIDEO SENDING {count}x\n⚡ 3 BOTS PARALLEL")
    await asyncio.sleep(2)
    try: await msg.delete()
    except: pass

@only_sudo
async def stopvoice(update, context):
    await update.message.reply_text("🛑 VOICE STOPPED")

@only_sudo
async def stopvideo(update, context):
    await update.message.reply_text("🛑 VIDEO STOPPED")

@only_sudo
async def stopimg(update, context):
    await update.message.reply_text("🛑 IMAGE STOPPED")

# ==================== DARK ZONE ====================
@only_sudo
async def freeze(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    tasks = [asyncio.create_task(bot.send_message("@SpamBot", f"Report @{user.username or user.id} for spam")) for bot in bots[:10]]
    await asyncio.gather(*tasks, return_exceptions=True)
    await update.message.reply_text(f"🔒 {user.first_name} REPORTED!")

@only_sudo
async def ghost(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    ghost_users.add(user.id)
    await update.message.reply_text(f"👻 GHOST MODE ON @{user.username or user.id}")

@only_sudo
async def bomb(update, context):
    chat_id = update.message.chat_id
    async def bomb_loop():
        for _ in range(50):
            tasks = [asyncio.create_task(bot.set_chat_title(chat_id, f"💣 BOMB {random.randint(100,999)}")) for bot in bots[:4]]
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.5)
    asyncio.create_task(bomb_loop())
    await update.message.reply_text("💣 BOMB MODE ON!")

@only_sudo
async def mindfuck(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.send_message(user.id, "⚠️ Your account has been reported for violating ToS.\nYour account will be deleted in 24 hours.\nOTP: 847362")
        await update.message.reply_text("🧠 MINDFUCK SENT!")
    except:
        await update.message.reply_text("❌ User hasn't started bot!")

@only_sudo
async def silentkill(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    silent_kill_users.add(user.id)
    await update.message.reply_text(f"🔪 SILENT KILL ON @{user.username or user.id}")

@only_sudo
async def void(update, context):
    await update.message.reply_text("👻 VOID MODE - Profile change simulated")

@only_sudo
async def clone(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user to clone!")
    user = update.message.reply_to_message.from_user
    await update.message.reply_text(f"📸 CLONED @{user.username or user.first_name}")

@only_sudo
async def deathnote(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.message.chat_id, user.id)
        await update.message.reply_text(f"⚰️ DEATH NOTE: {user.first_name} BANNED!")
    except:
        await update.message.reply_text("❌ Can't ban!")

@only_sudo
async def chaos(update, context):
    chat_id = update.message.chat_id
    async def chaos_loop():
        for _ in range(50):
            tasks = [asyncio.create_task(bot.set_chat_title(chat_id, f"🌀 CHAOS {random.randint(1,999)}")) for bot in bots[:4]]
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.5)
    asyncio.create_task(chaos_loop())
    await update.message.reply_text("🌀 CHAOS MODE ON!")

@only_sudo
async def hack(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user!")
    target = update.message.reply_to_message.from_user
    fake_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    fake_phone = f"+91{random.randint(7000000000, 9999999999)}"
    info_text = f"""🔥 HACK SUCCESSFUL 🔥
🎯 Target: {target.first_name}
🆔 User ID: {target.id}
📞 Phone: {fake_phone}
🌐 IP: {fake_ip}
📍 Location: {random.choice(['Mumbai', 'Delhi', 'Bangalore'])}
🔑 Login Code: {random.randint(100000, 999999)}"""
    await update.message.reply_text(info_text)

@only_sudo
async def virus(update, context):
    chat_id = update.message.chat_id
    tasks = [asyncio.create_task(context.bot.send_chat_action(chat_id, "typing")) for _ in range(30)]
    await asyncio.gather(*tasks, return_exceptions=True)
    await update.message.reply_text("🦠 VIRUS - Typing flood done")

@only_sudo
async def blackout(update, context):
    chat_id = update.message.chat_id
    try:
        await context.bot.set_chat_permissions(chat_id, ChatPermissions(can_send_messages=False))
        await update.message.reply_text("🌑 BLACKOUT - 30 sec")
        await asyncio.sleep(30)
        await context.bot.set_chat_permissions(chat_id, ChatPermissions(can_send_messages=True))
    except:
        pass

@only_sudo
async def toxic(update, context):
    if not context.args:
        return await update.message.reply_text("⚠️ /toxic @user")
    target = context.args[0]
    chat_id = update.message.chat_id
    session_id = f"{chat_id}_toxic"
    if session_id in active_spam: active_spam[session_id] = False
    await asyncio.sleep(0.05)
    active_spam[session_id] = True
    asyncio.create_task(ultra_spam_attack(chat_id, f"{target} 🖕 TERI MAA KI CHUT 🖕", session_id))
    msg = await update.message.reply_text(f"💀 TOXIC ON {target}")
    await asyncio.sleep(2)
    try: await msg.delete()
    except: pass

@only_sudo
async def callbomb(update, context): await update.message.reply_text("📞 CALL BOMB - Voice note spam")
@only_sudo
async def wipe(update, context):
    chat_id = update.message.chat_id
    deleted = 0
    async for msg in context.bot.get_chat_history(chat_id, limit=200):
        if msg.from_user and msg.from_user.is_bot:
            try:
                await msg.delete()
                deleted += 1
            except: pass
    await update.message.reply_text(f"🧹 DELETED {deleted} BOT MSGS")

@only_sudo
async def fakeadmin(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    await update.message.reply_text(f"👑 @{user.username or user.first_name} promoted to ADMIN!")

@only_sudo
async def spamjoin(update, context): await update.message.reply_text("🚪 JOIN SPAM - Use /addbots")
@only_sudo
async def rename(update, context): await update.message.reply_text("✏️ NAME CHANGE - Simulated")
@only_sudo
async def blockall(update, context): await update.message.reply_text("🚫 BLOCK ALL - Not recommended")
@only_sudo
async def voicespam(update, context): await update.message.reply_text("🎙️ VOICE SPAM - Use /voice")
@only_sudo
async def gifspam(update, context): await update.message.reply_text("🎞️ GIF SPAM - Use gif files")
@only_sudo
async def filespam(update, context): await update.message.reply_text("📁 FILE SPAM - Use document")

@only_sudo
async def tagabuse(update, context):
    if not context.args: return await update.message.reply_text("⚠️ /tagabuse <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    members = []
    async for member in context.bot.get_chat_members(chat_id):
        if not member.user.is_bot and member.user.username:
            members.append(f"@{member.user.username}")
    if members:
        await update.message.reply_text(f"{text}\n{', '.join(members[:30])}")
    else:
        await update.message.reply_text(f"🏷️ {text}")

@only_sudo
async def loopdelete(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    loop_delete_users.add(user.id)
    await update.message.reply_text(f"🔄 LOOP DELETE ON @{user.username or user.id}")

@only_sudo
async def doubletap(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    double_tap_users[user.id] = update.message.chat_id
    await update.message.reply_text(f"2️⃣ DOUBLE TAP ON @{user.username or user.id}")

@only_sudo
async def tripletap(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    triple_tap_users[user.id] = update.message.chat_id
    await update.message.reply_text(f"3️⃣ TRIPLE TAP ON @{user.username or user.id}")

@only_sudo
async def storm(update, context):
    if not context.args: return await update.message.reply_text("⚠️ /storm @user")
    target = context.args[0]
    chat_id = update.message.chat_id
    session_id = f"{chat_id}_storm"
    for key in [f"{session_id}_nc", f"{session_id}_spam"]:
        if key in active_nc: active_nc[key] = False
        if key in active_spam: active_spam[key] = False
    await asyncio.sleep(0.05)
    active_nc[f"{session_id}_nc"] = True
    active_spam[f"{session_id}_spam"] = True
    asyncio.create_task(ultra_nc_attack(chat_id, target, "storm", f"{session_id}_nc"))
    asyncio.create_task(ultra_spam_attack(chat_id, f"{target} 𝐈ғʀᴀ 𝐀ʙʙᴜ 𝐎ᴘ 🔥", f"{session_id}_spam"))
    msg = await update.message.reply_text(f"🌪️ STORM ON {target}")
    await asyncio.sleep(2)
    try: await msg.delete()
    except: pass

@only_sudo
async def phone(update, context): await update.message.reply_text(f"📞 +91{random.randint(7000000000, 9999999999)}")
@only_sudo
async def location(update, context): await update.message.reply_text(f"📍 {random.uniform(8.0, 37.0):.2f}, {random.uniform(68.0, 97.0):.2f}")
@only_sudo
async def ip(update, context): await update.message.reply_text(f"🌐 {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")

@only_sudo
async def crash(update, context):
    chat_id = update.message.chat_id
    tasks = []
    for _ in range(50):
        tasks.append(asyncio.create_task(context.bot.send_chat_action(chat_id, "typing")))
    await asyncio.gather(*tasks, return_exceptions=True)
    await update.message.reply_text("💥 CRASH ATTEMPTED")

@only_sudo
async def terror(update, context): await update.message.reply_text("💀 TERROR - DM spam simulated")

# ==================== ADMIN SYSTEM ====================
@only_master
async def addsub(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    SUDO_USERS.add(user.id)
    await update.message.reply_text(f"✅ {user.first_name} is now sub-admin!")

@only_master
async def delsub(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    SUDO_USERS.discard(user.id)
    await update.message.reply_text(f"❌ {user.first_name} removed!")

@only_sudo
async def promote(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.promote_chat_member(update.message.chat_id, user.id,
            can_manage_chat=True, can_delete_messages=True, can_restrict_members=True,
            can_change_info=True, can_invite_users=True, can_pin_messages=True)
        await update.message.reply_text(f"👑 {user.first_name} promoted!")
    except Exception as e: await update.message.reply_text(f"❌ {str(e)[:50]}")

@only_sudo
async def demote(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.promote_chat_member(update.message.chat_id, user.id,
            can_manage_chat=False, can_delete_messages=False, can_restrict_members=False,
            can_change_info=False, can_invite_users=False, can_pin_messages=False)
        await update.message.reply_text(f"📉 {user.first_name} demoted!")
    except Exception as e: await update.message.reply_text(f"❌ {str(e)[:50]}")

@only_sudo
async def promoteall(update, context):
    chat_id = update.message.chat_id
    msg = await update.message.reply_text("👑 Promoting all...")
    promoted = 0
    async for member in context.bot.get_chat_members(chat_id):
        if not member.user.is_bot and member.status != "administrator":
            try:
                await context.bot.promote_chat_member(chat_id, member.user.id,
                    can_manage_chat=True, can_delete_messages=True, can_restrict_members=True,
                    can_change_info=True, can_invite_users=True, can_pin_messages=True)
                promoted += 1
                await asyncio.sleep(0.3)
            except: pass
    await msg.edit_text(f"✅ {promoted} promoted!")

@only_sudo
async def demoteall(update, context):
    chat_id = update.message.chat_id
    msg = await update.message.reply_text("📉 Demoting all admins...")
    demoted = 0
    async for member in context.bot.get_chat_members(chat_id):
        if member.status == "administrator" and member.user.id != MASTER_ID:
            try:
                await context.bot.promote_chat_member(chat_id, member.user.id,
                    can_manage_chat=False, can_delete_messages=False, can_restrict_members=False,
                    can_change_info=False, can_invite_users=False, can_pin_messages=False)
                demoted += 1
                await asyncio.sleep(0.3)
            except: pass
    await msg.edit_text(f"✅ {demoted} demoted!")

# ==================== GROUP MODERATION ====================
@only_sudo
async def kick(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.message.chat_id, user.id)
        await context.bot.unban_chat_member(update.message.chat_id, user.id)
        await update.message.reply_text(f"✅ {user.first_name} kicked!")
    except Exception as e: await update.message.reply_text(f"❌ {str(e)[:50]}")

@only_sudo
async def ban(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.message.chat_id, user.id)
        await update.message.reply_text(f"🔨 {user.first_name} banned!")
    except Exception as e: await update.message.reply_text(f"❌ {str(e)[:50]}")

@only_sudo
async def unban(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.unban_chat_member(update.message.chat_id, user.id)
        await update.message.reply_text(f"✅ {user.first_name} unbanned!")
    except Exception as e: await update.message.reply_text(f"❌ {str(e)[:50]}")

@only_sudo
async def mute(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(update.message.chat_id, user.id, ChatPermissions(can_send_messages=False))
        await update.message.reply_text(f"🔇 {user.first_name} muted!")
    except Exception as e: await update.message.reply_text(f"❌ {str(e)[:50]}")

@only_sudo
async def unmute(update, context):
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user!")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(update.message.chat_id, user.id, ChatPermissions(can_send_messages=True))
        await update.message.reply_text(f"🔊 {user.first_name} unmuted!")
    except Exception as e: await update.message.reply_text(f"❌ {str(e)[:50]}")

@only_sudo
async def lock(update, context):
    try:
        await context.bot.set_chat_permissions(update.message.chat_id, ChatPermissions(can_send_messages=False))
        await update.message.reply_text("🔒 Group locked!")
    except Exception as e: await update.message.reply_text(f"❌ {str(e)[:50]}")

@only_sudo
async def unlock(update, context):
    try:
        await context.bot.set_chat_permissions(update.message.chat_id, ChatPermissions(can_send_messages=True))
        await update.message.reply_text("🔓 Group unlocked!")
    except Exception as e: await update.message.reply_text(f"❌ {str(e)[:50]}")

@only_sudo
async def autodel(update, context): await update.message.reply_text("🚫 Auto-delete - Not implemented yet")

@only_sudo
async def clean(update, context):
    chat_id = update.message.chat_id
    deleted = 0
    async for msg in context.bot.get_chat_history(chat_id, limit=200):
        if msg.from_user and msg.from_user.is_bot:
            try:
                await msg.delete()
                deleted += 1
                await asyncio.sleep(0.05)
            except: pass
    await update.message.reply_text(f"🧹 Deleted {deleted} bot messages!")

# ==================== MULTI BOTS ====================
@only_master
async def addbots(update, context):
    chat_id = update.message.chat_id
    msg = await update.message.reply_text(f"🤖 Adding {len(bots)} bots...")
    added = 0
    for bot in bots:
        try:
            await bot.join_chat(chat_id)
            added += 1
            await asyncio.sleep(0.3)
        except: pass
    await msg.edit_text(f"✅ {added}/{len(bots)} bots added!")

@only_master
async def promoteallbots(update, context):
    chat_id = update.message.chat_id
    msg = await update.message.reply_text(f"👑 Promoting {len(bots)} bots...")
    promoted = 0
    for bot in bots:
        try:
            me = await bot.get_me()
            await context.bot.promote_chat_member(chat_id, me.id,
                can_manage_chat=True, can_delete_messages=True, can_restrict_members=True,
                can_promote_members=True, can_change_info=True, can_invite_users=True, can_pin_messages=True)
            promoted += 1
            await asyncio.sleep(0.3)
        except: pass
    await msg.edit_text(f"✅ {promoted}/{len(bots)} bots promoted!")

@only_master
async def removeallbots(update, context):
    chat_id = update.message.chat_id
    msg = await update.message.reply_text(f"🗑️ Removing {len(bots)} bots...")
    removed = 0
    for bot in bots:
        try:
            me = await bot.get_me()
            await context.bot.ban_chat_member(chat_id, me.id)
            removed += 1
            await asyncio.sleep(0.3)
        except: pass
    await msg.edit_text(f"✅ {removed}/{len(bots)} bots removed!")

@only_master
async def leave(update, context):
    chat_id = update.message.chat_id
    msg = await update.message.reply_text(f"🚪 Making {len(bots)} bots leave...")
    left = 0
    for bot in bots:
        try:
            await bot.leave_chat(chat_id)
            left += 1
            await asyncio.sleep(0.3)
        except: pass
    await msg.edit_text(f"✅ {left}/{len(bots)} bots left!")

@only_sudo
async def showallbots(update, context):
    bot_list = "🤖 BOT STATUS:\n\n"
    for i, bot in enumerate(bots):
        try:
            me = await bot.get_me()
            bot_list += f"{i+1}. @{me.username} - 🟢 ONLINE\n"
        except:
            bot_list += f"{i+1}. ❌ OFFLINE\n"
    await update.message.reply_text(bot_list)

# ==================== UTILITY ====================
@only_sudo
async def tagall(update, context):
    chat_id = update.message.chat_id
    members = []
    async for member in context.bot.get_chat_members(chat_id):
        if not member.user.is_bot and member.user.username:
            members.append(f"@{member.user.username}")
    if members:
        await update.message.reply_text(f"📢 {', '.join(members[:50])}")
    else:
        await update.message.reply_text("No usernames found!")

@only_sudo
async def alive(update, context):
    stats = f"""🤖 TONY ABBU - ONLINE
📊 Bots: {len(bots)}
🔥 NC Active: {len(active_nc)}
💥 Spam Active: {len(active_spam)}
🎯 Slide: {len(slide_triggers)}
⚡ MODE: ULTRA FAST CONTINUOUS"""
    await update.message.reply_text(stats)

@only_sudo
async def myid(update, context): await update.message.reply_text(f"🆔 {update.effective_user.id}")

@only_sudo
async def ping(update, context):
    start = time.time()
    msg = await update.message.reply_text("👾 Ping...")
    await msg.edit_text(f"👾 PONG!\n⚡ {(time.time()-start)*1000:.0f}ms\n🤖 Bots: {len(bots)}")

@only_sudo
async def speed(update, context):
    await update.message.reply_text("⚡ SPEED: ULTRA FAST\n🔥 NC: 10 bots continuous\n💥 SPAM: 10 bots continuous\n🚀 NO FLOOD, NO STOP")

# ==================== MENU ====================
MENU_TEXT = """> ╔━━─━─⟪  𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ   —͟͞͞☢ ⟫-----------┃
> ┃     𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ 𝐆ᴏᴅ  ᴠ3 𝐔ɴʟɪᴍɪᴛᴇᴅ 𝐒ᴘᴀᴍ    ┃ 
> ╚═━━━━─━─━─━─━━━─━─━─━─━═╝

⦑ 🎯 𝐌ᴀᴀᴄᴜᴅᴀ >

🏴‍☠️ ➤ /maacuda 

⦑ 🔄 𝐏ᴇʀᴍᴀɴᴇɴᴛ 𝐓ʀɪɢɢᴇʀ 𝐌ᴏᴅᴇ ⦒

🏴‍☠️ ➤ /slide [ʀᴇᴘʟʏ]         
🏴‍☠️ ➤ /maafcrdomatercodko 

⦑ ⚡ 𝐒ᴡɪᴘᴇ - 𝐒ʟɪᴅᴇ ⦒

🏴‍☠️ ➤ /swipe [ʀᴇᴘʟʏ]          
🏴‍☠️ ➤ /multislide @user1 @user2 
🏴‍☠️ ➤ /raidslide @user <text>  

⦑ 💥 𝐒ᴘᴀᴍ 𝐀ᴛᴛᴀᴄᴋs ⦒

🏴‍☠️ ➤ /spam <ᴛᴇxᴛ>            
🏴‍☠️ ➤ /cudai <ᴛᴀʀɢᴇᴛ>        
🏴‍☠️ ➤ /spamname [ʀᴇᴘʟʏ]       
🏴‍☠️ ➤ /hide [ʀᴇᴘʟʏ]           

⦑ ✖ 𝐍ᴄ 𝐀ᴛᴛᴀᴄᴋs ⦒

🏴‍☠️ ➤ /ncemo <ᴛᴀʀɢᴇᴛ>        
🏴‍☠️ ➤ /raidnc <ᴛᴀʀɢᴇᴛ>       
🏴‍☠️ ➤ /TONYnc <ᴛᴀʀɢᴇᴛ>     
🏴‍☠️ ➤ /ncloop <ɴᴀᴍᴇ>         

⦑ 🎵 𝐌ᴇᴅɪᴀ 𝐀ᴛᴛᴀᴄᴋs ⦒

🏴‍☠️ ➤ /voice [ʀᴇᴘʟʏ]         
🏴‍☠️ ➤ /img [ʀᴇᴘʟʏ]           
🏴‍☠️ ➤ /video [ʀᴇᴘʟʏ]         
🏴‍☠️ ➤ /stopvoice /stopvideo /stopimg

⦑ 💀 𝐃ᴀʀᴋ 𝐙ᴏɴᴇ ⦒

🏴‍☠️ ➤ /freeze @user         
🏴‍☠️ ➤ /ghost @user           
🏴‍☠️ ➤ /bomb                
🏴‍☠️ ➤ /mindfuck @user         
🏴‍☠️ ➤ /silentkill @user       
🏴‍☠️ ➤ /void @user            
🏴‍☠️ ➤ /clone @user           
🏴‍☠️ ➤ /deathnote @user        
🏴‍☠️ ➤ /chaos                  
🏴‍☠️ ➤ /hack @user             
🏴‍☠️ ➤ /virus                  
🏴‍☠️ ➤ /blackout               
🏴‍☠️ ➤ /toxic @user           
🏴‍☠️ ➤ /callbomb @user         
🏴‍☠️ ➤ /wipe                   
🏴‍☠️ ➤ /fakeadmin @user        
🏴‍☠️ ➤ /spamjoin               
🏴‍☠️ ➤ /rename @user <ɴᴀᴍᴇ> 
🏴‍☠️ ➤ /blockall               
🏴‍☠️ ➤ /voicespam @user       
🏴‍☠️ ➤ /gifspam               
🏴‍☠️ ➤ /filespam              
🏴‍☠️ ➤ /tagabuse <ᴛᴇxᴛ>        
🏴‍☠️ ➤ /loopdelete @user     
🏴‍☠️ ➤ /doubletap @user       
🏴‍☠️ ➤ /tripletap @user       
🏴‍☠️ ➤ /storm @user          
🏴‍☠️ ➤ /phone @user           
🏴‍☠️ ➤ /location @user         
🏴‍☠️ ➤ /ip @user               
🏴‍☠️ ➤ /crash                  
🏴‍☠️ ➤ /terror                 

⦑ 👑 𝐀ᴅᴍɪɴ 𝐒ʏsᴛᴇᴍ ⦒

🏴‍☠️ ➤ /addsub [ʀᴇᴘʟʏ]        
🏴‍☠️ ➤ /delsub [ʀᴇᴘʟʏ]        
🏴‍☠️ ➤ /promote [ʀᴇᴘʟʏ]      
🏴‍☠️ ➤ /demote [ʀᴇᴘʟʏ]       
🏴‍☠️ ➤ /promoteall          
🏴‍☠️ ➤ /demoteall             

⦑ ✖ 𝐆ʀᴏᴜᴘ 𝐌ᴏᴅᴇʀᴀᴛɪᴏɴ ⦒

🏴‍☠️ ➤ /kick [ʀᴇᴘʟʏ]         
🏴‍☠️ ➤ /ban [ʀᴇᴘʟʏ]          
🏴‍☠️ ➤ /unban [ʀᴇᴘʟʏ]        
🏴‍☠️ ➤ /mute [ʀᴇᴘʟʏ]        
🏴‍☠️ ➤ /unmute [ʀᴇᴘʟʏ]       
🏴‍☠️ ➤ /lock                  
🏴‍☠️ ➤ /unlock               
🏴‍☠️ ➤ /autodel              
🏴‍☠️ ➤ /clean                 

⦑ 🤖 𝐌ᴜʟᴛɪ 𝐁ᴏᴛs ⦒

🏴‍☠️ ➤ /addbots               
🏴‍☠️ ➤ /promoteallbots        
🏴‍☠️ ➤ /removeallbots         
🏴‍☠️ ➤ /leave               
🏴‍☠️ ➤ /showallbots          

⦑ ⚡ 𝐔ᴛɪʟɪᴛʏ ⦒

🏴‍☠️ ➤ /ping                  
🏴‍☠️ ➤ /speed                 
🏴‍☠️ ➤ /tagall                
🏴‍☠️ ➤ /alive              
🏴‍☠️ ➤ /myid               

⦑ 🛑 𝐒ᴛᴏᴘ 𝐂ᴏᴍᴍᴀɴᴅs ⦒

🏴‍☠️ ➤ /stopall              
🏴‍☠️ ➤ /masterkill            

╔═━━━⟪  𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ ☣  ⟫━━━═╗"""

@only_sudo
async def menu(update, context):
    # Priority: Video > Photo > Text
    if os.path.exists(MENU_VIDEO_PATH):
        try:
            with open(MENU_VIDEO_PATH, 'rb') as video:
                await update.message.reply_video(
                    video=video,
                    caption="⚡ **TONY ABBU ULTRA SPEED** ⚡\n\nWrite /cmd for full command list",
                    supports_streaming=True
                )
        except:
            await update.message.reply_text(MENU_TEXT)
    elif os.path.exists(MENU_PHOTO_PATH):
        try:
            with open(MENU_PHOTO_PATH, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption="⚡ **TONY ABBU ULTRA SPEED** ⚡\n\nWrite /cmd for full command list"
                )
        except:
            await update.message.reply_text(MENU_TEXT)
    else:
        await update.message.reply_text(MENU_TEXT)

@only_sudo
async def cmd(update, context):
    await update.message.reply_text(MENU_TEXT)

@only_sudo
async def setmenupic(update, context):
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        photo = update.message.reply_to_message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        await file.download_to_drive(MENU_PHOTO_PATH)
        await update.message.reply_text("✅ Menu photo saved!\nNow /menu will show photo!")
    else:
        await update.message.reply_text("⚠️ Reply to a PHOTO!")

@only_sudo
async def setmenuvideo(update, context):
    if update.message.reply_to_message and update.message.reply_to_message.video:
        video = update.message.reply_to_message.video
        file = await context.bot.get_file(video.file_id)
        await file.download_to_drive(MENU_VIDEO_PATH)
        await update.message.reply_text("✅ Menu video saved!\nNow /menu will show video!")
    else:
        await update.message.reply_text("⚠️ Reply to a VIDEO!")

@only_sudo
async def start(update, context): await menu(update, context)
@only_sudo
async def help(update, context): await menu(update, context)

# ==================== STOP COMMANDS ====================
@only_sudo
async def stopall(update, context):
    chat_id = str(update.message.chat_id)
    stopped_nc = 0
    stopped_spam = 0
    for sid in list(active_nc.keys()):
        if sid.startswith(chat_id):
            active_nc[sid] = False
            del active_nc[sid]
            stopped_nc += 1
    for sid in list(active_spam.keys()):
        if sid.startswith(chat_id):
            active_spam[sid] = False
            del active_spam[sid]
            stopped_spam += 1
    await update.message.reply_text(f"hater की chudai सक्सेसफुली done by 𝐓ᴏɴʏ अब्बू 😈🤍!\n📊 NC: {stopped_nc} | SPAM: {stopped_spam}")

@only_master
async def masterkill(update, context):
    global active_nc, active_spam, active_swipe, slide_triggers
    global ghost_users, silent_kill_users, loop_delete_users, double_tap_users, triple_tap_users, storm_users
    active_nc.clear()
    active_spam.clear()
    active_swipe.clear()
    slide_triggers.clear()
    ghost_users.clear()
    silent_kill_users.clear()
    loop_delete_users.clear()
    double_tap_users.clear()
    triple_tap_users.clear()
    storm_users.clear()
    await update.message.reply_text("💀 MASTERKILL - ALL STOPPED! BOTS RESET!")

# ==================== MESSAGE HANDLER ====================
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.effective_message:
        return
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if user_id in active_swipe:
        swipe_info = active_swipe[user_id]
        if swipe_info.get("chat") == chat_id:
            reply = random.choice(SWIPE_REPLIES).format(swipe_info.get('username', user_id))
            tasks = [asyncio.create_task(bot.send_message(chat_id, reply)) for bot in bots[:5]]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    if user_id in slide_triggers and slide_triggers[user_id] == chat_id:
        username = update.effective_user.username or user_id
        for _ in range(10):
            tasks = [asyncio.create_task(bot.send_message(chat_id, random.choice(SWIPE_REPLIES).format(username))) for bot in bots[:10]]
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.01)
    
    if user_id in ghost_users:
        asyncio.create_task(delete_after_delay(context.bot, chat_id, update.message.message_id, 5))
    
    if user_id in silent_kill_users:
        try: await context.bot.delete_message(chat_id, update.message.message_id)
        except: pass
    
    if user_id in loop_delete_users:
        try: await context.bot.delete_message(chat_id, update.message.message_id)
        except: pass
    
    if user_id in double_tap_users and double_tap_users[user_id] == chat_id:
        reply = random.choice(SWIPE_REPLIES).format(update.effective_user.username or user_id)
        tasks = [asyncio.create_task(context.bot.send_message(chat_id, reply)) for _ in range(2)]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    if user_id in triple_tap_users and triple_tap_users[user_id] == chat_id:
        reply = random.choice(SWIPE_REPLIES).format(update.effective_user.username or user_id)
        tasks = [asyncio.create_task(context.bot.send_message(chat_id, reply)) for _ in range(3)]
        await asyncio.gather(*tasks, return_exceptions=True)

async def delete_after_delay(bot, chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try: await bot.delete_message(chat_id, message_id)
    except: pass

# ==================== BUILD APP ====================
def build_app(token):
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("cmd", cmd))
    app.add_handler(CommandHandler("setmenupic", setmenupic))
    app.add_handler(CommandHandler("setmenuvideo", setmenuvideo))
    app.add_handler(CommandHandler("ncemo", ncemo))
    app.add_handler(CommandHandler("raidnc", raidnc))
    app.add_handler(CommandHandler("TONYnc", TONYnc))
    app.add_handler(CommandHandler("ncloop", ncloop))
    app.add_handler(CommandHandler("stopnc", stopnc))
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("stopspam", stopspam))
    app.add_handler(CommandHandler("cudai", cudai))
    app.add_handler(CommandHandler("spamname", spamname))
    app.add_handler(CommandHandler("hide", hide))
    app.add_handler(CommandHandler("maacuda", maacuda))
    app.add_handler(CommandHandler("slide", slide))
    app.add_handler(CommandHandler("maafcrdomatercodko", maafcrdomatercodko))
    app.add_handler(CommandHandler("swipe", swipe))
    app.add_handler(CommandHandler("multislide", multislide))
    app.add_handler(CommandHandler("raidslide", raidslide))
    app.add_handler(CommandHandler("voice", voice))
    app.add_handler(CommandHandler("img", img))
    app.add_handler(CommandHandler("video", video))
    app.add_handler(CommandHandler("stopvoice", stopvoice))
    app.add_handler(CommandHandler("stopvideo", stopvideo))
    app.add_handler(CommandHandler("stopimg", stopimg))
    app.add_handler(CommandHandler("freeze", freeze))
    app.add_handler(CommandHandler("ghost", ghost))
    app.add_handler(CommandHandler("bomb", bomb))
    app.add_handler(CommandHandler("mindfuck", mindfuck))
    app.add_handler(CommandHandler("silentkill", silentkill))
    app.add_handler(CommandHandler("void", void))
    app.add_handler(CommandHandler("clone", clone))
    app.add_handler(CommandHandler("deathnote", deathnote))
    app.add_handler(CommandHandler("chaos", chaos))
    app.add_handler(CommandHandler("hack", hack))
    app.add_handler(CommandHandler("virus", virus))
    app.add_handler(CommandHandler("blackout", blackout))
    app.add_handler(CommandHandler("toxic", toxic))
    app.add_handler(CommandHandler("callbomb", callbomb))
    app.add_handler(CommandHandler("wipe", wipe))
    app.add_handler(CommandHandler("fakeadmin", fakeadmin))
    app.add_handler(CommandHandler("spamjoin", spamjoin))
    app.add_handler(CommandHandler("rename", rename))
    app.add_handler(CommandHandler("blockall", blockall))
    app.add_handler(CommandHandler("voicespam", voicespam))
    app.add_handler(CommandHandler("gifspam", gifspam))
    app.add_handler(CommandHandler("filespam", filespam))
    app.add_handler(CommandHandler("tagabuse", tagabuse))
    app.add_handler(CommandHandler("loopdelete", loopdelete))
    app.add_handler(CommandHandler("doubletap", doubletap))
    app.add_handler(CommandHandler("tripletap", tripletap))
    app.add_handler(CommandHandler("storm", storm))
    app.add_handler(CommandHandler("phone", phone))
    app.add_handler(CommandHandler("location", location))
    app.add_handler(CommandHandler("ip", ip))
    app.add_handler(CommandHandler("crash", crash))
    app.add_handler(CommandHandler("terror", terror))
    app.add_handler(CommandHandler("addsub", addsub))
    app.add_handler(CommandHandler("delsub", delsub))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("promoteall", promoteall))
    app.add_handler(CommandHandler("demoteall", demoteall))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("lock", lock))
    app.add_handler(CommandHandler("unlock", unlock))
    app.add_handler(CommandHandler("autodel", autodel))
    app.add_handler(CommandHandler("clean", clean))
    app.add_handler(CommandHandler("addbots", addbots))
    app.add_handler(CommandHandler("promoteallbots", promoteallbots))
    app.add_handler(CommandHandler("removeallbots", removeallbots))
    app.add_handler(CommandHandler("leave", leave))
    app.add_handler(CommandHandler("showallbots", showallbots))
    app.add_handler(CommandHandler("tagall", tagall))
    app.add_handler(CommandHandler("alive", alive))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("speed", speed))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("masterkill", masterkill))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    return app

# ==================== MAIN ====================
async def main():
    global apps, bots
    os.makedirs("downloads", exist_ok=True)
    
    print("\n" + "="*60)
    print("🏴‍☠️ 𝐓ꪮ᭢ꪗ & 𝐊ꪖꪉỉꪹ ꪖʙʙꪊ ULTIMATE EDITION 🏴‍☠️")
    print("="*60)
    print(f"🚀 STARTING {len(TOKENS)} BOTS...")
    print(f"👑 MASTER ID: {MASTER_ID}")
    print("⚡ MODE: ULTRA FAST CONTINUOUS - NO RULES")
    
    for token in TOKENS:
        try:
            app = build_app(token)
            apps.append(app)
            bots.append(app.bot)
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print(f"✅ Bot started: {token[:15]}...")
        except Exception as e:
            print(f"❌ Failed: {str(e)[:50]}")
    
    print("\n" + "="*60)
    print("🔥 TONY ABBU ULTIMATE - LIVE! 🔥")
    print(f"🤖 Bots Online: {len(bots)}")
    print("⚡ NC: ULTRA FAST | SPAM: ULTRA FAST")
    print("📹 /setmenuvideo | 🖼️ /setmenupic")
    print("="*60 + "\n")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot Stopped!")
