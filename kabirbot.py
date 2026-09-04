#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import sys
import asyncio
import json
import os
import random
import time
import logging
import hashlib
import getpass
import html
from io import BytesIO
from typing import Dict, List, Set
from datetime import datetime, timedelta, timezone
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, PrefixHandler, CallbackQueryHandler
from telegram.error import RetryAfter, TimedOut, NetworkError, TelegramError
from telegram.constants import ParseMode
import requests
import yt_dlp
from gtts import gTTS


# ==================== CONFIGURATION ====================
BOT_TOKENS = [
    "8675374289:AAFU60_j3y6v2LpOBbYyxiNecyF0CMr2s8A",                                                                            
    "8767383748:AAHC1v9IVqohAIXgHQ9cDFS5iG-uT4tNjDU",                                                                         
    "8686695294:AAE1UTqFyPuEuUJ1fLtZCK_dU4kv6pMCdBc",
    "8260784450:AAFXcfOql66h8eapZpt8iMroxmXHigCA_Qk",
    "8881669451:AAEfzqe3nRhgLXmrVDjwrITMg-7jiLQFFLE",
    "8926486828:AAHkV06-W12U4anMb7umis04GCQIXez1bz0",
    "7722202626:AAHhJ62vF95oXbPwE8Z3OcotYX4zlUC3Vhs",
    "8617206776:AAHwXjNvMpWjw0Qu8SZstDj1hRGi5lqRMe4",
    "8999273910:AAHbsNCEiMOO6_B5-Nh4BnVXrt2Jvi5FUYo",
    "8670479769:AAGB4UUsyyhcPce1-qocLIyD4owJYRQn9n4",
    
   
]

OWNER_ID = [8678482053, 8996032103]
SUDO_FILE = "sudo.json"
SAFE_USERS_FILE = "safe_users.json"
GROUPS_FILE = "raid_groups.json"
STICKER_FILE = "stickers.json"
VOICE_CLONES_FILE = "voice_clones.json"
PFP_FOLDER = "pfp_images"
TEMPEST_API_KEY = "sk_e326b337242b09b451e8f18041fd0a7149cc895648e36538"

# ==================== RAID TEXTS ====================
RAID_TEXTS = [
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचो 𝐊ᴀʙɪʀ बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝐊ᴀʙɪʀ बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को 𝐊ᴀʙɪʀ बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝐊ᴀʙɪʀ /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝐊ᴀʙɪʀ बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती𝐊ᴀʙɪʀ🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝐊ᴀʙɪʀ बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ𝐊ᴀʙɪʀɴᴏ बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को 𝐊ᴀʙɪʀ बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝐊ᴀʙɪʀ /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝐊ᴀʙɪʀ बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती𝐊ᴀʙɪʀ🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝐊ᴀʙɪʀ बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝐊ᴀʙɪʀ बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को 𝐊ᴀʙɪʀ बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝐊ᴀʙɪʀ /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝐊ᴀʙɪʀ बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती𝐊ᴀʙɪʀ🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝐊ᴀʙɪʀ बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝐊ᴀʙɪʀ बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को 𝐊ᴀʙɪʀ बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝐊ᴀʙɪʀ /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝐊ᴀʙɪʀᴏ बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐"
]

PERSONAL_TEXTS = [
    "{name} तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
    "{name} 𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
    "{name} 𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही 🚂 ",
    "{name} 📷𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ 📷 ",
    "{name} 𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎ ",
    "{name} 🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ 🔭",
    "{name} तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
    "{name} 𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
    "{name} 𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही 🚂 ",
    "{name} 📷𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ 📷 ",
    "{name} 𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎ ",
    "{name} 🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ 🔭",
    "{name} तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
    "{name} 𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
    "{name} 𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही 🚂 ",
    "{name} 📷𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ 📷 ",
    "{name} 𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎ ",
    "{name} 🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ 🔭",
    "{name} तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
    "{name} 𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
    "{name} 𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही 🚂 ",
]

REACTIONS = ["👍","👎","❤️","🔥","🥰","😁","🤔","🤯","😱","🤬","😢","🎉","🤩","🤮","💩","🙏","👏","🤝","🤡","💀"]

COPYPASTAS = [
    "Navy Seal Copypasta: What the fuck did you just fucking say about me, you little bitch? I'll have you know I graduated top of my class...",
    "Lorem Ipsum: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua...",
    "Raid Message: ⚠️ THIS GROUP HAS BEEN RAIDED ⚠️ RESISTANCE IS FUTILE ⚠️",
]

TEXT_ARTS = [
    "\n╔══════════════╗\n║  RAIDED BY  ║\n║   ULTIMATE  ║\n╚══════════════╝\n",
    "\n▀▄▀▄ MEGA BOT ▄▀▄▀\n  TAKING OVER\n▄▀▄▀ GET REKT ▀▄▀▄\n",
]

# ==================== NC EMOJI SETS ====================
FIRE_EMOJIS = ["🔥","🌋","💥","⚡","☄️","🌪️","🏜️","🌶️","♨️","🧨","💣","🪓","⚔️","🗡️","🏹","💢","❤️‍🔥","🥵","😤","👹","👺","🔴","🟠","🫚","🌡️","🐉","🦁","🐯","🦊","🔶","🔸","🔺","🔻","💫","✨","🌠","🌅","🌄","🎆","🎇","🧱","🪨"]
WATER_EMOJIS = ["💧","🌊","🐋","🐬","🐟","🐠","🐡","🦈","🐙","🦑","🦐","🦞","🦀","🐚","🌸","💦","🫧","🪸","🌀","⛵","🏊","🤽","🚿","🛁","🌧️","☔","⛈️","🌦️","🏄","🧊","🫗","🌬️","❄️","🏔️","🗻","🏞️","🌫️","🌨️","⛄","🌈","🫙","🍶","🫖","🧋","🐸","🦢","🦩","🪷","🌺","🐊","🦭","🐳","🌐","🫐","💙","🩵","🔵","🟦"]
LAVA_EMOJIS = ["🌋","🔥","💥","🫨","♨️","🟠","🟡","🔴","☄️","⚡","💢","😤","🥵","🧱","🪨","💣","🧨","🌪️","🌡️","🦴","🐉","🔶","🔸","🔺","🔻","🌊","💨","🌫️","🏔️","⛰️","🗻","🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘","🪐","💫","✨","🌠","🎇","🎆","🔮","🫀","🧠","👁️","🦷","🦴","🐊","🦎"]
HELL_EMOJIS = ["👹","👺","😈","💀","☠️","🔱","🩸","🕷","🕸","🦇","🌑","🖤","🔮","⚰️","🪦","🗡️","⚔️","🔥","💥","😱","🤬","👻","🎃","🦴","💣","🧿","🌚","🕯️","🪄","🧙","🧛","🧟","🧌","🐺","🦉","🐦‍⬛","🪲","🐍","🦂","🕷","🪳","🦟","🐛","🌿","🍄","🌾","🫀","🧠","👁️","👄","🫦"]
SYMBOL_LIST = ["×","~","•","★","☆","▲","▼","◆","◇","■","□","●","○","✦","✧","⚡","✨","💫","🔱","⚜️","🏵","❋","✿","❀","✾","❃","❂","❁","❄","꧁","꧂","༺","༻","⫷","⫸","《","》","【","】","〖","〗","「","」","∞","Ω","Δ","Σ","Ψ","Φ","Λ","Θ","Ξ","Π","©","®","™","⁂","※","✰","✯","✮","✭","✬","✫","✪","✩","✸","✷","✶","✵","✴","✳","✲","⊛","⊕","⊗","⊘","⊙","⊚","⊜","⊝","◉","◎","◍","◌","○","◊","◈","『","』","〔","〕","｛","｝","〈","〉","⌘","⌥","⌫","⏎","⇧","⇪"]
FLAG_NC_EMOJIS = ["🇮🇳","🇺🇸","🇬🇧","🇨🇦","🇦🇺","🇩🇪","🇫🇷","🇯🇵","🇰🇷","🇨🇳","🇷🇺","🇧🇷","🇮🇹","🇪🇸","🇵🇰","🇧🇩","🇳🇵","🇱🇰","🇦🇪","🇸🇦","🇶🇦","🇹🇷","🇪🇬","🇿🇦","🇳🇬","🇰🇪","🇲🇽","🇦🇷","🇨🇱","🇨🇴","🇵🇪","🇻🇳","🇹🇭","🇲🇾","🇸🇬","🇵🇭","🇮🇩","🇮🇷","🇮🇶","🇸🇾","🇯🇴","🇰🇼","🇧🇭","🇴🇲","🇾🇪","🇱🇧","🇮🇱","🇵🇸","🇺🇦","🇵🇱","🇸🇪","🇳🇴","🇩🇰","🇫🇮","🇳🇱","🇧🇪","🇨🇭","🇦🇹","🇵🇹","🇬🇷","🇭🇺","🇨🇿","🇷🇴","🇧🇬","🇭🇷","🇸🇰","🇸🇮","🇷🇸","🇦🇱","🇲🇰","🇧🇦","🇲🇪","🇿🇼","🇬🇭","🇪🇹","🇹🇿","🇺🇬","🇲🇦","🇩🇿","🇹🇳","🇱🇾","🇸🇩","🇸🇴","🇨🇩","🏴‍☠️","🏳️","🏁","🚩","🎌","🏴","🏳️‍🌈","🏳️‍⚧️"]

