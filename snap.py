# ═══════════════════════════════════════════════════════════════
#   👻 SNAPCHAT TERMINAL CHAT — by - 𝐊 ꫀ ꜱ ʜ ꫝ ꪜ ᴀ 🍃
#   Termux Ready | Full Featured | Python 3.6+
#   Install: pip install colorama pyfiglet rich
# ═══════════════════════════════════════════════════════════════

import sys
import subprocess
import os

# ── Auto-install missing packages (Termux friendly) ───────────
REQUIRED = ['colorama', 'pyfiglet', 'rich']

def auto_install():
    for pkg in REQUIRED:
        try:
            __import__(pkg)
        except ImportError:
            print(f"[*] Installing {pkg}...")
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', pkg, '-q'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"[✓] {pkg} installed!")

auto_install()

# ── Standard imports ──────────────────────────────────────────
import socket
import threading
import datetime
import time
import json
import hashlib
import re
import random

# ── colorama ─────────────────────────────────────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=True, strip=False)
    Y  = Fore.YELLOW;  G  = Fore.GREEN;   C  = Fore.CYAN
    R  = Fore.RED;     W  = Fore.WHITE;   M  = Fore.MAGENTA
    O  = Fore.LIGHTYELLOW_EX; BL = Fore.BLUE
    B  = Style.BRIGHT; X  = Style.RESET_ALL
except Exception:
    Y=G=C=R=W=M=O=BL=B=X=''

# ── pyfiglet ─────────────────────────────────────────────────
try:
    import pyfiglet
    HAS_FIGLET = True
except Exception:
    HAS_FIGLET = False

# ── rich ─────────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    HAS_RICH = True
except Exception:
    HAS_RICH = False

# ══════════════════════════════════════════════════════════════
#                        CONFIG
# ══════════════════════════════════════════════════════════════
HOST          = '0.0.0.0'
PORT          = 9999
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE_DIR, 'accounts.json')
BANNED_FILE   = os.path.join(BASE_DIR, 'banned.json')
OWNER         = '- 𝐊 ꫀ ꜱ ʜ ꫝ ꪜ ᴀ 🍃'
MAX_HISTORY   = 50

# ── ANSI Stripper ─────────────────────────────────────────────
ANSI_RE = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
def strip_ansi(s): return ANSI_RE.sub('', s)

# ── Get device IP (works on Termux / Linux) ──────────────────
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

# ══════════════════════════════════════════════════════════════
#                   FIGHTING COMMANDS (40+)
# ══════════════════════════════════════════════════════════════
FIGHT_CMDS = {
    '/slap'     : ('💥', '{a} ne {t} ko itna ZABARDAST THAPPAD maara ke chehra sunn ho gaya! 👋🔥'),
    '/punch'    : ('🥊', '{a} ne {t} ke seedha muh par UPPERCUT maara! Daant toot gaye! 💢😤'),
    '/kick'     : ('🦵', '{a} ne {t} ko FLYING KICK maar ke 10 meter door udaa diya! 💨😵'),
    '/bite'     : ('🦷', '{a} ne {t} ko kaan par KAATA! Khoon nikal raha hai! 😈🩸'),
    '/headbutt' : ('🤕', '{a} ne {t} ko HEADBUTT maara! Dono ke tare dikh rahe hain! ⭐😵'),
    '/choke'    : ('😤', '{a} ne {t} ka gala pakad ke HAATH SE DABA DIYA! 🤛💀'),
    '/stomp'    : ('👣', '{a} ne {t} ko zameen par giraa ke JOOTE SE RUNDA! 👟💢'),
    '/scratch'  : ('🐱', '{a} ne {t} ko NAKHOON se aisa nokha ki nishaan pad gaye! 😼🩸'),
    '/smash'    : ('💣', '{a} ne {t} ko uthaa ke seedha ZAMEEN PAR PATAAK DIYA! BOOM! 💥'),
    '/elbow'    : ('💪', '{a} ne {t} ki naak par ELBOW maara! Naak tedi ho gayi! 😂💢'),
    '/bomb'     : ('💣', '{a} ne {t} par NUCLEAR BOMB gira diya! Server hil gaya! ☢️💥'),
    '/laser'    : ('🔫', '{a} ne {t} par LASER BEAM chalaaya! Raakh ho gaya! ⚡💀'),
    '/thunder'  : ('⚡', '{a} ne {t} par BIJLI giraayi! Jal gaya bilkul! 🌩️😵'),
    '/nuke'     : ('☢️',  '{a} ne poori duniya mein {t} ko dhoondh ke NUKE maar diya! 💥🌍'),
    '/missile'  : ('🚀', '{a} ne {t} par MISSILE daag diya! Seedha target! 💥🎯'),
    '/chainsaw' : ('🪚', '{a} ne {t} ke peeche CHAINSAW leke bhaagna shuru kar diya! 😱 RUN!'),
    '/cannon'   : ('💫', '{a} ne {t} ko tope se UDAA DIYA! Seedha chand par gaya! 🌙😂'),
    '/roast'    : ('🔥', '{a} ne {t} ko itna ROAST kiya ke server ka temperature badh gaya! 🌶️💀'),
    '/expose'   : ('📢', '{a} ne {t} ki sari SECRETS poori chat mein bata di! 🙊😱'),
    '/expose2'  : ('🗂️',  '{a} ne {t} ke sare LOG SERVER PAR UPLOAD kar diye! 🤫📁'),
    '/mock'     : ('😝', '{a} ne {t} ki NAKAL utaar ke sabko hasakar pagal kar diya! 🤡😂'),
    '/shame'    : ('😳', '{a} ne {t} ko itna SHARMINDA kiya ke woh undercover ho gaya! 🫣💀'),
    '/diss'     : ('🎤', '{a} ne {t} par itni tagdi DISS track release ki ke woh retire ho gaya! 🎵💀'),
    '/tickle'   : ('😂', '{a} ne {t} ko itna GUDUDAAYA ke woh hansate hansate gir gaya! 🤣'),
    '/fart'     : ('💨', '{a} ne {t} ke muh ke paas PAAD maara! Atmosphere kharab! 🤢😷'),
    '/splash'   : ('💦', '{a} ne {t} par poori BALTI THANDA PAANI phenk diya! Brrrr! 🥶'),
    '/troll'    : ('🃏', '{a} ne {t} ko itna TROLL kiya ke woh chat hi chhod ke chala gaya! 😂🚶'),
    '/wedgie'   : ('😬', '{a} ne {t} ko CHEENTI ki tarah uthaa ke WEDGIE de diya! 😖😂'),
    '/ban'      : ('🔨', '{a} ne {t} ko SERVER SE PERMANENTLY BAN maar diya! GOODBYE! 🚫'),
    '/mute'     : ('🔇', '{a} ne {t} ko MUTE kar diya! Ab koi nahi sunoga isko! 🔕😒'),
    '/kick2'    : ('🥾', '{a} ne {t} ko server se BOOT maar ke nikaala! Alvida! 👋'),
    '/arrest'   : ('🚔', '{a} ne {t} ko HANDCUFFS lagaa ke JAIL bhej diya! 👮⛓️'),
    '/ghost'    : ('👻', '{a} ne {t} ko PERMANENTLY GHOST kar diya! Tu exist hi nahi! 😤'),
    '/block'    : ('🚫', '{a} ne {t} ko BLOCK maar ke recycle bin mein daala! 🗑️😂'),
    '/report'   : ('📋', '{a} ne {t} ko 50 DIFFERENT PLATFORMS par REPORT kar diya! 😤📱'),
    '/kill'     : ('💀', '{a} ne {t} ko GAME OVER kar diya! Press F to pay respects! ⚰️😂'),
    '/destroy'  : ('🌪️',  '{a} ne {t} ko itna DESTROY kiya ke DNA bhi nahi mila! 💥🔬'),
    '/delete'   : ('🗑️',  '{a} ne {t} ko seedha HARD DRIVE SE DELETE kar diya! Permanently! 💾❌'),
    '/hug'      : ('🤗', '{a} ne {t} ko itni zor ki JHAPPI di ke haddiyan charachrayi! 🫂❤️'),
    '/cry'      : ('😭', '{a} ne {t} ko dekh ke RONA shuru kar diya! Aansu band nahi ho rahe! 💧'),
    '/love'     : ('❤️',  '{a} ne {t} ko PYAAR BHARE DESH se greet kiya! 💕😊'),
}

