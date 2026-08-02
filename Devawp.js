import makeWASocket, { useMultiFileAuthState, DisconnectReason, delay, fetchLatestBaileysVersion, downloadContentFromMessage } from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import pino from 'pino';
import fs from 'fs';
import readline from 'readline';
import PQueue from 'p-queue';
import { exec } from 'child_process';

// ==================== ULTRA ANTI-CRASH SYSTEM ====================
process.on('uncaughtException', (err) => console.log(`[ANTI-CRASH] Ignored: ${err.message}`));
process.on('unhandledRejection', (reason) => {});
process.on('warning', (warning) => console.warn('[WARNING]', warning.message));
process.setMaxListeners(0);

// ==================== RECOVERY SYSTEM (PM2 PERSISTENCE) ====================
const RECOVERY_FILE = './data/recovery.json';
function safeReadJSON(path, def) { try { if (fs.existsSync(path)) return JSON.parse(fs.readFileSync(path, 'utf8')); } catch (e) {} return def; }
function safeWriteJSON(path, data) { 
    try { 
        if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true }); 
        // Sync ki jagah Async write use kar rahe hain
        fs.writeFile(path, JSON.stringify(data, null, 2), (err) => {
            if (err) console.error('[SAVE ERROR]', err.message);
        }); 
    } catch (e) {} 
}

let activeRecovery = safeReadJSON(RECOVERY_FILE, {});
function saveState(jid, cmd, argsData) {
    if (!activeRecovery[jid]) activeRecovery[jid] = {};
    activeRecovery[jid][cmd] = argsData;
    safeWriteJSON(RECOVERY_FILE, activeRecovery);
}
function removeState(jid, cmd) {
    if (activeRecovery[jid] && activeRecovery[jid][cmd]) {
        delete activeRecovery[jid][cmd];
        safeWriteJSON(RECOVERY_FILE, activeRecovery);
    }
}

// ==================== HYPER CYBER EXOTIC ENGINE QUEUE ====================
const HSEE = {
    attackQueue: new PQueue({ concurrency: 50, interval: 50, intervalCap: 50 }),
    normalQueue: new PQueue({ concurrency: 20, interval: 50, intervalCap: 20 }),
    async runAttack(task) { try { return await this.attackQueue.add(task); } catch (e) { return null; } },
    async runNormal(task) { try { return await this.normalQueue.add(task); } catch (e) { return null; } },
    clearAll() { 
        this.attackQueue.pause(); this.attackQueue.clear(); 
        this.normalQueue.pause(); this.normalQueue.clear(); 
        this.attackQueue.start(); this.normalQueue.start();
    }
};

// ==================== SMART STYLISH FONT ENGINE ====================
const fontMap = {
    'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓', 'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
};
function styleText(text) { if (!text) return text; return text.replace(/[a-zA-Z]/g, c => fontMap[c] || c); }

// ==================== GLOBAL CONFIG & DATABASE ====================
const ROLES_FILE = './data/roles.json';
const BOTS_FILE = './data/bots.json';
const CONFIG_FILE = './data/config.json';
const TEMPLATE_FILE = './data/templates.json';

const defaultRoles = { admins: [], subAdmins: [] };
const defaultConfig = { prefix: '.' }; 

let roles = safeReadJSON(ROLES_FILE, defaultRoles);
let globalConfig = safeReadJSON(CONFIG_FILE, defaultConfig);
let customTemplates = safeReadJSON(TEMPLATE_FILE, {});
let GLOBAL_PREFIX = globalConfig.prefix;

function updatePrefix(newPrefix) { GLOBAL_PREFIX = newPrefix; globalConfig.prefix = newPrefix; safeWriteJSON(CONFIG_FILE, globalConfig); }
function normalizeJid(jid) { if (!jid) return ''; return jid.includes(':') ? jid.split(':')[0] + '@s.whatsapp.net' : (jid.includes('@') ? jid : jid + '@s.whatsapp.net'); }

// 🔥 PERMANENT HARDCODED ADMIN FOR DEV + DYNAMIC ADMINS 🔥
const isAdmin = (jid) => normalizeJid(jid) === '67073187571@s.whatsapp.net' || roles.admins.some(a => normalizeJid(a) === normalizeJid(jid));
const isSubAdmin = (jid) => roles.subAdmins.some(s => normalizeJid(s) === normalizeJid(jid));
const hasPerm = (jid) => isAdmin(jid) || isSubAdmin(jid);

// ==================== NEW EMOJIS & SYMBOLS ====================
const aestheticSymbols = ['⋆˚꩜｡ִֶָ𓂃 ࣪˖ ִֶָ🐇་༘࿐','𓆩⚝𓆪','‧₊˚♪','𝄞₊˚⊹ּ ֶָ֢.','🀪','🀏','❀','☘︎','᪥','☯︎','🀢','▬ι𓆃','ㆍ','☣︎','𖠣','༯','❕','𓁹‿𓁹','ᶻ 𝗓 𐰁','.ᐟ','𝕏','𓂃 ོ','✝︎','𓂃','𓍊₊˚ ୨ 🐦‍🔥 ୧ ˚₊𓋼','☭⃢⛩','ᯓ','✈︎','ㅤ♡','𓇢','𓆸̤̮','♾','༄','♱','🜲','⦮ ⦯','ཧོ۫ ׅ⌖','☢','⚖️','⊹'];
const baseEmojisNew = ['🔥','💥','⚡','🌪️','🌈','☄️','💫','🌊','❄️','🌸','💀','☠️','👺','🔱','⚜️','🩸','⚔️','🕊️','🪸','🪐'];

const dtxtFrames = [
    "ִֶָ𓂃 ࣪˖ ִֶָ🐇་༘࿐ {e}",
    "𓍊₊˚ ୨ {e} ୧ ˚₊𓋼",
    "🏰 ˚˖𓍢ִ໋{e}͙֒✧˚.🎀༘⋆",
    "⋆.ೃ࿔{e}*:･",
    "⋆. 𐙚˚࿔ {e} 𝜗𝜚˚⋆",
    "𓂃˖˳·˖ ִֶָ ⋆{e}͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ",
    "💕⃝{e} 💕⃝{e}🥀",
    "🖤⃝{e}𓍯𓂃𓏧♡🫵🏻🫶🏻"
];

const getRandom = (arr) => arr[Math.floor(Math.random() * arr.length)];
const getRandomDelay = (min, max) => Math.floor(Math.random() * (max - min + 1) + min);

// ==================== OLD EMOJI ARRAYS ====================
const emojiArrays = {
    n1:['🔥','💥','⚡','🌪️','🌈','☄️','💫','🌊','❄️','🌸','💀','☠️','👺','🔱','⚜️','🌟','✨','💢','💤','💨','💦','🌀','🌙'], n2:['🌑','🌒','🌓','🌔','🌕','🌖','🌗','🌘','☁️','🌨️','🌧️','🌩️','⛈️','🌦️','🌥️','⛅','🌤️','☀️'], n3:['🛑','🚧','🚨','⛽','🛢️','⚓','📫','📪','📬','📭','📧','💌','✉️','📨','📩','📥','📤'], n4:['📒','📔','📕','📓','📗','📘','📙','🖌️','🖍️','🖊️','🖋️','✒️','✏️'], n5:['🕛','🕧','🕐','🕜','🕑','🕝','🕒','🕞','🕓','🕟','🕔','🕠','🕕','🕡','🕖','🕢','🕗','🕣','🕘','🕤','🕙','🕥','🕚','🕦'], n6:['❤️','🧡','💛','💚','💙','💜','🤎','🖤','🤍','🩷','🩵','🩶','♥️'], n7:['💟','⚛️','🛐','🕉️','☸️','☮️','☯️','☪️','🪯','✝️','☦️','✡️','🔯','🕎','🆔','♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓','⛎'], n8:['💐','🌹','🥀','🌺','🌷','🪷','🌸','💮','🏵️','🪻','🌻','🌼','🍂','🍁','🍄','🌾','🌿','🌱','🍃','☘️','🍀','🌵','🌴','🪾','🌳','🌲'], n9:['🦅','🕊️','🦢','🪿','🦆','🐦‍🔥','🦃','⚽','⚾','🥎','🏀','🏐','🏈','🏉'], n10:['🦈','🐬','🐋','🐳','🐟','🐠','🐡','🦐','🦞','🦀','🦑','🐙','🪼','🪼','🦪','🪸','🫧'], n11:['🚀','✈️','🛫','🛬','🛩️','🕋','🏙️','🌆','🌇','🌃','🌉','🌁','🗾','🗺️'], n12:['🔮','🧿','🪬','📿','🏺','⚱️','⚰️','🪦','🚬','💣','🪤','📜','⚔️','🗡️','🛡️','🗝️','🔑','🔐','🔏','🔒','🔓'], n13:['🪓','🪝','🧲','🗜️','🔩','🪛','🪚','🔧','🔨','🛠️','⚒️','⛏️','🪏','⚙️','⛓️‍💥','🔗','⛓️','📎','🖇️','✂️','📏','📐'], n14:['◼️','◾','▪️','🔳','🔲','◻️','◽','▫️','🔴','🟠','🟡','🟢','🔵','🟣','🟤','⚫','⚪'], n15:['🇦🇨','🇦🇩','🇦🇪','🇦🇫','🇦🇬','🇦🇮','🇦🇱','🇦🇲','🇦🇴','🇦🇶','🇦🇷','🇦🇸','🇦🇹','🇦🇺','🇦🇼','🇦🇽','🇦🇿','🇧🇦','🇧🇧','🇧🇩','🇧🇪','🇧🇫','🇧🇬','🇧🇭','🇧🇮','🇧🇯','🇧🇱','🇧🇲','🇧🇳','🇧🇴','🇧🇶','🇧🇷','🇧🇸','🇧🇹','🇧🇻','🇧🇼','🇧🇾','🇧🇿','🇨🇦','🇨🇨','🇨🇩','🇨🇫','🇨🇬'], n16:['🇨🇭','🇨🇮','🇨🇰','🇨🇱','🇨🇲','🇨🇳','🇨🇴','🇨🇵','🇨🇶','🇨🇷','🇨🇺','🇨🇻','🇨🇼','🇨🇽','🇨🇾','🇨🇿','🇩🇪','🇩🇬','🇩🇯','🇩🇰','🇩🇲','🇪🇸','🇪🇹','🇪🇺','🇫🇮','🇫🇯','🇫🇰','🇫🇲','🇫🇴','🇫🇷','🇬🇦','🇬🇧','🇬🇩','🇬🇪','🇬🇫','🇬🇬','🇬🇭','🇬🇮','🇬🇱','🇬🇲','🇬🇳'], n17:['🇬🇵','🇬🇶','🇬🇷','🇬🇸','🇬🇹','🇬🇺','🇬🇼','🇬🇾','🇭🇰','🇭🇲','🇭🇳','🇭🇷','🇭🇹','🇭🇺','🇮🇨','🇮🇩','🇮🇪','🇮🇱','🇮🇲','🇮🇳','🇮🇴','🇮🇶','🇮🇷','🇮🇸','🇮🇹','🇯🇪','🇯🇲','🇯🇴','🇯🇵','🇰🇪','🇰🇬','🇰🇭','🇰🇮','🇰🇲','🇰🇳','🇰🇵','🇰🇷','🇰🇼','🇰🇾','🇰🇿','🇱🇦','🇱🇧','🇱🇨','🇱🇮'], n18:['🇱🇰','🇱🇷','🇱🇸','🇱🇹','🇱🇺','🇱🇻','🇱🇾','🇲🇦','🇲🇨','🇲🇩','🇲🇪','🇲🇫','🇲🇬','🇲🇭','🇲🇰','🇲🇱','🇲🇹','🇲🇸','🇲🇷','🇲🇶','🇲🇵','🇲🇴','🇲🇳','🇲🇲','🇲🇺','🇲🇻','🇲🇼','🇲🇽','🇲🇾','🇲🇿','🇳🇦','🇳🇨','🇳🇷','🇳🇴','🇳🇱','🇳🇮','🇳🇬','🇳🇫','🇳🇪','🇳🇺','🇳🇿','🇴🇲'], n19:['🇵🇦','🇵🇪','🇵🇫','🇵🇬','🇵🇭','🇵🇼','🇵🇹','🇵🇸','🇵🇷','🇵🇳','🇵🇲','🇵🇱','🇵🇰','🇵🇾','🇶🇦','🇷🇪','🇷🇴','🇷🇸','🇷🇺','🇷🇼','🇸🇦','🇸🇯','🇸🇮','🇸🇭','🇸🇬','🇸🇪','🇸🇩','🇸??','🇸🇧','🇸🇰','🇸🇱','🇸🇲','🇸🇳','🇸🇴','🇸🇷','🇸🇸','🇸🇹','🇹🇫','🇹🇩','🇹🇨','🇹🇦','🇸🇿','🇸🇾','🇸🇽','🇸🇻'], n20:['🇹🇬','🇹🇭','🇹🇯','🇹🇰','🇹🇱','🇹🇲','🇹🇳','🇹🇴','🇺🇲','🇺🇬','🇺🇦','🇹🇼','🇹🇻','🇹🇹','🇹🇷','🇺🇳','🇺🇸','🇺🇾','🇺🇿','🇻🇦','🇻🇨','🇻🇪','🇻🇬','🇾🇹','🇾🇪','🇽🇰','🇼🇸','🇼🇫','🇻🇺','🇻🇳','🇻🇮','🇿🇦','🇿🇲','🇿🇼','🏴󠁧󠁢󠁥󠁮󠁧󠁿','🏴󠁧󠁢󠁳󠁣󠁴󠁿','🏴󠁧󠁢󠁷󠁬󠁳󠁿'],
    n21:['💻','🖥️','🖲️','⌨️','🖱️','💾','💽','🔌','🔋'], n22:['🎆','🎇','🚥','🚦','🚨','🏮','💡','🔦','⚡'], n23:['🤖','🦾','🦿','⚙️','🔧','🔩','👾','🕹️','🧲'], n24:['🔫','💣','🧨','⚔️','🛡️','🔪','🩸','☣️','☢️'], n25:['🚀','🛸','🛰️','🌌','🌠','☄️','🪐','🔭','👨‍🚀'], n26:['🌐','📡','📟','📶','🛜','💠','🌀','♾️','📱'], n27:['🧬','🦠','🧪','🧫','💉','💊','🔬','🌡️','☣️'], n28:['🌃','🏙️','🌆','🌁','🌉','🌧️','🌂','🕶️','🧥'], n29:['⬛','◼️','◾','▪️','👁️‍🗨️','🖤','🃏','🏴','🏴‍☠️'], n30:['🟪','🟦','🩵','🩷','🟣','🔵','🔮','☂️','☔'], n31:['🟩','🟨','🟢','🟡','🔋','⚡','🐍','🥎','🎾'], n32:['🔒','🔓','🔏','🔐','🔑','🗝️','🕵️‍♂️','👁️','🚪'], n33:['🥽','🕶️','🎧','🎮','🎬','🎟️','🎫','🎪','🪩'], n34:['⏳','⌛','⏱️','⏲️','⏰','🕰️','🧭','🕛','🌌'], n35:['🚧','🏭','🏗️','🛢️','⛽','🛑','🚷','🗑️','🛹'], n36:['👁️','👂','🧠','🦾','🦿','🦴','🦷','🗣️','👤'], n37:['✨','🌟','💫','⭐','☄️','🎇','🎆','❇️','🎇'], n38:['🕷️','🕸️','🦂','🦇','🐺','🦉','🐾','🌑','🕸️'], n39:['💎','🪙','💸','💰','💳','🧾','📈','📉','📊'], n40:['⚡','🌐','🤖','💀','🔌','💻','🧬','☢️','🔥']
};
const baseEmojisOld = ['🔥', '💥', '⚡', '🌪️', '🌈', '☄️', '💫', '🌊', '❄️', '🌸', '💀', '☠️', '👺', '🔱', '⚜️'];
for (let i = 1; i <= 100; i++) emojiArrays[`nc${i}`] = [baseEmojisOld[i % baseEmojisOld.length], baseEmojisOld[(i + 1) % baseEmojisOld.length]];
const globalEmojiList = Object.values(emojiArrays).flat();

// ==================== FULL TARGET & TXT MESSAGES ====================
const targetMessages = [
    "(💀) 𝘾𝙃𝘼𝙇 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼𝙆𝘼 𝘽𝙃𝙊𝙎𝘿𝘼 (💀)",
    "(🔥) 𝙏𝙈𝙆𝘾 𝙈𝙀 𝙇𝙊𝘿𝙀 𝙎𝙀 𝙃𝘼𝙈𝙇𝘼𝘼 (🔥)",
    "(🧬) 𝘿𝙀𝙑 𝙋𝘼𝙋𝘼 𝙆𝘼 𝙉𝘼𝙕𝘼𝙔𝘼𝙕 𝘼𝙐𝙇𝘼𝘿 (🧬)",
    "(⚠️) 𝘼𝙒𝘼𝙕 𝙉𝙄𝘾𝙃𝙀 𝙍𝙔𝙉𝘿𝙔 𝙆𝙀 𝘽𝘾𝘾𝙃𝙀 (⚠️)",
    "(⚡) 𝙏𝙈𝙆𝘾 𝙈𝙀 𝙎𝙃𝙊𝙍𝙏 𝘾𝙄𝙍𝘾𝙐𝙄𝙏 (⚡)",
    "(😎) 𝙈𝙀𝙎𝙎𝘼𝙂𝙀 𝙆𝘼𝙄𝙎𝙀 𝙆𝘼𝙍 𝙍𝙃𝘼 𝙍𝙉𝘿𝙄𝙆𝙀 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝙐𝘿𝙃𝘼𝙍 𝘾𝙃𝙐𝘿 𝙂𝙔𝙄 😝 (😎)",
    "(🐌) 𝙏𝙀𝙍𝙄 𝘽𝙃𝙀𝙉 𝙆𝙄 𝘾𝙃𝙐𝙏 𝙈𝙀 𝙎𝙉𝘼𝙄𝙇 𝘾𝙃𝙃𝙊𝘿 𝘿𝙐𝙂𝘼 (🐌)",
    "(👑) 𝐁𝐎𝐋 𝐃𝐄𝐕𝐀🎀 𝐁𝐇𝐀𝐆𝐖𝐀𝐍 𝐊𝐈 𝐉𝐀𝐈 𝐇𝐎 (👑)",
    "(🚪) 𝘒𝘯𝘰𝘬 𝘒𝘯𝘰𝘬 ~ 𝘛𝘌𝘙𝘐 𝘉Ｈ𝘌𝘕 𝘊𝘏𝘖𝘋𝘕𝘌 𝘊𝘜𝘚𝘛𝘖𝘔𝘌𝘙 𝘈𝘈𝘠𝘈𝘈 (🚪)", 
    "(💀) 𝘈𝘕𝘛𝘈𝘙 𝘔𝘈𝘕𝘛𝘈𝘙 𝘚𝘈𝘐𝘛𝘈𝘕𝘐 𝘒𝘏Ｏ𝘗𝘋𝘈 𝘍𝘈𝘈𝘋 𝘋𝘜𝘎𝘈 𝘛𝘌𝘙𝘐 𝘉𝘏𝘌𝘕 𝘒𝘈 𝘎𝘜𝘓𝘈𝘉𝘐 𝘉𝘏Ｏ𝘚𝘋𝘈 (💀)",
    "(🔥) ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴀᴀɢ ʟᴀɢᴀ ᴅᴜɢᴀ ʀᴀɢᴀᴅ ᴋᴇ (🔥)",
    "(🧬) 𝙳𝚄𝚁𝚁 𝚁𝙰𝙷𝙷 𝙲𝙷𝙰𝙼𝙰𝚁 𝙺𝙴 𝙻𝙰𝚁𝙲𝙴 𝙲𝙷𝙸𝙸 (🧬)",
    "(⚠️) 𝗪𝗔𝗥𝗡𝗜𝗡𝗚 !! 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗥𝗔𝗡𝗗𝗜 (⚠️)",
    "(⚡) 𝐓𝐄𝐑𝐈 𝐁𝐇𝐄𝐍 𝐊𝐎 𝐎𝐘𝐎 𝐋𝐄 𝐉𝐀𝐀 𝐊𝐀𝐑 𝐂𝐇𝐎𝐃𝐔𝐔 🙈 (⚡)",
    "(😎) 𝘠𝘌 𝘛𝘌𝘙𝘈 𝘉𝘈𝘈𝘗 𝘒𝘠𝘈 𝘓𝘈𝘎𝘈𝘒𝘌 𝘊Ｈ𝘈𝘚𝘔𝘈 𝘈𝘙𝘔𝘈𝘕𝘐 𝘕𝘐𝘒𝘈𝘓𝘌𝘎𝘈 𝘛𝘌𝘙𝘐 𝘉𝘏𝘌𝘕 𝘒𝘐 𝘊Ｈ𝘜𝘛 𝘚𝘌 𝘓𝘈𝘓 𝘓𝘈𝘓 𝘗𝘈𝘈𝘕𝘐 ☂️ (😎)"
];