# ==================== TEMPEST VOICE CHARACTERS ====================
VOICE_CHARACTERS = {
    1: {"name": "Urokodaki", "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Deep Indian voice - Urokodaki style", "style": "deep_masculine"},
    2: {"name": "Kanae", "voice_id": "EXAVITQu4vr4xnSDxMaL", "description": "Cute sweet voice - Kanae style", "style": "soft_feminine"},
    3: {"name": "Uppermoon", "voice_id": "AZnzlk1XvdvUeBnXmlld", "description": "Creepy dark deep voice - Uppermoon style", "style": "dark_creepy"},
    4: {"name": "Tanjiro", "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Heroic determined voice", "style": "heroic"},
    5: {"name": "Nezuko", "voice_id": "EXAVITQu4vr4xnSDxMaL", "description": "Cute mute sounds", "style": "cute_mute"},
    6: {"name": "Zenitsu", "voice_id": "AZnzlk1XvdvUeBnXmlld", "description": "Scared whiny voice", "style": "scared_whiny"},
    7: {"name": "Inosuke", "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Wild aggressive voice", "style": "wild_aggressive"},
    8: {"name": "Muzan", "voice_id": "AZnzlk1XvdvUeBnXmlld", "description": "Evil mastermind voice", "style": "evil_calm"},
    9: {"name": "Shinobu", "voice_id": "EXAVITQu4vr4xnSDxMaL", "description": "Gentle but deadly voice", "style": "gentle_deadly"},
    10: {"name": "Giyu", "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Silent serious voice", "style": "silent_serious"},
}