EIGHTBALL = [
    'Bilkul haan! 🎯', 'Pakka nahi... 🤔', 'HAAN HAAN HAAN! 🔥',
    'Nahi bhai, bilkul nahi. ❌', 'Shayad... 😶', 'Pata nahi yaar 🤷',
    'Definitely haan! ✅', 'Kal poochhna 😴', 'Signs keh rahe hain HAAN 🌟',
    'Mere khayal mein nahi 😬', '100% pakka! 💯', 'Dubara socho 🔄',
]

# ══════════════════════════════════════════════════════════════
#                   ACCOUNTS & BANS
# ══════════════════════════════════════════════════════════════
accounts_lock = threading.Lock()

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

def load_accounts(): return load_json(ACCOUNTS_FILE, {})
def save_accounts(d): save_json(ACCOUNTS_FILE, d)
def load_banned():    return load_json(BANNED_FILE, [])
def save_banned(d):   save_json(BANNED_FILE, d)
def hash_pw(pw):      return hashlib.sha256(pw.encode()).hexdigest()

def is_admin(uname):
    if uname == OWNER: return True
    with accounts_lock:
        acc = load_accounts()
    return acc.get(uname, {}).get('role') in ('admin', 'owner')

def recv_line(conn):
    """Read one line from socket (newline terminated)."""
    buf = b''
    while True:
        try:
            ch = conn.recv(1)
        except Exception:
            return ''
        if not ch or ch == b'\n':
            return buf.decode(errors='ignore').strip()
        buf += ch

# ══════════════════════════════════════════════════════════════
#                   SERVER GLOBAL STATE
# ══════════════════════════════════════════════════════════════
clients      = {}   # conn -> username
nicks        = {}   # conn -> session nick
statuses     = {}   # username -> status string
afk_status   = {}   # username -> afk reason
chat_history = []   # list of plain text strings
chat_topic   = ['👻 SNAPCHAT CHAT — Sab ka swagat hai!']
lock         = threading.Lock()
hist_lock    = threading.Lock()

def add_history(plain_line):
    with hist_lock:
        chat_history.append(plain_line)
        if len(chat_history) > MAX_HISTORY:
            chat_history.pop(0)

def get_display(conn):
    return nicks.get(conn) or clients.get(conn, '???')

def find_conn_by_name(target):
    t = target.lower()
    with lock:
        for c, uname in clients.items():
            if uname.lower() == t or nicks.get(c, '').lower() == t:
                return c, uname
    return None, None

def broadcast(msg, skip=None):
    with lock:
        for conn in list(clients):
            if conn != skip:
                try:    conn.sendall(msg.encode('utf-8'))
                except: clients.pop(conn, None)

def send_to(conn, msg):
    try: conn.sendall(msg.encode('utf-8'))
    except: pass

# ══════════════════════════════════════════════════════════════
#               LOGIN / REGISTER FLOW
# ══════════════════════════════════════════════════════════════
def server_login_flow(conn):
    banner = (
        f"\n{Y}{B}╔══════════════════════════════════════════╗\n"
        f"║   👻  SNAPCHAT CHAT  —  Login System   ║\n"
        f"║         Owner: {OWNER}            ║\n"
        f"╚══════════════════════════════════════════╝{X}\n\n"
        f"  {G}1{X} → Login  (purana account)\n"
        f"  {C}2{X} → Register (naya account banao)\n\n"
        f"{Y}Choice (1 ya 2): {X}"
    )
    send_to(conn, banner)
    choice = recv_line(conn)
    banned = load_banned()

    # ── REGISTER ──────────────────────────────────────────────
    if choice == '2':
        send_to(conn, f"{C}Naya username (2-20 chars, a-z 0-9 _ -): {X}")
        uname = recv_line(conn)

        if not uname or len(uname) < 2:
            send_to(conn, f"{R}❌ Username kam se kam 2 chars ka hona chahiye!\n{X}"); return None
        if len(uname) > 20:
            send_to(conn, f"{R}❌ Username zyada se zyada 20 chars!\n{X}"); return None
        if not re.match(r'^[a-zA-Z0-9_\-]+$', uname):
            send_to(conn, f"{R}❌ Sirf letters, numbers, _ aur - allowed!\n{X}"); return None
        if uname.lower() in [b.lower() for b in banned]:
            send_to(conn, f"{R}❌ Yeh username BANNED hai! 🚫\n{X}"); return None

        with accounts_lock:
            acc = load_accounts()
            if uname.lower() in [k.lower() for k in acc]:
                send_to(conn, f"{R}❌ Username pehle se hai! Doosra chunno.\n{X}"); return None

        send_to(conn, f"{C}Password (min 4 chars): {X}")
        pw = recv_line(conn)
        if len(pw) < 4:
            send_to(conn, f"{R}❌ Password 4 chars se kum nahi ho sakta!\n{X}"); return None

        send_to(conn, f"{C}Password dobara likho: {X}")
        pw2 = recv_line(conn)
        if pw != pw2:
            send_to(conn, f"{R}❌ Passwords match nahi kiye!\n{X}"); return None

        with accounts_lock:
            acc = load_accounts()
            acc[uname] = {
                'password': hash_pw(pw),
                'created':  datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                'role':     'user',
                'bio':      ''
            }
            save_accounts(acc)

        send_to(conn, f"{G}{B}✅ Account bana diya! Welcome {uname}! 🎉{X}\n")
        print(f"{G}[REGISTER] {uname}{X}")
        return uname

    # ── LOGIN ─────────────────────────────────────────────────
    else:
        for attempt in range(3):
            send_to(conn, f"{Y}Username: {X}"); uname = recv_line(conn)
            send_to(conn, f"{Y}Password: {X}"); pw    = recv_line(conn)

            if uname.lower() in [b.lower() for b in banned]:
                send_to(conn, f"{R}❌ Yeh account BANNED hai! 🚫\n{X}"); return None

            with accounts_lock: acc = load_accounts()
            if uname in acc and acc[uname]['password'] == hash_pw(pw):
                send_to(conn, f"{G}{B}✅ Login! Welcome back {uname}! 👻{X}\n")
                print(f"{G}[LOGIN] {uname}{X}")
                return uname

            left = 2 - attempt
            if left > 0:
                send_to(conn, f"{R}❌ Galat! {left} mauke bache.\n{X}")
            else:
                send_to(conn, f"{R}❌ 3 baar galat! 🚫\n{X}")
    return None