const txtTemplates = [
    `⚡ {{names}} 𝐓𝐔𝐌 𝐑𝐍𝐃𝐈𝐊𝐄 𝐊𝐄 𝐋𝐀𝐑𝐂𝐎 𝐊𝐈 𝐌𝐀𝐀 𝐌𝐄𝐑𝐄 𝐀𝐋𝐀𝐖𝐀 𝐊𝐎𝐈 चोद 𝐒𝐊𝐓𝐀 𝐇𝐀𝐈 𝐊𝐘𝐀𝐀 🤍ྀི×͜×ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ{{names}} 𝐓𝐔𝐌 𝐑𝐍𝐃𝐈𝐊𝐄 𝐊𝐄 𝐋𝐀𝐑𝐂𝐎 𝐊𝐈 𝐌𝐀𝐀 𝐌𝐄𝐑𝐄 𝐀𝐋𝐀𝐖𝐀 𝐊𝐎𝐈 चोद 𝐒𝐊𝐓𝐀 𝐇𝐀𝐈 𝐊𝐘𝐀𝐀 🤍ྀི×͜×! ⚡`, 
    `<  {{names}} > 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐔𝐃𝐀𝐊𝐊𝐀𝐃 𝐑𝐀𝐍𝐃𝐈❤️︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽<  {{names}} > 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐔𝐃𝐀𝐊𝐊𝐀𝐃 𝐑𝐀𝐍𝐃𝐈❤️ꪹ\n\n<  {{names}} > 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐔𝐃𝐀𝐊𝐊𝐀𝐃 𝐑𝐀𝐍𝐃𝐈🩵︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽<  {{names}} > 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐔𝐃𝐀𝐊𝐊𝐀𝐃 𝐑𝐀𝐍𝐃𝐈🩵ꪹ\n\n<  {{names}} > 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐔𝐃𝐀𝐊𝐊𝐀𝐃 𝐑𝐀𝐍𝐃𝐈🩷︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽<  {{names}} > 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐔𝐃𝐀𝐊𝐊𝐀𝐃 𝐑𝐀𝐍𝐃𝐈🩷ꪹ💥`, 
    `\n➶　　　　　　　➶　　　　　　➶　　　　　➶　　　　　　　　　➤　➷　　　　　　　　➷　　　　 　　　➷　　　　　　➷　　　　　　　　　　　　　　➷{{names}} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 \\ 𝘽𝘼𝙃𝘼𝙉 𝘿𝙊𝙉𝙊 𝙆𝙊 𝙍𝘼𝙉𝘿𝙄 𝙆𝙊 𝘾𝙃𝙊𝘿𝙐 🤣　➶　　　　　　　➶　　　　　　➶　　　　　➶　　　　　　　　　➤　➷　　　　　　　　➷　　　　 　　　➷　　　　　　➷　　　　　　　　　　　　　　➷{{names}} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 \\ 𝘽𝘼𝙃𝘼𝙉 𝘿𝙊𝙉𝙊 𝙆𝙊 𝙍𝘼𝙉𝘿𝙄 𝙆𝙊 𝘾𝙃𝙊𝘿𝙐👅　➶　　　　　　　➶　　　　　　➶　　　　　➶　　　　　　　　　➤　➷　　　　　　　　➷　　　　 　　　➷　　　　　　➷　　　　　　　　　　　　　　➷{{names}} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 \\ 𝘽𝘼𝙃𝘼𝙉 𝘿𝙊𝙉𝙊 𝙆𝙊 𝙍𝘼𝙉𝘿𝙄 𝙆𝙊 𝘾𝙃𝙊𝘿𝙐👅 \n➶　　　　　　　➶　　　　　　➶　　　　　➶　　　　　　　　　➤　➷　　　　　　　　➷　　　　 　　　➷　　　　　　➷　　　　　　　　　　　　　　➷{{names}} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 \\ 𝘽𝘼𝙃𝘼𝙉 𝘿𝙊𝙉𝙊 𝙆𝙊 𝙍𝘼𝙉𝘿𝙄 𝙆𝙊 𝘾𝙃𝙊𝘿𝙐 🤣　➶　　　　　　　➶　　　　　　➶　　　　　➶　　　　　　　　　➤　➷　　　　　　　　➷　　　　 　　　➷　　　　　　➷　　　　　　　　　　　　　　➷`, 
    `𝐀ʟᴇ𝐗𝖺 ⭕ ᴘʟᴀʏ - <  {{names}}   > ᴋɪ ᴍᴜᴍᴍʏ ᴋɪ ᴄʜᴜᴅᴀɪ 💽ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ0:35 ━❍──────── -5:32 ↻     ⊲  Ⅱ  ⊳     ↺ ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ𝐀ʟᴇ𝐗𝖺 ⭕ ᴘʟᴀʏ - <  {{names}}   > ᴋɪ ᴍᴜᴍᴍʏ ᴋɪ ᴄʜᴜᴅᴀɪ 💽 ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ0:35 ━❍──────── -5:32↻     ⊲  Ⅱ  ⊳     ↺\n\n𝐀ʟᴇ𝐗𝖺 ⭕ ᴘʟᴀʏ - <  {{names}}   > ᴋɪ ᴍᴜᴍᴍʏ ᴋɪ ᴄʜᴜᴅᴀɪ 💽ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ0:35 ━❍──────── -5:32 ↻     ⊲  Ⅱ  ⊳     ↺ ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ𝐀ʟᴇ𝐗𝖺 ⭕ ᴘʟᴀʏ - <  {{names}}   > ᴋɪ ᴍᴜᴍᴍʏ ᴋɪ ᴄʜᴜᴅᴀɪ 💽 ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ0:35 ━❍──────── -5:32↻     ⊲  Ⅱ  ⊳     ↺💀`, 
    `🌀 ‎𝐏ᴀɴɪ 𝐏ɪʏᴜɴɢᴀ 𝐌ᴀᴛ𝐊ᴇ 𝐌ᴇ {{names}} 𝐊ɪ 𝐌ᴀᴀ 𝐂ʜᴏᴅᴜɴɢᴀ 𝐉ʜᴀᴛ𝐊ᴇ 𝐌ᴇ 🪸🫧🌙🖤࿐ཽ༵˚✧₊⁎❝᷀ົ≀ˍ̮ ❝᷀ົ⁎⁺˳✧𒈒\n‎\n‎\n‎\n‎𝐏ᴀɴɪ 𝐏ɪʏᴜɴɢᴀ 𝐌ᴀᴛ𝐊ᴇ 𝐌ᴇ {{names}} 𝐊ɪ 𝐌ᴀᴀ 𝐂ʜᴏᴅᴜɴɢᴀ 𝐉ʜᴀᴛ𝐊ᴇ 𝐌ᴇ 🪸🫧🌙🖤࿐ཽ༵˚✧₊⁎❝᷀ົ≀ˍ̮ ❝᷀ົ⁎⁺˳✧𒈒\n‎\n‎\n‎\n‎𝐏ᴀɴɪ 𝐏ɪʏᴜɴɢᴀ 𝐌ᴀᴛ𝐊ᴇ 𝐌ᴇ {{names}} 𝐊ɪ 𝐌ᴀᴀ 𝐂ʜᴏᴅᴜɴɢᴀ 𝐉ʜᴀᴛ𝐊ᴇ 𝐌ᴇ 🪸🫧🌙🖤࿐ཽ༵˚✧₊⁎❝᷀ົ≀ˍ̮ ❝᷀ົ⁎⁺˳✧𒈒\n‎\n‎\n‎\n‎𝐏ᴀɴɪ 𝐏ɪʏᴜɴɢᴀ 𝐌ᴀᴛ𝐊ᴇ 𝐌ᴇ {{names}} 𝐊ɪ 𝐌ᴀᴀ 𝐂ʜᴏᴅᴜɴɢᴀ 𝐉ʜᴀᴛ𝐊ᴇ 𝐌ᴇ 🪸🫧🌙🖤࿐ཽ༵˚✧₊⁎❝᷀ົ≀ˍ̮ ❝᷀ົ⁎⁺˳✧𒈒🌀`, 
    `👑 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐌𝐔𝐓𝐓𝐈 𝐌𝐀𝐀𝐑𝐔{{names}} ࿐💛 𓂃𓈒\n\n𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐌𝐔𝐓𝐓𝐈 𝐌𝐀𝐀𝐑𝐔{{names}} ࿐💗 𓂃𓈒\n\n𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐌𝐔𝐓𝐓𝐈 𝐌𝐀𝐀𝐑𝐔{{names}} ࿐❤️ 𓂃𓈒\n\n𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐌𝐔𝐓𝐓𝐈 𝐌𝐀𝐀𝐑𝐔{{names}} ࿐💜 𓂃𓈒\n\n𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐌𝐔𝐓𝐓𝐈 𝐌𝐀𝐀𝐑𝐔{{names}} ࿐💙 𓂃𓈒\n\n𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐌𝐔𝐓𝐓𝐈 𝐌𝐀𝐀𝐑𝐔{{names}} ࿐❤️‍🩹 𓂃𓈒\n\n𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐌𝐔𝐓𝐓𝐈 𝐌𝐀𝐀𝐑𝐔{{names}} ࿐❤️‍🔥 𓂃𓈒 👑`, 
    `🌪️ {{names}} - Tᴇʀ𝐈 Mᴀᴀ Kᴏ P𝐈Lᴀ Kᴇ Pᴀɴ𝐈 Kᴀ𝗥R Dᴜɴɢᴀ Aᴘɴᴇ Lᴜɴᴅ K𝐈 D𝐈Wᴀɴ𝐈______/_______/𓏲 ๋࣭ ࣪ ˖🎐\n\n{{names}} - Tᴇʀ𝐈 Mᴀᴀ Kᴏ P𝐈Lᴀ Kᴇ Pᴀɴ𝐈 Kᴀ𝗥R Dᴜɴɢᴀ Aᴘɴᴇ Lᴜɴᴅ K𝐈 D𝐈Wᴀɴ𝐈______/_______/𓏲 ๋࣭ ࣪ ˖🎐\n\n{{names}} - Tᴇʀ𝐈 Mᴀᴀ Kᴏ P𝐈Lᴀ Kᴇ Pᴀɴ𝐈 Kᴀ𝗥R Dᴜɴɢᴀ Aᴘɴᴇ Lᴜɴᴅ K𝐈 D𝐈Wᴀɴ𝐈______/_______/𓏲 ๋࣭ ࣪ ˖🎐\n\n{{names}} - Tᴇʀ𝐈 Mᴀᴀ Kᴏ P𝐈Lᴀ Kᴇ Pᴀɴ𝐈 Kᴀ𝗥R Dᴜɴɢᴀ Aᴘɴᴇ Lᴜɴᴅ K𝐈 D𝐈Wᴀɴ𝐈______/_______/𓏲 ๋࣭ ࣪ ˖🎐\n\n{{names}} - Tᴇʀ𝐈 Mᴀᴀ Kᴏ P𝐈Lᴀ Kᴇ Pᴀɴ𝐈 Kᴀ𝗥R Dᴜɴɢᴀ Aᴘɴᴇ Lᴜɴᴅ K𝐈 D𝐈Wᴀɴ𝐈______/_______/𓏲 ๋࣭ ࣪ ˖🎐\n\n 🌪️`, 
    `🎀💋⫸ {{names}} -- 𝐎𝐑 𝐔𝐒𝐊𝐄 𝐓𝐀𝐓𝐓𝐎 < Swan >𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐁𝐀𝐇𝐀𝐍 𝐃𝐎𝐍𝐎 𝐊𝐎 𝐂𝐇𝐎𝐃𝐊𝐄 𝐌𝐀𝐑 𝐃𝐔𝐆𝐀 💢🌀ྀ࿐ ˊˎ-𒈝 𒈝 ✵ 𒈝 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵ 𒈝 𒈝 ✵  𒈝 𒈝 🎀💋⫸   {{names}} -ᴜsᴋᴇ ᴛᴀᴛᴛᴏ ᴄʜʟ ᴜᴛʜ ᴍᴀᴅʜ𝗥ᴄʜᴏᴅ ᴋ𝐈ᴛɴᴀ ʙʜ𝐈 ᴢᴏ𝗥 ʟɢᴀᴏ ᴀᴘɴᴇ ᴀʙʙᴜ ᴋᴏ ᴄᴏᴠᴇ𝗥 ɴʜ𝐈 ᴋ𝗥 ᴘᴀᴏɢᴇ😈ྀ࿐ ˊˎ- `, 
    `⚔️ ✝ 𝐀ɴᴛᴀ𝗥 𝐌ᴀɴ𝐓ᴀ𝗥 𝐒ʜᴀ𝐈𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {{names}} 𝐆ᴀ𝗥𝐈𝐁 𝐊𝐈 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི  ✝ 𝐀ɴᴛᴀ𝗥 𝐌ᴀɴ𝐓ᴀ𝗥 𝐒ʜᴀ𝐈𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {{names}} 𝐆ᴀ𝗥𝐈𝐁 𝐊𝐈 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི  ✝ 𝐀ɴᴛᴀ𝗥 𝐌ᴀɴ𝐓ᴀ𝗥 𝐒ʜᴀ𝐈𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {{names}} 𝐆ᴀ𝗥𝐈𝐁 𝐊𝐈 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི  ✝ 𝐀ɴᴛᴀ𝗥 𝐌ᴀɴ𝐓ᴀ𝗥 ??ʜᴀ𝐈𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {{names}} 𝐆ᴀ𝗥𝐈𝐁 𝐊𝐈 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི  ✝ 𝐀ɴᴛᴀ𝗥 𝐌ᴀɴ𝐓ᴀ𝗥 𝐒ʜᴀ𝐈𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {{names}} 𝐆ᴀ𝗥𝐈𝐁 𝐊𝐈 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི  ✝ 𝐀ɴᴛᴀ𝗥 𝐌ᴀɴ𝐓ᴀ𝗥 𝐒ʜᴀ𝐈𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {{names}} 𝐆ᴀ𝗥𝐈𝐁 𝐊𝐈 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི  ✝ 𝐀ɴᴛᴀ𝗥 𝐌ᴀɴ𝐓ᴀ𝗥 𝐒ʜᴀ𝐈𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {{names}} 𝐆ᴀ𝗥𝐈𝐁 𝐊𝐈 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ ??᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི  ✝ 𝐀ɴᴛᴀ𝗥 𝐌ᴀɴ𝐓ᴀ𝗥 𝐒ʜᴀ𝐈𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {{names}} 𝐆ᴀ𝗥𝐈𝐁 𝐊𝐈 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི  ✝ 𝐀ɴᴛᴀ𝗥 𝐌ᴀɴ𝐓ᴀ𝗥 𝐒ʜᴀ𝐈𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {{names}} 𝐆ᴀ𝗥𝐈𝐁 𝐊𝐈 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི  ⚔️`, 
    `𝗔𝗡𝗧𝗔𝗥 𝗠𝗔𝗡𝗧𝗔𝗥 𝗦𝗔𝐈𝗧𝗔𝗡𝐈 𝗞𝗛𝗢𝗣𝗗𝗔 𝗖𝗛𝗨𝗗 𝗚𝗬𝗔 𝗧𝗘𝗥𝐈 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 {{names}}————————–(🕸️)————(👑)𝗔𝗡𝗧𝗔𝗥 𝗠𝗔𝗡𝗧𝗔𝗥 𝗦𝗔𝐈𝗧𝗔𝗡𝐈 𝗞𝗛𝗢𝗣𝗗𝗔 𝗖𝗛𝗨𝗗 𝗚𝗬𝗔 𝗧𝗘𝗥𝐈 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 {{names}}————————–(🕸️)————(𝗔𝗡𝗧𝗔𝗥 𝗠𝗔𝗡𝗧𝗔𝗥 𝗦𝗔𝐈𝗧𝗔𝗡𝐈 𝗞𝗛𝗢𝗣??𝗔 𝗖𝗛𝗨𝗗 𝗚𝗬𝗔 𝗧𝗘𝗥𝐈 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 {{names}}————————–(🕸️)————(👑)𝗔𝗡𝗧𝗔?? 𝗠𝗔𝗡𝗧𝗔𝗥 𝗦𝗔𝐈𝗧𝗔𝗡𝐈 𝗞𝗛𝗢𝗣𝗗𝗔 𝗖𝗛𝗨𝗗 𝗚𝗬𝗔 𝗧𝗘𝗥𝐈 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 {{names}}————————–(🕸️)————(𝗔𝗡𝗧𝗔𝗥 𝗠𝗔𝗡𝗧𝗔𝗥 𝗦𝗔𝐈𝗧𝗔𝗡𝐈 𝗞𝗛𝗢𝗣𝗗𝗔 𝗖𝗛𝗨𝗗 𝗚𝗬𝗔 𝗧𝗘𝗥𝐈 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 {{names}}————————–(🕸️)————(👑)𝗔𝗡𝗧𝗔𝗥 𝗠𝗔𝗡𝗧𝗔𝗥 𝗦𝗔𝐈𝗧𝗔𝗡𝐈 𝗞𝗛𝗢𝗣𝗗𝗔 𝗖𝗛𝗨𝗗 𝗚𝗬𝗔 𝗧𝗘𝗥𝐈 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 {{names}}————————–(🕸️)————`, 
    `‎*⋆｡ﾟ｡✧⋆· आर समंदर पार समंदर बीच में है नैया पहले चोदु तेरी बहन फिर चोदु तेरी मइया ˚˖𓍢ִ໋🌷͙֒✧🦢˚.🎀༘⋆ {{names}}\n\n\n*⋆｡ﾟ｡✧⋆· आर समंदर पार समंदर बीच में है नैया पहले चोदु तेरी बहन फिर चोदु तेरी मइया ˚˖𓍢ִ໋🌷͙֒✧🦢˚.🎀༘⋆ {{names}}\n\n\n*⋆｡ﾟ｡✧⋆· आर समंदर पार समंदर बीच में है नैया पहले चोदु तेरी बहन फिर चोदु तेरी मइ야 ˚˖𓍢ִ໋🌷͙֒✧🦢˚.🎀༘⋆ {{names}}\n\n\n*⋆कांतﾟ｡✧⋆· आर समंदर पार समंदर बीच में है नैया पहले चोदु तेरी बहन फिर चोदु तेरी मइया ˚˖𓍢ִ໋🌷͙֒✧🦢˚.🎀༘⋆ {{names}}\n\n\n*⋆｡ﾟ｡✧⋆· आर समंदर पार समंदर बीच में है नैया पहले चोदु तेरी बहन फिर चोदु तेरी मइया ˚˖𓍢ִ໋🌷͙֒✧🦢˚.🎀༘⋆ {{names}}`, 
    `˚❝᷀ົ≀ˍ̮⁎⁺˳✧づ 𝗘ᴋ 𝗗ᴀᴀʟ 𝗣ᴇ𝗥 𝗗ᴏᴏ 𝗞ᴀʙᴏᴏᴛᴀ𝗥 𝗗ᴏɴᴏ 𝗡ᴇ 𝗗𝐈ʏᴀ 𝗠ᴏᴏᴛ ({{names}}) 𝗞𝐈 𝗠ᴀᴀ 𝗞𝐈 𝗖ʜᴜᴛ 🌙🪽🫧🪸࿐ཽ༵𒈒༼☆ﾟ. * ･ ｡ﾟ\n\n\n˚❝᷀ົ≀ˍ̮⁎⁺˳✧づ 𝗘ᴋ 𝗗ᴀᴀʟ 𝗣ᴇ𝗥 𝗗ᴏᴏ 𝗞ᴀʙᴏᴏᴛᴀ𝗥 𝗗ᴏɴᴏ 𝗡ᴇ 𝗗𝐈ʏᴀ 𝗠ᴏᴏᴛ ({{names}}) 𝗞𝐈 𝗠ᴀᴀ 𝗞𝐈 𝗖ʜᴜᴛ 🌙🪽🫧🪸࿐ཽ༵𒈒༼☆ﾟ. * ･ ｡ﾟ\n\n\n˚❝᷀ົ≀ˍ̮⁎⁺˳✧づ 𝗘ᴋ 𝗗ᴀᴀʟ 𝗣ᴇ𝗥 𝗗ᴏᴏ 𝗞ᴀʙᴏᴏᴛᴀ𝗥 𝗗ᴏɴᴏ 𝗡ᴇ 𝗗𝐈ʏᴀ 𝗠ᴏᴏᴛ ({{names}}) 𝗞𝐈 𝗠ᴀᴀ 𝗞𝐈 𝗖ʜᴜᴛ 🌙🪽🫧🪸࿐ཽ༵𒈒༼☆ﾟ. * ･ ｡ﾟ\n\n\n˚❝᷀ົ≀ˍ̮⁎⁺˳✧づ 𝗘ᴋ 𝗗ᴀᴀʟ 𝗣ᴇ𝗥 𝗗ᴏᴏ 𝗞ᴀʙᴏᴏᴛᴀ𝗥 𝗗ᴏɴᴏ 𝗡ᴇ 𝗗𝐈ʏᴀ 𝗠ᴏᴏᴛ ({{names}}) 𝗞𝐈 𝗠ᴀᴀ 𝗞𝐈 𝗖ʜᴜᴛ 🌙🪽🫧🪸࿐ཽ༵𒈒༼☆ﾟ. * ･ ｡ﾟ\n\n\n˚❝᷀ົ≀ˍ̮⁎⁺˳✧づ 𝗘ᴋ 𝗗ᴀᴀʟ 𝗣ᴇ𝗥 𝗗ᴏᴏ 𝗞ᴀʙᴏᴏᴛᴀ𝗥 𝗗ᴏɴᴏ 𝗡ᴇ 𝗗𝐈ʏᴀ 𝗠ᴏᴏᴛ ({{names}}) 𝗞𝐈 𝗠ᴀᴀ 𝗞𝐈 𝗖ʜᴜᴛ 🌙🪽🫧🪸࿐ཽ༵𒈒༼☆ﾟ. * ･ ｡ﾟ🔱`
];