# ==================== GLOBAL STATE ====================
class MegaState:
    def __init__(self):
        self.sudo_users: Set[int] = {OWNER_ID}
        self.safe_users: Set[int] = set()
        self.safe_usernames: Dict[str, int] = {}
        self.raid_groups: Set[int] = set()

        self.swipe_active: Dict[str, Dict[int, str]] = {}
        self.spam_active: Dict[str, Dict[int, str]] = {}
        self.auto_delete_active: Dict[str, Dict[int, bool]] = {}
        self.nc_active: Dict[str, Dict[int, bool]] = {}
        self.conemo_active: Dict[str, Dict[int, str]] = {}
        self.pfp_active: Dict[str, bool] = {}
        self.pfp_images: Dict[str, List[str]] = {}
        self.grouppfp_active: Dict[str, Dict[int, bool]] = {}
        self.grouppfp_images: Dict[str, List[str]] = {}

        self.gcnc_active: Dict[int, bool] = {}
        self.ncemo_active: Dict[int, bool] = {}
        self.nctime_active: Dict[int, bool] = {}
        self.ncbaap_active: Dict[int, bool] = {}
        self.betanc_active: Dict[int, bool] = {}
        self.raidnc_active: Dict[int, bool] = {}
        self.ultragc_active: Dict[int, bool] = {}
        self.godmode_active: Dict[int, bool] = {}

        self.slide_targets: Set[int] = set()
        self.slidespam_targets: Set[int] = set()
        self.delete_targets: Set[int] = set()
        self.reply_bomb_targets: Dict[int, int] = {}
        self.mention_spam_targets: Dict[int, List[str]] = {}
        self.emoji_flood_active: Dict[int, str] = {}
        self.media_spam: Dict[str, any] = {}
        self.reaction_spam_active: Set[int] = set()
        self.delete_spam_active: Set[int] = set()
        self.active_reactions: Dict[int, str] = {}

        self.stickers: Dict[int, List[str]] = {}
        self.sticker_spam_active: Dict[int, bool] = {}

        self.chat_photos: Dict[int, List[bytes]] = {}
        self.photo_loop_active: Dict[int, bool] = {}

        self.voice_clones: Dict[str, Dict] = {}
        self.bot_delays: Dict[int, float] = {}

        self.delete_delay = 0.05
        self.spam_delay = 0.3
        self.nc_speed = 0.01
        self.pfp_speed = 0.5
        self.kennc_speed = 0.01

        self.start_time = time.time()
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists(SUDO_FILE):
                with open(SUDO_FILE, "r") as f:
                    self.sudo_users = set(json.load(f))
                    self.sudo_users.add(OWNER_ID)
        except:
            self.sudo_users = {OWNER_ID}
        try:
            if os.path.exists(SAFE_USERS_FILE):
                with open(SAFE_USERS_FILE, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.safe_users = set(data.get("user_ids", []))
                        self.safe_usernames = data.get("usernames", {})
                    else:
                        self.safe_users = set(data)
        except:
            self.safe_users = set()
            self.safe_usernames = {}
        try:
            if os.path.exists(GROUPS_FILE):
                with open(GROUPS_FILE, "r") as f:
                    self.raid_groups = set(json.load(f))
        except:
            self.raid_groups = set()
        try:
            if os.path.exists(STICKER_FILE):
                with open(STICKER_FILE, "r") as f:
                    data = json.load(f)
                    self.stickers = {int(k): v for k, v in data.items()}
        except:
            self.stickers = {}
        try:
            if os.path.exists(VOICE_CLONES_FILE):
                with open(VOICE_CLONES_FILE, "r") as f:
                    self.voice_clones = json.load(f)
        except:
            self.voice_clones = {}
        if not os.path.exists(PFP_FOLDER):
            os.makedirs(PFP_FOLDER)

    def save_sudo(self):
        with open(SUDO_FILE, "w") as f:
            json.dump(list(self.sudo_users), f)

    def save_safe_users(self):
        with open(SAFE_USERS_FILE, "w") as f:
            json.dump({"user_ids": list(self.safe_users), "usernames": self.safe_usernames}, f)

    def save_groups(self):
        with open(GROUPS_FILE, "w") as f:
            json.dump(list(self.raid_groups), f)

    def save_stickers(self):
        with open(STICKER_FILE, "w") as f:
            json.dump({str(k): v for k, v in self.stickers.items()}, f)

    def save_voice_clones(self):
        with open(VOICE_CLONES_FILE, "w") as f:
            json.dump(self.voice_clones, f)

    def init_bot_state(self, token: str):
        for attr in ["swipe_active", "spam_active", "auto_delete_active", "nc_active", "conemo_active", "grouppfp_active"]:
            d = getattr(self, attr)
            if token not in d:
                d[token] = {}

    def is_sudo(self, user_id: int) -> bool:
        return user_id in self.sudo_users

    def is_safe(self, user_id: int, username: str = None) -> bool:
        return user_id in self.safe_users or (username and username in self.safe_usernames)


state = MegaState()
apps = []
bots = []

# ==================== FLOOD CONTROL ====================
flood_wait_status: Dict[str, Dict] = {}
auto_flood_control: bool = True
flood_notification_enabled: bool = False  # toggled by /floodstatuson and /floodstatusoff

async def smart_send(bot, chat_id: int, text: str, **kwargs) -> bool:
    token = str(bot.token)
    for attempt in range(5):
        try:
            await bot.send_message(chat_id, text, **kwargs)
            flood_wait_status.pop(token, None)
            return True
        except RetryAfter as e:
            wait_time = e.retry_after
            flood_wait_status[token] = {"chat_id": chat_id, "retry_after": wait_time, "time": time.time()}
            if flood_notification_enabled:
                for other_bot in bots:
                    if str(other_bot.token) != token:
                        try:
                            await other_bot.send_message(chat_id, f"⚠️ **FLOOD WAIT**\n🤖 Bot `{token[:10]}...` waiting `{wait_time}s`\n🔄 Auto-resuming...", parse_mode=ParseMode.MARKDOWN)
                            break
                        except: continue
            if auto_flood_control:
                await asyncio.sleep(wait_time + 0.5)
            else:
                return False
        except (TimedOut, NetworkError):
            await asyncio.sleep(3)
        except TelegramError:
            await asyncio.sleep(2)
            return False
    return False

async def smart_set_title(bot, chat_id: int, title: str) -> bool:
    token = str(bot.token)
    for attempt in range(5):
        try:
            await bot.set_chat_title(chat_id, title)
            return True
        except RetryAfter as e:
            wait_time = e.retry_after
            flood_wait_status[token] = {"chat_id": chat_id, "retry_after": wait_time, "time": time.time()}
            if flood_notification_enabled:
                for other_bot in bots:
                    if str(other_bot.token) != token:
                        try:
                            await other_bot.send_message(chat_id, f"⚠️ **NC FLOOD WAIT**\n🤖 Bot `{token[:10]}...` waiting `{wait_time}s`\n🔄 Auto-resuming...", parse_mode=ParseMode.MARKDOWN)
                            break
                        except: continue
            if auto_flood_control:
                await asyncio.sleep(wait_time + 0.5)
            else:
                return False
        except Exception:
            await asyncio.sleep(0.5)
            return False
    return False

# ==================== FREEZE ====================
freeze_active: Dict[int, str] = {}
freeze_banned_bots: Dict[int, set] = {}

# ==================== DECORATORS ====================
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not state.is_sudo(update.effective_user.id):
            try:
                await update.message.reply_text("❌ ʏᴇʜ ʙᴀs ᴛᴇʀᴀ ʙᴀᴀᴘ ʟᴇᴘɪɴᴏ ᴋʀ sᴋᴛᴀ ʜ ⋆𓂃 ོ☼𓂃 🖕")
            except: pass
            return
        return await func(update, context)
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != OWNER_ID:
            try:
                await update.message.reply_text("❌ ʏᴇʜ ʙᴀs ᴛᴇʀᴀ ʙᴀᴀᴘ ʟᴇᴘɪɴᴏ ᴋʀ sᴋᴛᴀ ʜ ⋆𓂃 ོ☼𓂃 🖕")
            except: pass
            return
        return await func(update, context)
    return wrapper

# ==================== BASIC COMMANDS ====================
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚔️ **⏤͟͞ 𝐊ᴀʙɪʀᴏ 愛 𝗩𝟭𝟲**\n\n"
        "✨ **Welcome to  𝐊ᴀʙɪʀ Ultimate Bot!**\n"
        "📖 Type **-help** to open the command menu.\n"
        "🚀 Ultra Fast • Stable • Powerful",
        parse_mode=ParseMode.MARKDOWN
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        "⚡ **𝐊ᴀʙɪʀ 愛 𝐄𝐧𝐠𝐢𝐧𝐞 𝐁𝐨𝐨𝐭𝐢𝐧𝐠...**",
        parse_mode=ParseMode.MARKDOWN
    )

    frames = [
        "⚡ **𝐊ᴀʙɪʀ 愛 𝐄𝐧𝐠𝐢𝐧𝐞 𝐁𝐨𝐨𝐭𝐢𝐧𝐠...**\n\n`▰▱▱▱▱▱▱▱▱▱ 25%`\n\n🔄 Initializing...",
        "⚡ **𝐊ᴀʙɪʀ 愛 𝐄𝐧𝐠𝐢𝐧𝐞 𝐁𝐨𝐨𝐭𝐢𝐧𝐠...**\n\n`▰▰▰▰▱▱▱▱▱▱ 50%`\n\n⚙️ Loading Modules...",
        "⚡ **𝐊ᴀʙɪʀ 愛 𝐄𝐧𝐠𝐢𝐧𝐞 𝐁𝐨𝐨𝐭𝐢𝐧𝐠...**\n\n`▰▰▰▰▰▰▰▱▱▱ 75%`\n\n🚀 Syncing System...",
        "✅ **𝐊ᴀʙɪʀ 愛 𝐄𝐧𝐠𝐢𝐧𝐞 𝐑𝐞𝐚𝐝𝐲!**\n\n`▰▰▰▰▰▰▰▰▰▰ 100%`\n\n✨ Opening Menu..."
    ]

    for frame in frames:
        await msg.edit_text(frame, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(0.25)

    help_text = """╔════════════════════════════╗
         ⚔️ 𝐊ᴀʙɪʀ 𝐓𝐇𝐄 𝐋𝐀𝐒𝐓 𝐄𝐌𝐏𝐄𝐑𝐎𝐑   ⚔️
      『 𝐁ᴇʏᴏɴᴅ • 𝐋ɪᴍɪᴛꜱ • 𝐄ᴅɪᴛɪᴏɴ 』
╚════════════════════════════╝

╭━━━〔 💣 𝐒ᴘᴀᴍ 𝐌ᴏᴅᴜʟᴇ 〕━━━╮
┃ ✦ 𝐒ᴘᴀᴍ <ɴ> <ᴛᴇxᴛ>
┃ ✦ 𝐒ᴡɪᴘᴇ <ɴ> <ᴛᴇxᴛ>
┃ ✦ 𝐒ᴛᴏᴘ𝐒ᴘᴀᴍ
╰━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━〔 🔥 𝐍ᴀᴍᴇ 𝐂ʜᴀɴɢᴇʀꜱ 〕━━━╮
┃ ✦ 𝐅ɪʀᴇ𝐍ᴄ
┃ ✦ 𝐖ᴀᴛᴇʀ𝐍ᴄ
┃ ✦ 𝐋ᴀᴠᴀ𝐍ᴄ
┃ ✦ 𝐇ᴇʟʟ𝐍ᴄ
┃ ✦ 𝐒ʏᴍʙᴏʟ𝐍ᴄ
┃ ✦ 𝐅ʟᴀɢ𝐍ᴄ
┃ ✦ 𝐒ᴛᴏᴘ𝐍ᴄ
╰━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━〔 🎯 𝐓ᴀʀɢᴇᴛ & 𝐄ᴍᴏᴊɪ 〕━━━╮
┃ ✦ 𝐓ᴀʀɢᴇᴛ𝐒ʟɪᴅᴇ
┃ ✦ 𝐒ʟɪᴅᴇ𝐒ᴘᴀᴍ
┃ ✦ 𝐓ᴀʀɢᴇᴛ𝐃ᴇʟᴇᴛᴇ
┃ ✦ 𝐄ᴍᴏᴊɪ𝐅ʟᴏᴏᴅ
┃ ✦ 𝐄ᴍᴏᴊɪ𝐒ᴘᴀᴍ
┃ ✦ 𝐑ᴀɴᴅᴏᴍ𝐄ᴍᴏᴊɪ
┃ ✦ 𝐂ʟᴇᴀʀ𝐓ᴀʀɢᴇᴛꜱ
╰━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━〔 🖼️ 𝐏ꜰᴘ & 𝐌ᴇᴅɪᴀ 〕━━━╮
┃ ✦ 𝐒ᴀᴠᴇ𝐏ꜰᴘ
┃ ✦ 𝐒ᴛᴀʀᴛ𝐏ꜰᴘ
┃ ✦ 𝐒ᴛᴏᴘ𝐏ꜰᴘ
┃ ✦ 𝐒ᴀᴠᴇ𝐆ʀᴏᴜᴘ𝐏ꜰᴘ
┃ ✦ 𝐒ᴀᴠᴇ𝐏ʜᴏᴛᴏ
┃ ✦ 𝐒ᴛᴀʀᴛ𝐏ʜᴏᴛᴏ
┃ ✦ 𝐒ᴛᴏᴘ𝐏ʜᴏᴛᴏ
┃ ✦ 𝐂ʟᴇᴀʀ𝐏ʜᴏᴛᴏꜱ
╰━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━〔 🎭 𝐒ᴛɪᴄᴋᴇʀ & 𝐕ᴏɪᴄᴇ 〕━━━╮
┃ ✦ 𝐍ᴇᴡ𝐒ᴛɪᴄᴋᴇʀ
┃ ✦ 𝐌ᴜʟᴛɪ𝐒ᴛɪᴄᴋᴇʀ
┃ ✦ 𝐀ɴɪᴍᴇ𝐕ɴ
┃ ✦ 𝐓ᴇᴍᴘᴇꜱᴛ
┃ ✦ 𝐂ʟᴏɴᴇ𝐕ɴ
┃ ✦ 𝐕ᴏɪᴄᴇꜱ
╰━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━〔 🛡️ 𝐆ʀᴏᴜᴘ & 𝐑ᴀɪᴅ 〕━━━╮
┃ ✦ 𝐀ᴅᴅ𝐆ʀᴏᴜᴘ
┃ ✦ 𝐑ᴇᴍᴏᴠᴇ𝐆ʀᴏᴜᴘ
┃ ✦ 𝐑ᴀɪᴅ𝐀ʟʟ
┃ ✦ 𝐅ʀᴇᴇᴢᴇ
┃ ✦ 𝐔ɴ𝐅ʀᴇᴇᴢᴇ
┃ ✦ 𝐊ɪʟʟ𝐀ʟʟ
┃ ✦ 𝐊ɪʟʟ𝐀ʟʟ𝐎ꜰꜰ
┃ ✦ 𝐒ᴛᴏᴘ𝐀ʟʟ
╰━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━〔 👑 𝐀ᴅᴍɪɴ & 𝐈ɴꜰᴏ 〕━━━╮
┃ ✦ 𝐁ᴇᴛᴀ
┃ ✦ 𝐃ᴇʟ𝐒ᴜᴅᴏ
┃ ✦ 𝐒ᴀꜰᴇ
┃ ✦ 𝐔ɴ𝐒ᴀꜰᴇ
┃ ✦ 𝐌ʏ𝐈ᴅ
┃ ✦ 𝐏ɪɴɢ
┃ ✦ 𝐒ᴛᴀᴛᴜꜱ
┃ ✦ 𝐁ᴏᴛ𝐈ɴꜰᴏ
┃ ✦ 𝐔ᴘᴛɪᴍᴇ
┃ ✦ 𝐃ᴇʟᴀʏ
┃ ✦ 𝐍ᴄ𝐃ᴇʟᴀʏ
╰━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━〔 ✨ 𝐄xᴛʀᴀꜱ 〕━━━╮
┃ ✦ 𝐖ᴏʀᴅ𝐁ᴏᴍʙ
┃ ✦ 𝐂ᴏᴜɴᴛᴅᴏᴡɴ
┃ ✦ 𝐌ᴇɴᴛɪᴏɴ𝐒ᴘᴀᴍ
┃ ✦ 𝐅ᴏʀᴡᴀʀᴅ𝐁ᴏᴍʙ
┃ ✦ 𝐏ᴇʀꜱᴏɴᴀʟ𝐑ᴀɪᴅ
┃ ✦ 𝐄ᴍᴏᴊɪ𝐑ᴀɪɴ
┃ ✦ 𝐅ʟᴏᴏᴅ𝐒ᴛᴀᴛᴜꜱ𝐎ɴ
┃ ✦ 𝐅ʟᴏᴏᴅ𝐒ᴛᴀᴛᴜꜱ𝐎ꜰꜰ
╰━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━〔 🎮 𝐆𝐚𝐦𝐞𝐎𝐯𝐞𝐫 〕━━━╮
┃ ✦ 𝐒𝐞𝐭𝐆𝐚𝐦𝐞𝐎𝐯𝐞𝐫
┃ ✦ 𝐆𝐚𝐦𝐞𝐎𝐯𝐞𝐫
┃ ✦ 𝐆𝐚𝐦𝐞𝐎𝐯𝐞𝐫𝐒𝐭𝐚𝐭𝐮𝐬
╰━━━━━━━━━━━━━━━━━━━━━━╯
╔════════════════════════════════╗
   『 ⚔️ 𝐊ᴀʙɪʀ 愛 𝐔ʟᴛɪᴍᴀᴛᴇ  ⚔️ 』
╚════════════════════════════════╝"""

    await msg.edit_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    await msg.edit_text(f"🏓 Pong! `{round((time.time() - start) * 1000)}ms`", parse_mode=ParseMode.MARKDOWN)

async def uptime_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = time.time() - state.start_time
    h, rem = divmod(int(uptime), 3600)
    m, s = divmod(rem, 60)
    await update.message.reply_text(f"⏰ **Uptime:** {h}h {m}m {s}s\n🤖 **Active Bots:** {len(bots)}", parse_mode=ParseMode.MARKDOWN)

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 **BOT STATUS**\n\n🤖 Bots: {len(bots)}\n👑 Sudo: {len(state.sudo_users)}\n🛡️ Safe: {len(state.safe_users)}\n📋 Groups: {len(state.raid_groups)}\n\n⚡ Speeds:\n• Delete: {state.delete_delay}s\n• Spam: {state.spam_delay}s\n• NC: {state.nc_speed}s\n• PFP: {state.pfp_speed}s\n\n🎯 Active Targets:\n• Slide: {len(state.slide_targets)}\n• Slidespam: {len(state.slidespam_targets)}\n• Delete: {len(state.delete_targets)}",
        parse_mode=ParseMode.MARKDOWN
    )