# ══════════════════════════════════════════════════════════════
#                   SERVER — CLIENT HANDLER
# ══════════════════════════════════════════════════════════════
def handle_client(conn, addr):
    name = None
    try:
        name = server_login_flow(conn)
        if not name:
            conn.close(); return

        # Ban check post-login
        if name.lower() in [b.lower() for b in load_banned()]:
            send_to(conn, f"{R}❌ Account ban hai! 🚫\n{X}"); conn.close(); return

        with lock: clients[conn] = name
        t_join = datetime.datetime.now().strftime("%H:%M")
        broadcast(f"{G}{B}>>> {name} chat mein aa gaye! 👻  [{t_join}]{X}\n", skip=conn)

        # Topic + help hint
        send_to(conn, f"{Y}{B}📌 Topic: {chat_topic[0]}{X}\n")
        send_to(conn, f"{C}'/help' likho commands ke liye.{X}\n\n")

        # Last 10 messages
        with hist_lock: recent = list(chat_history[-10:])
        if recent:
            send_to(conn, f"{BL}{B}── Pichle messages ──{X}\n")
            for h in recent: send_to(conn, h + '\n')
            send_to(conn, f"{BL}{B}─────────────────────{X}\n\n")

        # ── Main message loop ──────────────────────────────
        while True:
            try:
                data = conn.recv(8192)
            except Exception:
                break
            if not data: break

            raw = data.decode(errors='ignore')
            for msg in raw.split('\n'):
                msg = msg.strip()
                if not msg: continue
                if msg.lower() == 'quit': raise ConnectionResetError

                t    = datetime.datetime.now().strftime("%H:%M")
                disp = get_display(conn)

                # ── Private Message ──────────────────────
                if msg.startswith('__PM__:'):
                    payload = msg[7:]
                    idx = payload.find('|')
                    if idx != -1:
                        target, pm_text = payload[:idx], payload[idx+1:]
                        tc, tname = find_conn_by_name(target)
                        if tc:
                            send_to(tc,   f"{M}{B}[DM ← {disp}]{X}{M} {pm_text}{X}\n")
                            send_to(conn, f"{M}{B}[DM → {tname}]{X}{M} {pm_text}{X}\n")
                        else:
                            send_to(conn, f"{R}❌ '{target}' online nahi hai.{X}\n")

                # ── Online List ──────────────────────────
                elif msg == '__ONLINE__':
                    with lock:
                        online_list = [(get_display(c), statuses.get(clients[c], ''), afk_status.get(clients[c])) for c in clients]
                    lines = [f"\n{G}{B}╔══ 🟢 Online Users ({len(online_list)}) ══╗{X}"]
                    for n_, s_, afk_ in online_list:
                        afk_tag = f"  {Y}[AFK: {afk_}]{X}" if afk_ else ''
                        st_tag  = f"  {C}({s_}){X}"         if s_  else ''
                        lines.append(f"  {G}● {n_}{X}{st_tag}{afk_tag}")
                    lines.append(f"{G}{B}╚{'═'*26}╝{X}\n")
                    send_to(conn, '\n'.join(lines) + '\n')

                # ── Profile ──────────────────────────────
                elif msg.startswith('__PROFILE__:'):
                    target = msg[12:].strip() or name
                    with accounts_lock: acc = load_accounts()
                    if target in acc:
                        u       = acc[target]
                        role    = u.get('role', 'user').upper()
                        bio     = u.get('bio', '(khaali)')
                        status  = statuses.get(target, '(koi status nahi)')
                        online_ = '🟢 Online' if any(clients[c] == target for c in clients) else '🔴 Offline'
                        send_to(conn,
                            f"\n{Y}{B}╔══ 👤 Profile: {target} ══╗{X}\n"
                            f"  Haalat  : {online_}\n"
                            f"  Role    : {role}\n"
                            f"  Joined  : {u.get('created','?')}\n"
                            f"  Bio     : {bio}\n"
                            f"  Status  : {status}\n"
                            f"{Y}{B}╚{'═'*28}╝{X}\n"
                        )
                    else:
                        send_to(conn, f"{R}❌ User '{target}' nahi mila.{X}\n")

                # ── Status ───────────────────────────────
                elif msg.startswith('__STATUS__:'):
                    st = msg[11:].strip()
                    statuses[name] = st
                    send_to(conn, f"{G}✅ Status set: '{st}'{X}\n")
                    broadcast(f"{C}ℹ️  {disp} ka naya status: '{st}'{X}\n", skip=conn)

                # ── Nick ─────────────────────────────────
                elif msg.startswith('__NICK__:'):
                    new_nick = msg[9:].strip()
                    if not new_nick:
                        nicks.pop(conn, None)
                        send_to(conn, f"{G}✅ Nick reset, '{name}' wapas.{X}\n")
                    elif len(new_nick) > 20:
                        send_to(conn, f"{R}❌ Nick 20 chars se zyada nahi!{X}\n")
                    else:
                        nicks[conn] = new_nick
                        broadcast(f"{C}ℹ️  {name} ka nick ab '{new_nick}' hai!{X}\n", skip=conn)
                        send_to(conn, f"{G}✅ Nick set: '{new_nick}'{X}\n")

                # ── Bio ──────────────────────────────────
                elif msg.startswith('__BIO__:'):
                    bio = msg[8:].strip()[:100]
                    with accounts_lock:
                        acc = load_accounts()
                        if name in acc:
                            acc[name]['bio'] = bio
                            save_accounts(acc)
                    send_to(conn, f"{G}✅ Bio update ho gayi: '{bio}'{X}\n")

                # ── AFK ──────────────────────────────────
                elif msg.startswith('__AFK__:'):
                    reason = msg[8:].strip() or 'AFK'
                    afk_status[name] = reason
                    broadcast(f"{Y}💤 {disp} AFK gaya — {reason}{X}\n")

                elif msg == '__BACK__':
                    afk_status.pop(name, None)
                    broadcast(f"{G}👋 {disp} wapas aa gaya!{X}\n")

                # ── Change Password ───────────────────────
                elif msg.startswith('__CHANGEPASS__:'):
                    payload = msg[15:]
                    idx = payload.find('|')
                    if idx != -1:
                        old_pw, new_pw = payload[:idx], payload[idx+1:]
                        with accounts_lock:
                            acc = load_accounts()
                            if name in acc and acc[name]['password'] == hash_pw(old_pw):
                                if len(new_pw) < 4:
                                    send_to(conn, f"{R}❌ Naya password 4 chars se kum nahi ho sakta!{X}\n")
                                else:
                                    acc[name]['password'] = hash_pw(new_pw)
                                    save_accounts(acc)
                                    send_to(conn, f"{G}✅ Password badal gaya! Agli baar naya wala use karo.{X}\n")
                            else:
                                send_to(conn, f"{R}❌ Purana password galat hai!{X}\n")

                # ── Topic ────────────────────────────────
                elif msg.startswith('__TOPIC__:'):
                    if is_admin(name):
                        topic = msg[10:].strip()
                        chat_topic[0] = topic
                        broadcast(f"{Y}{B}📌 Topic badla: {topic}  (by {disp}){X}\n")
                    else:
                        send_to(conn, f"{R}❌ Sirf admin/owner topic set kar sakte hain!{X}\n")

                # ── Announce ─────────────────────────────
                elif msg.startswith('__ANNOUNCE__:'):
                    if is_admin(name):
                        ann = msg[13:].strip()
                        line = (
                            f"\n{Y}{B}╔{'═'*40}╗{X}\n"
                            f"{Y}{B}║  📢 ANNOUNCEMENT by {disp}{X}{Y}{B}  ║{X}\n"
                            f"{Y}{B}║  {ann:<38}║{X}\n"
                            f"{Y}{B}╚{'═'*40}╝{X}\n"
                        )
                        broadcast(line)
                    else:
                        send_to(conn, f"{R}❌ Sirf admin/owner announce kar sakte hain!{X}\n")

                # ── Kickout ──────────────────────────────
                elif msg.startswith('__KICKOUT__:'):
                    if is_admin(name):
                        target = msg[12:].strip()
                        tc, tname = find_conn_by_name(target)
                        if tc:
                            send_to(tc, f"{R}{B}⚠️  {disp} ne tumhe KICK kar diya! 👢{X}\n")
                            time.sleep(0.3)
                            tc.close()
                            broadcast(f"{R}🦵 {tname} ko {disp} ne KICK kar diya!{X}\n")
                        else:
                            send_to(conn, f"{R}❌ '{target}' online nahi hai.{X}\n")
                    else:
                        send_to(conn, f"{R}❌ Sirf admin/owner kick kar sakte hain!{X}\n")

                # ── Ban ──────────────────────────────────
                elif msg.startswith('__BANUSER__:'):
                    if is_admin(name):
                        target = msg[12:].strip()
                        banned = load_banned()
                        if target.lower() not in [b.lower() for b in banned]:
                            banned.append(target)
                            save_banned(banned)
                        tc, tname = find_conn_by_name(target)
                        if tc:
                            send_to(tc, f"{R}{B}🚫 Tumhara account PERMANENTLY BAN ho gaya!{X}\n")
                            time.sleep(0.3)
                            tc.close()
                        broadcast(f"{R}{B}🔨 {target} ko {disp} ne PERMANENTLY BAN kar diya!{X}\n")
                    else:
                        send_to(conn, f"{R}❌ Sirf admin/owner ban kar sakte hain!{X}\n")

                # ── Unban ────────────────────────────────
                elif msg.startswith('__UNBAN__:'):
                    if is_admin(name):
                        target = msg[10:].strip()
                        banned = load_banned()
                        banned = [b for b in banned if b.lower() != target.lower()]
                        save_banned(banned)
                        send_to(conn, f"{G}✅ '{target}' unban ho gaya!{X}\n")
                        broadcast(f"{G}🔓 {target} unban ho gaya. (by {disp}){X}\n")
                    else:
                        send_to(conn, f"{R}❌ Sirf admin/owner unban kar sakte hain!{X}\n")

                # ── Make Admin ───────────────────────────
                elif msg.startswith('__MAKEADMIN__:'):
                    if name == OWNER:
                        target = msg[14:].strip()
                        with accounts_lock:
                            acc = load_accounts()
                            if target in acc:
                                acc[target]['role'] = 'admin'
                                save_accounts(acc)
                                send_to(conn, f"{G}✅ {target} ab ADMIN hai! 🎖️{X}\n")
                                tc, _ = find_conn_by_name(target)
                                if tc: send_to(tc, f"{Y}{B}🎖️  Mubarak! Tumhe Admin bana diya gaya!{X}\n")
                            else:
                                send_to(conn, f"{R}❌ User account nahi mila.{X}\n")
                    else:
                        send_to(conn, f"{R}❌ Sirf OWNER admin bana sakta hai!{X}\n")

                # ── History ──────────────────────────────
                elif msg == '__HISTORY__':
                    with hist_lock: recent = list(chat_history[-20:])
                    send_to(conn, f"\n{BL}{B}── 📜 Chat History (last {len(recent)}) ──{X}\n")
                    for h in recent: send_to(conn, h + '\n')
                    send_to(conn, f"{BL}{B}{'─'*34}{X}\n\n")

                # ── /me action ───────────────────────────
                elif msg.startswith('__ME__:'):
                    action = msg[7:]
                    line = f"{C}* {disp} {action}{X}"
                    broadcast(line + '\n', skip=conn)
                    send_to(conn, line + '\n')
                    add_history(f"* {disp} {action}")

                # ── Fight ────────────────────────────────
                elif msg.startswith('__FIGHT__:'):
                    line = f"{R}{B}{msg[10:]}{X}"
                    broadcast(line + '\n', skip=conn)
                    add_history(strip_ansi(line))

                # ── Spam ─────────────────────────────────
                elif msg.startswith('__SPAM__:'):
                    broadcast(f"{M}💬 {B}[SPAM]{X}{M} {disp}:{X} {W}{msg[9:]}{X}\n", skip=conn)

                # ── System ───────────────────────────────
                elif msg.startswith('__SYSTEM__:'):
                    line = f"{O}{B}{msg[11:]}{X}"
                    broadcast(line + '\n', skip=conn)
                    add_history(strip_ansi(line))

                # ── Normal message ───────────────────────
                else:
                    if name in afk_status:
                        afk_status.pop(name)
                        broadcast(f"{G}👋 {disp} wapas aa gaya! (auto){X}\n")
                    line = f"{Y}[{t}] {B}{disp}:{X} {W}{msg}{X}"
                    broadcast(line + '\n', skip=conn)
                    add_history(f"[{t}] {disp}: {msg}")

    except Exception:
        pass
    finally:
        with lock:
            clients.pop(conn, None)
            nicks.pop(conn, None)
        if name:
            statuses.pop(name, None)
            afk_status.pop(name, None)
            broadcast(f"{R}<<< {name} chale gaye 👋{X}\n")
            print(f"{R}[LOGOUT] {name}{X}")
        try: conn.close()
        except: pass