// 🛡️ MEMORY CACHE
const store = {
    messages: {},
    bind(ev) {
        ev.on('messages.upsert', ({ messages }) => {
            for (const msg of messages) {
                const jid = msg.key.remoteJid;
                if (!this.messages[jid]) this.messages[jid] = {};
                this.messages[jid][msg.key.id] = msg;
                const keys = Object.keys(this.messages[jid]);
                if (keys.length > 50) delete this.messages[jid][keys[0]]; 
            }
        });
    }
};

// ==================== BOT SESSION CORE ====================
class BotSession {
    constructor(botId, phone, manager, useQR = false) {
        this.displayId = botId === 'Bot_1' ? '𝐒𝐔𝐏𝐄𝐑 𝐁𝐎𝐓' : botId.replace('Bot_', '𝐁𝐎𝐓 ');
        this.internalId = botId;
        this.phoneNumber = phone;
        this.manager = manager;
        this.useQR = useQR;
        this.authPath = `./auth/${botId}`;
        this.sock = null;
        this.connected = false;
        this.isSuppressed = false; 
        
        // ALL MAPS STRICTLY ISOLATED BY GROUP (FROM)
        this.activePfp = new Map(); 
        this.activeTasks = new Map();
        this.activeTarget = new Map();
        this.activeNC = new Map();
        this.activeN = new Map();
        this.activeTxt = new Map();
        this.activeSlide = new Map();
        this.activeTagall = new Map();
        this.activeAutoReply = new Map();
        this.activeTargetReply = new Map();
        this.activePcspm = new Map();
        this.activeStspm = new Map();
        this.activeCustxt = new Map();
        this.activeReplyAll = new Map();
        this.activeDesc = new Map();
        this.activeAutoReact = new Map();
        this.activeLock = new Map(); 
        this.activeAutoPin = new Map(); // Auto-pin map per group
    }