async def active_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    features = []
    if state.nctime_active.get(chat_id): features.append("✅ NC Time")
    if state.ncbaap_active.get(chat_id): features.append("✅ NCBAAP")
    if chat_id in state.emoji_flood_active: features.append(f"✅ Emoji Flood ({state.emoji_flood_active[chat_id]})")
    if chat_id in state.active_reactions: features.append(f"✅ Reactions ({state.active_reactions[chat_id]})")
    if state.photo_loop_active.get(chat_id): features.append("✅ Photo Loop")
    if state.sticker_spam_active.get(chat_id): features.append("✅ Sticker Spam")
    if state.ultragc_active.get(chat_id): features.append("✅ Ultra GC")
    if state.godmode_active.get(chat_id): features.append("✅ God Mode")
    msg = "🎯 **Active Features:**\n\n" + "\n".join(features) if features else "❌ No active features in this chat"
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def myid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, chat = update.effective_user, update.effective_chat
    await update.message.reply_text(
        f"🆔 **Your Info:**\n• User ID: `{user.id}`\n• Username: @{user.username or 'None'}\n• First Name: {user.first_name}\n• Chat ID: `{chat.id}`\n• Chat Type: {chat.type}",
        parse_mode=ParseMode.MARKDOWN
    )

async def ready_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ **Bot Ready!**\n\n🤖 Active Bots: {len(bots)}\n⚡ All systems operational", parse_mode=ParseMode.MARKDOWN)

async def botinfo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"⚔️ **• ⏤͟͞ 𝐊ᴀʙɪʀ愛𓆪BOT V16 — MEGA ULTIMATE EDITION**\n\n👑 Creator:  THE GREAT WARRIOR\n🤖 Active Bots: {len(bots)}\n⚡ Total Commands: 70+\n━━━━━━━━━━━━━━━━━━━━━",
        parse_mode=ParseMode.MARKDOWN
    )

# ==================== SUDO MANAGEMENT ====================
@only_owner
async def beta_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try: user_id = int(context.args[0])
        except: return await update.message.reply_text("❌ Invalid user ID")
    else:
        return await update.message.reply_text("❌ Reply to a user or provide ID")
    state.sudo_users.add(user_id)
    state.save_sudo()
    await update.message.reply_text(f"✅ User `{user_id}` added to sudo!", parse_mode=ParseMode.MARKDOWN)

@only_owner
async def delsudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try: user_id = int(context.args[0])
        except: return await update.message.reply_text("❌ Invalid user ID")
    else:
        return await update.message.reply_text("❌ Reply to a user or provide ID")
    if user_id == OWNER_ID:
        return await update.message.reply_text("❌ Cannot remove owner!")
    state.sudo_users.discard(user_id)
    state.save_sudo()
    await update.message.reply_text(f"✅ User `{user_id}` removed from sudo!", parse_mode=ParseMode.MARKDOWN)

@only_sudo
async def listsudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sudo_list = "\n".join([f"• `{uid}`" for uid in state.sudo_users])
    await update.message.reply_text(f"👑 **Sudo Users:**\n\n{sudo_list}", parse_mode=ParseMode.MARKDOWN)

# ==================== SAFE USERS ====================
@only_sudo
async def safe_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        user_id, username = user.id, user.username
    elif context.args:
        arg = context.args[0]
        if arg.startswith("@"):
            username, user_id = arg[1:], None
        else:
            try: user_id, username = int(arg), None
            except: return await update.message.reply_text("❌ Invalid input")
    else:
        return await update.message.reply_text("❌ Reply to user or provide ID/username")
    if user_id: state.safe_users.add(user_id)
    if username: state.safe_usernames[username] = user_id or 0
    state.save_safe_users()
    await update.message.reply_text("✅ User added to safe list!")

@only_sudo
async def unsafe_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        user_id, username = user.id, user.username
    elif context.args:
        arg = context.args[0]
        if arg.startswith("@"):
            username, user_id = arg[1:], None
        else:
            try: user_id, username = int(arg), None
            except: return await update.message.reply_text("❌ Invalid input")
    else:
        return await update.message.reply_text("❌ Reply to user or provide ID/username")
    if user_id: state.safe_users.discard(user_id)
    if username: state.safe_usernames.pop(username, None)
    state.save_safe_users()
    await update.message.reply_text("✅ User removed from safe list!")

# ==================== SPAM ====================
@only_sudo
async def spam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("Usage: -spam <count> <text>")
    try: count, text = int(context.args[0]), " ".join(context.args[1:])
    except: return await update.message.reply_text("❌ Invalid count")
    count = min(count, 500)
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"🚀 Starting spam: {count} messages")
    for bot in bots:
        asyncio.create_task(spam_worker(bot, chat_id, text, count))

async def spam_worker(bot, chat_id, text, count):
    for _ in range(count):
        try:
            await smart_send(bot, chat_id, text)
            await asyncio.sleep(state.spam_delay)
        except Exception as e:
            logging.error(f"Spam error: {e}")
            await asyncio.sleep(2)

@only_sudo
async def unspam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Spam stopped!")

@only_sudo
async def swipe_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("Usage: -swipe <count> <text>")
    try: count, text = int(context.args[0]), " ".join(context.args[1:])
    except: return await update.message.reply_text("❌ Invalid count")
    count = min(count, 500)
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"💨 Starting swipe: {count} messages")
    for bot in bots:
        asyncio.create_task(swipe_worker(bot, chat_id, text, count))

async def swipe_worker(bot, chat_id, text, count):
    for _ in range(count):
        try:
            await bot.send_message(chat_id, text)
            await asyncio.sleep(0.05)
        except:
            await asyncio.sleep(1)

@only_sudo
async def stopswipe_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Swipe stopped!")

@only_sudo
async def raidspam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: -raidspam <count>")
    try: count = min(int(context.args[0]), 500)
    except: return await update.message.reply_text("❌ Invalid count")
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"💥 Starting raid spam: {count}")
    for bot in bots:
        asyncio.create_task(raid_spam_worker(bot, chat_id, count))

async def raid_spam_worker(bot, chat_id, count):
    for _ in range(count):
        try:
            await smart_send(bot, chat_id, random.choice(RAID_TEXTS))
            await asyncio.sleep(state.spam_delay)
        except:
            await asyncio.sleep(2)

# ==================== NAME CHANGERS ====================
def _make_nc(emoji_list, label):
    @only_sudo
    async def start_nc(update, context):
        if not context.args:
            return await update.message.reply_text(f"Usage: -{label} <text>")
        name = " ".join(context.args)
        chat_id = update.effective_chat.id
        state.gcnc_active[chat_id] = True
        await update.message.reply_text(f"✅ {label} started!\n📝 Text: {name}")
        for bot in bots:
            asyncio.create_task(_nc_worker(bot, chat_id, name, emoji_list))
    return start_nc

async def _nc_worker(bot, chat_id, base_name, emoji_list):
    while state.gcnc_active.get(chat_id):
        try:
            e1, e2 = random.choice(emoji_list), random.choice(emoji_list)
            await smart_set_title(bot, chat_id, f"{e1} {base_name} {e2}")
            await asyncio.sleep(state.nc_speed)
        except Exception as e:
            logging.error(f"NC error: {e}")
            await asyncio.sleep(0.5)

firenc_cmd = _make_nc(FIRE_EMOJIS, "firenc")
waternc_cmd = _make_nc(WATER_EMOJIS, "waternc")
lavanc_cmd = _make_nc(LAVA_EMOJIS, "lavanc")
hellnc_cmd = _make_nc(HELL_EMOJIS, "hellnc")
flagnc_cmd = _make_nc(FLAG_NC_EMOJIS, "flagnc")

@only_sudo
async def symbolnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: -symbolnc <text>")
    name = " ".join(context.args)
    chat_id = update.effective_chat.id
    state.gcnc_active[chat_id] = True
    await update.message.reply_text(f"✦ Symbol NC started!\n📝 Text: {name}")
    for bot in bots:
        asyncio.create_task(_symbolnc_worker(bot, chat_id, name))

async def _symbolnc_worker(bot, chat_id, base_name):
    while state.gcnc_active.get(chat_id):
        try:
            s = [random.choice(SYMBOL_LIST) for _ in range(4)]
            await smart_set_title(bot, chat_id, f"{s[0]}{s[1]} {base_name} {s[2]}{s[3]}")
            await asyncio.sleep(state.nc_speed)
        except Exception as e:
            logging.error(f"SymbolNC error: {e}")
            await asyncio.sleep(0.5)

@only_sudo
async def stopnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.gcnc_active[update.effective_chat.id] = False
    await update.message.reply_text("⏹ NC stopped!")
    
# ==================== ADMIN PERMISSIONS ====================
ADMIN_PERMISSIONS = {
    "can_manage_chat": True,
    "can_change_info": True,
    "can_delete_messages": True,
    "can_invite_users": True,
    "can_restrict_members": True,
    "can_pin_messages": True,
    "can_promote_members": True,
    "can_manage_topics": True,
    "is_anonymous": False,
}