def run_server():
    local_ip = get_local_ip()
    if HAS_FIGLET:
        print(f"{Y}{B}" + pyfiglet.figlet_format("- 𝐊 ꫀ ꜱ ʜ ꫝ ꪜ ᴀ 🍃", font='small') + X)

    print(f"{Y}{B}╔══════════════════════════════════════════╗{X}")
    print(f"{Y}{B}║   👻 SNAPCHAT CHAT SERVER — PORT {PORT}   ║{X}")
    print(f"{Y}{B}║       Owner: {OWNER}               ║{X}")
    print(f"{Y}{B}╚══════════════════════════════════════════╝{X}")
    print(f"{G}✅ Server ON!{X}")
    print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{X}")
    print(f"{W}  Local IP   : {Y}{local_ip}{X}")
    print(f"{W}  Port       : {Y}{PORT}{X}")
    print(f"{W}  Connect    : {C}python snapchat.py client {local_ip}{X}")
    print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{X}\n")

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind((HOST, PORT))
    except OSError:
        print(f"{R}❌ Port {PORT} busy hai! Koi aur process use kar raha hai.{X}")
        print(f"{Y}Tip: 'pkill -f snapchat' try karo Termux mein.{X}")
        sys.exit(1)
    srv.listen()
    print(f"{G}Waiting for connections...{X}\n")
    while True:
        try:
            conn, addr = srv.accept()
            print(f"{C}[+] {addr[0]}:{addr[1]}{X}")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print(f"\n{Y}Server band ho gaya. Bye! 👻{X}")
            break