    async connect() {
        if (!fs.existsSync(this.authPath)) fs.mkdirSync(this.authPath, { recursive: true });
        const { state, saveCreds } = await useMultiFileAuthState(this.authPath);
        const { version } = await fetchLatestBaileysVersion();

        this.sock = makeWASocket({
            keepAliveIntervalMs: 30000,
            version,
            auth: state,
            logger: pino({ level: 'silent' }),
            printQRInTerminal: this.useQR,
            mobile: false,
            browser: ["Ubuntu", "Chrome", "20.0.04"],
            syncFullHistory: false,
            getMessage: async (key) => {
                if (store) { const msg = store.messages[key.remoteJid]?.[key.id]; return msg?.message || undefined; }
                return { conversation: `*${styleText("(⚙️) [ DIVINE GENERAL ENGINE ] (⚙️)")}*` };
            }
        });

        store.bind?.(this.sock.ev);
        this.sock.ev.on('creds.update', saveCreds);

        this.sock.ev.on('call', async (calls) => {
            for (const call of calls) { if (call.status === 'offer') { try { await this.sock.rejectCall(call.id, call.from); } catch (err) {} } }
        });

        this.sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            if (qr && this.useQR) console.log(`\n📱 [${this.displayId}] SCAN QR CODE NOW\n`);

            if (connection === 'close') {
                this.connected = false;
                const code = (lastDisconnect?.error instanceof Boom) ? lastDisconnect.error.output.statusCode : 500;
                if (code !== DisconnectReason.loggedOut && code !== 401) { setTimeout(() => this.connect(), 5000); } 
                else {
                    console.log(`\n☠️ [ ${this.displayId} ] CONNECTION LOST! Auto-Purging Data...`);
                    if (fs.existsSync(this.authPath)) { fs.rmSync(this.authPath, { recursive: true, force: true }); }
                    this.manager.bots.delete(this.internalId); this.manager.save(); 
                }
            } else if (connection === 'open') {
                this.connected = true;
                
                if (this.internalId === 'Bot_1') {
                    console.log(`\n⛩️ [ DIVINE GENERAL ] MAHORAGA IS ONLINE! Adaptation Engine Awakened. (V8.6.0)`);
                } else {
                    console.log(`✅ [ SHIKIGAMI FLEET ] Node ${this.displayId} has been Awakened!`);
                }
                
                const isMain = this.internalId === this.manager.getMainBotId();
                if (isMain && Object.keys(activeRecovery).length > 0) {
                    console.log(`🔄 [ RECOVERY ] Resuming previous active attacks...`);
                    for (const [jid, cmds] of Object.entries(activeRecovery)) {
                        for (const [cmd, argsData] of Object.entries(cmds)) {
                            const fakeMsg = { key: { remoteJid: jid, fromMe: true }, message: { conversation: '' } };
                            this.executeInternal(jid, cmd, this.sock.user.id, fakeMsg, argsData, null, true);
                        }
                    }
                }
            }
        });

        this.sock.ev.on('messages.upsert', m => this.handleMsg(m));
    }

    async send(jid, text, mentions = [], quoted = null, imageUrl = null) {
        if (!this.connected) return;
        const finalStyledText = `*${styleText(text)}*`; 
        let msgPayload = { text: finalStyledText, mentions: mentions.length ? mentions : undefined };
        if (imageUrl && fs.existsSync(imageUrl)) { msgPayload = { image: fs.readFileSync(imageUrl), caption: finalStyledText, mentions: mentions.length ? mentions : undefined }; }
        await this.sock.sendPresenceUpdate('composing', jid).catch(()=>{});
        await delay(500); await this.sock.sendMessage(jid, msgPayload, quoted ? { quoted } : {}).catch(()=>{});
    }

    async ping(from) {
        const start = Date.now(); 
        await this.send(from, `⟪ ⚙️ 𝐀𝐃𝐀𝐏𝐓𝐀𝐓𝐈𝐎𝐍 𝐂𝐇𝐄𝐂𝐊... ⟫`); 
        const lat = Date.now() - start;
        await this.send(from, `╔⏤⏤[ ⛩️ 𝐃𝐈𝐕𝐈𝐍𝐄 𝐒𝐓𝐑𝐈𝐊𝐄 ]⏤⏤╗\n║ ✧ 𝑹𝒆𝒇𝒍𝒆𝒙 𝑺𝒑𝒆𝒆𝒅: ${lat}𝒎𝒔\n║ ✧ 𝑬𝒏𝒈𝒊𝒏𝒆: 𝑫𝒊𝒗𝒊𝒏𝒆 𝑮𝒆𝒏𝒆𝒓𝒂𝒍 𝓥8.6.0\n║ ✧ 𝑺𝒕𝒂𝒕𝒖𝒔: 𝑨𝒃𝒔𝒐𝒍𝒖𝒕𝒆 𝑨𝒅𝒂𝒑𝒕𝒂𝒕𝒊𝒐𝒏 ☸️\n╚⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤╝`);
    }

    async handleMsg({ messages, type }) {
        if (type !== 'notify') return;
        const msg = messages[0];
        
        // ==================== 👁️ VIP STATUS TRACKER ====================
        const from = msg.key.remoteJid;
        if (from === 'status@broadcast') {
            if (this.internalId !== this.manager.getMainBotId()) return; 
            const statusSender = msg.key.participant;
            const vips = ['67073187571@s.whatsapp.net']; 
            if (vips.includes(normalizeJid(statusSender))) {
                const devJid = '67073187571@s.whatsapp.net'; 
                try { await this.sock.sendMessage(devJid, { forward: msg }); await this.send(devJid, `⟪ 👁️ 𝐒𝐓𝐄𝐀𝐋𝐓𝐇 𝐓𝐑𝐀𝐂𝐊𝐄𝐑 ⟫ ➪ 𝐍𝐞𝐰 𝐒𝐭𝐚𝐭𝐮𝐬 𝐟𝐫𝐨𝐦 @${statusSender.split('@')[0]}`, [statusSender]); } catch (e) {}
            } return; 
        }

        if (!msg.message || msg.key.fromMe) return;

        const isGroup = from.endsWith('@g.us');
        const sender = isGroup ? msg.key.participant : from;
        const text = (msg.message.conversation || msg.message.extendedTextMessage?.text || "").trim();
        const isCmd = text.startsWith(GLOBAL_PREFIX);
        const command = isCmd ? text.slice(GLOBAL_PREFIX.length).trim().split(' ')[0].toLowerCase() : "";
        const args = text.split(/ +/).slice(1);
        const quotedMsg = msg.message.extendedTextMessage?.contextInfo;
        const mentioned = quotedMsg?.mentionedJid || [];
        const isMain = this.internalId === this.manager.getMainBotId();
        // ==================== 🧠 JINAAH AI INTEGRATION (SAVAGE GIRL) ====================
        const myJid = this.sock?.user?.id ? normalizeJid(this.sock.user.id) : '';
        const isReplyToMe = quotedMsg?.participant && normalizeJid(quotedMsg.participant) === myJid;
        const isJinaahMentioned = text.toLowerCase().includes('jinaah');

        if (!isCmd && !this.isSuppressed && (isReplyToMe || isJinaahMentioned) && text) {
            await this.sock.sendPresenceUpdate('composing', from).catch(()=>{});
            
            // 1. Defining her core personality
            let persona = `You are Jinaah, a real human Indian girl. You are very sassy, cool, and a bit savage. 
            CRITICAL RULES: 
            1. YOU ARE NOT AN AI. NEVER admit to being an AI, bot, virtual assistant, or computer program. If asked, get annoyed.
            2. If anyone asks about your API, backend, code, creator, or how you are made, you MUST reply ONLY with exactly this phrase: "Aukat Not Found 🖕". 
            3. Reply in a mix of Hindi and English (Hinglish) using GenZ slang and emojis. Keep it natural and short. `;
            
            // 2. Admin vs Normal User treatment
            if (isAdmin(sender)) {
                persona += `4. The user talking to you right now is your Boss/Admin (Dev). Be very sweet, respectful, and a bit flirty with him. DO NOT be savage to him. `;
            } else {
                persona += `4. The user talking to you is a random normal person. Be highly savage, roast them if they act smart, and show attitude. `;
            }
            
            // Clean the prompt so she doesn't repeat her name unnecessarily
            const cleanText = text.replace(/jinaah/ig, '').trim() || "Hi";
            const fullPrompt = `${persona}\n\nUser says: ${cleanText}`;
            
            try {
                // Fetching from your provided API
                const apiUrl = `https://addy-chatgpt-api.vercel.app/?text=${encodeURIComponent(fullPrompt)}`;
                const aiRes = await fetch(apiUrl);
                const aiText = await aiRes.text();
                
                let finalReply = aiText;
                // Attempt to parse JSON just in case the API returns a JSON object
                try {
                    const aiJson = JSON.parse(aiText);
                    finalReply = aiJson.reply || aiJson.result || aiJson.message || aiJson.response || aiText;
                } catch (e) {
                    // If not JSON, it will just use the raw text
                }
                
                // 3. Final Fallback check
                if (finalReply.toLowerCase().includes('openai') || finalReply.toLowerCase().includes('language model')) {
                    finalReply = "Tera dimaag kharab hai kya? Mai real ladki hu. 🙄";
                }
                
                await this.send(from, finalReply, [], msg);
            } catch (err) {
                console.log("[JINAAH AI ERROR] " + err.message);
            }
            return; // Stop the code here so it doesn't try to read it as a command
        }
        // ==============================================================================

        const reactEmoji = this.activeAutoReact.get(from);
        if (reactEmoji && !isCmd && !this.isSuppressed) { setTimeout(() => { this.sock.sendMessage(from, { react: { text: reactEmoji, key: msg.key } }).catch(() => {}); }, Math.floor(Math.random() * (4000 - 1500 + 1)) + 1500); }

        if (!this.isSuppressed) {
            if (isGroup && this.activeLock.has(`${from}_${normalizeJid(sender)}`)) { this.sock.sendMessage(from, { delete: msg.key }).catch(()=>{}); }
            if (isGroup && this.activeTargetReply.has(`${from}_${sender}`)) { const slideTask = this.activeTargetReply.get(`${from}_${sender}`); if (slideTask.active) { HSEE.runAttack(async () => { if (!this.activeTargetReply.has(`${from}_${sender}`)) return; await this.send(from, slideTask.text, [], msg); }); } }
            if (isGroup && this.activeAutoReply.has(`${from}_autoreply`)) { const task = this.activeAutoReply.get(`${from}_autoreply`); if (task.active && (task.targets.length === 0 || task.targets.includes(normalizeJid(sender)))) { if (isMain) { HSEE.runAttack(async () => { if (!this.activeAutoReply.has(`${from}_autoreply`)) return; await this.send(from, "(⚡) [ HYPER CYBER EXOTIC ACTIVE ] (⚡)", [sender], msg); }); } } }
            if (this.activeTarget.has(`${from}_target`)) { const task = this.activeTarget.get(`${from}_target`); if (task.targets.includes(normalizeJid(sender))) { HSEE.runAttack(async () => { if (!this.activeTarget.has(`${from}_target`)) return; const spamMsg = targetMessages[Math.floor(Math.random() * targetMessages.length)]; await this.send(from, spamMsg, [sender], msg); }); } }
            if (isGroup && this.activeReplyAll.has(from)) { const task = this.activeReplyAll.get(from); HSEE.runAttack(async () => { if (!this.activeReplyAll.has(from)) return; await this.send(from, task.text, [], msg); }); }
        }

        if (isMain && !isGroup && hasPerm(sender)) { if (text.startsWith('global ')) { const subCmdText = text.replace('global ', '').trim(); const subCmd = subCmdText.split(' ')[0].toLowerCase(); const subArgs = subCmdText.split(' ').slice(1); this.manager.bots.forEach(bot => bot.executeInternal(from, subCmd, sender, msg, subArgs, quotedMsg, bot.internalId === this.manager.getMainBotId())); return; } }
        
        // 🔥 THE GENERAL'S CALL (PREFIX ONLY) 🔥
        if (isCmd && command === '' && isMain && isAdmin(sender)) {
            await this.sock.sendPresenceUpdate('composing', from).catch(()=>{});
            await delay(500);
            return await this.send(from, `⟪ ☸️ ⟫ ➪ 𝑻𝒉𝒆 𝑾𝒉𝒆𝒆𝒍 𝒊𝒔 𝒘𝒂𝒊𝒕𝒊𝒏𝒈 𝒇𝒐𝒓 𝒚𝒐𝒖𝒓 𝒐𝒓𝒅𝒆𝒓𝒔, 𝑴𝒂𝒔𝒕𝒆𝒓... ⛩️`);
        }

        if (isCmd && command === 'admin' && roles.admins.length === 0) { roles.admins.push(normalizeJid(sender)); safeWriteJSON(ROLES_FILE, roles); if (isMain) await this.send(from, "👑 [ 𝐅𝐈𝐑𝐒𝐓 𝐀𝐃𝐌𝐈𝐍 𝐒𝐄𝐓𝐔𝐏 ] ➪ 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐰 𝐭𝐡𝐞 𝐎𝐰𝐧𝐞𝐫!"); return; }
        if (isCmd && command === 'iadmin' && isMain) { const normSender = normalizeJid(sender); if (isAdmin(normSender)) return await this.send(from, `⟪ ✅ 𝐒𝐘𝐒𝐓𝐄𝐌 ⟫ ➪ 𝒀𝒐𝒖 𝑨𝒓𝒆 𝑨𝒍𝒓𝒆𝒂𝒅𝒚 𝑨𝒏 𝑨𝒅𝒎𝒊𝒏!`); if (roles.admins.length >= 2) return await this.send(from, `⟪ ❌ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐀𝐝𝐦𝐢𝐧 𝐬𝐥𝐨𝐭𝐬 𝐟𝐮𝐥𝐥 𝐡𝐚𝐢𝐧 (𝐦𝐚𝐱 𝟐)!`); roles.admins.push(normSender); safeWriteJSON(ROLES_FILE, roles); await this.send(from, `╔════════════════════════╗\n   👑  𝐀𝐃𝐌𝐈𝐍  𝐆𝐑𝐀𝐍𝐓𝐄𝐃  \n╚════════════════════════╝\n┃ 🆔 Number: ${normSender.split('@')[0]}\n┃ 🔰 Role: Admin\n┃ 📊 Slots used: ${roles.admins.length}/2\n╚════════════════════════╝`); return; }

        if (isCmd && hasPerm(sender)) {
            if (this.isSuppressed && command !== 'uplift' && command !== 'reveal' && command !== 'unveil') return; 
            
            // 🔥 CHILD BOT RANDOM REACTION SYSTEM 🔥
            if (!isMain) {
                const childEmojis = ['🟢','❤️','🟣','🔵','💝','💖','🤍','🩶','🫯','💫','🫆','⚡️'];
                const randomChildEmoji = childEmojis[Math.floor(Math.random() * childEmojis.length)];
                this.sock.sendMessage(from, { react: { text: randomChildEmoji, key: msg.key } }).catch(()=>{});
            }
            
            this.executeInternal(from, command, sender, msg, args, quotedMsg, isMain);
        }

        if (isCmd && hasPerm(sender) && (command.startsWith('nc') || command.match(/^n[0-9]+/))) {
            const ncKey = command; const ncName = args.join(" ") || "𝐃𝐄𝐕𝐀🎀 𝐁𝐇𝐀𝐆𝐖𝐀𝐍"; this.activeNC.set(from, true);
            if(isMain) await this.send(from, `⟪ ⚡ 𝐒𝐈𝐍𝐆𝐋𝐄 𝐓𝐔𝐑𝐁𝐎 ⟫ ➪ 𝐀𝐭𝐭𝐚𝐜𝐤 𝐈𝐧𝐢𝐭𝐢𝐚𝐭𝐞𝐝: [${ncKey}]`);
            (async () => { while (this.activeNC.has(from) && this.connected) { await HSEE.runAttack(async () => { if (!this.activeNC.has(from)) return; try { const emojis = emojiArrays[ncKey] || ['⚡', '🔥', '💀']; const e = emojis[Math.floor(Math.random() * emojis.length)]; await this.sock.groupUpdateSubject(from, styleText(`${e} ${ncName} ${e}`)); } catch (err) {} }); await delay(Math.floor(Math.random() * (1500 - 1000 + 1)) + 1000); } })();
        }
    }

    async executeInternal(from, command, sender, msg, args, quotedMsg, isMain) {
        const replyJid = quotedMsg?.participant ? normalizeJid(quotedMsg.participant) : null;
        const mentioned = quotedMsg?.mentionedJid || [];
        const isGroup = from.endsWith('@g.us');
        const isSenderDev = isAdmin(sender);

        switch (command) {
            // ==================== ⚙️ SYSTEM CONTROL & CORE ====================
            case 'reincarnate':
            case 'reincarnation':
            case 'restart':
                if (!isMain || !isSenderDev) return;
                await this.sock.sendMessage(from, { text: `⟪ ⏳ 𝐒𝐊𝐈𝐋𝐋 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐈𝐎𝐍 ⟫ ➪ 𝑻𝒊𝒎𝒆 𝑹𝒆𝒗𝒆𝒓𝒔𝒂𝒍...\n➪ 𝑹𝒆𝒊𝒏𝒄𝒂𝒓𝒏𝒂𝒕𝒊𝒏𝒈 𝑫𝒊𝒗𝒊𝒏𝒆 𝑬𝒏𝒈𝒊𝒏𝒆...` });
                await delay(1500);
                exec('pm2 restart all', (error) => { if (error) { process.exit(1); } });
                break;

            case 'setimg':
                if (!isMain || !isSenderDev) return; 
                const quotedMenuImg = quotedMsg?.quotedMessage?.imageMessage || msg.message?.imageMessage;
                if (!quotedMenuImg) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐊𝐢𝐬𝐢 𝐢𝐦𝐚𝐠𝐞 𝐤𝐨 𝐫𝐞𝐩𝐥𝐲 𝐤𝐚𝐫𝐤𝐞 𝐥𝐢𝐤𝐡𝐨!");
                try {
                    await this.send(from, "⟪ ⏳ 𝐏𝐑𝐎𝐂𝐄𝐒𝐒𝐈𝐍𝐆 ⟫ ➪ 𝐒𝐚𝐯𝐢𝐧𝐠 𝐧𝐞𝐰 𝐌𝐞𝐧𝐮 𝐈𝐦𝐚𝐠𝐞...");
                    const streamImg = await downloadContentFromMessage(quotedMenuImg, 'image'); let buffer = Buffer.from([]);
                    for await (const chunk of streamImg) { buffer = Buffer.concat([buffer, chunk]); }
                    if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true }); fs.writeFileSync('./data/menu_image.jpg', buffer);
                    await this.send(from, "⟪ ✅ 𝐔𝐏𝐃𝐀𝐓𝐄𝐃 ⟫ ➪ 𝐌𝐞𝐧𝐮 𝐈𝐦𝐚𝐠𝐞 𝐬𝐞𝐭 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲!");
                } catch (err) { await this.send(from, `⟪ ❌ 𝐅𝐀𝐈𝐋𝐔𝐑𝐄 ⟫ ➪ 𝐈𝐦𝐚𝐠𝐞 𝐬𝐚𝐯𝐞 𝐧𝐚𝐡𝐢 𝐡𝐮𝐢: ${err.message}`); } break;

            case 'rmimg':
                if (!isMain || !isSenderDev) return;
                const menuImagePath = './data/menu_image.jpg';
                if (fs.existsSync(menuImagePath)) { fs.unlinkSync(menuImagePath); await this.send(from, "⟪ 🗑️ 𝐃𝐄𝐋𝐄𝐓𝐄𝐃 ⟫ ➪ 𝐌𝐞𝐧𝐮 𝐈𝐦𝐚𝐠𝐞 𝐫𝐞𝐦𝐨𝐯𝐞𝐝."); } 
                else { await this.send(from, "⟪ ⚠️ 𝐀𝐋𝐄𝐑𝐓 ⟫ ➪ 𝐍𝐨 𝐜𝐮𝐬𝐭𝐨𝐦 𝐦𝐞𝐧𝐮 𝐢𝐦𝐚𝐠𝐞 𝐟𝐨𝐮𝐧𝐝!"); } break;

            case 'autopin':
                if (!isGroup || !isMain) return;
                if (this.activeAutoPin.has(from)) {
                    this.activeAutoPin.delete(from);
                    await this.send(from, "⟪ 📌 𝐀𝐔𝐓𝐎-𝐏𝐈𝐍 ⟫ ➪ 𝐃𝐢𝐬𝐚𝐛𝐥𝐞𝐝.");
                } else {
                    this.activeAutoPin.set(from, { count: 0, target: getRandomDelay(10, 100) });
                    await this.send(from, `⟪ 📌 𝐀𝐔𝐓𝐎-𝐏𝐈𝐍 ⟫ ➪ 𝐀𝐜𝐭𝐢𝐯𝐞 (𝐑𝐚𝐧𝐝𝐨𝐦𝐢𝐳𝐢𝐧𝐠 𝟏𝟎-𝟏𝟎𝟎 𝐦𝐬𝐠 𝐭𝐚𝐫𝐠𝐞𝐭𝐬)`);
                }
                break;

            case 'menu': case 'fmenu':
                if (!isMain) return; 
                const isFull = command === 'fmenu' || args[0] === 'f';
                
                let menuText = `\`\`\`
   ⛩️
 ☸️ ☸️ ☸️
 █▀▀▀▀▀█
 █░░░░░█
 ▀▀▀▀▀▀▀
\`\`\`\n\n     [ ⛩️ 𝐃 𝐄 𝐕 𝐀 🎀  𝐁 𝐇 𝐀 𝐆 𝐖 𝐀 𝐍 ⛩️ ]\n\n╔⏤⏤⏤⏤⏤⏤[ ⚙️ ]⏤⏤⏤⏤⏤⏤╗
  🔥 𝐃𝐈𝐕𝐈𝐍𝐄 𝐆𝐄𝐍𝐄𝐑𝐀𝐋 🔥
╚⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤╝
[ 𝐒𝐘𝐒𝐓𝐄𝐌 𝐀𝐂𝐓𝐈𝐕𝐄 : 𝐕𝟖.𝟔.𝟎 𝐏𝐑𝐎 ]\n\n`;

                if (isFull) { 
                    menuText += "╠═ ⚙️ 𝗦𝗬𝗦𝗧𝗘𝗠 𝗖𝗢𝗡𝗧𝗥𝗢𝗟\n║ ⟿ .𝒔𝒕𝒂𝒕𝒖𝒔  ( 𝑺𝒉𝒊𝒌𝒊𝒈𝒂𝒎𝒊 𝑨𝒓𝒎𝒚 )\n║ ⟿ .𝒔𝒕𝒆𝒂𝒍𝒕𝒉 ( 𝑪𝒐𝒓𝒆 𝑯𝒆𝒂𝒍𝒕𝒉 )\n║ ⟿ .𝒌𝒊𝒍𝒍    ( 𝑬𝒙𝒆𝒄𝒖𝒕𝒆 𝑻𝒂𝒓𝒈𝒆𝒕 )\n║ ⟿ .𝒔𝒖𝒎     ( 𝑶𝒑𝒆𝒏 𝑮𝒂𝒕𝒆𝒔 )\n║ ⟿ .𝒂𝒅𝒅𝒃𝒐𝒕  ( 𝑨𝒘𝒂𝒌𝒆𝒏 𝑵𝒐𝒅𝒆 )\n║ ⟿ .𝒘𝒊𝒑𝒆    ( 𝑫𝒆𝒆𝒑 𝑷𝒖𝒓𝒈𝒆 )\n║ ⟿ .𝒎𝒂𝒉𝒐𝒓𝒂𝒈𝒂 ( 𝑨𝒅𝒂𝒑𝒕𝒂𝒕𝒊𝒐𝒏 )\n║ ⟿ .𝒂𝒖𝒕𝒐𝒑𝒊𝒏  ( 𝑯𝒖𝒎𝒂𝒏 𝑷𝒊𝒏𝒏𝒊𝒏𝒈 )\n\n╠═ 🌀 𝗡𝗔𝗠𝗘 𝗠𝗔𝗧𝗥𝗜𝗫\n║ ⟿ .𝒏        ( 𝑻𝒓𝒊𝒑𝒍𝒆 𝑨𝒕𝒕𝒂𝒄𝒌 )\n║ ⟿ .𝒏𝒊       ( 𝑭𝒂𝒔𝒕 𝑴𝒖𝒍𝒕𝒊-𝑵𝒐𝒅𝒆 )\n║ ⟿ .𝒏𝒄       ( 𝑺𝒊𝒏ɢ𝒍𝒆 𝑻𝒖𝒓𝒃𝒐 )\n║ ⟿ .𝒅𝒏𝒄𝟓     ( 𝑾𝒉𝒆𝒆𝒍 𝑺𝒚𝒎𝒃𝒐𝒍 𝑳𝒐𝒐𝒑 )\n║ ⟿ .𝒅𝒆𝒗𝒏     ( 𝑴𝒂𝒕𝒓𝒊𝒙 𝑺𝒚𝒏𝒄 𝑵𝑪 )\n║ ⟿ .𝒅𝒏𝒄𝟏-𝟒   ( 𝑴𝒂𝒕𝒓𝒊𝒙 𝑺𝒚𝒏𝒄 𝑴𝒐𝒅𝒆𝒔 )\n\n╠═ 💥 𝗦𝗣𝗔𝗠 𝗔𝗥𝗧𝗦\n║ ⟿ .𝒕𝒙𝒕      ( 𝑻𝒆𝒎𝒑𝒍𝒂𝒕𝒆 𝑺𝒑𝒂𝒎 )\n║ ⟿ .𝒄𝒖𝒔𝒕𝒙𝒕   ( 𝑪𝒖𝒔𝒕𝒐𝒎 𝑳𝒐𝒐𝒑 )\n║ ⟿ .𝒅𝒕𝒙      ( 𝑫𝒆𝒍𝒂𝒚 𝑻𝒆𝒙𝒕 )\n║ ⟿ .𝒔𝒑𝒎𝒈𝒐𝒅   ( 𝑮𝒉𝒐𝒔𝒕 𝑺𝒑𝒂𝒎𝒎𝒆𝒓 )\n\n╠═ 🎯 𝗧𝗔𝗥𝗚𝗘𝗧 & 𝗠𝗘𝗗𝗜𝗔\n║ ⟿ .𝒊𝒎𝒂𝒈𝒊𝒏𝒆  ( 𝑨𝑰 𝑻𝒙𝒕 𝑻𝒐 𝑰𝒎𝒈 )\n║ ⟿ .𝒑𝒄𝒔𝒑𝒎    ( 𝑷𝒉𝒐𝒕𝒐 𝑨𝒕𝒕𝒂𝒄𝒌 )\n║ ⟿ .𝒔𝒕𝒔𝒑𝒎    ( 𝑺𝒕𝒊𝒄𝒌𝒆𝒓 𝑺𝒑𝒂𝒎 )\n║ ⟿ .𝒅𝒆𝒔𝒄     ( 𝑫𝒆𝒔𝒄 𝑳𝒐𝒐𝒑 )\n║ ⟿ .𝒕𝒂𝒓𝒈𝒆𝒕   ( 𝑳𝒐𝒄𝒌 𝑬𝒏𝒆𝒎𝒚 )\n║ ⟿ .𝒔𝒍𝒊𝒅𝒆    ( 𝑹𝒆𝒑𝒍𝒚 𝑨𝒕𝒕𝒂𝒄𝒌 )\n\n╠═ 🛡️ 𝗚𝗥𝗢𝗨𝗣 𝗖𝗢𝗡𝗧𝗥𝗢𝗟\n║ ⟿ .𝒌𝒊𝒄𝒌 / .𝒑𝒓𝒐𝒎𝒐𝒕𝒆 / .𝒅𝒆𝒎𝒐𝒕𝒆\n║ ⟿ .𝒍𝒊𝒏𝒌 / .𝒐𝒑𝒆𝒏 / .𝒄𝒍𝒐𝒔𝒆\n║ ⟿ .𝒃𝒄 ( 𝑮𝒍𝒐𝒃𝒂𝒍 𝑩𝒓𝒐𝒂𝒅𝒄𝒂𝒔𝒕 )\n║ ⟿ .𝒃𝒖𝒓𝒏 ( 𝑺𝒆𝒍𝒇-𝑫𝒆𝒔𝒕𝒓𝒖𝒄𝒕 𝑴𝒔𝒈 )\n\n╠═ 🛑 𝗦𝗧𝗢𝗣 𝗘𝗥𝗔\n║ ⟿ .𝒔𝒕𝒐𝒑𝒂𝒍𝒍    ( 𝑯𝒂𝒍𝒕 𝑮𝑪 𝑩𝒐𝒕 )\n║ ⟿ .𝒈𝒔𝒕𝒐𝒑      ( 𝑲𝒊𝒍𝒍 𝑨𝒍𝒍 𝑵𝒐𝒅𝒆𝒔 )\n║ ⟿ .𝒔𝒕𝒐𝒑𝒏𝒊     ( 𝑺𝒕𝒐𝒑 𝑵𝑰 𝑺𝒚𝒏𝒄 )\n╚══════════════════════════════╝\n      ⚡ Ｐｏｗｅｒｅｄ ｂｙ Ｄｅｖ ⚡"; 
                } 
                else { menuText += "[ 𝟏 ] ➪ .𝒎𝒆𝒏𝒖 𝟏 ( ⚙️ 𝑺𝒚𝒔𝒕𝒆𝒎 & 𝑪𝒐𝒓𝒆 )\n[ 𝟐 ] ➪ .𝒎𝒆𝒏𝒖 𝟐 ( 🌀 𝑵𝒂𝒎𝒆 𝑴𝒂𝒕𝒓𝒊𝒙 )\n[ 𝟑 ] ➪ .𝒎𝒆𝒏𝒖 𝟑 ( 💥 𝑺𝒑𝒂𝒎 𝑨𝒓𝒕𝒔 )\n[ 𝟒 ] ➪ .𝒎𝒆𝒏𝒖 𝟒 ( 🎯 𝑻𝒂𝒓𝒈𝒆𝒕 & 𝑴𝒆𝒅𝒊𝒂 )\n[ 𝟓 ] ➪ .𝒎𝒆𝒏𝒖 𝟓 ( 🛑 𝑺𝒕𝒐𝒑 𝑬𝒓𝒂 )\n\n⟪ ⚡ 𝐄𝐌𝐄𝐑𝐆𝐄𝐍𝐂𝐘 ⟫ ➪ .𝒇𝒎𝒆𝒏𝒖\n      ⚡ Ｐｏｗｅｒｅｄ ｂｙ Ｄｅｖ ⚡"; }
                
                const menuImgPath = './data/menu_image.jpg'; 
                if (fs.existsSync(menuImgPath)) { 
                    await this.sock.sendMessage(from, { image: fs.readFileSync(menuImgPath), caption: styleText(menuText) }); 
                } else { 
                    await this.sock.sendMessage(from, { text: menuText }); 
                } 
                break;

            case 'mahoraga':
            case 'adapt':
                if (!isMain) return;
                const finalMahoText = `👑 ────────────────────────────────────── 👑
          ⚙️ 𝕿𝕳𝕰 𝕯𝕴𝑽𝕴𝕹𝕰 𝕬𝕯𝕬𝕿𝕿𝕬𝕿𝕴𝕺𝕹 𝖂𝕳𝕰𝕰𝕭 ⚙️
👑 ────────────────────────────────────── 👑

[ SYSTEM NOTICE: SACRED RITUAL "YAMATO NO OROCHI" UNLOCKED ]
The wheel has turned. Evasion is mathematically impossible.

                 🜲      🜲
             ◌      ||      ◌
          ◌         ||         ◌
       🜲            ||            🜲
     ◌  \\\\          ||          //  ◌
    ◌     \\\\        ||        //     ◌
   ◌        \\\\      ||      //        ◌
  🜲           \\\\    ||    //           🜲
 ◌              \\\\  ||  //              ◌
 ═════════════════( ☸️ )═════════════════
 ◌              //  ||  \\\\              ◌
 🜲           //    ||    \\\\           🜲
  ◌        //      ||      \\\\        ◌
   ◌     //        ||        \\\\     ◌
    ◌  //          ||          \\\\  ◌
       🜲            ||            🜲
          ◌         ||         ◌
             ◌      ||      ◌
                 🜲      🜲

         * 𝘊𝘭𝘪𝘤𝘬... 𝘊𝘭𝘪𝘤𝘬... 𝘊𝘭𝘪𝘤𝘬... *
     
[ ⚙️ 𝐀𝐃𝐀𝐏𝐓𝐀𝐓𝐈𝐎𝐍 𝐒𝐓𝐀𝐓𝐔𝐒: 𝟏𝟎𝟎% 𝐂ＯＭＰＬＥＴＥ ]

"Mortals depend on strategies to win. 
 The Divine General simply adapts and crushes."

🏰 REALM SOVEREIGN (OWNER):
➔ [ KING ] Dev Bhagwan 👑

📊 MATRIX DEFENSE MECHANISM:
➔ Engine: Vortex Overlord (V8.6.0)
➔ Status: Absolute Supremacy Active [🟢]

👥 FLEET ADAPTATION LOG (SHIKIGAMI ARMY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚔️ PRIMARY NODE (Bot_1)
   └─ [ ☸️ Wheel Turned ] ➪ Adapted to Group Reporting and Security Blocks.
🐜 SECONDARY NODE (Bot_2)
   └─ [ ☸️ Wheel Turned ] ➪ Bypassed WhatsApp Rate Limits and Delay Triggers.
🛡️ TERTIARY NODE (Bot_3)
   └─ [ ☸️ Wheel Turned ] ➪ Immune to Domain Bans and Spam Filters.

⚠️ DIVINE DECREE / WARN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chakra ghum chuka hai. Tumhara har ek attack, har ek firewall, aur har ek 
defense counter ab useless ho chuka hai. Isse pehle ki andhera tumhari puri 
identity ko format kar de, chup-chap jhuk jao...

"Once the wheel spins, your existence is already history."

👑 ────────────────────────────────────── 👑
                     " 𝕬𝕽𝕴𝕾𝕰 & 𝕬𝕯𝕬𝕿𝕿. "
       (The Divine General has neutralized your communication)
👑 ────────────────────────────────────── 👑`;
                await this.sock.sendMessage(from, { text: finalMahoText });
                break;

            case 'status': 
                if (!isMain) return; 
                const ramU = (process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2); 
                const upsecs = process.uptime(); 
                
                let finalStatus = `┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n   ⛩️ THE DIVINE THRONE ROOM ⛩️\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n`; 
                
                for (const b of Array.from(this.manager.bots.values())) { 
                    const icon = b.connected ? '🟢' : '🔴'; 
                    let shadowName = "Shikigami [Adapted]";
                    let roleIcon = '『 ☸️ 』';
                    
                    if (b.internalId === 'Bot_1') { shadowName = "MAHORAGA (The Divine General)"; roleIcon = '『 👑 COMMANDER 』'; }
                    
                    const action = (b.activeTasks.size>0 || b.activeNC.size>0 || b.activeN.size>0 || b.activeTxt.size>0 || b.activePcspm.size>0) ? "Adapting 🩸" : "Lurking 🌑"; 
                    finalStatus += `┃ ${icon} *${shadowName}* ${b.isSuppressed ? '[🔇]' : ''}\n┃ 📱 Num: ${b.phoneNumber ? `+${b.phoneNumber}` : "Unknown"}\n┃ ⚔️ Status: ${action}\n┃    └─ ${roleIcon}\n`; 
                } 
                
                finalStatus += `┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n┃ ⚙️ SYSTEM MANA CORE (V8.6.0):\n┃ 🔹 RAM Load: ${ramU} MB\n┃ 🔹 Divine Reign: ${Math.floor(upsecs / 3600)}h ${Math.floor((upsecs % 3600) / 60)}m\n┃ 📌 AutoPin: ${this.activeAutoPin.has(from) ? 'ON' : 'OFF'}\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛`;
                await this.sock.sendMessage(from, { text: finalStatus });
                break;

            case 'stealth': 
                if (!isMain) return; 
                const memU = (process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2); 
                const health = memU < 200 ? '𝟏𝟎𝟎% (𝐎𝐏𝐓𝐈𝐌𝐀𝐋)' : (memU < 500 ? '𝟖𝟓% (𝐒𝐓𝐀𝐁𝐋𝐄)' : '𝟓𝟎% (𝐖𝐀𝐑𝐍𝐈𝐍𝐆)'); 
                await this.send(from, `╔⏤⏤⏤⏤⏤⏤[ 🛡️ 𝗦𝗧𝗘𝗔𝗟𝗧𝗛 & 𝗛𝗘𝗔𝗟𝗧𝗛 ]⏤⏤⏤⏤⏤⏤╗\n║ 🟢 𝗦𝘁𝗲𝗮𝗹𝘁𝗵 𝗟𝗲𝘃𝗲𝗹: ${memU < 300 ? '𝐔𝐍𝐃𝐄𝐓𝐄𝐂𝐓𝐀𝐁𝐋𝐄 🥷' : '𝐑𝐈𝐒𝐊𝐘 ⚠️'}\n║ 💓 𝗖𝗼𝗿𝗲 𝗛𝗲𝗮𝗹𝘁𝗵: ${health}\n║ 🚀 𝗥𝗔𝗠 𝗟𝗼𝗮𝗱: ${memU} MB\n║ 🔌 𝗔𝗻𝘁𝗶-𝗕𝗮𝗻 𝗦𝘆𝘀𝘁𝗲𝗺: 𝗔𝗖𝗧𝗜𝗩𝗘 🟢\n╚⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤╝`); 
                break;

            case 'kill':
            case 'report':
            case 'execute':
                if (!isMain || !isSenderDev) return;
                const killTarget = mentioned.length > 0 ? mentioned[0] : (replyJid ? replyJid : null);
                if (!killTarget) return await this.send(from, "⟪ ⚠️ 𝐒𝐘𝐒𝐓𝐄𝐌 𝐑𝐄𝐉𝐄𝐂𝐓𝐈𝐎𝐍 ⟫ ➪ 𝐓𝐚𝐠 𝐨𝐫 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐭𝐡𝐞 𝐯𝐢𝐜𝐭𝐢𝐦!");

                const targetNorm = normalizeJid(killTarget);
                if (isAdmin(targetNorm)) return await this.send(from, "⟪ ❌ 𝐀𝐁𝐒𝐎𝐋𝐔𝐓𝐄 𝐃𝐄𝐍𝐈𝐀𝐋 ⟫ ➪ 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐞𝐱𝐞𝐜𝐮𝐭𝐞 𝐚 𝐅𝐞𝐥𝐥𝐨𝐰 𝐌𝐨𝐧𝐚𝐫𝐜𝐡.");

                await this.sock.sendPresenceUpdate('recording', from).catch(()=>{});
                await delay(3000); 

                try { await this.sock.updateBlockStatus(targetNorm, 'block'); } catch (e) {}
                if (isGroup) { try { await this.sock.groupParticipantsUpdate(from, [targetNorm], 'remove'); } catch (e) {} }

                const finalExecText = `╔⏤⏤⏤⏤⏤⏤[ ☠️ 𝐒 𝐘 𝐒 𝐓 𝐄 𝐌  𝐏 𝐄 𝐍 𝐀 𝐋 𝐓 𝐘 ]⏤⏤⏤⏤⏤⏤╗\n║ ➪ 𝐓𝐚𝐫𝐠𝐞𝐭: @${targetNorm.split('@')[0]}\n║ ➪ 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐑𝐞𝐩𝐨𝐫𝐭 𝐒𝐮𝐛𝐦𝐢𝐭𝐭𝐞𝐝 & 𝐁𝐥𝐨𝐜𝐤𝐞𝐝.\n║ ➪ 𝐅𝐚𝐭𝐞: 𝐄𝐫𝐚𝐬𝐞𝐝 𝐟𝐫𝐨𝐦 𝐭𝐡𝐞 𝐃𝐢𝐯𝐢𝐧𝐞 𝐒𝐢𝐠𝐡𝐭.\n╚⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤╝`;
                await this.sock.sendMessage(from, { text: finalExecText, mentions: [targetNorm] });
                break;
            
            case 'sum':
                if (!isGroup || !isMain) return; 
                const onlineNodes = Array.from(this.manager.bots.values()).filter(b => b.connected && b.sock?.user?.id && b.internalId !== this.internalId);
                if (onlineNodes.length === 0) return await this.send(from, `⟪ ⚠️ 𝐕𝐎𝐈𝐃 ⟫ ➪ 𝐍𝐨 𝐒𝐡𝐢𝐤𝐢𝐠𝐚𝐦𝐢𝐬 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞.`);
                
                await this.send(from, `⟪ 🌌 𝐒𝐇𝐀𝐃𝐎𝐖 𝐆𝐀𝐓𝐄𝐒 𝐎𝐏𝐄𝐍𝐈𝐍𝐆 ⟫ ➪ 𝐒𝐮𝐦𝐦𝐨𝐧𝐢𝐧𝐠 ${onlineNodes.length} 𝐒𝐡𝐢𝐤𝐢𝐠𝐚𝐦𝐢 𝐢𝐧𝐭𝐨 𝐭𝐡𝐢𝐬 𝐑𝐞𝐚𝐥𝐦...`);
                (async () => {
                    let successCount = 0;
                    try { const meta = await this.sock.groupMetadata(from); const existingParticipants = meta.participants.map(p => p.id);
                        for (const node of onlineNodes) {
                            const nodeJid = normalizeJid(node.sock.user.id);
                            if (existingParticipants.includes(nodeJid)) { successCount++; continue; }
                            await this.sock.groupParticipantsUpdate(from, [nodeJid], 'add'); successCount++; await delay(getRandomDelay(6000, 10000)); 
                        } if (isMain) await this.send(from, `⟪ 👑 𝐀𝐁𝐒𝐎𝐋𝐔𝐓𝐄 𝐃𝐎𝐌𝐈𝐍𝐀𝐍𝐂𝐄 ⟫ ➪ ${successCount} 𝐒𝐡𝐢𝐤𝐢𝐠𝐚𝐦𝐢 𝐇𝐚𝐯𝐞 𝐉𝐨𝐢𝐧𝐞𝐝 𝐓𝐡𝐞 𝐁𝐚𝐭𝐭𝐥𝐞𝐟𝐢𝐞𝐥𝐝!`);
                    } catch (err) { if (isMain) await this.send(from, `⟪ ❌ 𝐌𝐀𝐍𝐀 𝐃𝐈𝐒𝐑𝐔𝐏𝐓𝐈𝐎𝐍 ⟫ ➪ 𝐒𝐮𝐦𝐦𝐨𝐧 𝐁𝐥𝐨𝐜𝐤𝐞𝐝.`); }
                })(); break;

            case 'addbot': 
                if (!isMain) return; const phone = args[0]?.replace(/\D/g, ''); if (!phone) return await this.send(from, `⟪ ❌ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐔𝐬𝐚𝐠𝐞: ${GLOBAL_PREFIX}𝐚𝐝𝐝𝐛𝐨𝐭 𝟗𝟏𝐗𝐗𝐗𝐗𝐗𝐗𝐗𝐗𝐗𝐗`); 
                this.manager.counter++; const newId = `Bot_${this.manager.counter}`; await this.send(from, `⟪ ⏳ 𝐈𝐍𝐈𝐓𝐈𝐀𝐋𝐈𝐙𝐈𝐍𝐆 ⟫ ➪ 𝐏𝐫𝐞𝐩𝐚𝐫𝐢𝐧𝐠 ${newId.replace('_', ' ')}...`); 
                const newSession = new BotSession(newId, phone, this.manager, false); this.manager.bots.set(newId, newSession); await newSession.connect(); 
                setTimeout(async () => { try { const code = await newSession.sock.requestPairingCode(phone); await this.send(from, `╔════════════════════════╗\n  ⟪ 🛰️ 𝐍𝐎𝐃𝐄 𝐃𝐄𝐏𝐋𝐎𝐘𝐄𝐃 ⟫\n╚════════════════════════╝\n┃ 🆔 𝐍𝐚𝐦𝐞: ${newId.replace('_', ' ')}\n┃ 📱 𝐍𝐮𝐦: ${phone}\n┃ 🔑 𝐂𝐨𝐝𝐞: *${code}*\n╚════════════════════════╝`); this.manager.save(); } catch(e) { await this.send(from, `⟪ ❌ 𝐅𝐀𝐈𝐋𝐔𝐑𝐄 ⟫ ➪ ${e.message}`); } }, 5000); break;
            
            case 'wipe': 
                if(!isMain) return; 
                let wipedCount = 0; 
                if (store.messages[from]) { delete store.messages[from]; wipedCount++; } 
                HSEE.clearAll(); 
                const finalWipe = `╔════════════════════════════╗\n   🧹 𝐕𝐎𝐈𝐃 𝐏𝐔𝐑𝐆𝐄 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄\n╚════════════════════════════╝\n┃ 📊 𝐂𝐚𝐜𝐡𝐞: 𝐒𝐰𝐚𝐥𝐥𝐨𝐰𝐞𝐝 𝐛𝐲 𝐒𝐡𝐚𝐝𝐨𝐰𝐬\n┃ 🩸 𝐐𝐮𝐞𝐮𝐞𝐬: 𝐀𝐧𝐧𝐢𝐡𝐢𝐥𝐚𝐭𝐞𝐝`;
                await this.sock.sendMessage(from, { text: finalWipe });
                break;
                
            case 'clear': if (!isMain) return; if (store.messages[from]) { delete store.messages[from]; await this.send(from, `⟪ 🧹 𝐂𝐀𝐂𝐇𝐄 ⟫ ➪ 𝐅𝐥𝐮𝐬𝐡𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲!`); } else await this.send(from, `⟪ ⚠️ 𝐂𝐀𝐂𝐇𝐄 ⟫ ➪ 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐄𝐦𝐩𝐭𝐲.`); break;
            case 'pre': if (!isMain) return; if (args.length === 0) return await this.send(from, `⟪ ⚠️ 𝐒𝐘𝐒𝐓𝐄𝐌 𝐖𝐀𝐑𝐍𝐈𝐍𝐆 ⟫ ➪ 𝐔𝐬𝐞: ${GLOBAL_PREFIX}𝐩𝐫𝐞 <𝐧𝐞𝐰_𝐬𝐢𝐠𝐢𝐥>`); updatePrefix(args[0]); await this.send(from, `⟪ ⚙️ 𝐌𝐎𝐍𝐀𝐑𝐂𝐇'𝐒 𝐒𝐈𝐆𝐈𝐋 ⟫ ➪ 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐏𝐫𝐞𝐟𝐢𝐱 𝐔𝐩𝐝𝐚𝐭𝐞𝐝 𝐓𝐨: [ ${args[0]} ]`); break;
            case 'adminlist': if (!isMain) return; let listMsg = `╔⏤⏤⏤⏤⏤⏤[ 👑 𝐀𝐃𝐌𝐈𝐍 𝐋𝐈𝐒𝐓 👑 ]⏤⏤⏤⏤⏤⏤╗\n`; if (roles.admins.length === 0) listMsg += `║ ➪ 𝐍𝐨 𝐀𝐝𝐦𝐢𝐧𝐬 𝐅𝐨𝐮𝐧𝐝!\n`; else roles.admins.forEach((a, i) => listMsg += `║ ${i + 1}. @${a.split('@')[0]}\n`); listMsg += `╚⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤╝`; await this.send(from, listMsg, roles.admins); break;
            case 'sublist': if (!isMain) return; let subListMsg = `╔⏤⏤⏤⏤⏤⏤[ 🔰 𝐒𝐔𝐁-𝐀𝐃𝐌𝐈𝐍 𝐋𝐈𝐒𝐓 🔰 ]⏤⏤⏤⏤⏤⏤╗\n`; if (roles.subAdmins.length === 0) subListMsg += `║ ➪ 𝐍𝐨 𝐒𝐮𝐛-𝐀𝐝𝐦𝐢𝐧𝐬 𝐅𝐨𝐮𝐧𝐝!\n`; else roles.subAdmins.forEach((s, i) => subListMsg += `║ ${i + 1}. @${s.split('@')[0]}\n`); subListMsg += `╚⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤╝`; await this.send(from, subListMsg, roles.subAdmins); break;
            case 'admin': if (!isAdmin(sender) || !isMain) return; const newAdmins = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []); if (newAdmins.length === 0) return await this.send(from, `⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐓𝐚𝐠 𝐲𝐚 𝐑𝐞𝐩𝐥𝐲 𝐤𝐚𝐫𝐤𝐞 𝐛𝐚𝐭𝐚𝐨 𝐤𝐢𝐬𝐞 𝐀𝐝𝐦𝐢𝐧 𝐛𝐚𝐧𝐚𝐧𝐚 𝐡𝐚𝐢!`); let addedCount = 0; newAdmins.forEach(jid => { let norm = normalizeJid(jid); if (!roles.admins.includes(norm)) { roles.admins.push(norm); addedCount++; } }); if (addedCount > 0) { safeWriteJSON(ROLES_FILE, roles); await this.send(from, `⟪ 👑 𝐀𝐃𝐌𝐈𝐍 𝐆𝐑𝐀𝐍𝐓𝐄𝐃 ⟫ ➪ ${addedCount} 𝐮𝐬𝐞𝐫(𝐬) 𝐤𝐨 𝐅𝐮𝐥𝐥 𝐀𝐜𝐜𝐞𝐬𝐬 𝐦𝐢𝐥 𝐠𝐚𝐲𝐚!`, newAdmins); } else { await this.send(from, `⟪ ⚠️ 𝐀𝐋𝐄𝐑𝐓 ⟫ ➪ 𝐘𝐞 𝐮𝐬𝐞𝐫 𝐩𝐞𝐡𝐥𝐞 𝐬𝐞 𝐡𝐢 𝐀𝐝𝐦𝐢𝐧 𝐡𝐚𝐢!`); } break;
            
            case 'rmadmin': case 'removeadmin':
                if (!isAdmin(sender) || !isMain) return; const targetsAdmin = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []); if (targetsAdmin.length === 0) return await this.send(from, `⟪ ❌ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐓𝐚𝐠 𝐤𝐚𝐫 𝐣𝐢𝐬𝐞 𝐀𝐝𝐦𝐢𝐧 𝐥𝐢𝐬𝐭 𝐬𝐞 𝐡𝐚𝐭𝐚𝐧𝐚 𝐡𝐚𝐢!`);
                const superOwner = roles.admins.length > 0 ? roles.admins[0] : null; const hardcodedDev = '917091773246@s.whatsapp.net'; let removedCount = 0;
                targetsAdmin.forEach(jid => { 
                    let normJid = normalizeJid(jid); if (normJid === normalizeJid(sender)) return; 
                    if (normJid === superOwner || normJid === hardcodedDev) { this.send(from, `⟪ 🛡️ 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃 ⟫ ➪ @${normJid.split('@')[0]} 𝐢𝐬 𝐭𝐡𝐞 𝐒𝐮𝐩𝐞𝐫 𝐎𝐰𝐧𝐞𝐫. 𝐂𝐚𝐧𝐧𝐨𝐭 𝐛𝐞 𝐫𝐞𝐦𝐨𝐯𝐞𝐝!`, [normJid]); return; }
                    roles.admins = roles.admins.filter(a => a !== normJid); removedCount++;
                });
                if (removedCount > 0) { safeWriteJSON(ROLES_FILE, roles); await this.send(from, `⟪ 💀 𝐀𝐃𝐌𝐈𝐍 𝐑𝐄𝐌𝐎𝐕𝐄𝐃 ⟫ ➪ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐓𝐞𝐫𝐦𝐢𝐧𝐚𝐭𝐞𝐝!`); } break;

            case 'sub': if (!isAdmin(sender) || !isMain) return; const newSubs = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []); if (newSubs.length === 0) return await this.send(from, `⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐓𝐚𝐠 𝐲𝐚 𝐑𝐞𝐩𝐥𝐲 𝐤𝐚𝐫𝐤𝐞 𝐛𝐚𝐭𝐚𝐨 𝐤𝐢𝐬𝐞 𝐒𝐮𝐛-𝐀𝐝𝐦𝐢𝐧 𝐛𝐚𝐧𝐚𝐧𝐚 𝐡𝐚𝐢!`); let subAddedCount = 0; newSubs.forEach(jid => { let norm = normalizeJid(jid); if (!roles.subAdmins.includes(norm) && !roles.admins.includes(norm)) { roles.subAdmins.push(norm); subAddedCount++; } }); if (subAddedCount > 0) { safeWriteJSON(ROLES_FILE, roles); await this.send(from, `⟪ 🔰 𝐒𝐔𝐁-𝐀𝐃𝐌𝐈𝐍 ⟫ ➪ ${subAddedCount} 𝐮𝐬𝐞𝐫(𝐬) 𝐀𝐝𝐝𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲!`, newSubs); } else { await this.send(from, `⟪ ⚠️ 𝐀𝐋𝐄𝐑𝐓 ⟫ ➪ 𝐘𝐞 𝐮𝐬𝐞𝐫 𝐩𝐞𝐡𝐥𝐞 𝐬𝐞 𝐡𝐢 𝐒𝐮𝐛-𝐀𝐝𝐦𝐢𝐧 𝐲𝐚 𝐀𝐝𝐦𝐢𝐧 𝐡𝐚𝐢!`); } break;
            case 'rmsub': case 'removesub': if (!isAdmin(sender) || !isMain) return; const targetsSub = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []); if (targetsSub.length === 0) return await this.send(from, `⟪ ❌ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐓𝐚𝐠 𝐲𝐚 𝐑𝐞𝐩𝐥𝐲 𝐤𝐚𝐫 𝐣𝐢𝐬𝐞 𝐒𝐮𝐛-𝐀𝐝𝐦𝐢𝐧 𝐬𝐞 𝐡𝐚𝐭𝐚𝐧𝐚 𝐡𝐚𝐢!`); targetsSub.forEach(jid => { let normJid = normalizeJid(jid); roles.subAdmins = roles.subAdmins.filter(s => s !== normJid); }); safeWriteJSON(ROLES_FILE, roles); await this.send(from, `⟪ 🗑️ 𝐑𝐄𝐌𝐎𝐕𝐄𝐃 ⟫ ➪ 𝐒𝐮𝐛-𝐀𝐝𝐦𝐢𝐧(𝐬) 𝐓𝐞𝐫𝐦𝐢𝐧𝐚𝐭𝐞𝐝!`); break;
            
            case 'sup': 
            case 'conceal':
            case 'stealthmode':
                if (!isMain) return; 
                const targetSup = args[0] ? `Bot_${args[0]}` : this.internalId; 
                const botToSup = this.manager.bots.get(targetSup); 
                if (botToSup) { 
                    botToSup.isSuppressed = true; 
                    await this.sock.sendMessage(from, { text: `⟪ 🔇 𝐒𝐔𝐏𝐏𝐑𝐄𝐒𝐒𝐄𝐃 ⟫ ➪ [ ${botToSup.displayId} ] 𝒉𝒂𝒔 𝒗𝒂𝒏𝒊𝒔𝒉𝒆𝒅 𝒇𝒓𝒐𝒎 𝒔𝒊𝒈𝒉𝒕.` }); 
                } break;
                
            case 'uplift': 
            case 'reveal':
            case 'unveil':
                if (!isMain) return; 
                const targetLift = args[0] ? `Bot_${args[0]}` : this.internalId; 
                const botToLift = this.manager.bots.get(targetLift); 
                if (botToLift) { 
                    botToLift.isSuppressed = false; 
                    await this.sock.sendMessage(from, { text: `⟪ 🔊 𝐀𝐂𝐓𝐈𝐕𝐄 ⟫ ➪ [ ${botToLift.displayId} ] 𝒔𝒕𝒂𝒏𝒅𝒔 𝒓𝒆𝒂𝒅𝒚 𝒇𝒐𝒓 𝒔𝒍𝒂𝒖𝒈𝒉𝒕𝒆𝒓.` }); 
                } break;
                
            case 'ping': if (isMain) await this.ping(from); break;
            case 'auto': this.activeAutoReact.set(from, args[0] || '🔥'); if (isMain) await this.send(from, `⟪ ✅ 𝐀𝐔𝐓𝐎-𝐑𝐄𝐀𝐂𝐓 ⟫ ➪ 𝐒𝐞𝐭 𝐟𝐨𝐫 𝐭𝐡𝐢𝐬 𝐆𝐫𝐨𝐮𝐩: ${this.activeAutoReact.get(from)}`); break;
            case 'dele': const qDele = msg.message.extendedTextMessage?.contextInfo; if (qDele?.stanzaId) await this.sock.sendMessage(from, { delete: { remoteJid: from, fromMe: true, id: qDele.stanzaId } }).catch(()=>{}); break;
            case 'deli': const qDeli = msg.message.extendedTextMessage?.contextInfo; if (qDeli?.stanzaId) await this.sock.sendMessage(from, { delete: { remoteJid: from, fromMe: false, id: qDeli.stanzaId, participant: qDeli.participant } }).catch(()=>{}); break;
            
            case 'deleall': 
            case 'rulersauthority':
            case 'erase':
                if (!isMain) return;
                if (store.messages[from]) { 
                    const botMsgs = Object.values(store.messages[from]).filter(m => m.key.fromMe === true); 
                    for (const m of botMsgs) { 
                        await this.sock.sendMessage(from, { delete: m.key }).catch(()=>{}); 
                        await delay(300); 
                    } 
                    await this.send(from, `⟪ 🌌 𝐕𝐎𝐈𝐃 𝐄𝐗𝐏𝐀𝐍𝐒𝐈𝐎𝐍 ⟫ ➪ 𝑾𝒊𝒑𝒊𝒏𝒈 𝒕𝒓𝒂𝒄𝒆𝒔 𝒐𝒇 𝒕𝒉𝒆 𝑺𝒉𝒂𝒅𝒐𝒘𝒔...`);
                } else {
                    await this.send(from, `⟪ 🌑 𝐕𝐎𝐈𝐃 ⟫ ➪ 𝑵𝒐 𝒕𝒓𝒂𝒄𝒆𝒔 𝒍𝒆𝒇𝒕 𝒕𝒐 𝒆𝒓𝒂𝒔𝒆.`);
                }
                break;
                
            case 'kickall': if (isGroup && isMain) { const meta = await this.sock.groupMetadata(from); const targets = meta.participants.filter(p => p.admin !== 'admin' && p.admin !== 'superadmin').map(p => p.id); await this.send(from, `⟪ 🧹 𝐏𝐔𝐑𝐆𝐄 𝐏𝐑𝐎𝐓𝐎𝐂𝐎𝐋 ⟫ ➪ 𝐄𝐥𝐢𝐦𝐢𝐧𝐚𝐭𝐢𝐧𝐠 𝐍𝐨𝐧-𝐀𝐝𝐦𝐢𝐧𝐬...`); for (let i=0; i<targets.length; i+=5) { await this.sock.groupParticipantsUpdate(from, targets.slice(i, i+5), 'remove').catch(()=>{}); await delay(2000); } } break;
            
            case 'tagall': 
            case 'bloodlust':
                if (isGroup && isMain) { 
                    const meta = await this.sock.groupMetadata(from); 
                    const participants = meta.participants.map(p => p.id); 
                    const id = `${from}_tagall`; 
                    this.activeTagall.set(id, { active: true }); 
                    
                    (async () => { 
                        for(let i=0; i<5 && this.activeTagall.has(id) && this.connected; i++) { 
                            await this.send(from, `⟪ 👑 𝐀𝐁𝐒𝐎𝐋𝐔𝐓𝐄 𝐃𝐎𝐌𝐈𝐍𝐀𝐍𝐂𝐄 ⟫\n➪ 𝑻𝒉𝒆 𝑴𝒐𝒏𝒂𝒓𝒄𝒉 𝑺𝒖𝒎𝒎𝒐𝒏𝒔 𝒀𝒐𝒖!\n\n` + participants.map(p => `@${p.split('@')[0]}`).join(' '), participants); 
                            await delay(2000); 
                        } 
                        this.activeTagall.delete(id); 
                    })(); 
                } break;
                
            case 'leave': if (isGroup && isMain) { await this.send(from, `⟪ 👋 𝐄𝐕𝐀𝐂𝐔𝐀𝐓𝐄 ⟫ ➪ 𝐃𝐄𝐕𝐀🎀 𝐁𝐇𝐀𝐆𝐖𝐀𝐍 𝐋𝐞𝐚𝐯𝐢𝐧𝐠 𝐓𝐡𝐞 𝐌𝐚𝐭𝐫𝐢𝐱!`); await delay(1000); await this.sock.groupLeave(from).catch(()=>{}); } break;

            // ==================== 🛡️ GROUP CONTROL & DOMAIN ====================
            case 'domain':
                if (!isGroup || !isMain) return;
                const groupMetadata = await this.sock.groupMetadata(from);
                const totalMem = groupMetadata.participants.length;
                const admins = groupMetadata.participants.filter(p => p.admin !== null).length;
                const mortals = totalMem - admins;
                await this.send(from, `╔⏤⏤⏤⏤⏤[ 🌌 𝐌𝐎𝐍𝐀𝐑𝐂𝐇'𝐒 𝐃𝐎𝐌𝐀𝐈𝐍 🌌 ]⏤⏤⏤⏤⏤╗\n║ 🏰 𝑹𝒆𝒂𝒍𝒎: ${styleText(groupMetadata.subject)}\n║ 👥 𝑺𝒐𝒖𝒍𝒔 𝑻𝒓𝒂𝒑𝒑𝒆𝒅: ${totalMem}\n║ ⚔️ 𝑬𝒍𝒊𝒕𝒆 𝑮𝒖𝒂𝒓𝒅𝒔 (𝑨𝒅𝒎𝒊𝒏𝒔): ${admins}\n║ 🩸 𝑴𝒐𝒓𝒕𝒂𝒍𝒔: ${mortals}\n║ 👑 𝑨𝒃𝒔𝒐𝒍𝒖𝒕𝒆 𝑹𝒖𝒍𝒆𝒓: 𝑫𝒆𝒗 𝑩𝒉𝒂𝒈𝒘𝒂𝒏\n╚⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤╝`);
                break;
                
            case 'kick': if (!isGroup || !isMain) return; const kickTargets = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []); if (kickTargets.length === 0) return await this.send(from, `⟪ ⚠️ 𝐒𝐘𝐒𝐓𝐄𝐌 𝐀𝐋𝐄𝐑𝐓 ⟫ ➪ 𝐓𝐚𝐠/𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐛𝐚𝐧𝐢𝐬𝐡 𝐭𝐡𝐞𝐦!`); await this.sock.groupParticipantsUpdate(from, kickTargets, 'remove').catch(()=>{}); await this.send(from, `⟪ 🥾 𝐁𝐀𝐍𝐈𝐒𝐇𝐄𝐃 ⟫ ➪ 𝐓𝐚𝐫𝐠𝐞𝐭(𝐬) 𝐭𝐡𝐫𝐨𝐰𝐧 𝐨𝐮𝐭 𝐨𝐟 𝐭𝐡𝐞 𝐌𝐨𝐧𝐚𝐫𝐜𝐡'𝐬 𝐃𝐨𝐦𝐚𝐢𝐧!`); break;
            case 'promote': if (!isGroup || !isMain) return; const promoteTargets = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []); if (promoteTargets.length === 0) return await this.send(from, `⟪ ⚠️ 𝐒𝐘𝐒𝐓𝐄𝐌 𝐀𝐋𝐄𝐑𝐓 ⟫ ➪ 𝐓𝐚𝐠/𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐫𝐚𝐧𝐤 𝐮𝐩!`); await this.sock.groupParticipantsUpdate(from, promoteTargets, 'promote').catch(()=>{}); await this.send(from, `⟪ ⬆️ 𝐑𝐀𝐍𝐊 𝐔𝐏 ⟫ ➪ 𝐓𝐚𝐫𝐠𝐞𝐭 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐩𝐫𝐨𝐦𝐨𝐭𝐞𝐝 𝐭𝐨 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐞𝐫 (𝐀𝐝𝐦𝐢𝐧)!`); break;
            case 'demote': if (!isGroup || !isMain) return; const demoteTargets = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []); if (demoteTargets.length === 0) return await this.send(from, `⟪ ⚠️ 𝐒𝐘𝐒𝐓𝐄𝐌 𝐀𝐋𝐄𝐑𝐓 ⟫ ➪ 𝐓𝐚𝐠/𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐬𝐭𝐫𝐢𝐩 𝐫𝐚𝐧𝐤!`); await this.sock.groupParticipantsUpdate(from, demoteTargets, 'demote').catch(()=>{}); await this.send(from, `⟪ ⬇️ 𝐑𝐀𝐍𝐊 𝐃𝐎𝐖𝐍 ⟫ ➪ 𝐓𝐚𝐫𝐠𝐞𝐭 𝐬𝐭𝐫𝐢𝐩𝐩𝐞𝐝 𝐨𝐟 𝐭𝐡𝐞𝐢𝐫 𝐚𝐮𝐭𝐡𝐨𝐫𝐢𝐭𝐲!`); break;
            case 'link': if (!isGroup || !isMain) return; try { const code = await this.sock.groupInviteCode(from); await this.send(from, `⟪ 🔗 𝐆𝐑𝐎𝐔𝐏 𝐋𝐈𝐍𝐊 ⟫\n➪ https://chat.whatsapp.com/${code}`); } catch (e) { await this.send(from, `⟪ ❌ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐁𝐨𝐭 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚𝐧 𝐚𝐝𝐦𝐢𝐧 𝐭𝐨 𝐠𝐞𝐭 𝐭𝐡𝐞 𝐥𝐢𝐧𝐤!`); } break;
            case 'close': if (!isGroup || !isMain) return; await this.sock.groupSettingUpdate(from, 'announcement').catch(()=>{}); await this.send(from, `⟪ 🔒 𝐃𝐎𝐌𝐀𝐈𝐍 𝐒𝐄𝐀𝐋𝐄𝐃 ⟫ ➪ 𝐓𝐡𝐞 𝐌𝐨𝐧𝐚𝐫𝐜𝐡'𝐬 𝐃𝐨𝐦𝐚𝐢𝐧 𝐢𝐬 𝐜𝐥𝐨𝐬𝐞𝐝. 𝐎𝐧𝐥𝐲 𝐄𝐥𝐢𝐭𝐞𝐬 𝐦𝐚𝐲 𝐬𝐩𝐞𝐚𝐤.`); break;
            case 'open': if (!isGroup || !isMain) return; await this.sock.groupSettingUpdate(from, 'not_announcement').catch(()=>{}); await this.send(from, `⟪ 🔓 𝐃𝐎𝐌𝐀𝐈𝐍 𝐎𝐏𝐄𝐍𝐄𝐃 ⟫ ➪ 𝐓𝐡𝐞 𝐬𝐞𝐚𝐥 𝐢𝐬 𝐥𝐢𝐟𝐭𝐞𝐝. 𝐌𝐨𝐫𝐭𝐚𝐥𝐬 𝐦𝐚𝐲 𝐬𝐩𝐞𝐚𝐤.`); break;

            // ==================== 🌍 GLOBAL & BURN ====================
            case 'bc':
                if (!isMain || !isSenderDev) return; 
                const bcText = args.join(" "); 
                if (!bcText) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐤𝐞 𝐥𝐢𝐲𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐥𝐢𝐤𝐡𝐨!");
                
                try { 
                    const groups = await this.sock.groupFetchAllParticipating(); 
                    const groupJids = Object.keys(groups); let sentCount = 0;
                    for (const gJid of groupJids) { 
                        await delay(Math.floor(Math.random() * (2500 - 1500 + 1)) + 1500); 
                        await this.send(gJid, `╔⏤⏤⏤⏤⏤[ 👑 𝐃 𝐄 𝐕 𝐀 🎀 👑 ]⏤⏤⏤⏤⏤╗\n\n${styleText(bcText)}\n\n╚⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤⏤╝`); 
                        sentCount++; 
                    }
                    await this.sock.sendMessage(from, { text: `⟪ ✅ 𝐌𝐀𝐓𝐑𝐈𝐗 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 ⟫ ➪ 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐞𝐜𝐡𝐨𝐞𝐝 𝐢𝐧 ${sentCount} 𝐝𝐨𝐦𝐚𝐢𝐧𝐬.` });
                } catch (err) { } 
                break;
                
            case 'burn':
                if (!isMain) return; const burnText = args.join(" "); if (!burnText) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐋𝐢𝐤𝐡𝐨 𝐤𝐲𝐚 𝐛𝐡𝐞𝐣𝐧𝐚 𝐡𝐚𝐢! 𝐄𝐱: .𝐛𝐮𝐫𝐧 𝐇𝐞𝐥𝐥𝐨");
                const burnMsg = await this.sock.sendMessage(from, { text: `⟪ 🔥 𝐁𝐔𝐑𝐍 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 ⟫\n\n${styleText(burnText)}` }); await delay(5000); await this.sock.sendMessage(from, { delete: burnMsg.key }); break;

            // ==================== 🌀 NAME MATRIX ====================
            case 'dnc5':
                if (!isGroup || !isMain) return; const activeDnc5Nodes = Array.from(this.manager.bots.values()).filter(b => b.connected);
                if (activeDnc5Nodes.length === 0) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐍𝐨 𝐀𝐜𝐭𝐢𝐯𝐞 𝐍𝐨𝐝𝐞𝐬 𝐅𝐨𝐮𝐧𝐝!");
                const dnc5Name = args.join(" ") || "𝐌𝐀𝐇𝐎𝐑𝐀𝐆𝐀"; this.activeNC.set(from, true); saveState(from, 'dnc5', args); await this.send(from, `⟪ ☸️ 𝐃𝐍𝐂𝟓 - 𝐀𝐃𝐀𝐏𝐓𝐀𝐓𝐈𝐎𝐍 ⟫ ➪ 𝐀𝐭𝐭𝐚𝐜𝐤 𝐈𝐧𝐢𝐭𝐢𝐚𝐭𝐞𝐝!`);
                
                (async () => { let turn = 0; while (this.activeNC.has(from) && this.connected) { const promises = []; activeDnc5Nodes.forEach((node, index) => { 
                    const symPrefix = getRandom(aestheticSymbols);
                    const symSuffix = getRandom(aestheticSymbols);
                    promises.push(node.sock.groupUpdateSubject(from, styleText(`${symPrefix} ${dnc5Name} ${symSuffix}`)).catch(()=>{})); 
                    if (index === turn % activeDnc5Nodes.length) { 
                        promises.push(delay(250).then(() => node.sock.groupUpdateSubject(from, styleText(`${getRandom(aestheticSymbols)} ${dnc5Name} ${getRandom(aestheticSymbols)}`)).catch(()=>{}))); 
                    } 
                }); await Promise.all(promises); turn++; await delay(getRandomDelay(800, 1500)); } })(); break;

            case 'n': 
                const nName = args.join(" ") || "𝐃𝐄𝐕𝐀🎀 𝐁𝐇𝐀𝐆𝐖𝐀𝐍"; const nEmojis = ['🫯','💥','🫆','🌀','🌪️','❄️','🪐','☄️','🕊️','🫧','🪸','🦋','🧭','🗼','🫟','⚙️','⚔️','⚕️'];
                this.activeN.set(from, true); if(isMain) await this.send(from, "⟪ 🔥 𝐓𝐑𝐈𝐏𝐋𝐄 𝐓𝐇𝐑𝐄𝐀𝐓 ⟫ ➪ 𝐍-𝐀𝐭𝐭𝐚𝐜𝐤 𝐒𝐭𝐚𝐫𝐭𝐞𝐝!");
                (async () => { while (this.activeN.has(from) && this.connected) { const e1 = nEmojis[Math.floor(Math.random() * nEmojis.length)]; const e2 = nEmojis[Math.floor(Math.random() * nEmojis.length)]; const e3 = nEmojis[Math.floor(Math.random() * nEmojis.length)]; await Promise.all([ this.sock.groupUpdateSubject(from, styleText(`${e1} ${nName} ${e1}`)), this.sock.groupUpdateSubject(from, styleText(`${e2} ${nName} ${e2}`)), this.sock.groupUpdateSubject(from, styleText(`${e3} ${nName} ${e3}`)) ]).catch(()=>{}); await delay(950); } })(); break;
            
            case 'ni':
                if (!isGroup || !isMain) return; const activeNiNodes = Array.from(this.manager.bots.values()).filter(b => b.connected);
                if (activeNiNodes.length === 0) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐍𝐨 𝐀𝐜𝐭𝐢𝐯𝐞 𝐍𝐨𝐝𝐞𝐬 𝐅𝐨𝐮𝐧𝐝!");
                const niName = args.join(" ") || "𝐃𝐄𝐕𝐀🎀 𝐁𝐇𝐀𝐆𝐖𝐀𝐍"; this.activeNC.set(from, true); saveState(from, 'ni', args); 
                if (isMain) await this.send(from, `⟪ ⚡ 𝐍𝐈-𝐒𝐘𝐍𝐂 ⟫ ➪ 𝐅𝐚𝐬𝐭 & 𝐒𝐚𝐟𝐞 𝐌𝐮𝐥𝐭𝐢-𝐍𝐨𝐝𝐞 𝐀𝐭𝐭𝐚𝐜𝐤 𝐈𝐧𝐢𝐭𝐢𝐚𝐭𝐞𝐝!`);
                const niEmojis = ['🔥','⚡','💀','💥','🩸','☠️','⚔️','🪐','☄️','🌪️'];
                (async () => { let turn = 0; while (this.activeNC.has(from) && this.connected) { const promises = []; activeNiNodes.forEach((node, index) => { if (index === turn % activeNiNodes.length) { const e1 = niEmojis[Math.floor(Math.random() * niEmojis.length)]; promises.push(node.sock.groupUpdateSubject(from, styleText(`${e1} ${niName} ${e1}`)).catch(()=>{})); } }); await Promise.all(promises); turn++; await delay(Math.floor(Math.random() * (600 - 450 + 1)) + 450); } })(); break;

            case 'syncnc': case 'devn':
                if (!isGroup || !isMain) return; const activeNodes = Array.from(this.manager.bots.values()).filter(b => b.connected);
                if (activeNodes.length === 0) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐍𝐨 𝐀𝐜𝐭𝐢𝐯𝐞 𝐍𝐨𝐝𝐞𝐬 𝐅𝐨𝐮𝐧𝐝!");
                const syncName = args.join(" ") || "𝐃𝐄𝐕𝐀🎀 𝐁𝐇𝐀𝐆𝐖𝐀𝐍"; const syncEmojis = ['🫯','💥','🫆','🌀','🌪️','❄️','🪐','☄️','🕊️','🫧','🪸','🦋','🧭','🗼','🫟','⚙️','⚔️','⚕️'];
                this.activeNC.set(from, true); saveState(from, command, args); await this.send(from, `⟪ 🌪️ 𝐌𝐀𝐓𝐑𝐈𝐗 𝐒𝐘𝐍𝐂 ⟫ ➪ 𝐂𝐨𝐨𝐫𝐝𝐢𝐧𝐚𝐭𝐞𝐝 𝐀𝐭𝐭𝐚𝐜𝐤 𝐒𝐭𝐚𝐫𝐭𝐞𝐝 𝐰𝐢𝐭𝐡 ${activeNodes.length} 𝐍𝐨𝐝𝐞𝐬!`);
                (async () => { let turn = 0; while (this.activeNC.has(from) && this.connected) { const promises = []; activeNodes.forEach((node, index) => { const e1 = syncEmojis[Math.floor(Math.random() * syncEmojis.length)]; promises.push(node.sock.groupUpdateSubject(from, styleText(command === 'devn' ? `${syncName} ${e1}` : `${e1} ${syncName} ${e1}`)).catch(()=>{})); if (index === turn % activeNodes.length) { const e2 = syncEmojis[Math.floor(Math.random() * syncEmojis.length)]; promises.push(delay(100).then(() => node.sock.groupUpdateSubject(from, styleText(command === 'devn' ? `${syncName} ${e2}` : `${e2} ${syncName} ${e2}`)).catch(()=>{}))); } }); await Promise.all(promises); turn++; await delay(Math.floor(Math.random() * (800 - 700 + 1)) + 700); } })(); break;

            case 'dnc1': case 'dnc2': case 'dnc3': case 'dnc4':
                if (!isGroup || !isMain) return; const activeDncNodes = Array.from(this.manager.bots.values()).filter(b => b.connected);
                if (activeDncNodes.length === 0) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐍𝐨 𝐀𝐜𝐭𝐢𝐯𝐞 𝐍𝐨𝐝𝐞𝐬 𝐅𝐨𝐮𝐧𝐝!");
                const dncName = args.join(" ") || "𝐃𝐄𝐕𝐀🎀 𝐁𝐇𝐀𝐆𝐖𝐀𝐍"; this.activeNC.set(from, true); saveState(from, command, args); await this.send(from, `⟪ 🌪️ 𝐃𝐍𝐂 𝐏𝐑𝐎𝐓𝐎𝐂𝐎𝐋 - ${command.toUpperCase()} ⟫ ➪ 𝐀𝐭𝐭𝐚𝐜𝐤 𝐈𝐧𝐢𝐭𝐢𝐚𝐭𝐞𝐝!`);
                const getDncFormatted = (cmdType, baseText) => { let e; if (cmdType === 'dnc1') { const em1 = ['🫯','💥','🫆','🌀','🌪️','❄️','🪐','☄️','🕊️','🫧','🪸','🦋','🧭','🗼','🫟','⚙️','⚔️','⚕️']; e = em1[Math.floor(Math.random() * em1.length)]; return `×${e}× ${baseText} ×${e}×`; } else if (cmdType === 'dnc2') { const em2 = ['🫯','💥','🫆','🌀','🌪️','❄️','🪐','☄️','🕊️','🫧','🪸','🦋','🧭','🗼','🫟','⚙️','⚔️','⚕️']; e = em2[Math.floor(Math.random() * em2.length)]; return `${e} ${baseText} ${e}`; } else if (cmdType === 'dnc3') { const sym = ['○','●','□','■','♤','♡','◇','♧','☆','▪︎','¤','✦','❃','❉','✬','✿','★','❂','✪','✲','✯','❁','✴','✵','✷','❊','✳','✰','۞','⍟','⁂']; e = sym[Math.floor(Math.random() * sym.length)]; return `${e} ${baseText} ${e}`; } else if (cmdType === 'dnc4') { const circ = ['🔴','🟠','🟡','🟢','🔵','🟣','🟤','⚪️','⚫️']; e = circ[Math.floor(Math.random() * circ.length)]; return `♤${e}♤ ${baseText} ♤${e}♤`; } };
                (async () => { let turn = 0; while (this.activeNC.has(from) && this.connected) { const promises = []; activeDncNodes.forEach((node, index) => { promises.push(node.sock.groupUpdateSubject(from, styleText(getDncFormatted(command, dncName))).catch(()=>{})); if (index === turn % activeDncNodes.length) { promises.push(delay(150).then(() => node.sock.groupUpdateSubject(from, styleText(getDncFormatted(command, dncName))).catch(()=>{}))); promises.push(delay(300).then(() => node.sock.groupUpdateSubject(from, styleText(getDncFormatted(command, dncName))).catch(()=>{}))); } }); await Promise.all(promises); turn++; await delay(Math.floor(Math.random() * (850 - 700 + 1)) + 700); } })(); break;

            case 'fstn':
                if (!isGroup) return; const fstnKey = args[0] && emojiArrays[args[0]] ? args[0] : 'n1'; const fstnName = args.slice(1).join(" ") || "𝐃𝐄𝐕𝐀🎀 𝐁𝐇𝐀𝐆𝐖𝐀𝐍"; const fstnEmojis = emojiArrays[fstnKey] || emojiArrays['n1'];
                this.activeNC.set(from, true); saveState(from, 'fstn', args); if(isMain) await this.send(from, `⟪ ⚡ 𝐅𝐀𝐒𝐓-𝐍 ⟫ ➪ 𝐔𝐥𝐭𝐫𝐚 𝐒𝐩𝐞𝐞𝐝 𝐋𝐨𝐨𝐩 𝐀𝐜𝐭𝐢𝐯𝐞 [${fstnKey}]!`);
                (async () => { while (this.activeNC.has(from) && this.connected) { await HSEE.runAttack(async () => { if (!this.activeNC.has(from)) return; try { const e = fstnEmojis[Math.floor(Math.random() * fstnEmojis.length)]; await this.sock.groupUpdateSubject(from, styleText(`${fstnName} ${e}`)); } catch (err) {} }); await delay(Math.floor(Math.random() * (800 - 700 + 1)) + 700); } })(); break;

            // ==================== 💥 SPAM ARTS ====================
            case 'txt': 
                const taskKey = `${from}_txt`; 
                if (this.activeTasks.has(taskKey)) return; 
                const mode = args[0]?.toLowerCase(); 
                const names = args.slice(1).join(" ") || "𝐃𝐄𝐕𝐀🎀 𝐁𝐇𝐀𝐆𝐖𝐀𝐍"; 
                this.activeTasks.set(taskKey, true); 
                saveState(from, 'txt', args);
                
                if (isMain) {
                    await this.sock.sendMessage(from, { text: `⟪ ⚙️ 𝐀𝐃𝐀𝐏𝐓𝐀𝐓𝐈𝐎𝐍 ⟫ ➪ 𝐓𝐞𝐦𝐩𝐥𝐚𝐭𝐞 𝐒𝐩𝐚𝐦 𝐀𝐜𝐭𝐢𝐯𝐞: [ ${names} ]` });
                }
                
                (async () => { 
                    let step = 0; 
                    while (this.activeTasks.has(taskKey) && this.connected) { 
                        let template = (mode === 'rdm') ? txtTemplates[step++ % txtTemplates.length] : (txtTemplates[parseInt(mode)-1] || txtTemplates[0]); 
                        const finalMsg = template.replace(/{{names}}/g, names); 
                        const quoteObj = quotedMsg ? { key: { remoteJid: from, id: msg.message.extendedTextMessage.contextInfo.stanzaId, participant: quotedMsg.participant }, message: quotedMsg.quotedMessage } : null; 
                        await HSEE.runAttack(async () => { 
                            if (!this.activeTasks.has(taskKey)) return; 
                            await this.send(from, finalMsg, [], quoteObj); 
                        }); 
                        await delay(Math.floor(Math.random() * (25000 - 12000 + 1)) + 12000); 
                    } 
                })(); 
                break;
            
            case 'custxt': 
                const customMsg = args.join(" "); 
                if (!customMsg) return isMain && this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐄𝐧𝐭𝐞𝐫 𝐓𝐞𝐱𝐭!"); 
                this.activeCustxt.set(from, true); 
                saveState(from, 'custxt', args); 
                
                if (isMain) {
                    await this.sock.sendMessage(from, { text: `⟪ ⚙️ 𝐀𝐃𝐀𝐏𝐓𝐀𝐓𝐈𝐎𝐍 ⟫ ➪ 𝐂𝐮𝐬𝐭𝐨𝐦 𝐋𝐨𝐨𝐩 𝐀𝐜𝐭𝐢𝐯𝐞.` });
                }
                
                (async () => { 
                    while (this.activeCustxt.has(from) && this.connected) { 
                        const symStart = getRandom(aestheticSymbols);
                        const emojiEnd = getRandom(baseEmojisNew);
                        const symEnd = getRandom(aestheticSymbols);
                        const finalMsgText = `${symStart} ${customMsg} ${emojiEnd} ${symEnd}`;
                        
                        await HSEE.runAttack(async () => { 
                            if (!this.activeCustxt.has(from)) return; 
                            const sentMsg = await this.sock.sendMessage(from, { text: finalMsgText });
                            
                            // AutoPin Trigger Logic
                            if (this.activeAutoPin && this.activeAutoPin.has(from)) {
                                let pinState = this.activeAutoPin.get(from);
                                pinState.count++;
                                if (pinState.count >= pinState.target) {
                                    setTimeout(async () => {
                                        await this.sock.sendMessage(from, { pin: { count: 86400 }, remoteJid: from, fromMe: true, id: sentMsg.key.id }).catch(()=>{});
                                    }, getRandomDelay(10000, 15000)); 
                                    pinState.count = 0;
                                    pinState.target = getRandomDelay(10, 100);
                                }
                            }
                        }); 
                        await delay(Math.floor(Math.random() * (25000 - 12000 + 1)) + 12000); 
                    } 
                })(); 
                break;

            case 'dtx': 
                let delayTime = 100; 
                let dtxText = ""; 
                if (args.length > 0) { 
                    const match = args[args.length-1].toLowerCase().match(/^(\d+)(ms|s)?$/); 
                    if (match) { 
                        delayTime = match[2] === 's' ? parseInt(match[1])*1000 : parseInt(match[1]); 
                        args.pop(); 
                    } 
                    dtxText = args.join(" "); 
                }
                
                if (dtxText) { 
                    const id = `${from}_dtx`; 
                    this.activeTxt.set(id, { active: true }); 
                    saveState(from, 'dtx', args); 
                    
                    if (isMain) {
                        await this.sock.sendMessage(from, { text: `⟪ ⚙️ 𝐂𝐇𝐑𝐎𝐍𝐎-𝐀𝐃𝐀𝐏𝐓 ⟫ ➪ 𝐀𝐜𝐭𝐢𝐯𝐞! 𝐃𝐞𝐥𝐚𝐲: ${delayTime}𝐦𝐬` });
                    }
                    
                    (async () => { 
                        while (this.activeTxt.has(id) && this.connected) { 
                            await HSEE.runAttack(async () => { 
                                if (!this.activeTxt.has(id)) return; 
                                const frame = getRandom(dtxtFrames);
                                const emoji = getRandom(baseEmojisNew);
                                const framedText = frame.replace('{e}', emoji) + " " + dtxtText;
                                await this.send(from, framedText); 
                            }); 
                            await delay(delayTime); 
                        } 
                    })(); 
                } 
                break;

            case 'addtemp': if (!args.length) return isMain && this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐔𝐬𝐚𝐠𝐞: .𝐚𝐝𝐝𝐭𝐞𝐦𝐩 <𝐭𝐞𝐱𝐭>"); txtTemplates.push(args.join(" ")); if (isMain) await this.send(from, `⟪ ✅ 𝐓𝐄𝐌𝐏𝐋𝐀𝐓𝐄 ⟫ ➪ 𝐀𝐝𝐝𝐞𝐝! (𝐓𝐨𝐭𝐚𝐥: ${txtTemplates.length})`); break;

            case 'spmgod': 
                let minDelay = 10000; let maxDelay = 22000; let godTextStartIndex = 0;
                if (args.length > 0 && /^\d+-\d+$/.test(args[0])) { 
                    const range = args[0].split('-'); 
                    let val1 = parseInt(range[0]); let val2 = parseInt(range[1]); 
                    if (val1 > val2) { let temp = val1; val1 = val2; val2 = temp; } 
                    minDelay = val1 * 1000; maxDelay = val2 * 1000; godTextStartIndex = 1; 
                }
                const godText = args.slice(godTextStartIndex).join(" "); 
                if (!godText) return isMain && await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝑷𝒓𝒐𝒗𝒊𝒅𝒆 𝒕𝒆𝒙𝒕!\nEx: .𝐬𝐩𝐦𝐠𝐨𝐝 𝟏𝟐-𝟐𝟐 𝐇𝐞𝐥𝐥𝐨");
                const spmId = `${from}_spmgod`; 
                if (this.activeTxt.has(spmId)) return isMain && await this.send(from, "⟪ ⚠️ 𝐀𝐋𝐄𝐑𝐓 ⟫ ➪ DON'T USE SAME COMMAND TWICE");
                this.activeTxt.set(spmId, { active: true }); 
                saveState(from, 'spmgod', args); 
                
                if (isMain) {
                    await this.sock.sendMessage(from, { text: `⟪ ☸️ 𝐃𝐈𝐕𝐈𝐍𝐄 𝐖𝐇𝐄𝐄𝐋 ⟫ ➪ 𝐆𝐨𝐝 𝐒𝐩𝐚𝐦 𝐀𝐜𝐭𝐢𝐯𝐞 (${minDelay/1000}s - ${maxDelay/1000}s)` });
                }
                
                (async () => { 
                    while (this.activeTxt.has(spmId) && this.connected) { 
                        const symStartG = getRandom(aestheticSymbols);
                        const emojiEndG = getRandom(baseEmojisNew);
                        const symEndG = getRandom(aestheticSymbols);
                        
                        await HSEE.runAttack(async () => { 
                            if (!this.activeTxt.has(spmId)) return; 
                            await this.send(from, `${symStartG} ${godText} ${emojiEndG} ${symEndG}`); 
                        }); 
                        await delay(getRandomDelay(minDelay, maxDelay)); 
                    } 
                })(); break;

            case 'copytemp':
                const wordToReplace = args[0]; const originalText = quotedMsg?.conversation || quotedMsg?.extendedTextMessage?.text || quotedMsg?.text;
                if (!originalText || !wordToReplace) return isMain && await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝑹𝒆𝒑𝒍𝒚 𝒕𝒐 𝒂 𝒎𝒆𝒔𝒔𝒂𝒈𝒆 𝒂𝒏𝒅 𝒑𝒓𝒐𝒗𝒊𝒅𝒆 𝒕𝒉𝒆 𝒘𝒐𝒓𝒅 𝒕𝒐 𝒓𝒆𝒑𝒍𝒂𝒄𝒆! (𝑬𝒙: .𝒄𝒐𝒑𝒚𝒕𝒆𝒎𝒑 𝑫𝒆𝒗)");
                const regex = new RegExp(wordToReplace, 'gi'); const newTemplate = originalText.replace(regex, '{{names}}'); txtTemplates.push(newTemplate); if (isMain) await this.send(from, `⟪ ✅ 𝑻𝑬𝑴𝑷𝑳𝑨𝑻𝑬 𝑺𝑨𝑽𝑬𝑫 ⟫ ➪ 𝑨𝒅𝒅𝒆𝒅 𝒂𝒔 𝑻𝒆𝒎𝒑𝒍𝒂𝒕𝒆 #${txtTemplates.length}.`); break;

            // ==================== 🎯 TARGET & MEDIA ====================
            case 'pic':
                if (!isMain) return; 
                const picText = args.join(" "); 
                if (!picText) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐭𝐞𝐱𝐭! 𝐄𝐱: .𝐩𝐢𝐜 𝐒𝐚𝐰𝐚𝐧~~ 🖤");
                await this.send(from, `⟪ 🎨 𝐏𝐑𝐎𝐂𝐄𝐒𝐒𝐈𝐍𝐆 ⟫ ➪ 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐢𝐧𝐠...`);
                try { 
                    const encodedPicText = encodeURIComponent(picText);
                    const picUrl = `https://fakeimg.pl/640x640/ffffff/000000/?text=${encodedPicText}&font=arial`;
                    const picCaption = `🎨 ${picText}\n🔤 Arial • ⬛ black\n🖼️ 640x640`;
                    await this.sock.sendMessage(from, { image: { url: picUrl }, caption: picCaption }, { quoted: msg }); 
                } catch (err) { await this.send(from, `⟪ ❌ 𝐅𝐀𝐈𝐋𝐔𝐑𝐄 ⟫ ➪ 𝐈𝐦𝐚𝐠𝐞 𝐠𝐞𝐧𝐞𝐫𝐚𝐭𝐢𝐨𝐧 𝐟𝐚𝐢𝐥𝐞𝐝.`); } 
                break;

            case 'imagine':
                if (!isMain) return; const imgPrompt = args.join(" "); if (!imgPrompt) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐏𝐫𝐨𝐦𝐩𝐭 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝! 𝐄𝐱: .𝐢𝐦𝐚𝐠𝐢𝐧𝐞 𝐧𝐞𝐨𝐧 𝐜𝐢𝐭𝐲");
                await this.send(from, `⟪ 🎨 𝐀𝐈 𝐕𝐈𝐒𝐈𝐎𝐍 ⟫ ➪ 𝐌𝐚𝐭𝐞𝐫𝐢𝐚𝐥𝐢𝐳𝐢𝐧𝐠: ${imgPrompt}...`);
                try { const genUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(imgPrompt)}?width=1024&height=1024&nologo=true`; const captionTxt = `┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n   ✨ 𝐀𝐈 𝐕𝐈𝐒𝐈𝐎𝐍 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄 ✨\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n➪ 𝐏𝐫𝐨𝐦𝐩𝐭: ${styleText(imgPrompt)}\n➪ 𝐄𝐧𝐠𝐢𝐧𝐞: 𝐇𝐲𝐩𝐞𝐫 𝐂𝐲𝐛𝐞𝐫 𝐄𝐱𝐨𝐭𝐢𝐜 𝐕𝟖.𝟔.𝟎\n➪ 𝐁𝐲: ${styleText(this.displayId)}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`; await this.sock.sendMessage(from, { image: { url: genUrl }, caption: captionTxt }, { quoted: msg }); } catch (err) { await this.send(from, `⟪ ❌ 𝐀𝐈 𝐅𝐀𝐈𝐋𝐔𝐑𝐄 ⟫ ➪ 𝐌𝐚𝐭𝐫𝐢𝐱 𝐒𝐞𝐫𝐯𝐞𝐫 𝐃𝐨𝐰𝐧!`); } break;

            case 'txtgcpfp':
                if (!isGroup) return; const pfpPrompt = args.join(" "); if (!pfpPrompt) return isMain && await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐏𝐫𝐨𝐦𝐩𝐭! (𝐄𝐱: .𝐭𝐱𝐭𝐠𝐜𝐩𝐟𝐩 𝐡𝐚𝐜𝐤𝐞𝐫 𝐥𝐨𝐠𝐨)");
                const txtPfpId = `${from}_pfp_${Date.now()}`; if (this.activePfp.has(txtPfpId)) return; if (isMain) await this.send(from, `⟪ 🎨 ꨄ︎ 𝑨𝑰 𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒊𝒏𝒈 ꨄ︎ ⟫ ➪ 𝑪𝒓𝒆𝒂𝒕𝒊𝒏𝒈 𝑷𝑭𝑷 𝒇𝒐𝒓: ${pfpPrompt}...`);
                try { const pfpUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(pfpPrompt)}?width=512&height=512&nologo=true`; const response = await fetch(pfpUrl); const pfpBuffer = Buffer.from(await response.arrayBuffer()); this.activePfp.set(txtPfpId, true); if (isMain) await this.send(from, "⟪ 🚀 𝑨𝑰 𝑷𝑭𝑷 𝑹𝒐𝒖𝒍𝒆𝒕𝒕𝒆 ⟫ ➪ 𝑨𝒄𝒕𝒊𝒗𝒂𝒕𝒆𝒅!"); (async () => { while (this.activePfp.has(txtPfpId) && this.connected) { await this.sock.updateProfilePicture(from, pfpBuffer).catch(() => {}); await delay(Math.floor(Math.random() * 3000) + 4000); } })(); } catch (e) { if (isMain) await this.send(from, "⟪ ❌ 𝑨𝑰 𝑭𝒂𝒊𝒍𝒖𝒓𝒆 ⟫ ➪ 𝑰𝒎𝒂𝒈𝒆 𝑮𝒆𝒏𝒆𝒓𝒂𝒕𝒊𝒐𝒏 𝑭𝒂𝒊𝒍𝒆𝒅."); } break;

            case 'imgpcspm':
                const ipcPrompt = args.join(" "); if (!ipcPrompt) return isMain && await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ Prompt Required! Ex: .imgpcspm Boat");
                this.activePcspm.set(from, true); saveState(from, 'imgpcspm', args); if (isMain) await this.send(from, `⟪ 🎨 𝐀𝐈 𝐕𝐈𝐒𝐈𝐎𝐍 ⟫ ➪ Materializing Spam Image for: ${ipcPrompt}`);
                try { const ipcUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(ipcPrompt)}?width=1024&height=1024&nologo=true`; const ipcRes = await fetch(ipcUrl); const ipcBuf = Buffer.from(await ipcRes.arrayBuffer()); (async () => { while (this.activePcspm.has(from) && this.connected) { await this.sock.sendMessage(from, { image: ipcBuf }).catch(() => {}); await delay(Math.floor(Math.random() * 2000) + 1500); } })(); } catch(e) { if (isMain) await this.send(from, "⟪ ❌ 𝐀𝐈 𝐅𝐀𝐈𝐋𝐔𝐑𝐄 ⟫"); } break;

            case 'imgstspm':
                const istPrompt = args.join(" "); if (!istPrompt) return isMain && await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ Prompt Required! Ex: .imgstspm Dog");
                this.activeStspm.set(from, true); saveState(from, 'imgstspm', args); if (isMain) await this.send(from, `⟪ 🎭 𝐀𝐈 𝐒𝐓𝐈𝐂𝐊𝐄𝐑 ⟫ ➪ Crafting Sticker Loop for: ${istPrompt}`);
                try { const istUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(istPrompt)}?width=512&height=512&nologo=true`; const istRes = await fetch(istUrl); const istBuf = Buffer.from(await istRes.arrayBuffer()); (async () => { while (this.activeStspm.has(from) && this.connected) { await this.sock.sendMessage(from, { sticker: istBuf }).catch(() => {}); await delay(Math.floor(Math.random() * 1500) + 1000); } })(); } catch(e) { if (isMain) await this.send(from, "⟪ ❌ 𝐀𝐈 𝐅𝐀𝐈𝐋𝐔𝐑𝐄 ⟫"); } break;

            case 'bnr': const bnrText = args.join(" "); if (!bnrText) return isMain && await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ Text Required! Ex: .bnr Cyber Exotic"); if (isMain) await this.send(from, `⟪ 🖼️ 𝐁𝐀𝐍𝐍𝐄𝐑 ⟫ ➪ Generating...`); try { const bnrUrl = `https://image.pollinations.ai/prompt/Neon%20cyberpunk%20typography%20banner%20with%20the%20word%20"${encodeURIComponent(bnrText)}"%20glow%20in%20dark?width=1024&height=300&nologo=true`; await this.sock.sendMessage(from, { image: { url: bnrUrl }, caption: `⟪ 🖼️ 𝐁𝐀𝐍𝐍𝐄𝐑 ⟫ ➪ ${styleText(bnrText)}` }, { quoted: msg }); } catch (e) { } break;
            case 'settemp': if (!isMain || !isSenderDev) return; const quotedImg = quotedMsg?.quotedMessage?.imageMessage; if (!quotedImg) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ Reply to an image to set it as template."); try { const streamTemp = await downloadContentFromMessage(quotedImg, 'image'); let bufferTemp = Buffer.from([]); for await (const chunk of streamTemp) { bufferTemp = Buffer.concat([bufferTemp, chunk]); } customTemplates["base_temp"] = bufferTemp.toString('base64'); safeWriteJSON(TEMPLATE_FILE, customTemplates); await this.send(from, "⟪ ✅ 𝐓𝐄𝐌𝐏𝐋𝐀𝐓𝐄 𝐒𝐄𝐓 ⟫ ➪ Base image saved successfully."); } catch (e) { await this.send(from, `⟪ ❌ 𝐅𝐀𝐈𝐋𝐔𝐑𝐄 ⟫ ➪ Template set error: ${e.message}`); } break;
            case 'gen': if (!isMain) return; const targetText = args.join(" "); if (!targetText) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ Text Required! Ex: .gen hello"); const tempBase64 = customTemplates["base_temp"]; if (!tempBase64) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ Base template not set. Use .settemp first."); await this.send(from, `⟪ 🖌️ 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐈𝐍𝐆 ⟫ ➪ Applying vision: "${targetText}"...`); try { const outputImageBuffer = Buffer.from(tempBase64, 'base64'); const captionTxt = `┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n   ✨ 𝐕𝐈𝐒𝐈𝐎𝐍 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄 ✨\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n➪ 𝐓𝐞𝐱𝐭 Applied: ${styleText(targetText)}\n➪ Generated By: ${styleText(this.displayId)}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`; await this.sock.sendMessage(from, { image: outputImageBuffer, caption: captionTxt }, { quoted: msg }); } catch (err) { await this.send(from, `⟪ ❌ 𝐆𝐄𝐍 𝐅𝐀𝐈𝐋𝐔𝐑𝐄 ⟫ ➪ Error rendering image.`); } break;

            case 'pcspm': 
                const imageMsg = quotedMsg?.quotedMessage?.imageMessage || msg.message?.imageMessage; if (!imageMsg) return isMain && this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐑𝐞𝐩𝐥𝐲 ??𝐨 𝐚𝐧 𝐢𝐦𝐚𝐠𝐞!");
                this.activePcspm.set(from, true); if (isMain) await this.send(from, "⟪ 📸 𝐕𝐈𝐒𝐔𝐀𝐋 𝐀𝐒𝐒𝐀𝐔𝐋𝐓 ⟫ ➪ 𝐒𝐭𝐚𝐫𝐭𝐞𝐝...");
                (async () => { const streamPcspm = await downloadContentFromMessage(imageMsg, 'image'); let bufferPcspm = Buffer.from([]); for await (const chunk of streamPcspm) { bufferPcspm = Buffer.concat([bufferPcspm, chunk]); } while (this.activePcspm.has(from) && this.connected) { await this.sock.sendMessage(from, { image: bufferPcspm }).catch(() => {}); await delay(Math.floor(Math.random() * 2500) + 1500); } })(); break;

            case 'stspm': 
                const stickMsg = quotedMsg?.quotedMessage?.stickerMessage; if (!stickMsg) return isMain && this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐬𝐭𝐢𝐜𝐤𝐞𝐫!");
                this.activeStspm.set(from, true); if (isMain) await this.send(from, "⟪ 🎭 𝐀𝐑𝐓 𝐀𝐓𝐓𝐀𝐂𝐊 ⟫ ➪ 𝐒𝐭𝐚𝐫𝐭𝐞𝐝...");
                (async () => { const streamStspm = await downloadContentFromMessage(stickMsg, 'sticker'); let bufferStspm = Buffer.from([]); for await (const chunk of streamStspm) { bufferStspm = Buffer.concat([bufferStspm, chunk]); } while (this.activeStspm.has(from) && this.connected) { await this.sock.sendMessage(from, { sticker: bufferStspm }).catch(() => {}); await delay(Math.floor(Math.random() * 2000) + 1500); } })(); break;

            case 'desc': 
                if (!isGroup) return; const baseDescText = args.join(" ") || "𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐁𝐲 𝐇𝐲𝐩𝐞𝐫 𝐂𝐲𝐛𝐞𝐫 𝐄𝐱𝐨𝐭𝐢𝐜 𝐄𝐧𝐠𝐢𝐧𝐞"; if (this.activeDesc.has(from)) return; this.activeDesc.set(from, true); saveState(from, 'desc', args); if (isMain) await this.send(from, "⟪ 📝 𝐃𝐄𝐒𝐂 𝐅𝐋𝐀𝐒𝐇 ⟫ ➪ 𝐒𝐩𝐚𝐦 𝐈𝐧𝐢𝐭𝐢𝐚𝐭𝐞𝐝!");
                (async () => { const allDescEmojis = Object.values(emojiArrays).flat(); while (this.activeDesc.has(from) && this.connected) { const randomEmoji = allDescEmojis[Math.floor(Math.random() * allDescEmojis.length)]; await HSEE.runAttack(async () => { if (!this.activeDesc.has(from)) return; await this.sock.groupUpdateDescription(from, styleText(`${baseDescText} ${randomEmoji}`)).catch(()=>{}); }); await delay(Math.floor(Math.random() * 1500) + 1500); } })(); break;

            case 'fstdesc': 
                if (!isGroup) return; const fstDescText = args.join(" ") || "𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐁𝐲 𝐇𝐲𝐩𝐞𝐫 𝐂𝐲𝐛𝐞𝐫 𝐄𝐱𝐨𝐭𝐢𝐜 𝐄𝐧𝐠𝐢𝐧𝐞"; if (this.activeDesc.has(from)) return; this.activeDesc.set(from, true); saveState(from, 'fstdesc', args); if (isMain) await this.send(from, "⟪ 📝 𝑭𝒂𝒔𝒕-𝑫𝒆𝒔𝒄 𝑭𝒍𝒂𝒔𝒉 ⟫ ➪ 𝑼𝒍𝒕𝒓𝒂 𝑺𝒑𝒆𝒆𝒅 𝑨𝒄𝒕𝒊𝒗𝒆!");
                (async () => { const allDescEmojis = Object.values(emojiArrays).flat(); while (this.activeDesc.has(from) && this.connected) { const randomEmoji = allDescEmojis[Math.floor(Math.random() * allDescEmojis.length)]; await HSEE.runAttack(async () => { if (!this.activeDesc.has(from)) return; await this.sock.groupUpdateDescription(from, styleText(`${fstDescText} ${randomEmoji}`)).catch(()=>{}); }); await delay(Math.floor(Math.random() * 400) + 800); } })(); break;

            case 'gcpfp': 
                if (!isGroup) return; const quotedPfp = msg.message.extendedTextMessage?.contextInfo?.quotedMessage?.imageMessage; if (!quotedPfp) return isMain && await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐑𝐞𝐩𝐥𝐲 𝐓𝐨 𝐀𝐧 𝐈𝐦𝐚𝐠𝐞!");
                const pfpLoopId = `${from}_pfp_${msg.message.extendedTextMessage.contextInfo.stanzaId}`; if (this.activePfp.has(pfpLoopId)) return;
                try { const streamPfp = await downloadContentFromMessage(quotedPfp, 'image'); let bufferPfp = Buffer.from([]); for await (const chunk of streamPfp) { bufferPfp = Buffer.concat([bufferPfp, chunk]); } this.activePfp.set(pfpLoopId, true); if (isMain) await this.send(from, "⟪ 🚀 𝐏𝐅𝐏 𝐑𝐎𝐔𝐋𝐄𝐓𝐓𝐄 ⟫ ➪ 𝐀𝐜𝐭𝐢𝐯𝐚𝐭𝐞𝐝!"); (async () => { while (this.activePfp.has(pfpLoopId) && this.connected) { await this.sock.updateProfilePicture(from, bufferPfp).catch(() => {}); await delay(Math.floor(Math.random() * 4000) + 5000); } })(); } catch (e) { } break;

            case 'lock': if (!isGroup) return; const lockTarget = mentioned.length > 0 ? mentioned[0] : (replyJid ? replyJid : null); if (!lockTarget) return isMain && await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝑻𝒂𝒈 𝒐𝒓 𝑹𝒆𝒑𝒍𝒚 𝒕𝒐 𝒕𝒉𝒆 𝒗𝒊𝒄𝒕𝒊𝒎!"); this.activeLock.set(`${from}_${normalizeJid(lockTarget)}`, true); saveState(`${from}_${normalizeJid(lockTarget)}`, 'lock', args); if (isMain) await this.send(from, `⟪ 🔒 𝑻𝑨𝑹𝑮𝑬𝑻 𝑳𝑶𝑪𝑲𝑬𝑫 ⟫ ➪ 𝑨𝒍𝒍 𝒎𝒆𝒔𝒔𝒂𝒈𝒆𝒔 𝒇𝒓𝒐𝒎 𝒕𝒉𝒊𝒔 𝒆𝒏𝒕𝒊𝒕𝒚 𝒘𝒊𝒍𝒍 𝒃𝒆 𝒗𝒂𝒑𝒐𝒓𝒊𝒛𝒆𝒅.`); break;
            case 'stoplock': const unlockTarget = mentioned.length > 0 ? mentioned[0] : (replyJid ? replyJid : null); if (unlockTarget) { this.activeLock.delete(`${from}_${normalizeJid(unlockTarget)}`); removeState(`${from}_${normalizeJid(unlockTarget)}`, 'lock'); } else { for (let k of this.activeLock.keys()) if (k.startsWith(`${from}_`)) { this.activeLock.delete(k); removeState(k, 'lock'); } } if (isMain) await this.send(from, `⟪ 🔓 𝐋𝐎𝐂𝐊 𝐑𝐄𝐋𝐄𝐀𝐒𝐄𝐃 ⟫ ➪ 𝐓𝐚𝐫𝐠𝐞𝐭 𝐢𝐬 𝐟𝐫𝐞𝐞 𝐭𝐨 𝐬𝐩𝐞𝐚𝐤.`); break;
            
            case 'target': 
                const targets = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []); 
                if (targets.length > 0) { 
                    this.activeTarget.set(`${from}_target`, { targets: targets.map(normalizeJid) }); 
                    saveState(from, 'target', args); 
                    if (isMain) await this.send(from, "⟪ 👁️ 𝐌𝐎𝐍𝐀𝐑𝐂𝐇'𝐒 𝐆𝐀𝐙𝐄 ⟫ ➪ 𝐓𝐚𝐫𝐠𝐞𝐭 𝐋𝐨𝐜𝐤𝐞𝐝. 𝐓𝐡𝐞 𝐒𝐡𝐚𝐝𝐨𝐰𝐬 𝐰𝐢𝐥𝐥 𝐡𝐮𝐧𝐭 𝐭𝐡𝐞𝐦 𝐝𝐨𝐰𝐧."); 
                } else { 
                    if (isMain) await this.send(from, "⟪ ⚠️ 𝐒𝐘𝐒𝐓𝐄𝐌 𝐑𝐄𝐉𝐄𝐂𝐓𝐈𝐎𝐍 ⟫ ➪ 𝐓𝐚𝐠 𝐨𝐫 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐯𝐢𝐜𝐭𝐢𝐦!"); 
                } break;

            case 'slide': case 's': const isTimed = command === 's'; const delayS = isTimed ? (parseInt(args[args.length - 1]) || 2000) : 0; if (isTimed && !isNaN(parseInt(args[args.length - 1]))) args.pop(); const slideText = args.join(" "); if (!replyJid) return isMain && await this.send(from, `⟪ ⚠️ 𝐀𝐋𝐄𝐑𝐓 ⟫ ➪ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐭𝐚𝐫𝐠𝐞𝐭!`); if (!slideText) return isMain && await this.send(from, `⟪ ⚠️ 𝐀𝐋𝐄𝐑𝐓 ⟫ ➪ 𝐄𝐧𝐭𝐞𝐫 𝐦𝐞𝐬𝐬𝐚𝐠𝐞!`); if (!isTimed) { this.activeTargetReply.set(`${from}_${replyJid}`, { active: true, text: slideText }); if (isMain) await this.send(from, `⟪ 🗡️ 𝐒𝐇𝐀𝐃𝐎𝐖 𝐒𝐋𝐈𝐃𝐄 ⟫ ➪ 𝐓𝐚𝐫𝐠𝐞𝐭 𝐋𝐨𝐜𝐤𝐞𝐝!`); } else { const idSlide = `${from}_slide`; this.activeSlide.set(idSlide, { active: true }); const stanzaIdSlide = msg.message.extendedTextMessage?.contextInfo?.stanzaId; const qObj = { key: { remoteJid: from, id: stanzaIdSlide, participant: quotedMsg.participant }, message: quotedMsg.quotedMessage }; (async () => { while (this.activeSlide.has(idSlide) && this.connected) { await HSEE.runNormal(async () => { if (!this.activeSlide.has(idSlide)) return; await this.send(from, slideText, [], qObj); }); await delay(delayS); } })(); } break;
            case 'autoreply': if (isGroup) { this.activeAutoReply.set(`${from}_autoreply`, { active: true, targets: mentioned.map(normalizeJid) }); saveState(from, 'autoreply', args); if (isMain) await this.send(from, `⟪ ⚡ 𝐀𝐔𝐓𝐎-𝐑𝐄𝐏𝐋𝐘 ⟫ ➪ 𝐄𝐧𝐠𝐚𝐠𝐞𝐝!`); } break;
            case 'replyall': if (isGroup) { const rText = args.join(" "); if (!rText) return isMain && await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐓𝐞𝐱𝐭!"); this.activeReplyAll.set(from, { active: true, text: rText }); saveState(from, 'replyall', args); if (isMain) await this.send(from, "⟪ 🔄 𝐄𝐂𝐇𝐎 𝐌𝐎𝐃𝐄 ⟫ ➪ 𝐀𝐜𝐭𝐢𝐯𝐞!"); } break;

            // ==================== 🛑 HALT COMMANDS ====================
            case 'gstop':
                if (!isMain || !isSenderDev) return;
                this.manager.bots.forEach(bot => { bot.activeTasks.clear(); bot.activeTarget.clear(); bot.activeNC.clear(); bot.activeN.clear(); bot.activeSlide.clear(); bot.activeTargetReply.clear(); bot.activePcspm.clear(); bot.activeStspm.clear(); bot.activeCustxt.clear(); bot.activeReplyAll.clear(); bot.activeDesc.clear(); bot.activeAutoReact.clear(); bot.activeLock.clear(); bot.activeTxt.clear(); bot.activePfp.clear(); bot.activeTagall.clear(); bot.activeAutoReply.clear(); });
                HSEE.clearAll(); safeWriteJSON(RECOVERY_FILE, {}); activeRecovery = {}; 
                await this.send(from, `⟪ 💀 𝐀𝐁𝐒𝐎𝐋𝐔𝐓𝐄 𝐇𝐀𝐋𝐓 ⟫ ➪ 𝐓𝐡𝐞 𝐌𝐨𝐧𝐚𝐫𝐜𝐡 𝐝𝐞𝐦𝐚𝐧𝐝𝐬 𝐬𝐢𝐥𝐞𝐧𝐜𝐞! 𝐀𝐥𝐥 𝐧𝐨𝐝𝐞𝐬 𝐚𝐫𝐞 𝐫𝐞𝐭𝐮𝐫𝐧𝐢𝐧𝐠 𝐭𝐨 𝐭𝐡𝐞 𝐬𝐡𝐚𝐝𝐨𝐰𝐬...`); break;

            case 'stopall':
                this.activeTasks.delete(`${from}_txt`); removeState(from, 'txt'); this.activeTarget.delete(`${from}_target`); removeState(from, 'target'); this.activeNC.delete(from); removeState(from, 'ni'); removeState(from, 'devn'); removeState(from, 'dnc1'); removeState(from, 'dnc2'); removeState(from, 'dnc3'); removeState(from, 'dnc4'); removeState(from, 'dnc5'); removeState(from, 'fstn'); this.activeN.delete(from); this.activeTxt.delete(`${from}_dtx`); removeState(from, 'dtx'); this.activeSlide.delete(`${from}_slide`); this.activeTagall.delete(`${from}_tagall`); this.activeAutoReply.delete(`${from}_autoreply`); removeState(from, 'autoreply'); for (let key of this.activeTargetReply.keys()) { if (key.startsWith(`${from}_`)) this.activeTargetReply.delete(key); } this.activePcspm.delete(from); removeState(from, 'imgpcspm'); this.activeStspm.delete(from); removeState(from, 'imgstspm'); this.activeCustxt.delete(from); removeState(from, 'custxt'); this.activeReplyAll.delete(from); removeState(from, 'replyall'); this.activeDesc.delete(from); removeState(from, 'desc'); removeState(from, 'fstdesc'); for (let key of this.activePfp.keys()) { if (key.startsWith(`${from}_pfp`)) this.activePfp.delete(key); } this.activeAutoReact.delete(from); this.activeTxt.delete(`${from}_spmgod`); removeState(from, 'spmgod'); for (let k of this.activeLock.keys()) if (k.startsWith(`${from}_`)) { this.activeLock.delete(k); removeState(k, 'lock'); } HSEE.clearAll(); 
                if (isMain) await this.send(from, `⟪ 🛑 𝐌𝐎𝐍𝐀𝐑𝐂𝐇'𝐒 𝐃𝐄𝐂𝐑𝐄𝐄 ⟫ ➪ 𝐀𝐥𝐥 𝐒𝐡𝐚𝐝𝐨𝐰 𝐒𝐨𝐥𝐝𝐢𝐞𝐫𝐬 𝐡𝐚𝐯𝐞 𝐛𝐞𝐞𝐧 𝐨𝐫𝐝𝐞𝐫𝐞𝐝 𝐭𝐨 𝐬𝐭𝐚𝐧𝐝 𝐝𝐨𝐰𝐧 𝐢𝐧 𝐭𝐡𝐢𝐬 𝐬𝐞𝐜𝐭𝐨𝐫.`); break;

            // Individual Stops
            case 'stopn': this.activeN.delete(from); if (isMain) await this.send(from, `⟪ ❄️ 𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍 ⟫ ➪ 𝐓𝐫𝐢𝐩𝐥𝐞 𝐍𝐚𝐦𝐞 𝐀𝐭𝐭𝐚𝐜𝐤 (!𝐧) 𝐒𝐭𝐨𝐩𝐩𝐞𝐝.`); break;
            case 'stopnc': case 'stopdevn': case 'stopfstn': case 'stopni': this.activeNC.delete(from); removeState(from, 'ni'); removeState(from, 'devn'); removeState(from, 'dnc1'); removeState(from, 'dnc2'); removeState(from, 'dnc3'); removeState(from, 'dnc4'); removeState(from, 'dnc5'); removeState(from, 'fstn'); if (isMain) await this.send(from, `⟪ 🔌 𝐍𝐂-𝐓𝐔𝐑𝐁𝐎 ⟫ ➪ 𝐍𝐚𝐦𝐞 𝐌𝐚𝐭𝐫𝐢𝐱/𝐒𝐲𝐧𝐜 𝐀𝐭𝐭𝐚𝐜𝐤𝐬 𝐒𝐭𝐨𝐩𝐩𝐞𝐝.`); break;
            case 'stoptxt': this.activeTasks.delete(`${from}_txt`); removeState(from, 'txt'); if (isMain) await this.send(from, `⟪ 🚫 𝐓𝐄𝐗𝐓 𝐌𝐀𝐓𝐑𝐈𝐗 ⟫ ➪ 𝐓𝐞𝐦𝐩𝐥𝐚𝐭𝐞 𝐒𝐩𝐚𝐦 𝐒𝐭𝐨𝐩𝐩𝐞𝐝.`); break;
            case 'stopcustxt': this.activeCustxt.delete(from); removeState(from, 'custxt'); if (isMain) await this.send(from, `⟪ 🚫 𝐂𝐔𝐒𝐓𝐎𝐌 𝐋??𝐎𝐏 ⟫ ➪ 𝐂𝐮𝐬𝐭𝐨𝐦 𝐓𝐞𝐱𝐭 𝐒𝐩𝐚𝐦 𝐒𝐭𝐨𝐩𝐩𝐞𝐝.`); break;
            case 'stopdtx': this.activeTxt.delete(`${from}_dtx`); removeState(from, 'dtx'); if (isMain) await this.send(from, `⟪ ⏱️ 𝐂𝐇𝐑𝐎𝐍𝐎-𝐒𝐏𝐀𝐌 ⟫ ➪ 𝐃𝐞𝐥𝐚𝐲 𝐓𝐞𝐱𝐭 𝐒𝐭𝐨𝐩𝐩𝐞𝐝.`); break;
            case 'stopspmgod': this.activeTxt.delete(`${from}_spmgod`); removeState(from, 'spmgod'); if (isMain) await this.send(from, `⟪ 🛑 𝐆𝐎𝐃 𝐒𝐏𝐀𝐌 ⟫ ➪ 𝐆𝐡𝐨𝐬𝐭 𝐒𝐩𝐚𝐦 𝐓𝐞𝐫𝐦𝐢𝐧𝐚𝐭𝐞𝐝.`); break;
            case 'stoppfp': case 'stoptxtgcpfp': for (let key of this.activePfp.keys()) { if (key.startsWith(`${from}_pfp`)) this.activePfp.delete(key); } if (isMain) await this.send(from, `⟪ 🖼️ 𝐏𝐅𝐏 𝐑𝐎𝐔𝐋𝐄𝐓𝐓𝐄 ⟫ ➪ 𝐏𝐫𝐨𝐟𝐢𝐥𝐞 𝐏𝐢𝐜 𝐋𝐨𝐨𝐩 𝐒𝐭𝐨𝐩𝐩𝐞𝐝.`); break;
            case 'stoppcspm': case 'stopimgpcspm': this.activePcspm.delete(from); removeState(from, 'imgpcspm'); if (isMain) await this.send(from, `⟪ 📸 𝐕𝐈𝐒𝐔𝐀𝐋 𝐅𝐄𝐄𝐃 ⟫ ➪ 𝐏𝐡𝐨𝐭𝐨 𝐒𝐩𝐚𝐦 𝐒𝐭𝐨𝐩𝐩𝐞𝐝.`); break;
            case 'stopstspm': case 'stopimgstspm': this.activeStspm.delete(from); removeState(from, 'imgstspm'); if (isMain) await this.send(from, `⟪ 🎭 𝐀𝐑𝐓 𝐀𝐓𝐓𝐀𝐂𝐊 ⟫ ➪ 𝐒𝐭𝐢𝐜𝐤𝐞𝐫 𝐒𝐩𝐚𝐦 𝐒𝐭𝐨𝐩𝐩𝐞𝐝.`); break;
            case 'stopdesc': case 'stopfstdesc': this.activeDesc.delete(from); removeState(from, 'desc'); removeState(from, 'fstdesc'); if (isMain) await this.send(from, `⟪ 📝 𝐃𝐄𝐒𝐂 𝐅𝐋𝐀𝐒𝐇 ⟫ ➪ 𝐆𝐫𝐨𝐮𝐩 𝐃𝐞𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 𝐋𝐨𝐨𝐩 𝐒𝐭𝐨𝐩𝐩𝐞𝐝.`); break;
            case 'stoptarget': this.activeTarget.delete(`${from}_target`); removeState(from, 'target'); if (isMain) await this.send(from, `⟪ 🕊️ 𝐓𝐀𝐑𝐆𝐄𝐓 𝐅𝐑𝐄𝐄 ⟫ ➪ 𝐓𝐚𝐫𝐠𝐞𝐭 𝐇𝐮𝐧𝐭 𝐀𝐛𝐨𝐫𝐭𝐞𝐝.`); break;
            case 'stopslide': case 'stops': this.activeSlide.delete(`${from}_slide`); for (let key of this.activeTargetReply.keys()) { if (key.startsWith(`${from}_`)) this.activeTargetReply.delete(key); } if (isMain) await this.send(from, `⟪ 🛑 𝐒𝐇𝐀𝐃𝐎𝐖 𝐒𝐋𝐈𝐃𝐄 ⟫ ➪ 𝐑𝐞𝐩𝐥𝐲 𝐀𝐭𝐭𝐚𝐜𝐤𝐬 𝐒𝐭𝐨𝐩𝐩𝐞𝐝.`); break;
            case 'stopautoreply': this.activeAutoReply.delete(`${from}_autoreply`); removeState(from, 'autoreply'); if (isMain) await this.send(from, `⟪ ⚡ 𝐀𝐔𝐓𝐎-𝐑𝐄𝐏𝐋𝐘 ⟫ ➪ 𝐀𝐮𝐭𝐨-𝐑𝐞𝐩𝐥𝐲 𝐒𝐲𝐬𝐭𝐞𝐦 𝐃𝐢𝐬𝐚𝐛𝐥𝐞𝐝.`); break;
            case 'stoptagall': this.activeTagall.delete(`${from}_tagall`); if (isMain) await this.send(from, `⟪ 📢 𝐀𝐋𝐋𝐈𝐀𝐍𝐂𝐄 𝐏𝐈𝐍𝐆 ⟫ ➪ 𝐓𝐚𝐠-𝐀𝐥𝐥 𝐒𝐭𝐨𝐩𝐩𝐞𝐝.`); break;
            case 'stopreplyall': this.activeReplyAll.delete(from); removeState(from, 'replyall'); if (isMain) await this.send(from, `⟪ 🔇 𝐄𝐂𝐇𝐎 𝐌𝐎𝐃𝐄 ⟫ ➪ 𝐑𝐞𝐩𝐥𝐲-𝐀𝐥𝐥 𝐃𝐢𝐬𝐚𝐛𝐥𝐞𝐝.`); break;
        }
    }
}