# ==================== MASTER BOT RESPONSE ====================
MASTER_BOT_RESPONSES = {
    "~kabir1": "🔱𝐊ᴀʙɪʀɴ 𝐕𝟏 - 𝐒𝐔𝐃𝐎 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃",
    "~kabir2": "⚡ 𝐊ᴀʙɪʀ 𝐕𝟐 - 𝐒𝐔𝐃𝐎 𝐆𝐑𝐀𝐍𝐓𝐄𝐃",
    "~kabir3": "💀𝐊ᴀʙɪʀ 𝐕𝟑 - 𝐒𝐔𝐃𝐎 𝐌𝐎𝐃𝐄",
    "~kabir4": "🔥𝐊ᴀʙɪʀ 𝐕𝟒 - 𝐆𝐎𝐃 𝐌𝐎𝐃𝐄 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃",
    "~kabir5": "⚡ 𝐊ᴀʙɪʀ 𝐕𝟓 - 𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐏𝐎𝐖𝐄𝐑",
}

MASTER_BOT_TRIGGERS = list(MASTER_BOT_RESPONSES.keys())    

# ==================== TARGET COMMANDS ====================
@only_sudo
async def targetslide_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message")
    user_id = update.message.reply_to_message.from_user.id
    state.slide_targets.add(user_id)
    await update.message.reply_text(f"✅ Slide target added: `{user_id}`", parse_mode=ParseMode.MARKDOWN)

@only_sudo
async def stopslide_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.slide_targets.clear()
    await update.message.reply_text("✅ Slide targets cleared!")

@only_sudo
async def slidespam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message")
    user_id = update.message.reply_to_message.from_user.id
    state.slidespam_targets.add(user_id)
    await update.message.reply_text(f"✅ Slidespam target added: `{user_id}`", parse_mode=ParseMode.MARKDOWN)

@only_sudo
async def stopslidespam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.slidespam_targets.clear()
    await update.message.reply_text("✅ Slidespam targets cleared!")

@only_sudo
async def targetdelete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message")
    user_id = update.message.reply_to_message.from_user.id
    state.delete_targets.add(user_id)
    await update.message.reply_text(f"✅ Delete target added: `{user_id}`", parse_mode=ParseMode.MARKDOWN)

@only_sudo
async def stoptargetdelete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.delete_targets.clear()
    await update.message.reply_text("✅ Delete targets cleared!")

@only_sudo
async def cleartargets_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.slide_targets.clear()
    state.slidespam_targets.clear()
    state.delete_targets.clear()
    await update.message.reply_text("✅ All targets cleared!")

# ==================== EMOJI & REACTIONS ====================
@only_sudo
async def emojiflood_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: -emojiflood <emoji>")
    emoji = context.args[0]
    chat_id = update.effective_chat.id
    state.emoji_flood_active[chat_id] = emoji
    await update.message.reply_text(f"✅ Emoji flood started: {emoji}")
    for bot in bots:
        asyncio.create_task(emoji_flood_worker(bot, chat_id, emoji))

async def emoji_flood_worker(bot, chat_id, emoji):
    while state.emoji_flood_active.get(chat_id) == emoji:
        try:
            await bot.send_message(chat_id, emoji * 50)
            await asyncio.sleep(0.5)
        except:
            await asyncio.sleep(2)

@only_sudo
async def stopemojiflood_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.emoji_flood_active.pop(update.effective_chat.id, None)
    await update.message.reply_text("✅ Emoji flood stopped!")

@only_sudo
async def randomemoji_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    emoji = random.choice(REACTIONS)
    for bot in bots:
        try: await bot.send_message(chat_id, emoji * 50)
        except: pass

@only_sudo
async def emojispam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: -emojispam <emoji>")
    emoji = context.args[0]
    chat_id = update.effective_chat.id
    state.active_reactions[chat_id] = emoji
    await update.message.reply_text(f"✅ Emoji reaction spam started: {emoji}")

@only_sudo
async def stopemojispam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.active_reactions.pop(update.effective_chat.id, None)
    await update.message.reply_text("✅ Emoji reaction spam stopped!")

# ==================== TEXT FEATURES ====================
@only_sudo
async def copypasta_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(COPYPASTAS))

@only_sudo
async def textart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"```\n{random.choice(TEXT_ARTS)}\n```", parse_mode=ParseMode.MARKDOWN)

# ==================== AUTO DELETE ====================
@only_sudo
async def killall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    for token in state.auto_delete_active:
        state.auto_delete_active[token][chat_id] = True
    await update.message.reply_text("✅ Auto-delete enabled!")

@only_sudo
async def killalloff_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    for token in state.auto_delete_active:
        state.auto_delete_active[token].pop(chat_id, None)
    await update.message.reply_text("✅ Auto-delete disabled!")

# ==================== PFP FEATURES ====================
@only_sudo
async def savepfp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("❌ Reply to a photo!")
    photo = update.message.reply_to_message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    token = str(context.bot.token)
    if token not in state.pfp_images:
        state.pfp_images[token] = []
    file_path = f"{PFP_FOLDER}/pfp_{len(state.pfp_images[token])}.jpg"
    await file.download_to_drive(file_path)
    state.pfp_images[token].append(file_path)
    await update.message.reply_text(f"✅ PFP saved! Total: {len(state.pfp_images[token])}")

@only_sudo
async def startpfp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = str(context.bot.token)
    if not state.pfp_images.get(token):
        return await update.message.reply_text("❌ No PFPs saved! Use -savepfp first")
    state.pfp_active[token] = True
    await update.message.reply_text("✅ PFP loop started!")
    asyncio.create_task(pfp_worker(context.bot, token))

async def pfp_worker(bot, token):
    while state.pfp_active.get(token):
        try:
            photo_path = random.choice(state.pfp_images[token])
            with open(photo_path, "rb") as f:
                await bot.set_chat_photo(OWNER_ID, f)
            await asyncio.sleep(state.pfp_speed)
        except:
            await asyncio.sleep(5)

@only_sudo
async def stoppfp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.pfp_active[str(context.bot.token)] = False
    await update.message.reply_text("✅ PFP loop stopped!")

@only_sudo
async def savegrouppfp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("❌ Reply to a photo!")
    photo = update.message.reply_to_message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    token = str(context.bot.token)
    if token not in state.grouppfp_images:
        state.grouppfp_images[token] = []
    file_path = f"{PFP_FOLDER}/grouppfp_{len(state.grouppfp_images[token])}.jpg"
    await file.download_to_drive(file_path)
    state.grouppfp_images[token].append(file_path)
    await update.message.reply_text(f"✅ Group PFP saved! Total: {len(state.grouppfp_images[token])}")

@only_sudo
async def startgrouppfp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = str(context.bot.token)
    chat_id = update.effective_chat.id
    if not state.grouppfp_images.get(token):
        return await update.message.reply_text("❌ No group PFPs saved! Use -savegrouppfp first")
    if token not in state.grouppfp_active:
        state.grouppfp_active[token] = {}
    state.grouppfp_active[token][chat_id] = True
    await update.message.reply_text("✅ Group PFP loop started!")
    asyncio.create_task(grouppfp_worker(context.bot, token, chat_id))

async def grouppfp_worker(bot, token, chat_id):
    while state.grouppfp_active.get(token, {}).get(chat_id):
        try:
            photo_path = random.choice(state.grouppfp_images[token])
            with open(photo_path, "rb") as f:
                await bot.set_chat_photo(chat_id, f)
            await asyncio.sleep(state.pfp_speed)
        except:
            await asyncio.sleep(5)

@only_sudo
async def stopgrouppfp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = str(context.bot.token)
    chat_id = update.effective_chat.id
    if token in state.grouppfp_active:
        state.grouppfp_active[token].pop(chat_id, None)
    await update.message.reply_text("✅ Group PFP loop stopped!")

# ==================== PHOTO LOOP ====================
@only_sudo
async def savephoto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("❌ Reply to a photo!")
    chat_id = update.effective_chat.id
    photo = update.message.reply_to_message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    photo_bytes = await file.download_as_bytearray()
    if chat_id not in state.chat_photos:
        state.chat_photos[chat_id] = []
    state.chat_photos[chat_id].append(bytes(photo_bytes))
    await update.message.reply_text(f"✅ Photo saved! Total: {len(state.chat_photos[chat_id])}")

@only_sudo
async def startphoto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not state.chat_photos.get(chat_id):
        return await update.message.reply_text("❌ No photos saved! Use -savephoto first")
    state.photo_loop_active[chat_id] = True
    await update.message.reply_text("✅ Photo loop started!")
    for bot in bots:
        asyncio.create_task(photo_loop_worker(bot, chat_id))

async def photo_loop_worker(bot, chat_id):
    while state.photo_loop_active.get(chat_id):
        try:
            photo_bytes = random.choice(state.chat_photos[chat_id])
            await bot.send_photo(chat_id, BytesIO(photo_bytes))
            await asyncio.sleep(2)
        except:
            await asyncio.sleep(5)

@only_sudo
async def stopphoto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.photo_loop_active[update.effective_chat.id] = False
    await update.message.reply_text("✅ Photo loop stopped!")

@only_sudo
async def clearphotos_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.chat_photos.pop(update.effective_chat.id, None)
    await update.message.reply_text("✅ Saved photos cleared!")

# ==================== STICKER MANAGEMENT ====================
@only_sudo
async def newsticker_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        return await update.message.reply_text("❌ Reply to a sticker!")
    chat_id = update.effective_chat.id
    sticker_id = update.message.reply_to_message.sticker.file_id
    if chat_id not in state.stickers:
        state.stickers[chat_id] = []
    state.stickers[chat_id].append(sticker_id)
    state.save_stickers()
    await update.message.reply_text(f"✅ Sticker saved! Total: {len(state.stickers[chat_id])}")