# ══════════════════════════════════════════════════════════════
#                   CLIENT — COMMANDS
# ══════════════════════════════════════════════════════════════
def process_command(raw, sock, my_name):
    parts = raw.strip().split()
    cmd   = parts[0].lower()

    if cmd == '/help':
        show_chat_help(); return True

    if cmd in ('/online', '/users', '/who'):
        sock.sendall(b'__ONLINE__\n'); return True

    if cmd in ('/pm', '/w', '/dm', '/msg'):
        if len(parts) < 3: print(f"{R}Use: {cmd} <username> <message>{X}"); return True
        target = parts[1]; text = ' '.join(parts[2:])
        sock.sendall(f"__PM__:{target}|{text}\n".encode()); return True

    if cmd == '/profile':
        target = parts[1] if len(parts) > 1 else ''
        sock.sendall(f"__PROFILE__:{target}\n".encode()); return True

    if cmd == '/status':
        if len(parts) < 2: print(f"{R}Use: /status <message>{X}"); return True
        sock.sendall(f"__STATUS__:{' '.join(parts[1:])}\n".encode()); return True

    if cmd == '/nick':
        nick = ' '.join(parts[1:]) if len(parts) > 1 else ''
        sock.sendall(f"__NICK__:{nick}\n".encode()); return True

    if cmd == '/bio':
        if len(parts) < 2: print(f"{R}Use: /bio <text>{X}"); return True
        sock.sendall(f"__BIO__:{' '.join(parts[1:])}\n".encode()); return True

    if cmd == '/afk':
        reason = ' '.join(parts[1:]) if len(parts) > 1 else 'AFK'
        sock.sendall(f"__AFK__:{reason}\n".encode()); return True

    if cmd == '/back':
        sock.sendall(b'__BACK__\n'); return True

    if cmd == '/me':
        if len(parts) < 2: print(f"{R}Use: /me <action>{X}"); return True
        sock.sendall(f"__ME__:{' '.join(parts[1:])}\n".encode()); return True

    if cmd == '/changepass':
        if len(parts) < 3: print(f"{R}Use: /changepass <purana> <naya>{X}"); return True
        sock.sendall(f"__CHANGEPASS__:{parts[1]}|{parts[2]}\n".encode()); return True

    if cmd == '/history':
        sock.sendall(b'__HISTORY__\n'); return True

    if cmd == '/topic':
        if len(parts) < 2: print(f"{R}Use: /topic <text>{X}"); return True
        sock.sendall(f"__TOPIC__:{' '.join(parts[1:])}\n".encode()); return True

    if cmd == '/announce':
        if len(parts) < 2: print(f"{R}Use: /announce <message>{X}"); return True
        sock.sendall(f"__ANNOUNCE__:{' '.join(parts[1:])}\n".encode()); return True

    if cmd == '/kickout':
        if len(parts) < 2: print(f"{R}Use: /kickout <username>{X}"); return True
        sock.sendall(f"__KICKOUT__:{parts[1]}\n".encode()); return True

    if cmd == '/banuser':
        if len(parts) < 2: print(f"{R}Use: /banuser <username>{X}"); return True
        sock.sendall(f"__BANUSER__:{parts[1]}\n".encode()); return True

    if cmd == '/unbanuser':
        if len(parts) < 2: print(f"{R}Use: /unbanuser <username>{X}"); return True
        sock.sendall(f"__UNBAN__:{parts[1]}\n".encode()); return True

    if cmd == '/makeadmin':
        if len(parts) < 2: print(f"{R}Use: /makeadmin <username>{X}"); return True
        sock.sendall(f"__MAKEADMIN__:{parts[1]}\n".encode()); return True

    # ── Spam ─────────────────────────────────────────────────
    if cmd == '/spam':
        if len(parts) < 3: print(f"{R}Use: /spam <count> <msg>{X}"); return True
        try: count = max(1, min(500, int(parts[1])))
        except: print(f"{R}Count number hona chahiye!{X}"); return True
        text = ' '.join(parts[2:])
        print(f"{M}⚡ Spam shuru: {count}x ...{X}")
        for _ in range(count):
            sock.sendall(f"__SPAM__:{text}\n".encode()); time.sleep(0.03)
        print(f"{G}✅ Done!{X}"); return True

    if cmd == '/fastspam':
        if len(parts) < 3: print(f"{R}Use: /fastspam <count> <msg>{X}"); return True
        try: count = max(1, min(1000, int(parts[1])))
        except: print(f"{R}Count number hona chahiye!{X}"); return True
        text = ' '.join(parts[2:])
        print(f"{R}{B}🚀 ULTRA FAST SPAM: {count}x ...{X}")
        def send_chunk(n): sock.sendall((''.join([f"__SPAM__:{text}\n"] * n)).encode())
        threads = []; remaining = count
        while remaining > 0:
            n = min(50, remaining)
            t = threading.Thread(target=send_chunk, args=(n,), daemon=True)
            t.start(); threads.append(t); remaining -= n
        for t in threads: t.join()
        print(f"{G}✅ Fast Spam done!{X}"); return True

    if cmd == '/bombspam':
        if len(parts) < 2: print(f"{R}Use: /bombspam <msg>{X}"); return True
        text = ' '.join(parts[1:])
        print(f"{R}{B}💣 BOMB SPAM 500x!!{X}")
        sock.sendall((''.join([f"__SPAM__:{text}\n"] * 500)).encode())
        print(f"{G}✅ Done!{X}"); return True

    # ── Fighting ─────────────────────────────────────────────
    if cmd in FIGHT_CMDS:
        emoji, tmpl = FIGHT_CMDS[cmd]
        target = ' '.join(parts[1:]) if len(parts) > 1 else 'SABKO'
        msg = f"{emoji}  {tmpl.format(a=my_name, t=target)}"
        sock.sendall(f"__FIGHT__:{msg}\n".encode())
        print(f"{R}{B}{msg}{X}"); return True

    # ── Fun ──────────────────────────────────────────────────
    if cmd == '/shout':
        if len(parts) < 2: print(f"{R}Use: /shout <msg>{X}"); return True
        msg = f"📢📢 {my_name} CHILLA RAHA HAI: {' '.join(parts[1:]).upper()} !!!! 📢📢"
        sock.sendall(f"__SYSTEM__:{msg}\n".encode()); print(f"{O}{B}{msg}{X}"); return True

    if cmd == '/lol':
        msg = f"😂😂 {my_name} haas haas ke PAGAL ho gaya! HAHAHAHAHAHA 😂😂😂"
        sock.sendall(f"__SYSTEM__:{msg}\n".encode()); print(f"{G}{msg}{X}"); return True

    if cmd == '/rage':
        msg = f"😤💢 {my_name} GUSSE SE KAAN SE DHUAAN NIKAL RAHA HAI!!! 🔥🔥🔥"
        sock.sendall(f"__SYSTEM__:{msg}\n".encode()); print(f"{R}{B}{msg}{X}"); return True

    if cmd == '/flex':
        msg = f"💪😎 {my_name} flex maar raha hai! GOAT hun main! 👑🐐"
        sock.sendall(f"__SYSTEM__:{msg}\n".encode()); print(f"{Y}{B}{msg}{X}"); return True

    if cmd == '/rip':
        target = ' '.join(parts[1:]) if len(parts) > 1 else 'kisi ko'
        msg = f"⚰️  F in the chat for {target}. RIP 😂💀"
        sock.sendall(f"__SYSTEM__:{msg}\n".encode()); print(msg); return True

    if cmd == '/flip':
        result = random.choice(['🪙 HEADS! Seedha!', '🪙 TAILS! Ulta!'])
        msg = f"🎰 {my_name} ne coin flip kiya: {result}"
        sock.sendall(f"__SYSTEM__:{msg}\n".encode()); print(f"{Y}{B}{msg}{X}"); return True

    if cmd == '/roll':
        n = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 6
        n = max(2, min(1000, n))
        result = random.randint(1, n)
        msg = f"🎲 {my_name} ne dice roll kiya (1-{n}): {result}!"
        sock.sendall(f"__SYSTEM__:{msg}\n".encode()); print(f"{Y}{B}{msg}{X}"); return True

    if cmd == '/8ball':
        if len(parts) < 2: print(f"{R}Use: /8ball <sawaal>{X}"); return True
        q = ' '.join(parts[1:])
        ans = random.choice(EIGHTBALL)
        msg = f"🎱 {my_name}: '{q}'\n   → Magic 8-Ball: {ans}"
        sock.sendall(f"__SYSTEM__:{msg}\n".encode()); print(f"{C}{msg}{X}"); return True

    if cmd == '/clap':
        if len(parts) < 2: print(f"{R}Use: /clap <msg>{X}"); return True
        msg = f"👏 {my_name}: 👏 {' 👏 '.join(parts[1:])} 👏"
        sock.sendall(f"__SYSTEM__:{msg}\n".encode()); print(f"{G}{msg}{X}"); return True

    if cmd == '/sarcasm':
        if len(parts) < 2: print(f"{R}Use: /sarcasm <msg>{X}"); return True
        text = ' '.join(parts[1:])
        sar = ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
        msg = f"🙄 {my_name}: {sar}"
        sock.sendall(f"__SYSTEM__:{msg}\n".encode()); print(f"{M}{msg}{X}"); return True

    if cmd == '/quote':
        if len(parts) < 2: print(f"{R}Use: /quote <msg>{X}"); return True
        text = ' '.join(parts[1:])
        msg = f"💬 \"{text}\"  — {my_name}"
        sock.sendall(f"__SYSTEM__:{msg}\n".encode()); print(f"{C}{B}{msg}{X}"); return True

    if cmd == '/ascii':
        if not HAS_FIGLET: print(f"{R}pyfiglet install karo: pip install pyfiglet{X}"); return True
        if len(parts) < 2: print(f"{R}Use: /ascii <text>{X}"); return True
        art = pyfiglet.figlet_format(' '.join(parts[1:]), font='small')
        sock.sendall(f"__SYSTEM__:{art}\n".encode()); print(f"{Y}{art}{X}"); return True

    # ── FIXED COUNTDOWN ───────────────────────────────────────
    if cmd == '/countdown':
        n = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
        n = max(1, min(10, n))
        print(f"{Y}⏳ Countdown shuru!{X}")
        for i in range(n, 0, -1):
            sock.sendall(f"__SYSTEM__:⏳ {i}...\n".encode())
            time.sleep(1)
        sock.sendall("__SYSTEM__: BLAST OFF! \n".encode())
        return True

    if cmd == '/clear':
        os.system('clear'); return True

    if cmd == '/time':
        t = datetime.datetime.now().strftime("%A, %d %B %Y — %H:%M:%S")
        print(f"{C}🕐 {t}{X}"); return True

    if cmd == '/myip':
        print(f"{C}📡 Tumhara IP: {Y}{get_local_ip()}{X}"); return True

    return False