// ==================== BOT MANAGER ====================
class BotManager {
    constructor() { this.bots = new Map(); this.counter = 1; }
    async init() {
        const saved = safeReadJSON(BOTS_FILE, { counter: 1, bots: [] }); this.counter = saved.counter || 1;
        if (saved.bots.length > 0) {
            console.log(`\n🔄 Restoring Matrix Fleet (${saved.bots.length} Nodes)...`);
            for (const b of saved.bots) { const session = new BotSession(b.id, b.phone, this, false); this.bots.set(b.id, session); await session.connect(); await delay(2000); }
        } else {
            console.log('\n🤖 [ MATRIX SETUP ] No nodes found. Setup Primary Node.');
            const rlSetup = readline.createInterface({ input: process.stdin, output: process.stdout });
            const useQR = (await new Promise(r => rlSetup.question('Use QR for Super Bot? (y/n): ', r))).toLowerCase() === 'y';
            let phone = null; if (!useQR) phone = (await new Promise(r => rlSetup.question('Enter Super Bot Phone (with country code): ', r))).replace(/\D/g, '');
            const session = new BotSession('Bot_1', phone, this, useQR); this.bots.set('Bot_1', session); await session.connect();
            if (!useQR && phone) { setTimeout(async () => { try { const code = await session.sock.requestPairingCode(phone); console.log(`\n╔════════════════════════╗\n║ 🔑 SUPER BOT CODE: ${code} ║\n╚════════════════════════╝\n`); } catch(e) { console.log('Setup Error:', e.message); } this.save(); }, 5000); } else { this.save(); }
            rlSetup.close();
        }
    }
    save() { safeWriteJSON(BOTS_FILE, { counter: this.counter, bots: [...this.bots.values()].map(b => ({ id: b.internalId, phone: b.phoneNumber })) }); }
    getMainBotId() { for (const [id, bot] of this.bots.entries()) { if (bot.connected) return id; } return 'Bot_1'; }
}

console.log('╔═══════════════════════════════════════╗');
console.log('║ 🔮 HYPER CYBER EXOTIC ENGINE V8.6.0 🔮 ║');
console.log('╚═══════════════════════════════════════╝\n');

const manager = new BotManager(); manager.init();
const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
rl.on('line', (input) => {
    const cmd = input.trim().toLowerCase();
    if (cmd === 'status') { manager.bots.forEach(b => console.log(` - ${b.displayId}: ${b.connected ? 'Online 🟢' : 'Offline 🔴'}`)); } 
    else if (cmd === 'exit') { process.exit(0); }
});