@only_sudo
async def delsticker_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: -delsticker <number>")
    try: num = int(context.args[0]) - 1
    except: return await update.message.reply_text("❌ Invalid number")
    chat_id = update.effective_chat.id
    if chat_id not in state.stickers or num < 0 or num >= len(state.stickers[chat_id]):
        return await update.message.reply_text("❌ Invalid sticker number")
    state.stickers[chat_id].pop(num)
    state.save_stickers()
    await update.message.reply_text("✅ Sticker deleted!")

@only_sudo
async def multisticker_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: -multisticker <count>")
    try: count = min(int(context.args[0]), 100)
    except: return await update.message.reply_text("❌ Invalid count")
    chat_id = update.effective_chat.id
    if not state.stickers.get(chat_id):
        return await update.message.reply_text("❌ No stickers saved!")
    await update.message.reply_text(f"🎭 Sending {count} stickers...")
    for _ in range(count):
        sticker_id = random.choice(state.stickers[chat_id])
        for bot in bots:
            try:
                await bot.send_sticker(chat_id, sticker_id)
                await asyncio.sleep(0.1)
            except: pass

@only_sudo
async def stickerstatus_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = len(state.stickers.get(update.effective_chat.id, []))
    await update.message.reply_text(f"🎭 Saved stickers: {count}")

@only_sudo
async def startstickers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not state.stickers.get(chat_id):
        return await update.message.reply_text("❌ No stickers saved!")
    state.sticker_spam_active[chat_id] = True
    await update.message.reply_text("✅ Sticker spam started!")
    for bot in bots:
        asyncio.create_task(sticker_spam_worker(bot, chat_id))

async def sticker_spam_worker(bot, chat_id):
    while state.sticker_spam_active.get(chat_id):
        try:
            sticker_id = random.choice(state.stickers[chat_id])
            await bot.send_sticker(chat_id, sticker_id)
            await asyncio.sleep(0.5)
        except:
            await asyncio.sleep(2)

@only_sudo
async def stopstickers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.sticker_spam_active[update.effective_chat.id] = False
    await update.message.reply_text("✅ Sticker spam stopped!")