# ══════════════════════════════════════════════════════════════
#                         HELP MENU
# ══════════════════════════════════════════════════════════════
def show_chat_help():
    if HAS_RICH:
        c = Console()
        c.print(f"\n[bold yellow]╔════════════════════════════════════════════════════╗[/]")
        c.print(f"[bold yellow]║  👻 SNAPCHAT CHAT COMMANDS — Owner: {OWNER}  ║[/]")
        c.print(f"[bold yellow]╚════════════════════════════════════════════════════╝[/]\n")

        t0 = Table(title="👤 SOCIAL & ACCOUNT", box=box.SIMPLE_HEAVY, style="cyan")
        t0.add_column("Command", style="cyan bold", no_wrap=True)
        t0.add_column("Kya karta hai", style="white")
        for r in [
            ("/pm <user> <msg>",        "🔒 Private DM (/w /dm /msg)"),
            ("/online",                  "🟢 Online list (/users /who)"),
            ("/profile [user]",          "📋 Profile dekho"),
            ("/status <msg>",            "💬 Status set karo"),
            ("/nick <naam>",             "🏷️  Session nickname"),
            ("/bio <text>",              "📝 Bio set karo (max 100)"),
            ("/afk [reason]",            "💤 AFK mark karo"),
            ("/back",                    "👋 AFK se wapas"),
            ("/me <action>",             "✨ Action message"),
            ("/changepass <old> <new>",  "🔑 Password badlo"),
            ("/history",                 "📜 Last 20 messages"),
            ("/myip",                    "📡 Apna IP dekho"),
        ]: t0.add_row(*r)
        c.print(t0)

        t1 = Table(title="⚡ SPAM", box=box.SIMPLE_HEAVY, style="magenta")
        t1.add_column("Command", style="cyan bold"); t1.add_column("Kya karta hai", style="white")
        for r in [
            ("/spam <N> <msg>",     "N baar (max 500)"),
            ("/fastspam <N> <msg>", "Ultra fast N baar (max 1000) 🚀"),
            ("/bombspam <msg>",     "500x ek saath 💣"),
        ]: t1.add_row(*r)
        c.print(t1)

        t2 = Table(title="⚔️  FIGHTING (40+)", box=box.SIMPLE_HEAVY, style="red")
        t2.add_column("Commands", style="cyan bold"); t2.add_column("Type", style="white")
        for r in [
            ("/slap /punch /kick /bite /headbutt /choke /stomp /scratch /smash /elbow", "Classic 💥"),
            ("/bomb /laser /thunder /nuke /missile /chainsaw /cannon", "Weapons ☢️"),
            ("/roast /expose /expose2 /mock /shame /diss", "Humiliation 🔥"),
            ("/troll /wedgie /fart /tickle /splash", "Troll/Funny 🃏"),
            ("/ban /mute /kick2 /arrest /ghost /block /report", "Server ⚙️"),
            ("/kill /destroy /delete", "Deadly ☠️"),
            ("/hug /cry /love", "Friendly ❤️"),
        ]: t2.add_row(*r)
        c.print(t2)

        t3 = Table(title="🎮 FUN & GAMES", box=box.SIMPLE_HEAVY, style="yellow")
        t3.add_column("Command", style="cyan bold"); t3.add_column("Kya karta hai", style="white")
        for r in [
            ("/shout <msg>",    "📢 CAPS mein chillao"),
            ("/lol",            "😂 Haso"),
            ("/rage",           "😤 Gussa"),
            ("/flex",           "💪 Show off"),
            ("/rip <naam>",     "⚰️  F in chat"),
            ("/flip",           "🪙 Coin flip"),
            ("/roll [N]",       "🎲 Dice 1-N"),
            ("/8ball <q>",      "🎱 Magic 8 ball"),
            ("/clap <msg>",     "👏 Clap message"),
            ("/sarcasm <msg>",  "🙄 AlTeRnAtInG"),
            ("/quote <msg>",    "💬 Styled quote"),
            ("/ascii <text>",   "🔤 ASCII art"),
            ("/countdown [N]",  "⏳ Countdown (max 10)"),
            ("/clear",          "🖥️  Screen clear"),
            ("/time",           "🕐 Time dekho"),
        ]: t3.add_row(*r)
        c.print(t3)

        t4 = Table(title="👑 ADMIN COMMANDS", box=box.SIMPLE_HEAVY, style="bright_yellow")
        t4.add_column("Command", style="cyan bold"); t4.add_column("Kya karta hai", style="white")
        for r in [
            ("/kickout <user>",    "🦵 Server se KICK"),
            ("/banuser <user>",    "🔨 Permanently BAN"),
            ("/unbanuser <user>",  "🔓 Unban karo"),
            ("/announce <msg>",    "📢 Global announcement"),
            ("/topic <text>",      "📌 Chat topic set karo"),
            ("/makeadmin <user>",  "🎖️  Admin banao (sirf owner)"),
        ]: t4.add_row(*r)
        c.print(t4)
    else:
        print(f"""
{Y}{B}╔════════════════════════════════════════════════╗
║  👻 CHAT COMMANDS — Owner: {OWNER}      ║
╚════════════════════════════════════════════════╝{X}
{C}{B}SOCIAL:{X} /pm /w /dm | /online /users | /profile
        /status /nick /bio | /afk /back | /me
        /changepass | /history | /myip
{M}{B}SPAM:{X}   /spam /fastspam /bombspam
{R}{B}FIGHT:{X}  /slap /punch /kick /bite /headbutt /choke
        /stomp /scratch /smash /elbow /bomb /laser
        /thunder /nuke /missile /chainsaw /cannon
        /roast /expose /expose2 /mock /shame /diss
        /troll /wedgie /fart /tickle /splash /ban
        /mute /kick2 /arrest /ghost /block /report
        /kill /destroy /delete /hug /cry /love
{Y}{B}GAMES:{X}  /shout /lol /rage /flex /rip /flip /roll [N]
        /8ball /clap /sarcasm /quote /ascii /countdown
{Y}{B}ADMIN:{X}  /kickout /banuser /unbanuser /announce /topic /makeadmin
{G}{B}BASIC:{X}  /help  /clear  /time  /myip  quit
""")

# ══════════════════════════════════════════════════════════════
#                          CLIENT
# ══════════════════════════════════════════════════════════════
def run_client(server_ip='127.0.0.1'):
    if HAS_FIGLET:
        print(f"{Y}{B}" + pyfiglet.figlet_format("- 𝐊 ꫀ ꜱ ʜ ꫝ ꪜ ᴀ 🍃", font='small') + X)
    print(f"{Y}{B}╔══════════════════════════════════════════╗{X}")
    print(f"{Y}{B}║     👻 SNAPCHAT CHAT - {OWNER}      ║{X}")
    print(f"{Y}{B}║       Server: {server_ip}:{PORT}          ║{X}")
    print(f"{Y}{B}╚══════════════════════════════════════════╝{X}")
    print(f"{C}Connecting...{X}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((server_ip, PORT))
        sock.settimeout(None)
    except socket.timeout:
        print(f"{R}❌ Timeout! Server chal raha hai? IP sahi hai?{X}"); sys.exit(1)
    except ConnectionRefusedError:
        print(f"{R}❌ Connection refuse! Pehle server chalao.{X}"); sys.exit(1)
    except Exception as e:
        print(f"{R}❌ Error: {e}{X}"); sys.exit(1)

    print(f"{G}✅ Connected!{X}\n")

    my_name    = [None]
    login_done = threading.Event()
    NAME_EXCLUDE = {'Welcome', 'back', 'Login', 'ho', 'gaye', 'Account', 'ready', 'bana', 'diya'}

    def receiver(s):
        while True:
            try:
                data = s.recv(8192)
                if not data:
                    print(f"\n{R}Server band ho gaya.{X}")
                    os._exit(0)
                text = data.decode(errors='ignore')
                if my_name[0] is None:
                    if 'Welcome back' in text or ('Welcome' in text and '🎉' in text):
                        clean = strip_ansi(text)
                        for word in clean.split():
                            w = ''.join(ch for ch in word if ch.isalnum() or ch in '_-')
                            if w and w not in NAME_EXCLUDE and len(w) >= 2:
                                my_name[0] = w
                                login_done.set()
                                break
                print(text, end='', flush=True)
            except Exception:
                break

    threading.Thread(target=receiver, args=(sock,), daemon=True).start()

    try:
        # Login loop
        while not login_done.is_set():
            try:
                line = input()
            except EOFError:
                break
            sock.sendall((line + '\n').encode())
            time.sleep(0.15)

        my_name[0] = my_name[0] or 'User'
        print(f"\n{G}✅ Chat shuru! '/help' likho sab commands dekhne ke liye.{X}\n")

        # Chat loop
        while True:
            try:
                msg = input()
            except EOFError:
                break
            if not msg: continue
            if msg.startswith('/'):
                if process_command(msg, sock, my_name[0]): continue
            sock.sendall((msg + '\n').encode())
            if msg.lower() == 'quit':
                print(f"{Y}Bye! 👻{X}"); break

    except KeyboardInterrupt:
        pass
    finally:
        try: sock.sendall(b'quit\n')
        except: pass
        time.sleep(0.2)
        sock.close()
        print(f"\n{Y}Disconnected. Bye! 👻{X}")

# ══════════════════════════════════════════════════════════════
#                        MAIN HELP
# ══════════════════════════════════════════════════════════════
def show_help():
    if HAS_FIGLET:
        print(f"{Y}{B}" + pyfiglet.figlet_format("- 𝐊 ꫀ ꜱ ʜ ꫝ ꪜ ᴀ 🍃", font='small') + X)
    print(f"""
{Y}{B}╔═══════════════════════════════════════════════════╗
║   👻 SNAPCHAT TERMINAL CHAT — Termux Ready        ║
║             Owner: {OWNER}                  ║
╚═══════════════════════════════════════════════════╝{X}

{G}{B}Termux Setup (pehli baar):{X}
  {C}pkg update && pkg install python{X}
  {C}pip install colorama pyfiglet rich{X}
  {W}(Ya seedha script chalao — auto install ho jaayega!){X}

{G}{B}Server Chalao:{X}
  {C}python snapchat.py server{X}

{G}{B}Client Connect Karo:{X}
  {C}python snapchat.py client{X}              → Same device
  {C}python snapchat.py client 192.168.x.x{X}  → WiFi/Hotspot se

{Y}{B}Features:{X}
  ✅ Login / Register (accounts.json mein save)
  ✅ Private DM (/pm /w /dm)
  ✅ Online users list (/online)
  ✅ Profile, Bio, Status, Nickname
  ✅ AFK system (/afk /back)
  ✅ Chat history (last 50 messages)
  ✅ Admin: kick, ban, unban, announce, topic
  ✅ 40+ fighting commands
  ✅ Spam: normal / fast / bomb
  ✅ Games: coin flip, dice, 8-ball, countdown
  ✅ Fun: sarcasm, clap, quote, ASCII art
  ✅ Auto IP detect (/myip)
  ✅ Port busy error bataata hai

{M}Doston ko connect karne ke liye:{X}
  {W}1. Server wala 'python snapchat.py server' chalaye{X}
  {W}2. Server ka IP share kare (/myip command se){X}
  {W}3. Doston ke phone mein Termux + Python hona chahiye{X}
  {W}4. Sab ek WiFi / Hotspot par honay chahiye{X}

{C}Apna IP dekhne ke liye: {Y}python snapchat.py client → /myip{X}
""")

# ══════════════════════════════════════════════════════════════
#                          ENTRY
# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help', 'help'):
        show_help()
    elif args[0] == 'server':
        run_server()
    elif args[0] == 'client':
        ip = args[1] if len(args) > 1 else '127.0.0.1'
        run_client(ip)
    else:
        print(f"{R}Galat command! 'server' ya 'client' likho.{X}")
        show_help()