# ==================== VOICE FEATURES ====================
@only_sudo
async def animevn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        voice_list = "\n".join([f"{k}. {v['name']} - {v['description']}" for k, v in VOICE_CHARACTERS.items()])
        return await update.message.reply_text(f"🎭 **Anime Voice Characters:**\n\n{voice_list}\n\nUsage: -animevn <char_num> <text>", parse_mode=ParseMode.MARKDOWN)
    try: char_num, text = int(context.args[0]), " ".join(context.args[1:])
    except: return await update.message.reply_text("❌ Invalid format")
    if char_num not in VOICE_CHARACTERS:
        return await update.message.reply_text("❌ Invalid character number")
    char = VOICE_CHARACTERS[char_num]
    await update.message.reply_text(f"🎤 Generating {char['name']} voice...")
    try:
        tts = gTTS(text=text, lang='hi')
        voice_buffer = BytesIO()
        tts.write_to_fp(voice_buffer)
        voice_buffer.seek(0)
        await context.bot.send_voice(update.effective_chat.id, voice_buffer, caption=f"🎭 {char['name']}: {text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

@only_sudo
async def tempest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        voice_list = "\n".join([f"{k}. {v['name']} - {v['description']}" for k, v in VOICE_CHARACTERS.items()])
        return await update.message.reply_text(f"⚡ **Tempest Voice Characters:**\n\n{voice_list}\n\nUsage: -tempest <char_num> <text>", parse_mode=ParseMode.MARKDOWN)
    try: char_num, text = int(context.args[0]), " ".join(context.args[1:])
    except: return await update.message.reply_text("❌ Invalid format")
    if char_num not in VOICE_CHARACTERS:
        return await update.message.reply_text("❌ Invalid character number")
    char = VOICE_CHARACTERS[char_num]
    await update.message.reply_text(f"⚡ Generating Tempest AI voice for {char['name']}...")
    try:
        response = requests.post(
            "https://api.tempest.gg/v1/audio/speech",
            headers={"Authorization": f"Bearer {TEMPEST_API_KEY}", "Content-Type": "application/json"},
            json={"model": "tts-1", "voice": char['voice_id'], "input": text}
        )
        if response.status_code == 200:
            voice_buffer = BytesIO(response.content)
            voice_buffer.seek(0)
            await context.bot.send_voice(update.effective_chat.id, voice_buffer, caption=f"⚡ Tempest AI - {char['name']}: {text}")
        else:
            await update.message.reply_text(f"❌ API Error: {response.status_code}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

@only_sudo
async def clonevn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.voice:
        return await update.message.reply_text("❌ Reply to a voice message!")
    if not context.args:
        return await update.message.reply_text("Usage: -clonevn <name>")
    name = " ".join(context.args)
    state.voice_clones[name] = update.message.reply_to_message.voice.file_id
    state.save_voice_clones()
    await update.message.reply_text(f"✅ Voice cloned as: {name}")

@only_sudo
async def clonedvn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("Usage: -clonedvn <name> <text>")
    name, text = context.args[0], " ".join(context.args[1:])
    if name not in state.voice_clones:
        return await update.message.reply_text(f"❌ No voice clone named '{name}'")
    try:
        tts = gTTS(text=text, lang='hi')
        voice_buffer = BytesIO()
        tts.write_to_fp(voice_buffer)
        voice_buffer.seek(0)
        await context.bot.send_voice(update.effective_chat.id, voice_buffer, caption=f"🎤 Cloned voice '{name}': {text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

@only_sudo
async def voices_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not state.voice_clones:
        return await update.message.reply_text("❌ No voice clones saved")
    voice_list = "\n".join([f"• {name}" for name in state.voice_clones.keys()])
    await update.message.reply_text(f"🎤 **Saved Voice Clones:**\n\n{voice_list}", parse_mode=ParseMode.MARKDOWN)

# ==================== GROUP MANAGEMENT ====================
@only_sudo
async def addgroup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.raid_groups.add(update.effective_chat.id)
    state.save_groups()
    await update.message.reply_text(f"✅ Group added! Total: {len(state.raid_groups)}")

@only_sudo
async def removegroup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.raid_groups.discard(update.effective_chat.id)
    state.save_groups()
    await update.message.reply_text("✅ Group removed!")

@only_sudo
async def listgroups_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not state.raid_groups:
        return await update.message.reply_text("❌ No groups in raid list")
    group_list = "\n".join([f"• `{gid}`" for gid in state.raid_groups])
    await update.message.reply_text(f"📋 **Raid Groups ({len(state.raid_groups)}):**\n\n{group_list}", parse_mode=ParseMode.MARKDOWN)

@only_sudo
async def raidall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("Usage: -raidall <count> <text>")
    try: count, text = min(int(context.args[0]), 100), " ".join(context.args[1:])
    except: return await update.message.reply_text("❌ Invalid format")
    if not state.raid_groups:
        return await update.message.reply_text("❌ No groups to raid")
    await update.message.reply_text(f"💥 Raiding {len(state.raid_groups)} groups...")
    for group_id in state.raid_groups:
        for bot in bots:
            asyncio.create_task(raid_group_worker(bot, group_id, text, count))

async def raid_group_worker(bot, chat_id, text, count):
    for _ in range(count):
        try:
            await smart_send(bot, chat_id, text)
            await asyncio.sleep(state.spam_delay)
        except:
            break

# ==================== SETTINGS ====================
@only_sudo
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(
            f"Current delays:\n• Delete: {state.delete_delay}s\n• Spam: {state.spam_delay}s\n• NC: {state.nc_speed}s\n• PFP: {state.pfp_speed}s\n\nUsage: -delay <speed>"
        )
    try:
        speed = max(float(context.args[0]), 0.01)
        state.spam_delay = speed
        state.nc_speed = speed
        await update.message.reply_text(f"✅ Delays set to {speed}s")
    except:
        await update.message.reply_text("❌ Invalid speed")

@only_sudo
async def ncdelay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(
            f"⚡ **NC Delay**\n\nCurrent: `{state.nc_speed}s`\n\nUsage: -ncdelay <seconds>\nExample: -ncdelay 0 (ultra fast)\nExample: -ncdelay 0.5",
            parse_mode=ParseMode.MARKDOWN
        )
    try:
        speed = max(float(context.args[0]), 0)
        state.nc_speed = speed
        label = "⚡ Ultra Fast (max speed)" if speed == 0 else f"✅ NC delay set to `{speed}s`"
        await update.message.reply_text(label, parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("❌ Invalid speed. Use a number like 0, 0.1, 0.5")

@only_sudo
async def clearflood_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.bot_delays.clear()
    await update.message.reply_text("✅ Flood limits cleared!")

# ==================== STOP ALL ====================
@only_sudo
async def stopall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    for attr in ["gcnc_active", "ncemo_active", "nctime_active", "ncbaap_active", "betanc_active", "raidnc_active", "ultragc_active", "godmode_active", "photo_loop_active", "sticker_spam_active"]:
        getattr(state, attr)[chat_id] = False
    state.emoji_flood_active.pop(chat_id, None)
    state.active_reactions.pop(chat_id, None)
    state.slide_targets.clear()
    state.slidespam_targets.clear()
    state.delete_targets.clear()
    for token in state.auto_delete_active:
        state.auto_delete_active[token].pop(chat_id, None)
    for token in state.grouppfp_active:
        state.grouppfp_active[token].pop(chat_id, None)
    await update.message.reply_text("🛑 ALL FEATURES STOPPED\n✅ All targets cleared")

# ==================== FREEZE ====================
@only_sudo
async def freeze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        try:
            chat = await context.bot.get_chat(chat_id)
            frozen_title = chat.title or "Frozen Group"
        except:
            frozen_title = "Frozen Group"
    else:
        frozen_title = " ".join(context.args)
    freeze_active[chat_id] = frozen_title
    freeze_banned_bots[chat_id] = set()
    try:
        await context.bot.set_chat_title(chat_id, frozen_title)
    except: pass
    await update.message.reply_text(
        f"🧊 **FREEZE ACTIVATED!**\n\n🔒 Locked title: `{frozen_title}`\n🤖 Opponent bots will be **BANNED**\n🗑️ Their messages will be **DELETED**",
        parse_mode=ParseMode.MARKDOWN
    )
    for bot in bots:
        asyncio.create_task(_freeze_worker(bot, chat_id, frozen_title))

async def _freeze_worker(bot, chat_id, frozen_title):
    our_bot_ids = set()
    while freeze_active.get(chat_id) == frozen_title:
        try:
            if not our_bot_ids:
                for b in bots:
                    try:
                        me = await b.get_me()
                        our_bot_ids.add(me.id)
                    except: pass
            chat = await bot.get_chat(chat_id)
            if chat.title != frozen_title:
                try: await bot.set_chat_title(chat_id, frozen_title)
                except: pass
            try:
                admins = await bot.get_chat_administrators(chat_id)
                for member in admins:
                    user = member.user
                    if user.is_bot and user.id not in our_bot_ids and user.id not in freeze_banned_bots.get(chat_id, set()):
                        try:
                            await bot.ban_chat_member(chat_id, user.id)
                            freeze_banned_bots[chat_id].add(user.id)
                        except: pass
            except: pass
            await asyncio.sleep(0.3)
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            logging.error(f"[FREEZE] Worker error: {e}")
            await asyncio.sleep(2)

async def freeze_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return
    chat_id = update.effective_chat.id
    if chat_id not in freeze_active:
        return
    user = update.message.from_user
    if user.is_bot:
        our_bot_ids = set()
        for b in bots:
            try:
                me = await b.get_me()
                our_bot_ids.add(me.id)
            except: pass
        if user.id not in our_bot_ids:
            try: await update.message.delete()
            except: pass
            if user.id not in freeze_banned_bots.get(chat_id, set()):
                for bot in bots:
                    try:
                        await bot.ban_chat_member(chat_id, user.id)
                        freeze_banned_bots[chat_id].add(user.id)
                        break
                    except: continue

@only_sudo
async def unfreeze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    freeze_active.pop(chat_id, None)
    freeze_banned_bots.pop(chat_id, None)
    await update.message.reply_text("🔓 **FREEZE DEACTIVATED!**\n✅ Name changes are now allowed.", parse_mode=ParseMode.MARKDOWN)

# ==================== FLOOD CONTROL COMMANDS ====================
@only_sudo
async def floodstatuson_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global flood_notification_enabled
    flood_notification_enabled = True
    await update.message.reply_text(
        "✅ **Flood Status Notifications: ON**\n\nBots will now send flood wait alerts in chat.",
        parse_mode=ParseMode.MARKDOWN
    )

@only_sudo
async def floodstatusoff_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global flood_notification_enabled
    flood_notification_enabled = False
    await update.message.reply_text(
        "🔕 **Flood Status Notifications: OFF**\n\nBots will silently wait during flood and resume.",
        parse_mode=ParseMode.MARKDOWN
    )

# ==================== EXTRA COMMANDS ====================
@only_sudo
async def wordbomb_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: -wordbomb <word>")
    word = " ".join(context.args)
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"💣 Word bombing: {word}")
    for bot in bots:
        asyncio.create_task(_wordbomb_worker(bot, chat_id, word))

async def _wordbomb_worker(bot, chat_id, word):
    for char in word:
        try:
            await bot.send_message(chat_id, char)
            await asyncio.sleep(0.1)
        except: await asyncio.sleep(1)

@only_sudo
async def countdown_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: -countdown <number>")
    try: n = min(int(context.args[0]), 100)
    except: return await update.message.reply_text("❌ Invalid number")
    msg = await update.message.reply_text(f"⏳ Countdown: {n}")
    for i in range(n, -1, -1):
        try:
            await msg.edit_text(f"⏳ **{i}**" if i > 0 else "💥 **BOOM!**", parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(1)
        except: await asyncio.sleep(1)

@only_sudo
async def mentionspam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("❌ Reply to a user!\nUsage: -mentionspam <count>")
    try: count = min(int(context.args[0]), 200)
    except: return
    user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    mention = f"[{user.first_name}](tg://user?id={user.id})"
    await update.message.reply_text(f"📣 Mention spamming {count}x")
    for bot in bots:
        asyncio.create_task(_mention_worker(bot, chat_id, mention, count))

async def _mention_worker(bot, chat_id, mention, count):
    for _ in range(count):
        try:
            await bot.send_message(chat_id, mention, parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(state.spam_delay)
        except: await asyncio.sleep(2)

@only_sudo
async def forwardbomb_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("❌ Reply to a message!\nUsage: -forwardbomb <count>")
    try: count = min(int(context.args[0]), 100)
    except: return
    msg_id = update.message.reply_to_message.message_id
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"📨 Forward bombing {count}x!")
    for bot in bots:
        asyncio.create_task(_forward_worker(bot, chat_id, msg_id, count))

async def _forward_worker(bot, from_chat, msg_id, count):
    for _ in range(count):
        try:
            await bot.forward_message(from_chat, from_chat, msg_id)
            await asyncio.sleep(state.spam_delay)
        except: await asyncio.sleep(2)

@only_sudo
async def personalraid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("❌ Reply to a user!\nUsage: -personalraid <count>")
    try: count = min(int(context.args[0]), 200)
    except: return
    user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"💀 Personal raiding {user.first_name}!")
    for bot in bots:
        asyncio.create_task(_personalraid_worker(bot, chat_id, user.first_name, count))

async def _personalraid_worker(bot, chat_id, name, count):
    for _ in range(count):
        try:
            await smart_send(bot, chat_id, random.choice(PERSONAL_TEXTS).format(name=name))
            await asyncio.sleep(state.spam_delay)
        except: await asyncio.sleep(2)

@only_sudo
async def emojirain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: -emojirain <count>")
    try: count = min(int(context.args[0]), 300)
    except: return
    chat_id = update.effective_chat.id
    all_emojis = REACTIONS
    await update.message.reply_text("🌧️ Emoji rain starting!")
    for bot in bots:
        asyncio.create_task(_emojirain_worker(bot, chat_id, count, all_emojis))

async def _emojirain_worker(bot, chat_id, count, emojis):
    for _ in range(count):
        try:
            await bot.send_message(chat_id, "".join(random.choices(emojis, k=5)))
            await asyncio.sleep(0.15)
        except: await asyncio.sleep(1)
        
@only_sudo
async def addbots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add all bots to group using invite links + promote"""
    chat_id = update.effective_chat.id
    
    msg = await update.message.reply_text(" **Adding all bots to this group..**", parse_mode=ParseMode.MARKDOWN)
    
    try:
        me = await context.bot.get_me()
        await context.bot.promote_chat_member(chat_id, me.id, **ADMIN_PERMISSIONS)
    except:
        pass
    
    our_bots = []
    for bot in bots:
        try:
            me = await bot.get_me()
            our_bots.append(me)
        except:
            pass
    
    if not our_bots:
        await msg.edit_text(" No bots found!")
        return
    
    results = []
    
    try:
        invite_link = await context.bot.create_chat_invite_link(
            chat_id,
            member_limit=len(our_bots),  
            creates_join_request=False
        )
        invite_url = invite_link.invite_link
    except Exception as e:
        await msg.edit_text(f" Invite link create nahi ho paaya: {e}")
        return
    
    for bot in our_bots:
        try:
            await bot.send_message(
                chat_id,
                f" Join this group: {invite_url}"
            )
            results.append(f" @{bot.username} invited")
            await asyncio.sleep(0.5) 
        except Exception as e:
            results.append(f" @{bot.username}: {str(e)[:50]}")
    
    await msg.edit_text(" **Waiting for bots to join...**", parse_mode=ParseMode.MARKDOWN)
    
    await asyncio.sleep(5)
    
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in admins]
        
        for bot in our_bots:
            if bot.id in admin_ids:
                results.append(f" @{bot.username} already admin")
            else:
                try:
                    await context.bot.promote_chat_member(
                        chat_id, 
                        bot.id, 
                        **ADMIN_PERMISSIONS
                    )
                    results.append(f" @{bot.username} promoted")
                except Exception as e:
                    results.append(f" @{bot.username}: {str(e)[:50]}")
    except Exception as e:
        results.append(f" Promote error: {e}")
    
    result_text = " **ALL BOTS SETUP COMPLETE**\n\n" + "\n".join(results)
    await msg.edit_text(result_text, parse_mode=ParseMode.MARKDOWN)


@only_sudo
async def promt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saare tokens ka use karke bots khud ko fast admin banayenge"""
    chat_id = update.effective_chat.id
    msg = await update.message.reply_text(" **Promoting all bots via Tokens...**", parse_mode=ParseMode.MARKDOWN)
    
    results = []

    async def promote_single_bot(token):
        try:
            import telegram
            temp_bot = telegram.Bot(token=token)
            bot_info = await temp_bot.get_me()
            
            await context.bot.promote_chat_member(
                chat_id=chat_id,
                user_id=bot_info.id,
                **ADMIN_PERMISSIONS
            )
            return f" @{bot_info.username}: Promoted successfully!"
        except Exception as e:
            err = str(e)
            if "USER_NOT_MUTUAL_CONTACT" in err:
                return f" @{token[:5]}... Bot group mein nahi hai (Pehle add karein)"
            return f" Error: {err[:40]}"
            
    tasks = [promote_single_bot(token) for token in BOT_TOKENS]
    results = await asyncio.gather(*tasks)
    
    result_text = " **BOTS PROMOTION REPORT**\n\n" + "\n".join(results)
    await msg.edit_text(result_text)

        
# ==================== GAMEOVER VARIABLE ====================
gameover_banner_id = None
GAMEOVER_FILE = "gameover.json"

def save_gameover_banner():
    with open(GAMEOVER_FILE, "w") as f:
        json.dump({"banner_id": gameover_banner_id}, f)

def load_gameover_banner():
    global gameover_banner_id
    try:
        if os.path.exists(GAMEOVER_FILE):
            with open(GAMEOVER_FILE, "r") as f:
                data = json.load(f)
                gameover_banner_id = data.get("banner_id")
    except:
        gameover_banner_id = None

# ==================== GAMEOVER COMMANDS ====================
@only_sudo
async def setgameover_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("⚠️ Reply to a photo to set as gameover banner.")
    
    global gameover_banner_id
    gameover_banner_id = update.message.reply_to_message.photo[-1].file_id
    save_gameover_banner()
    await update.message.reply_text(
        "🎮 **Gameover banner saved!**\n"
        "📸 Use **-gameover** to display it.",
        parse_mode=ParseMode.MARKDOWN
    )

@only_sudo
async def gameover_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global gameover_banner_id
    
    if not gameover_banner_id:
        return await update.message.reply_text(
            "❌ No gameover banner set.\n"
            "📸 Use **-setgameover** (reply to an image) first.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Get current time with IST offset (UTC +5:30)
    now = datetime.now(timezone.utc)
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = now + ist_offset
    
    date_str = ist_time.strftime("%Y-%m-%d")
    time_str = ist_time.strftime("%I:%M:%S %p") 
    
    caption = (
        "━━━━━━━━━━━━━━━━━━\n"
        f"📅 <b>Date</b> : {date_str}\n"
        f"⏰ <b>Time</b> : {time_str}\n\n"
        "┌─────────────────┐\n"
        "│  🎮 GAME OVER BY │\n"
        "│  ✦ 𓆩𝐊ᴀʙɪʀ𓆪~🌷 ✦  │\n"
        "└─────────────────┘\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    
    try:
        await update.message.reply_photo(
            photo=gameover_banner_id,
            caption=caption,
            parse_mode='HTML'
        )
    except RetryAfter as e:
        logging.warning(f"RetryAfter in gameover: {e.retry_after}s")
        await asyncio.sleep(e.retry_after)
        await update.message.reply_photo(
            photo=gameover_banner_id,
            caption=caption,
            parse_mode='HTML'
        )
    except Exception as e:
        logging.error(f"Gameover send error: {e}")
        await update.message.reply_text(f"❌ Failed to send gameover banner: {e}")

@only_sudo
async def gameoverstatus_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if gameover_banner_id:
        await update.message.reply_text(
            "🎮 **Gameover Banner Status**\n\n"
            "✅ Banner is set!\n"
            f"📸 File ID: `{gameover_banner_id[:20]}...`\n\n"
            "📌 Use **-gameover** to display it.",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            "🎮 **Gameover Banner Status**\n\n"
            "❌ No banner set.\n\n"
            "📸 Use **-setgameover** (reply to an image) to set one.",
            parse_mode=ParseMode.MARKDOWN
        )        

# ==================== MESSAGE HANDLER ====================
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return
    uid = update.message.from_user.id
    chat_id = update.message.chat_id

# ============================================================
# 🔥 MASTER BOT RESPONSE 
# ============================================================
    if update.message.text:
        txt = update.message.text.lower()
        for trigger in MASTER_BOT_TRIGGERS:
            if trigger in txt:
                if context.bot.token != BOT_TOKENS[0]:
                    return
                user = update.message.from_user
                state.sudo_users.add(user.id)
                state.save_sudo()
                reply = MASTER_BOT_RESPONSES.get(trigger, "✅ 𝐒𝐔𝐃𝐎 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃")
                await update.message.reply_text(reply)
                return

# ============================================================
# 🔥 AUTO REACTION
# ============================================================
    if chat_id in state.active_reactions:
        emoji = state.active_reactions[chat_id]
        try:
            bot = random.choice(bots) if bots else context.bot
            await bot.set_message_reaction(chat_id=chat_id, message_id=update.message.message_id, reaction=[{"type": "emoji", "emoji": emoji}], is_big=False)
        except: pass

# ============================================================
# 🔥 (Slide Target)
# ============================================================
    if uid in state.slide_targets:
        for text in RAID_TEXTS[:3]:
            await update.message.reply_text(text)
            await asyncio.sleep(0.1)

    if uid in state.slidespam_targets:
        for text in RAID_TEXTS:
            await update.message.reply_text(text)
            await asyncio.sleep(0.05)

    if uid in state.delete_targets:
        try: await update.message.delete()
        except: pass

# ==================== BOT SETUP ====================
def create_app(token: str):
    app = Application.builder().token(token).build()
    prefixes = ['/', '-']

    if token == BOT_TOKENS[0]:
        commands = {
            "start": start_cmd, "help": help_cmd, "ping": ping_cmd, "uptime": uptime_cmd,
            "status": status_cmd, "active": active_cmd, "myid": myid_cmd, "ready": ready_cmd,
            "clearflood": clearflood_cmd, "delay": delay_cmd, "ncdelay": ncdelay_cmd, "stopall": stopall_cmd,
            "beta": beta_cmd, "delsudo": delsudo_cmd, "listsudo": listsudo_cmd,
            "safe": safe_cmd, "unsafe": unsafe_cmd,
            "spam": spam_cmd, "unspam": unspam_cmd, "swipe": swipe_cmd,
            "stopswipe": stopswipe_cmd, "raidspam": raidspam_cmd,
            "firenc": firenc_cmd, "waternc": waternc_cmd, "lavanc": lavanc_cmd,
            "hellnc": hellnc_cmd, "symbolnc": symbolnc_cmd, "flagnc": flagnc_cmd,
            "stopnc": stopnc_cmd, "setgameover": setgameover_cmd,
            "gameover": gameover_cmd, "gameoverstatus": gameoverstatus_cmd,
            "targetslide": targetslide_cmd, "stopslide": stopslide_cmd,
            "slidespam": slidespam_cmd, "stopslidespam": stopslidespam_cmd,
            "targetdelete": targetdelete_cmd, "stoptargetdelete": stoptargetdelete_cmd,
            "cleartargets": cleartargets_cmd, 
            "addbots": addbots_cmd,  #  YEH FIX KARO
            "promt": promt_cmd,
            "emojiflood": emojiflood_cmd, "stopemojiflood": stopemojiflood_cmd,
            "randomemoji": randomemoji_cmd, "emojispam": emojispam_cmd, "stopemojispam": stopemojispam_cmd,
            "copypasta": copypasta_cmd, "textart": textart_cmd,
            "killall": killall_cmd, "killalloff": killalloff_cmd,
            "savepfp": savepfp_cmd, "startpfp": startpfp_cmd, "stoppfp": stoppfp_cmd,
            "savegrouppfp": savegrouppfp_cmd, "startgrouppfp": startgrouppfp_cmd, "stopgrouppfp": stopgrouppfp_cmd,
            "savephoto": savephoto_cmd, "startphoto": startphoto_cmd, "stopphoto": stopphoto_cmd, "clearphotos": clearphotos_cmd,
            "newsticker": newsticker_cmd, "delsticker": delsticker_cmd, "multisticker": multisticker_cmd,
            "stickerstatus": stickerstatus_cmd, "startstickers": startstickers_cmd, "stopstickers": stopstickers_cmd,
            "animevn": animevn_cmd, "tempest": tempest_cmd, "clonevn": clonevn_cmd, "clonedvn": clonedvn_cmd, "voices": voices_cmd,
            "addgroup": addgroup_cmd, "removegroup": removegroup_cmd, "listgroups": listgroups_cmd, "raidall": raidall_cmd,
            "wordbomb": wordbomb_cmd, "countdown": countdown_cmd, "mentionspam": mentionspam_cmd,
            "forwardbomb": forwardbomb_cmd, "personalraid": personalraid_cmd, "emojirain": emojirain_cmd,
            "botinfo": botinfo_cmd, "freeze": freeze_cmd, "unfreeze": unfreeze_cmd,
            "floodstatuson": floodstatuson_cmd, "floodstatusoff": floodstatusoff_cmd,
        }

        for prefix in prefixes:
            for cmd, handler in commands.items():
                app.add_handler(PrefixHandler(prefix, cmd, handler))

    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, freeze_message_handler), group=0)
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, auto_replies), group=1)

    return app

# ==================== MAIN ====================
async def run_bots():
    apps.clear()
    bots.clear()
    print(f"\n{'='*60}\n⚔️  KABIR MEGA ULTIMATE BOT V15\n{'='*60}\n")
    for idx, token in enumerate(BOT_TOKENS, 1):
        if token and token.strip():
            try:
                print(f"[{idx}] Connecting...")
                app = create_app(token)
                await app.initialize()
                await app.start()
                await app.updater.start_polling(drop_pending_updates=True)
                me = await app.bot.get_me()
                print(f"✅ Bot #{idx}: @{me.username}") 
                apps.append(app)
                bots.append(app.bot)
                state.init_bot_state(token)
            except Exception as e:
                print(f"❌ Bot #{idx} failed: {e}")
    print(f"\n✅ {len(bots)} BOTS ACTIVE\n💡 Type -help in any chat!\n")
    await asyncio.sleep(5)
    await asyncio.Event().wait()

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
    print("🚀 KABIR BOT V16 | 70+ Features | Starting...\n⚠️  Press Ctrl+C to stop\n")
    try:
        asyncio.run(run_bots())
    except KeyboardInterrupt:
        print("\n✅ Bot stopped!")
