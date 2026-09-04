import makeWASocket, { 
    useMultiFileAuthState, 
    DisconnectReason, 
    fetchLatestBaileysVersion,
    downloadContentFromMessage,
    jidNormalizedUser
} from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import pino from 'pino';
import fs from 'fs';
import readline from 'readline';
import PQueue from 'p-queue';
import { exec } from 'child_process';
import NodeCache from 'node-cache';
import os from 'os';
import yts from 'yt-search';
import axios from 'axios';

// ==================== 🪐 ULTRA ANTI-CRASH & RAM MANAGEMENT ====================
process.on('uncaughtException', (err) => console.log(`[⚠️ IMMUNE] ${err.message}`));
process.on('unhandledRejection', (r) => console.log(`[⚠️ IMMUNE] ${r}`));
process.on('warning', (warning) => console.warn('[WARNING]', warning.message));
process.setMaxListeners(0);

setInterval(() => {
    if (typeof global.gc === 'function') global.gc();
}, 60000);

// ==================== 📡 DATABASE & PERSISTENCE ====================
const ROLES_FILE = './data/roles.json';
const BOTS_FILE = './data/bots.json';
const CONFIG_FILE = './data/config.json';
const RECOVERY_FILE = './data/recovery.json';
const TEMPLATE_FILE = './data/templates.json';

function safeReadJSON(path, def) { 
    try { 
        if (fs.existsSync(path)) return JSON.parse(fs.readFileSync(path, 'utf8')); 
    } catch (e) {} 
    return def; 
}

function safeWriteJSON(path, data) { 
    try { 
        if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true }); 
        fs.writeFileSync(path, JSON.stringify(data, null, 2)); 
    } catch (e) {} 
}

let roles = safeReadJSON(ROLES_FILE, { owner: null, admins: [], subAdmins: [] });
let globalConfig = safeReadJSON(CONFIG_FILE, { prefix: '.' });
let customTemplates = safeReadJSON(TEMPLATE_FILE, {});
let activeRecovery = safeReadJSON(RECOVERY_FILE, {});
let GLOBAL_PREFIX = globalConfig.prefix;
let IS_BOT_SLEEPING = false;
let GLOBAL_LOCK = false;

// ==================== 👑 APNA NUMBER YAHAN DALEIN 👑 ====================
// 👇 Niche '91XXXXXXXXXX' ko hata kar apna number likhein (country code ke sath, bina + ya space ke)
const OWNER_NUMBER = '91XXXXXXXXXX'; // 👈👈👈 YAHAN APNA_NUMBER_YAHAN_DALO
const SOLE_OWNER_JID = `${OWNER_NUMBER}@s.whatsapp.net`;

// 🔑 SECRET DM CLAIM TRIGGER
const SECRET_CLAIM_KEY = '.deva';

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

function normalizeJid(jid) { 
    if (!jid) return ''; 
    return jid.includes(':') ? jid.split(':')[0] + '@s.whatsapp.net' : (jid.includes('@') ? jid : jid + '@s.whatsapp.net'); 
}

// Single Owner check
const isOwner = (jid) => {
    const norm = normalizeJid(jid);
    return norm === SOLE_OWNER_JID || (roles.owner ? normalizeJid(roles.owner) === norm : false);
};
const isAdmin = (jid) => isOwner(jid) || roles.admins.some(a => normalizeJid(a) === normalizeJid(jid));
const isSubAdmin = (jid) => roles.subAdmins.some(s => normalizeJid(s) === normalizeJid(jid));
const hasPerm = (jid) => isOwner(jid) || isAdmin(jid) || isSubAdmin(jid);

// ==================== 🔤 ALL FONTS MAP ====================
const fontMap = {
    'A':'𝐀','B':'𝐁','C':'𝐂','D':'𝐃','E':'𝐄','F':'𝐅','G':'𝐆','H':'𝐇','I':'𝐈','J':'𝐉','K':'𝐊','L':'𝐋','M':'𝐌','N':'𝐍','O':'𝐎','P':'𝐏','Q':'𝐐','R':'𝐑','S':'𝐒','T':'𝐓','U':'𝐔','V':'𝐕','W':'𝐖','X':'𝐗','Y':'𝐘','Z':'𝐙',
    'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ғ','g':'ɢ','h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ','s':'s','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ'
};
function styleText(text) { if (!text) return text; return text.replace(/[a-zA-Z]/g, c => fontMap[c] || c); }

const getRandom = (arr) => arr[Math.floor(Math.random() * arr.length)];
const microYield = () => new Promise(resolve => setImmediate(resolve));

function formatUptime(uptime) {
    let s = Math.floor(uptime % 60);
    let m = Math.floor((uptime / 60) % 60);
    let h = Math.floor((uptime / (60 * 60)) % 24);
    let d = Math.floor(uptime / (60 * 60 * 24));
    return `${d}d ${h}h ${m}m ${s}s`;
}

// ==================== 🎨 ALL MERGED SYMBOLS ====================
const specialSymbols = [
    'ֺּׅ𓏽⑅','಄','ᛝ','‎ꫂ᭪݁','𓏲ּ𝄢','ೀ','.✦ ݁˖','୭ ˚. ᵎᵎ','╰┈➤','༉‧₊˚.','𓂃 ࣪˖ ִֶָ 𓈈','.𖥔 ݁ ˖','ᝰ.ᐟ','˙.꒷.𖦹˙—','𑁍ࠬܓ','ִֶָ⿻.','｡𖦹°‧','ᯓ★','𓋜','۶ৎ','°˖➴','ִ ࣪𖤐','𓂃 ࣪˖ ִֶཐི༏ཋྀ󠀮','˚˖𓍢ִ໋🦢˚','˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—','ꫂ ၴႅၴ','˚ ༘ ೀ⋆｡˚','⊱ ۫ ׅ ✧','🎧ྀི♪⋆.✮','ᥫ᭡.🍥⋆🐇་༘🌷.ೃ࿔','˚.🎀༘⋆','.𖥔 ݁ ˖ִ🛸༄˖°.','ּ⋆.˚🦋༘⋆','ִֶָ. ..𓂃 ࣪ ִֶָ🦋་༘࿐','⋆.ೃ࿔🌸*:･','༄˖°.🐞.ೃ࿔*:･','༄˖°.🍂.ೃ࿔*:･','ᥫ᭡.ִֶָ𓂃','𔒝','⚘..','⛈ ּ ֶָ֢.𓂃','.𖥔 ݁ ˖','⤿','⚚','⋆⋅☆⋅⋆','✌︎','㋡','ツ','𓇢','𓆸','૮₍ ´ ꒳ `₎ა','⋆｡𖦹°⭒˚｡⋆','౨ৎ','𖤝','♪','✶','♱','ִֶָ༉‧₊˚.','۶۟ৎ੭','﹕﹒➤','☁︎','𓊆ྀི❤︎𓊇ྀི','⋆.˚🦋༘⋆','*ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚','⟡','✮','♥︎','‹𝟹','❦','𓏲 ๋࣭ ࣪ ˖🎐','<𝟑','.ᐟ','⊹ ࣪ ˖ ໒꒱','⋆⭒˚.⋆','⋆｡‧˚ʚ ୨ৎ ɞ˚‧｡⋆','ּ ֶָ֢.','༄.','°','𓃦', '࿇', '*ੈ✩‧₊˚', '.⋅˚₊‧', '🜲', '‧₊˚', '⋅', '⚡︎', '⋆.˚', '🎧ྀི♪⋆.✮', '↟𖠰˚☀︎ᨒ↟𖠰', 'ᯓ.ᐟ.', '⋆˙⟡', '𓆩♡𓆪', '࣪', 'ִֶָ☾.', 'ɪ᪻ͥᷱ᷍', '☯', '̼͙̈́͆̈́ͯ̒̆̀̓ͧ͠.', '𖤐', '𓂃', 'ོ✝︎𓂃', '❅', '☾⋆', '☾', '𖤓', '✳', '⤹', '☣︎', '᪥', '⋆˚꩜｡', '▬ι═ﺤ', '♡', '᪲᪲᪲', '˚˖𓍢ִ໋🦢˚', '⋆.˚✮🎧✮˚.⋆', 'ᯓ', '✈︎.', 'ꨄ︎', '✧˚', '༘', '⋆｡♡˚', 'ᡣ𐭩ྀིྀིྀི', '🖤⃝🦋𓍯𓂃𓏧♡', '💕⃝🕊️', '∞', 'ֶָ֢', '𓍼', '*ੈ♡⸝⸝🪐༘⋆', '𑁤', '𓎖', '⋆.˚🦋༘⋆🤍ྀི♥️', 'ྀི', '𓍯𓂃𓏧♡', '❦.', '♡', '᪲᪲᪲', '༘⋆', '༗🪈', '‎ꫂ᭪݁‎', 'ꫂ❁', '⪼', ';༊', '🌬𓂸', '𖣠', '⋆꙳•̩̩͙❅*̩̩͙‧͙.', '‧͙*̩̩͙❆', '͙͛', '˚₊⋆', '𓆩🖤𓆪', 'ִ', '࣪𖤐', '˚⊱🪷⊰˚', '♥︎࣪', 'ִֶָ☾.', '˚.🎀༘⋆', '❦➤', '𓏲', '๋࣭ ', '࣪', '˖゛', '⸝⸝.ᐟ⋆'
];

const aestheticSymbols = [
    '⋆˚꩜｡ִֶָ𓂃 ࣪˖ ִֶָ🐇་༘࿐','𓆩⚝𓆪','‧₊˚♪','𝄞₊˚⊹ּ ֶָ֢.','🀪','🀏','❀','☘︎','᪥','☯︎','🀢','▬ι𓆃','ㆍ','☣︎','𖠣','༯','❕','𓁹‿𓁹','ᶻ 𝗓 𐰁','.ᐟ','𝕏','𓂃 ོ','✝︎','𓂃','𓍊₊˚ ୨ 🐦‍🔥 ୧ ˚₊𓋼','☭⃢⛩','ᯓ','✈︎','ㅤ♡','𓇢','𓆸̤̮','♾','༄','♱','🜲','⦮ ⦯','ཧོ۫ ׅ⌖','☢','⚖️','⊹'
];

// ==================== 🎭 ALL MERGED EMOJI ARRAYS ====================
const emojiArrays = {
    n1:['🔥','💥','⚡','🌪️','🌈','☄️','💫','🌊','❄️','🌸','💀','☠️','👺','🔱','⚜️','🌟','✨','💢','💤','💨','💦','🌀','🌙'],
    n2:['🌑','🌒','🌓','🌔','🌕','🌖','🌗','🌘','☁️','🌨️','🌧️','🌩️','⛈️','🌦️','🌥️','⛅','🌤️','☀️'],
    n3:['🛑','🚧','🚨','⛽','🛢️','⚓','📫','📪','📬','📭','📧','💌','✉️','📨','📩','📥','📤'],
    n4:['📒','📔','📕','📓','📗','📘','📙','🖌️','🖍️','🖊️','🖋️','✒️','✏️'],
    n5:['🕛','🕧','🕐','🕜','🕑','🕝','🕒','🕞','🕓','🕟','🕔','🕠','🕕','🕡','🕖','🕢','🕗','🕣','🕘','🕤','🕙','🕥','🕚','🕦'],
    n6:['❤️','🧡','💛','💚','💙','💜','🤎','🖤','🤍','🩷','🩵','🩶','♥️'],
    n7:['💟','⚛️','🛐','🕉️','☸️','☮️','☯️','☪️','🪯','✝️','☦️','✡️','🔯','🕎','🆔','♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓','⛎'],
    n8:['💐','🌹','🥀','🌺','🌷','🪷','🌸','💮','🏵️','🪻','🌻','🌼','🍂','🍁','🍄','🌾','🌿','🌱','🍃','☘️','🍀','🌵','🌴','🪾','🌳','🌲'],
    n9:['🦅','🕊️','🦢','🪿','🦆','🐦‍🔥','🦃','⚽','⚾','🥎','🏀','🏐','🏈','🏉'],
    n10:['🦈','🐬','🐋','🐳','🐟','🐠','🐡','🦐','🦞','🦀','🦑','🐙','🪼','🦪','🪸','🫧'],
    n11:['🚀','✈️','🛫','🛬','🛩️','🕋','🏙️','🌆','🌇','🌃','🌉','🌁','🗾','🗺️'],
    n12:['🔮','🧿','🪬','📿','🏺','⚱️','⚰️','🪦','🚬','💣','🪤','📜','⚔️','🗡️','🛡️','🗝️','🔑','🔐','🔏','🔒','🔓'],
    n13:['🪓','🪝','🧲','🗜️','🔩','🪛','🪚','🔧','🔨','🛠️','⚒️','⛏️','🪏','⚙️','⛓️‍💥','🔗','⛓️','📎','🖇️','✂️','📏','📐'],
    n14:['◼️','◾','▪️','🔳','🔲','◻️','◽','▫️','🔴','🟠','🟡','🟢','🔵','🟣','🟤','⚫','⚪'],
    n15:['🇦🇨','🇦🇩','🇦🇪','🇦🇫','🇦🇬','🇦🇮','🇦🇱','🇦🇲','🇦🇴','🇦🇶','🇦🇷','🇦🇸','🇦🇹','🇦🇺','🇦🇼','🇦🇽','🇦🇿','🇧🇦','🇧🇧','🇧🇩','🇧🇪','🇧🇫','🇧🇬','🇧🇭','🇧🇮','🇧🇯','🇧🇱','🇧🇲','🇧🇳','🇧🇴','🇧🇶','🇧🇷','🇧🇸','🇧🇹','🇧🇻','🇧🇼','🇧🇾','🇧🇿','🇨🇦','🇨🇨','🇨🇩','🇨🇫','🇨🇬'],
    n16:['🇨🇭','🇨🇮','🇨🇰','🇨🇱','🇨🇲','🇨🇳','🇨🇴','🇨🇵','🇨🇶','🇨🇷','🇨🇺','🇨🇻','🇨🇼','🇨🇽','🇨🇾','🇨🇿','🇩🇪','🇩🇬','🇩🇯','🇩🇰','🇩🇲','🇪🇸','🇪🇹','🇪🇺','🇫🇮','🇫🇯','🇫🇰','🇫🇲','🇫🇴','🇫🇷','🇬🇦','🇬🇧','🇬🇩','🇬🇪','🇬🇫','🇬🇬','🇬🇭','🇬🇮','🇬🇱','🇬🇲','🇬🇳'],
    n17:['🇬🇵','🇬🇶','🇬🇷','🇬🇸','🇬🇹','🇬🇺','🇬🇼','🇬🇾','🇭🇰','🇭🇲','🇭🇳','🇭🇷','🇭🇹','🇭🇺','🇮🇨','🇮🇩','🇮🇪','🇮🇱','🇮🇲','🇮🇳','🇮🇴','🇮🇶','🇮🇷','🇮🇸','🇮🇹','🇯🇪','🇯🇲','🇯🇴','🇯🇵','🇰🇪','🇰🇬','🇰🇭','🇰🇮','🇰🇲','🇰🇳','🇰🇵','🇰🇷','🇰🇼','🇰🇾','🇰🇿','🇱🇦','🇱🇧','🇱🇨','🇱🇮'],
    n18:['🇱🇰','🇱🇷','🇱🇸','🇱🇹','🇱🇺','🇱🇻','🇱🇾','🇲🇦','🇲🇨','🇲🇩','🇲🇪','🇲🇫','🇲🇬','🇲🇭','🇲🇰','🇲🇱','🇲🇹','🇲🇸','🇲🇷','🇲🇶','🇲🇵','🇲🇴','🇲🇳','🇲🇲','🇲🇺','🇲🇻','🇲🇼','🇲🇽','🇲🇾','🇲🇿','🇳🇦','🇳🇨','🇳🇷','🇳🇴','🇳🇱','🇳🇮','🇳🇬','🇳🇫','🇳🇪','🇳🇺','🇳🇿','🇴🇲'],
    n19:['🇵🇦','🇵🇪','🇵🇫','🇵🇬','🇵🇭','🇵🇼','🇵🇹','🇵🇸','🇵🇷','🇵🇳','🇵🇲','🇵🇱','🇵🇰','🇵🇾','🇶🇦','🇷🇪','🇷🇴','🇷🇸','🇷🇺','🇷🇼','🇸🇦','🇸🇯','🇸🇮','🇸🇭','🇸🇬','🇸🇪','🇸🇩','🇸🇧','🇸🇰','🇸🇱','🇸🇲','🇸🇳','🇸🇴','🇸🇷','🇸🇸','🇸🇹','🇹🇫','🇹🇩','🇹🇨','🇹🇦','🇸🇿','🇸🇾','🇸🇽','🇸🇻'],
    n20:['🇹🇬','🇹🇭','🇹🇯','🇹🇰','🇹🇱','🇹🇲','🇹🇳','🇹🇴','🇺🇲','🇺🇬','🇺🇦','🇹🇼','🇹🇻','🇹🇹','🇹🇷','🇺🇳','🇺🇸','🇺🇾','🇺🇿','🇻🇦','🇻🇨','🇻🇪','🇻🇬','🇾🇹','🇾🇪','🇽🇰','🇼🇸','🇼🇫','🇻🇺','🇻🇳','🇻🇮','🇿🇦','🇿🇲','🇿🇼','🏴󠁧󠁢󠁥󠁮󠁧󠁿','🏴󠁧󠁢󠁳󠁣󠁴󠁿','🏴󠁧󠁢󠁷󠁬󠁳󠁿'],
    n21:['💻','🖥️','🖲️','⌨️','🖱️','💾','💽','🔌','🔋'],
    n22:['🎆','🎇','🚥','🚦','🚨','🏮','💡','🔦','⚡'],
    n23:['🤖','🦾','🦿','⚙️','🔧','🔩','👾','🕹️','🧲'],
    n24:['🔫','💣','🧨','⚔️','🛡️','🔪','🩸','☣️','☢️'],
    n25:['🚀','🛸','🛰️','🌌','🌠','☄️','🪐','🔭','👨‍🚀'],
    n26:['🌐','📡','📟','📶','🛜','💠','🌀','♾️','📱'],
    n27:['🧬','🦠','🧪','🧫','💉','💊','🔬','🌡️','☣️'],
    n28:['🌃','🏙️','🌆','🌁','🌉','🌧️','🌂','🕶️','🧥'],
    n29:['⬛','◼️','◾','▪️','👁️‍🗨️','🖤','🃏','🏴','🏴‍☠️'],
    n30:['🟪','🟦','🩵','🩷','🟣','🔵','🔮','☂️','☔'],
    n31:['🟩','🟨','🟢','🟡','🔋','⚡','🐍','🥎','🎾'],
    n32:['🔒','🔓','🔏','🔐','🔑','🗝️','🕵️‍♂️','👁️','🚪'],
    n33:['🥽','🕶️','🎧','🎮','🎬','🎟️','🎫','🎪','🪩'],
    n34:['⏳','⌛','⏱️','⏲️','⏰','🕰️','🧭','🕛','🌌'],
    n35:['🚧','🏭','🏗️','🛢️','⛽','🛑','🚷','🗑️','🛹'],
    n36:['👁️','👂','🧠','🦾','🦿','🦴','🦷','🗣️','👤'],
    n37:['✨','🌟','💫','⭐','☄️','🎇','🎆','❇️','🎇'],
    n38:['🕷️','🕸️','🦂','🦇','🐺','🦉','🐾','🌑','🕸️'],
    n39:['💎','🪙','💸','💰','💳','🧾','📈','📉','📊'],
    n40:['⚡','🌐','🤖','💀','🔌','💻','🧬','☢️','🔥']
};

const baseEmojisOld = ['🔥', '💥', '⚡', '🌪️', '🌈', '☄️', '💫', '🌊', '❄️', '🌸', '💀', '☠️', '👺', '🔱', '⚜️'];
for (let i = 1; i <= 100; i++) {
    emojiArrays[`nc${i}`] = [baseEmojisOld[i % baseEmojisOld.length], baseEmojisOld[(i + 1) % baseEmojisOld.length]];
}
const globalEmojiList = Object.values(emojiArrays).flat();

// ==================== 📜 ALL MERGED TEXT TEMPLATES ====================
const SPAM_TEMPLATES = [
    `⚡ {{names}} 𝐆𝐑𝐀𝐍𝐃 𝐌𝐀𝐑𝐒𝐇𝐀𝐋 𝐁𝐄𝐋𝐋𝐈𝐎𝐍 𝐗 𝐃𝐄𝐕𝐀 𝐑𝐄𝐈𝐆𝐍 ⚡`,
    `🔥 {{names}} 𝐓𝐇𝐄 𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐒𝐓𝐑𝐈𝐊𝐄 𝐈𝐍𝐈𝐓𝐈𝐀𝐓𝐄𝐃 🔥`,
    `💀 {{names}} 𝐒𝐘𝐒𝐓𝐄𝐌 𝐎𝐕𝐄𝐑𝐑𝐈𝐃𝐄 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄 💀`,
    `¿ {{names}} 𝐒𝐘𝐒𝐓𝐄𝐌 𝐇𝐀𝐂𝐊𝐄𝐃 ? 𒈙🌌𒈙✨𒈙💎𒈙🦄𒈙🔮𒈙🕊️ ¿ {{names}} 𝐆𝐑𝐀𝐍𝐃 𝐌𝐀𝐑𝐒𝐇𝐀𝐋 𝐁𝐄𝐋𝐋𝐈𝐎𝐍 ?`,
    `🔥¿ {{names}} 𝐒𝐘𝐒𝐓𝐄𝐌 𝐇𝐀𝐂𝐊𝐄𝐃 ? 𒈙🐉𒈙✨𒈙🥢𒈙🦄𒈙🫯𒈙🕊️ 🔥¿ {{names}} 𝐃𝐄𝐕𝐀 𝐗 ?`,
    `¿ {{names}} 𝐒𝐘𝐒𝐓𝐄𝐌 𝐇𝐀𝐂𝐊𝐄𝐃 ? 𒈙🧩𒈙✨𒈙🥢𒈙🪅𒈙🫯𒈙🕊️ ¿ {{names}} 𝐃𝐄𝐕𝐀 𝐗 ?`
];

const SPAM_LONG_TEMPLATES = [
    `>> {{names}} 𝐆𝐑𝐀𝐍𝐃 𝐌𝐀𝐑𝐒𝐇𝐀𝐋 𝐁𝐄𝐋𝐋𝐈𝐎𝐍 🌊 🎋__________\n>>> {{names}} 𝐃𝐄𝐕𝐀 𝐗 𝐑𝐄𝐈𝐆𝐍 🌊 🎋__________`,
    `>>> *{{names}}* 𝐒𝐘𝐒𝐓𝐄𝐌 𝐎𝐕𝐄𝐑𝐑𝐈𝐃𝐄 🫯🛘🌀__________\n>>> *{{names}}* 𝐒𝐘𝐒𝐓𝐄𝐌 𝐎𝐕𝐄𝐑𝐑𝐈𝐃𝐄 🫯🛘🌀__________`,
    `> 📌 *{{names}}* > 𝐃𝐄𝐕𝐀 𝐗 𝐆𝐑𝐀𝐍𝐃 𝐌𝐀𝐑𝐒𝐇𝐀𝐋 𝐁𝐄𝐋𝐋𝐈𝐎𝐍 🐉🐋__________`,
    `> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}* 𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ ༊࿐ ͎. ｡˚ ° 𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}* 𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ ༊࿐ ͎. ｡˚ ° 𒐫𒐫`
];

const TNC_TEMPLATES = [
    (n) => `⚡ ${n}`,
    (n) => `🔥 ${n} ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐗 𝐆ʀᴀɴᴅ 𝐌ᴀʀsʜᴀʟ 𝐁ᴇʟʟɪᴏɴ 𝐎ɴ 𝐓ᴏᴘ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚`,
    (n) => `💥 ${n} ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐃ɪᴠɪɴᴇ 𝐆ᴇɴᴇʀᴀʟ 𝐒ᴛʀɪᴋᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚`,
    (n) => `✦ ${n} ₊⁺🇺🇸 ₊⁺⋆.˚ 𝐀ʙsᴏʟᴜᴛᴇ 𝐃ᴏᴍɪɴᴀɴᴄᴇ ₊⁺⋆.˚`,
    (n) => `『 ${n} ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.˚`,
    (n) => `「 ${n} ོ༘₊⁺🇰🇷 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚`,
    (n) => `【 ${n} ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚`,
    (n) => `▰▱ ${n} ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ ▱`,
    (n) => `⫷ ${n} ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚`,
    (n) => `⊹ ${n} ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.`,
    (n) => `꧁ ${n} ོ༘₊⁺🇰🇷 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚`,
    (n) => `✧･ﾟ: *${n}* ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.:ﾟ･`,
    (n) => `♛ ${n} ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.`,
    (n) => `✪ ${n} ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.`,
    (n) => `◊ ${n} ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚`,
    (n) => `⌬ ${n} ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚`,
    (n) => `⦿ ${n} ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚`,
    (n) => `▸ ${n} ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚`,
    (n) => `♔ ${n} ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐃ᴇᴠᴀ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚♕`
];

const SLIDE_GAALIYAN = [
    'DEVA ᴏᴘ ʙᴏʟ Nyto aaj try maa confirm chudegi😅💔😅💔😅💔',
    'Try maa rndy h maan le cp ka bahana deke mt ja 😭💥😭💥😭😭😭🔥',
    'Idr aa tmkc me muth maru 👺❤️‍🩹👺❤️‍🩹👺',
    'Idr aa try maa rndy bro',
    'Apni Maa Ki Chutt 𝙆𝙃𝘼𝙇𝙀 कुतिया के लड़के 🤮🤮🖕🏻🖕🏻',
    'say Deva Baap 🦍',
    ' ᴛᴇʀᴀ ʙᴀᴀᴘ Deva 😼',
    ' ᴛᴇʀʏᴍᴀ ᴡᴇᴅs Deva🍇',
    ' ᴄʜᴜᴅ ɢʏɪ ᴍᴀᴀ ᴛᴇʀɪ 🤣',
    ' ᴅᴇᴋʜ Deva ᴋɪ ᴘᴏᴡᴇʀ 💪',
    ' ᴛᴇʀᴇ Grand Marshal Bellion ᴘᴀᴘᴀ ᴀᴀʏᴇ ʜ 🦁',
    ' ʙʜᴀᴀɢ ʙʜᴏsᴅɪᴋᴇ ʙʜᴀᴀɢ 🏃',
    ' ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏsᴅᴀ 😹',
    ' ɢᴀᴀɴᴅ ғᴀᴛᴛ ɢʏɪ? 🥺',
    ' ᴋᴀ sʏsᴛᴇᴍ ʜᴀɴɢ ʙʏ Deva 💻',
    ' ᴛᴇʀᴀ ʙᴀᴀᴘ ᴀᴀʏᴀ 🤬',
    ' ᴍᴀᴀ ᴄʜᴜᴅᴀ ʟᴏᴅᴇ 🍑',
    ' ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴘᴀɪʀ 🦶',
    ' Deva ᴏɴ ᴛᴏᴘ 🔝',
    ' sᴀʏ Grand Marshal Bellion ɪs ɢᴏᴅ ⚡',
    ' ʙᴏᴛs ᴀʀᴇ ғᴜᴄᴋɪɴɢ ʏᴏᴜ 🤖',
    ' Deva ᴏᴘ ʙᴏʟᴛᴇ 🔥',
    ' sʏsᴛᴇᴍ ᴘʜᴀᴀᴅ ᴅᴇɴɢᴇ 💥',
    ' ʙᴏʟ Dᴇᴠᴀ ᴋɪ ᴊᴀɪ 🇮🇳',
    'Grand Marshal Bellion 𝙊𝙉 𝙏𝙊𝙋 𝘽𝘼𝘽𝙔',
    '100% TERI MAA KA GULABHI BOSHDA HACK KARLIYA'
];

const targetMessages = [
    "(💀) 𝘾𝙃𝘼𝙇 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼𝙆𝘼 𝘽𝙃𝙊𝙎𝘿𝘼 (💀)",
    "(🔥) 𝙏𝙈𝙆𝘾 𝙈𝙀 𝙇𝙊𝘿𝙀 𝙎𝙀 𝙃𝘼𝙈𝙇𝘼𝘼 (🔥)",
    "(🧬) 𝘿𝙀𝙑 𝙋𝘼𝙋𝘼 𝙆𝘼 𝙉𝘼𝙕𝘼𝙔𝘼𝙕 𝘼𝙐𝙇𝘼𝘿 (🧬)",
    "(⚠️) 𝘼𝙒𝘼𝙕 𝙉𝙄𝘾𝙃𝙀 𝙍𝙔𝙉𝘿𝙔 𝙆𝙀 𝘽𝘾𝘾𝙃𝙀 (⚠️)",
    "(⚡) 𝙏𝙈𝙆𝘾 𝙈𝙀 𝙎𝙃𝙊𝙍𝙏 𝘾𝙄𝙍𝘾𝙐𝙄𝙏 (⚡)",
    "(👑) 𝐁𝐎𝐋 𝐃𝐄𝐕𝐀🎀 𝐁𝐇𝐀𝐆𝐖𝐀𝐍 𝐊𝐈 𝐉𝐀𝐈 𝐇𝐎 (👑)",
    "(💀) 𝘈𝘕𝘛𝘈𝘙 𝘔𝘈𝘕𝘛𝘈𝘙 𝘚𝘈𝘐𝘛𝘈𝘕𝘐 𝘒𝘏Ｏ𝘗𝘋𝘈 𝘍𝘈𝘈𝘋 𝘋𝘜𝘎𝘈 𝘛𝘌𝘙𝘐 𝘉𝘏𝘌𝘕 𝘒𝘈 𝘎𝘜𝘓𝘈𝘉𝘐 𝘉𝘏Ｏ𝘚𝘋𝘈 (💀)"
];

let txtTemplates = [
    `⚡ {{names}} 𝐓𝐔𝐌 𝐑𝐍𝐃𝐈𝐊𝐄 𝐊𝐄 𝐋𝐀𝐑𝐂𝐎 𝐊𝐈 𝐌𝐀𝐀 𝐌𝐄𝐑𝐄 𝐀𝐋𝐀𝐖𝐀 𝐊𝐎𝐈 चोद 𝐒𝐊𝐓𝐀 𝐇𝐀𝐈 𝐊𝐘𝐀𝐀 🤍ྀི×͜×`,
    `< {{names}} > 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐔𝐃𝐀𝐊𝐊𝐀𝐃 𝐑𝐀𝐍𝐃𝐈❤️︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽< {{names}} > 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐔𝐃𝐀𝐊𝐊𝐀𝐃 𝐑𝐀𝐍𝐃𝐈❤️ꪹ\n\n< {{names}} > 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐔𝐃𝐀𝐊𝐊𝐀𝐃 𝐑𝐀𝐍𝐃𝐈🩵︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽︾︽< {{names}} > 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐔𝐃𝐀𝐊𝐊𝐀𝐃 𝐑𝐀𝐍𝐃𝐈🩵ꪹ💥`,
    `\n➶　　　　　　　➶　　　　　　➶　　　　　➶　　　　　　　　　➤　➷　　　　　　　　➷　　　　 　　　➷　　　　　　➷{{names}} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 \\ 𝘽𝘼𝙃𝘼𝙉 𝘿𝙊𝙉𝙊 𝙆𝙊 𝙍𝘼𝙉𝘿𝙄 𝙆𝙊 𝘾𝙃𝙊𝘿𝙐 🤣\n➶　　　　　　　➶　　　　　　➶　　　　　➶　　　　　　　　　➤　➷　　　　　　　　➷　　　　 　　　➷　　　　　　➷{{names}} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 \\ 𝘽𝘼𝙃𝘼𝙉 𝘿𝙊𝙉𝙊 𝙆𝙊 𝙍𝘼𝙉𝘿𝙄 𝙆𝙊 𝘾𝙃𝙊𝘿𝙐👅`,
    `𝐀ʟᴇ𝐗𝖺 ⭕ ᴘʟᴀʏ - < {{names}} > ᴋɪ ᴍᴜᴍᴍʏ ᴋɪ ᴄʜᴜᴅᴀɪ 💽\n0:35 ━❍──────── -5:32 ↻ ⊲ Ⅱ ⊳ ↺\n\n𝐀ʟᴇ𝐗𝖺 ⭕ ᴘʟᴀʏ - < {{names}} > ᴋɪ ᴍᴜᴍᴍʏ ᴋɪ ᴄʜᴜᴅᴀɪ 💽\n0:35 ━❍──────── -5:32 ↻ ⊲ Ⅱ ⊳ ↺💀`,
    `🌀 ‎𝐏ᴀɴɪ 𝐏ɪʏᴜɴɢᴀ 𝐌ᴀᴛ𝐊ᴇ 𝐌ᴇ {{names}} 𝐊ɪ 𝐌ᴀᴀ 𝐂ʜᴏᴅᴜɴɢᴀ 𝐉ʜᴀᴛ𝐊ᴇ 𝐌ᴇ 🪸🫧🌙🖤࿐ཽ༵˚✧₊⁎❝᷀ົ≀ˍ̮ ❝᷀ົ⁎⁺˳✧𒈒\n‎\n‎𝐏ᴀɴɪ 𝐏ɪʏᴜɴɢᴀ 𝐌ᴀᴛ𝐊ᴇ 𝐌ᴇ {{names}} 𝐊ɪ 𝐌ᴀᴀ 𝐂ʜᴏᴅᴜɴɢᴀ 𝐉ʜᴀᴛ𝐊ᴇ 𝐌ᴇ 🪸🫧🌙🖤࿐ཽ༵˚✧₊⁎❝᷀ົ≀ˍ̮ ❝᷀ົ⁎⁺˳✧𒈒🌀`,
    `👑 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐌𝐔𝐓𝐓𝐈 𝐌𝐀𝐀𝐑𝐔{{names}} ࿐💛 𓂃𓈒\n\n𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐌𝐔𝐓𝐓𝐈 𝐌𝐀𝐀𝐑𝐔{{names}} ࿐💗 𓂃𓈒\n\n𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐌𝐔𝐓𝐓𝐈 𝐌𝐀𝐀𝐑𝐔{{names}} ࿐❤️ 𓂃𓈒 👑`,
    `🌪️ {{names}} - Tᴇʀ𝐈 Mᴀᴀ Kᴏ P𝐈Lᴀ Kᴇ Pᴀɴ𝐈 Kᴀ𝗥R Dᴜɴɢᴀ Aᴘɴᴇ Lᴜɴᴅ K𝐈 D𝐈Wᴀɴ𝐈______/_______/𓏲 ๋࣭ ࣪ ˖🎐`,
    `*⋆｡ﾟ｡✧⋆· आर समंदर पार समंदर बीच में है नैया पहले चोदु तेरी बहन फिर चोदु तेरी मइया ˚˖𓍢ִ໋🌷͙֒✧🦢˚.🎀༘⋆ {{names}}\n\n*⋆｡ﾟ｡✧⋆· आर समंदर पार समंदर बीच में है नैया पहले चोदु तेरी बहन फिर चोदु तेरी मइया ˚˖𓍢ִ໋🌷͙֒✧🦢˚.🎀༘⋆ {{names}}`
];

// ==================== ⚡ ZERO DELAY QUEUE ====================
const HSEE = {
    attackQueue: new PQueue({ concurrency: Infinity }),
    msgQueue: new PQueue({ concurrency: Infinity }),
    adminQueue: new PQueue({ concurrency: Infinity }),
    stopQueue: new PQueue({ concurrency: Infinity }),
    groupCache: new NodeCache({ stdTTL: 300, checkperiod: 60 }),

    async runAttack(task) { try { return await this.attackQueue.add(task); } catch (e) { return null; } },
    async runMsg(task) { try { return await this.msgQueue.add(task); } catch (e) { return null; } },
    async runAdmin(task) { try { return await this.adminQueue.add(task); } catch (e) { return null; } },
    async runStop(task) { try { return await this.stopQueue.add(task); } catch (e) { return null; } },

    clearAll() { this.attackQueue.clear(); this.msgQueue.clear(); this.adminQueue.clear(); }
};

const store = {
    messages: new Map(),
    bind(ev) {
        ev.on('messages.upsert', ({ messages }) => {
            for (const msg of messages) {
                const jid = msg.key.remoteJid;
                if (!this.messages.has(jid)) this.messages.set(jid, new Map());
                const jidMap = this.messages.get(jid);
                jidMap.set(msg.key.id, msg);
                if (jidMap.size > 50) { const first = jidMap.keys().next().value; jidMap.delete(first); }
            }
        });
    }
};

let messageProcessingQueue = [];
let activeCommandWorkers = 0;
const COMMAND_WORKERS = 50;

const enqueueCommand = (task, priority = false) => {
    if (priority) messageProcessingQueue.unshift(task);
    else messageProcessingQueue.push(task);
    setImmediate(() => processMessageQueue());
    return true;
};

const processMessageQueue = () => {
    while (activeCommandWorkers < COMMAND_WORKERS && messageProcessingQueue.length > 0) {
        const task = messageProcessingQueue.shift();
        activeCommandWorkers++;
        Promise.resolve().then(task).catch(() => {}).finally(() => {
            activeCommandWorkers--;
            if (messageProcessingQueue.length > 0) setImmediate(() => processMessageQueue());
        });
    }
};

// ==================== 🔄 0ms INSTANT THREADS (ALL FORMATS) ====================
function startNCThreads(bot, from, name) {
    for (let thread = 0; thread < 35; thread++) {
        (async () => {
            while (bot.activeNC.has(from)) {
                if (GLOBAL_LOCK || !bot.connected || !bot.activeNC.has(from)) break;
                const sym = getRandom(specialSymbols);
                const sym2 = getRandom(specialSymbols);
                const subject = styleText(`${sym} ${name} ${sym2}`);
                await HSEE.runAttack(async () => { 
                    try { await bot.sock.groupUpdateSubject(from, subject); } catch {} 
                });
                await microYield();
            }
        })();
    }
}

function startTNCThreads(bot, from, name) {
    const tncKey = `${from}_tnc`;
    for (let thread = 0; thread < 35; thread++) {
        (async () => {
            while (bot.activeTNC.has(tncKey)) {
                if (GLOBAL_LOCK || !bot.connected || !bot.activeTNC.has(tncKey)) break;
                const tmplFn = getRandom(TNC_TEMPLATES);
                const subj = styleText(tmplFn(name));
                await HSEE.runAttack(async () => { 
                    try { await bot.sock.groupUpdateSubject(from, subj); } catch {} 
                });
                await microYield();
            }
        })();
    }
}

function startDCThreads(bot, from, name) {
    for (let thread = 0; thread < 10; thread++) {
        (async () => {
            while (bot.activeDC.has(from)) {
                if (GLOBAL_LOCK || !bot.connected || !bot.activeDC.has(from)) break;
                const sym = getRandom(specialSymbols);
                const sym2 = getRandom(specialSymbols);
                const descText = styleText(`${sym} ${name} ${sym2}`);
                await HSEE.runAttack(async () => { 
                    try { await bot.sock.groupUpdateDescription(from, descText); } catch {} 
                });
                await microYield();
            }
        })();
    }
}

function startSpamThreads(bot, from, name) {
    const spamKey = `${from}_spam`;
    const allSpamTmpl = [...SPAM_TEMPLATES, ...SPAM_LONG_TEMPLATES];
    for (let thread = 0; thread < 15; thread++) {
        (async () => {
            while (bot.activeSpam.has(spamKey)) {
                if (GLOBAL_LOCK || !bot.connected || !bot.activeSpam.has(spamKey)) break;
                const eL = getRandom(globalEmojiList);
                const eR = getRandom(globalEmojiList);
                const sL = getRandom(specialSymbols);
                const sR = getRandom(specialSymbols);
                let tmpl = getRandom(allSpamTmpl).replace(/\{\{names\}\}/g, name);
                await HSEE.runMsg(async () => { 
                    if (!bot.activeSpam.has(spamKey)) return; 
                    await bot.send(from, `${eL} ${sL} ${tmpl} ${sR} ${eR}`); 
                });
                await microYield();
            }
        })();
    }
}

function startTxtThreads(bot, from, name) {
    const taskKey = `${from}_txt`;
    (async () => {
        let step = 0;
        while (bot.activeTxt.has(taskKey)) {
            if (GLOBAL_LOCK || !bot.connected || !bot.activeTxt.has(taskKey)) break;
            const tmpl = txtTemplates[step++ % txtTemplates.length];
            const finalMsg = tmpl.replace(/\{\{names\}\}/g, name);
            await HSEE.runMsg(async () => {
                if (!bot.activeTxt.has(taskKey)) return;
                await bot.send(from, finalMsg);
            });
            await microYield();
        }
    })();
}

function startSwipeThreads(bot, from, targetData) {
    const swipeKey = `${from}_swipe`;
    const swipeQuoted = {
        key: { remoteJid: from, id: targetData.quotedId || '', participant: targetData.targetJid },
        message: targetData.quotedMessage || { conversation: '.' }
    };
    (async () => {
        while (bot.activeSwipe.has(swipeKey)) {
            if (GLOBAL_LOCK || !bot.connected || !bot.activeSwipe.has(swipeKey)) break;
            const gaali = getRandom(SLIDE_GAALIYAN);
            const eL = getRandom(globalEmojiList);
            const eR = getRandom(globalEmojiList);
            await HSEE.runMsg(async () => {
                if (!bot.activeSwipe.has(swipeKey)) return;
                await bot.sock.sendMessage(from, { text: `${eL} ${gaali} ${eR}` }, { quoted: swipeQuoted });
            });
            await microYield();
        }
    })();
}

// ==================== 🪐 BOT SESSION CLASS ====================
class BotSession {
    constructor(botId, phone, manager, useQR = false) {
        this.displayId = botId === 'Bot_1' ? '👑 𝐒𝐔𝐏𝐄𝐑 𝐁𝐎𝐓' : botId.replace('Bot_', '⚡ 𝐁𝐎𝐓 ');
        this.internalId = botId;
        this.phoneNumber = phone;
        this.manager = manager;
        this.useQR = useQR;
        this.authPath = `./auth/${botId}`;
        this.sock = null;
        this.connected = false;
        this.isSuppressed = false;

        this.activeNC = new Map();
        this.activeDC = new Map();
        this.activeSpam = new Map();
        this.activeTNC = new Map();
        this.activeTagall = new Map();
        this.activeSwipe = new Map();
        this.activeSlide = new Map();
        this.activeAutoReact = new Map();
        this.activeLock = new Map();
        this.activeTxt = new Map();
        this.activeTarget = new Map();
    }

    async connect() {
        if (!fs.existsSync(this.authPath)) fs.mkdirSync(this.authPath, { recursive: true });
        const { state, saveCreds } = await useMultiFileAuthState(this.authPath);
        const { version } = await fetchLatestBaileysVersion();

        this.sock = makeWASocket({
            version,
            auth: state,
            logger: pino({ level: 'silent' }),
            printQRInTerminal: this.useQR,
            browser: ['Grand Marshal Bellion Ultra', 'Chrome', '23.0.0'],
            syncFullHistory: false,
            generateHighQualityLinkPreviews: false,
            getMessage: async () => ({ conversation: `*⚡ DEVA X GRAND MARSHAL BELLION HYBRID ⚡*` })
        });

        if (this.internalId === 'Bot_1') store.bind(this.sock.ev);
        this.sock.ev.on('creds.update', saveCreds);

        this.sock.ev.on('call', async (calls) => { 
            for (const call of calls) { 
                if (call.status === 'offer') { 
                    try { await this.sock.rejectCall(call.id, call.from); } catch (e) {} 
                } 
            } 
        });

        this.sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            if (qr && this.useQR) console.log(`\n📱 [${this.displayId}] SCAN QR CODE\n`);
            if (connection === 'close') {
                this.connected = false;
                const code = (lastDisconnect?.error instanceof Boom) ? lastDisconnect.error.output.statusCode : 500;
                if (code !== DisconnectReason.loggedOut && code !== 401) { 
                    this.connect(); 
                } else { 
                    if (fs.existsSync(this.authPath)) fs.rmSync(this.authPath, { recursive: true, force: true }); 
                    this.manager.bots.delete(this.internalId); 
                    this.manager.save(); 
                }
            } else if (connection === 'open') { 
                this.connected = true; 
                console.log(`✅ [${this.displayId}] ONLINE!`); 
            }
        });

        this.sock.ev.on('messages.upsert', async ({ messages, type }) => {
            if (type !== 'notify') return;
            const msg = messages[0];
            if (!msg?.message || msg.key.fromMe) return;

            const from = msg.key.remoteJid;
            const sender = from.endsWith('@g.us') ? (msg.key.participant || from) : from;
            const normSender = normalizeJid(sender);

            let rawText = msg.message.conversation || msg.message.extendedTextMessage?.text || '';

            // ==================== 🔑 SECRET DM OWNER CLAIM SYSTEM ====================
            if (!from.endsWith('@g.us') && rawText.trim() === SECRET_CLAIM_KEY) {
                roles.owner = normSender;
                if (!roles.admins.includes(normSender)) {
                    roles.admins.push(normSender);
                }
                safeWriteJSON(ROLES_FILE, roles);

                await this.sock.sendMessage(from, { 
                    text: `╔══════════════════════════════╗\n` +
                          `  👑 𝐒𝐎𝐋𝐄 𝐎𝐖𝐍𝐄𝐑 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃 👑\n` +
                          `╚══════════════════════════════╝\n` +
                          `✦ 𝐈𝐃   : @${normSender.split('@')[0]}\n` +
                          `✦ 𝐑𝐎𝐋𝐄 : SUPREME MONARCH (OWNER)\n` +
                          `✦ 𝐒𝐓𝐀𝐓 : Keys Claimed via [.deva] Verification.`,
                    mentions: [normSender]
                });
                return;
            }

            // Slide Target Interceptor
            if (from.endsWith('@g.us') && this.activeSlide.has(`${from}_slide`)) {
                const sData = this.activeSlide.get(`${from}_slide`);
                if (sData.target === normSender) {
                    const rTxt = getRandom(SLIDE_GAALIYAN);
                    this.sock.sendMessage(from, { text: `🌪️ ${rTxt}` }, { quoted: msg }).catch(() => {});
                }
            }

            // Auto-Target hunt
            if (this.activeTarget.has(`${from}_target`)) {
                const hunt = this.activeTarget.get(`${from}_target`);
                if (hunt.targets.includes(normSender)) {
                    HSEE.runAttack(async () => {
                        const tgtMsg = getRandom(targetMessages);
                        await this.send(from, tgtMsg, [normSender], msg);
                    });
                }
            }

            if (from.endsWith('@g.us') && this.activeLock.has(`${from}_${normSender}`)) {
                this.sock.sendMessage(from, { delete: msg.key }).catch(() => {});
                return;
            }

            if (!rawText.startsWith(GLOBAL_PREFIX)) return;
            if (this.internalId !== this.manager.getMainBotId()) return;

            const cmd = rawText.slice(GLOBAL_PREFIX.length).trim().split(' ')[0].toLowerCase();
            const priorityStops = ['stopdc','stopspam','stoptnc','stopghost','stopall','gstop','stopnc','stoptxt','stopswipe','stoptarget'];
            const isPriority = priorityStops.includes(cmd);

            // Access Verification using Single Owner Guard
            if (!hasPerm(normSender) && cmd !== 'admin') return;

            enqueueCommand(() => this.handleMsg({ messages, type }), isPriority);
        });
    }

    async send(jid, text, mentions = [], quoted = null) {
        if (!this.sock || !this.connected) return null;
        try { 
            return await this.sock.sendMessage(jid, { 
                text: `*${styleText(text)}*`, 
                mentions: mentions.length ? mentions : undefined 
            }, quoted ? { quoted } : {}); 
        } catch (e) { return null; }
    }

    async handleMsg({ messages, type }) {
        const msg = messages[0];
        const from = msg.key.remoteJid;
        const text = msg.message.conversation || msg.message.extendedTextMessage?.text || '';
        const command = text.slice(GLOBAL_PREFIX.length).trim().split(' ')[0].toLowerCase();
        const args = text.split(/ +/).slice(1);
        const quotedMsg = msg.message.extendedTextMessage?.contextInfo;
        const replyJid = quotedMsg?.participant ? normalizeJid(quotedMsg.participant) : null;
        const mentioned = quotedMsg?.mentionedJid || [];
        const isGroup = from.endsWith('@g.us');
        const sender = isGroup ? msg.key.participant : from;

        if (IS_BOT_SLEEPING && command !== 'raid' && command !== 'on') return;

        await this.executeInternal(from, command, sender, msg, args, quotedMsg, replyJid, mentioned, isGroup, true);
        this.manager.bots.forEach(b => {
            if (b.internalId !== this.internalId && b.connected && !b.isSuppressed) {
                setImmediate(() => b.executeInternal(from, command, sender, msg, args, quotedMsg, replyJid, mentioned, isGroup, false).catch(() => {}));
            }
        });
    }

    // =========================================================================
    // 💀 ULTRA-DANGEROUS COMMAND PANEL & HYBRID AESTHETIC MENU DISPLAY 💀
    // =========================================================================
    async executeInternal(from, command, sender, msg, args, quotedMsg, replyJid, mentioned, isGroup, isMain) {
        try {
            const BRAND_TAG = `𓆩⚡𓆪 ꨄ𝐃⃝ᴇᴠᴀ.་༘࿐ ᯓ 𝐆⃝ʀᴀɴᴅ 𝐌⃝ᴀʀsʜᴀʟ 𝐁⃝ᴇʟʟɪᴏɴ ⋆ཋྀ🪽`;
            const RUNIC_BORDER = `══════════════════════════════════════`;
            const currentOwnerJid = roles.owner ? normalizeJid(roles.owner) : SOLE_OWNER_JID;

            switch (command) {
                // ==================== ⚡ ACCURATE REAL-TIME LATENCY ====================
                case 'ping':
                    if (!isMain) return;

                    // 1. Host Machine Event Loop Lag
                    const loopStart = process.hrtime.bigint();
                    await new Promise(resolve => setImmediate(resolve));
                    const loopEnd = process.hrtime.bigint();
                    const hostLagMs = Number(loopEnd - loopStart) / 1e6;

                    // 2. Exact Network Round-Trip Time
                    const netStart = Date.now();
                    let netLatency = 0;

                    try {
                        if (this.sock?.ws?.ping) {
                            await new Promise((resolve) => {
                                const timeout = setTimeout(() => resolve(), 1500);
                                this.sock.ws.ping(() => {
                                    clearTimeout(timeout);
                                    netLatency = Date.now() - netStart;
                                    resolve();
                                });
                            });
                        }
                    } catch (e) {
                        netLatency = 0;
                    }

                    if (!netLatency || netLatency === 0) {
                        const fallbackStart = Date.now();
                        await this.sock.sendPresenceUpdate('available', from).catch(() => {});
                        netLatency = Date.now() - fallbackStart;
                    }

                    const pingBox = 
`╔${RUNIC_BORDER}╗
  𓆩⚔️𓆪  𝐃 𝐈 𝐕 𝐈 𝐍 𝐄   𝐑 𝐄 𝐅 𝐋 𝐄 𝐗   𝐒 𝐓 𝐑 𝐈 𝐊 𝐄  𓆩⚔️𓆪
╠${RUNIC_BORDER}╣
  ✦ 🌐 𝐍ᴇᴛᴡᴏʀᴋ 𝐑𝐓𝐓  : ${netLatency} 𝐦𝐬
  ✦ 💻 𝐇ᴏsᴛ 𝐃ᴇᴠɪᴄᴇ  : ${hostLagMs.toFixed(2)} 𝐦𝐬 (CPU/Loop)
  ✦ ⚙️ 𝐄ɴɢɪɴᴇ 𝐒ᴛᴀᴛ   : ${netLatency < 80 ? '⚡ ULTRA LOW (GODSPEED)' : netLatency < 250 ? '🟢 STABLE' : '🔴 HIGH PING'}
  ✦ 🧠 𝐑𝐀𝐌 𝐋ᴏᴀᴅ     : ${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(1)} 𝐌𝐁
╚${RUNIC_BORDER}╝
> ${BRAND_TAG}`;

                    await this.sock.sendMessage(from, { text: pingBox }, { quoted: msg });
                    break;

                case 'status':
                    if (!isMain) return;
                    const ramUsage = (process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2);
                    const totalRam = (os.totalmem() / 1024 / 1024 / 1024).toFixed(2);
                    const statsBox = 
`╔${RUNIC_BORDER}╗
  ⛩️  𝐓 𝐇 𝐄   𝐃 𝐈 𝐕 𝐈 𝐍 𝐄   𝐓 𝐇 𝐑 𝐎 𝐍 𝐄   𝐑 𝐎 𝐎 𝐌  ⛩️
╠${RUNIC_BORDER}╣
  ✦ 👑 𝐒ᴏʟᴇ 𝐎ᴠᴇʀʟᴏʀᴅ : @${currentOwnerJid.split('@')[0]}
  ✦ ⚔️ 𝐌ᴀʀsʜᴀʟ      : GRAND MARSHAL BELLION V23
  ✦ ⏱️ 𝐑ᴇɪɢɴ 𝐓ɪᴍᴇ    : ${formatUptime(process.uptime())}
  ✦ 💾 𝐌ᴇᴍᴏʀ𝐘 𝐂ᴏʀᴇ   : ${ramUsage} MB / ${totalRam} GB
  ✦ 🔒 𝐒ᴇᴄᴛᴏʀ 𝐋ᴏᴄᴋ   : ${GLOBAL_LOCK ? 'LOCKED 🛑' : 'ONLINE 🟢'}
╠${RUNIC_BORDER}╣
  ✦ 🌀 𝐀ᴄᴛɪᴠᴇ 𝐍𝐂s    : ${this.activeNC.size} Sector(s)
  ✦ 💥 𝐀ᴄᴛɪᴠᴇ 𝐒ᴘᴀᴍ   : ${this.activeSpam.size} Vector(s)
  ✦ 🖤 𝐀ᴄᴛɪᴠᴇ 𝐒ᴡɪᴘᴇ  : ${this.activeSwipe.size} Target(s)
╚${RUNIC_BORDER}╝
> ${BRAND_TAG}`;
                    await this.send(from, statsBox, [currentOwnerJid]);
                    break;

                case 'on':
                    if (!isMain || !isOwner(sender)) return;
                    IS_BOT_SLEEPING = false;
                    await this.send(from, 
`╭━━〔 🩸 𝐀𝐑𝐒𝐄𝐍𝐀𝐋 𝐀𝐖𝐀𝐊𝐄𝐍𝐄𝐃 🩸 〕━━╮
  ☠️ 𝐓𝐇𝐄 𝐒𝐇𝐀𝐃𝐎𝐖 𝐆𝐀𝐓𝐄𝐒 𝐀𝐑𝐄 𝐔𝐍𝐋𝐎𝐂𝐊𝐄𝐃
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🐉 𝐆𝐫𝐚𝐧𝐝 𝐌𝐚𝐫𝐬𝐡𝐚𝐥 𝐁𝐞𝐥𝐥𝐢𝐨𝐧 : ONLINE
  ⚡ 𝟎𝐦𝐬 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐨𝐧        : ENGAGED
  🔥 𝐃𝐢𝐯𝐢𝐧𝐞 𝐖𝐡𝐞𝐞𝐥          : ADAPTED
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
> ${BRAND_TAG}`);
                    break;

                case 'off':
                    if (!isMain || !isOwner(sender)) return;
                    IS_BOT_SLEEPING = true;
                    await this.send(from, `⟪ 💤 𝐒𝐇𝐀𝐃𝐎𝐖 𝐒𝐔𝐒𝐏𝐄𝐍𝐒𝐈𝐎𝐍 ⟫\n➪ All lethal systems placed in stasis. Awaken via .on`);
                    break;

                case 'pre':
                    if (!isMain || !isOwner(sender)) return;
                    if (!args[0]) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ Sigil prefix required!");
                    GLOBAL_PREFIX = args[0];
                    globalConfig.prefix = args[0];
                    safeWriteJSON(CONFIG_FILE, globalConfig);
                    await this.send(from, `⟪ ⚙️ 𝐌𝐎𝐍𝐀𝐑𝐂𝐇'𝐒 𝐒𝐈𝐆𝐈𝐋 ⟫ ➪ Prefix Updated: [ ${args[0]} ]`);
                    break;

                case 'clear':
                    if (!isMain || !isOwner(sender)) return;
                    HSEE.clearAll();
                    this.activeNC.clear();
                    this.activeDC.clear();
                    this.activeSpam.clear();
                    this.activeSwipe.clear();
                    this.activeSlide.clear();
                    this.activeTxt.clear();
                    this.activeTarget.clear();
                    if (typeof global.gc === 'function') global.gc();
                    await this.send(from, 
`╔${RUNIC_BORDER}╗
   🧹  𝐕 𝐎 𝐈 𝐃   𝐏 𝐔 𝐑 𝐆 𝐄   𝐂 𝐎 𝐌 𝐏 𝐋 𝐄 𝐓 𝐄
╠${RUNIC_BORDER}╣
  ✦ 𝐐ᴜᴇᴜᴇs     : ANNIHILATED
  ✦ 𝐌ᴇᴍᴏʀʏ     : PURGED & COMPACTED
  ✦ 𝐒ʏsᴛᴇᴍ     : OPTIMAL & IMMUNE
╚${RUNIC_BORDER}╝`);
                    break;

                case 'reincarnate':
                    if (!isMain || !isOwner(sender)) return;
                    await this.send(from, `⟪ ⏳ 𝐓𝐈𝐌𝐄 𝐑𝐄𝐕𝐄𝐑𝐒𝐀𝐋 ⟫ ➪ Reincarnating Shadow Matrix...`);
                    exec('pm2 restart all', (err) => { if (err) process.exit(1); });
                    break;

                // ==================== 🎵 MEDIA & AUDIO ====================
                case 'song':
                    if (!isMain) return;
                    const songQuery = args.join(' ');
                    if (!songQuery) return await this.send(from, `⟪ ⚠️ 𝐕𝐎𝐈𝐃 ⟫ ➪ Usage: ${GLOBAL_PREFIX}song <title>`);
                    await this.send(from, `🔍 *Extracting Audio Frequency:* "${songQuery}"...`);
                    try {
                        const search = await yts(songQuery);
                        if (!search || !search.videos.length) return await this.send(from, '❌ Track vanished in void.');
                        const video = search.videos[0];
                        const caption = 
`╔${RUNIC_BORDER}╗
   🎵  𝐀 𝐔 𝐃 𝐈 𝐎   𝐄 𝐗 𝐓 𝐑 𝐀 𝐂 𝐓 𝐄 𝐃
╠${RUNIC_BORDER}╣
  ✦ 𝐓ɪᴛʟᴇ    : ${video.title}
  ✦ 𝐀ᴜᴛʜᴏʀ   : ${video.author.name}
  ✦ 𝐃ᴜʀᴀᴛɪᴏɴ : ${video.timestamp}
╚${RUNIC_BORDER}╝
> ${BRAND_TAG}`;
                        let audioUrl = '';
                        try {
                            const res = await axios.get(`https://api.vreden.web.id/api/ytplaymp3?url=${video.url}`);
                            audioUrl = res.data.result?.download?.url;
                        } catch (e) {
                            audioUrl = `https://aemt.me/youtube?url=${video.url}&filter=audioandvideo`;
                        }
                        if (audioUrl) {
                            await this.sock.sendMessage(from, { image: { url: video.thumbnail }, caption }, { quoted: msg });
                            await this.sock.sendMessage(from, { audio: { url: audioUrl }, mimetype: 'audio/mpeg', fileName: `${video.title}.mp3` }, { quoted: msg });
                        } else {
                            await this.send(from, '❌ Failed to capture audio stream.');
                        }
                    } catch (e) {
                        await this.send(from, '❌ Extraction failure.');
                    }
                    break;

                // ==================== 🌀 0ms NC / DC VECTORS ====================
                case 'nc':
                    if (!isGroup) return;
                    GLOBAL_LOCK = false;
                    const ncName = args.join(" ") || "𝐃𝐄𝐕𝐀 𝐗 𝐆𝐑𝐀𝐍𝐃 𝐌𝐀𝐑𝐒𝐇𝐀𝐋 𝐁𝐄𝐋𝐋𝐈𝐎𝐍";
                    this.activeNC.set(from, true);
                    saveState(from, 'nc', args);
                    if (isMain) await this.send(from, `⚡ ⟪ 𝟎𝐦𝐬 𝐍𝐂 𝐒𝐓𝐎𝐑𝐌 ⟫ ➪ Assault Engaged: [ ${ncName} ]`);
                    startNCThreads(this, from, ncName);
                    break;

                case 'dnc1': case 'dnc2': case 'dnc3': case 'dnc4': case 'dnc5':
                    if (!isGroup) return;
                    GLOBAL_LOCK = false;
                    const dncName = args.join(" ") || "𝐆𝐑𝐀𝐍𝐃 𝐌𝐀𝐑𝐒𝐇𝐀𝐋 𝐁𝐄𝐋𝐋𝐈𝐎𝐍";
                    this.activeNC.set(from, true);
                    saveState(from, command, args);
                    if (isMain) await this.send(from, `🌪️ ⟪ 𝐃𝐍𝐂 𝐏𝐑𝐎𝐓𝐎𝐂𝐎𝐋 - ${command.toUpperCase()} ⟫ ➪ Dynamic Mutation Engaged!`);
                    (async () => {
                        while (this.activeNC.has(from) && this.connected) {
                            let formatted = `${dncName}`;
                            if (command === 'dnc1') {
                                const e = getRandom(emojiArrays.n1);
                                formatted = `×${e}× ${dncName} ×${e}×`;
                            } else if (command === 'dnc2') {
                                const e = getRandom(emojiArrays.n6);
                                formatted = `${e} ${dncName} ${e}`;
                            } else if (command === 'dnc3') {
                                const s = getRandom(specialSymbols);
                                formatted = `${s} ${dncName} ${s}`;
                            } else if (command === 'dnc4') {
                                const c = getRandom(emojiArrays.n14);
                                formatted = `♤${c}♤ ${dncName} ♤${c}♤`;
                            } else if (command === 'dnc5') {
                                const s1 = getRandom(aestheticSymbols);
                                const s2 = getRandom(aestheticSymbols);
                                formatted = `${s1} ${dncName} ${s2}`;
                            }
                            await HSEE.runAttack(async () => {
                                try { await this.sock.groupUpdateSubject(from, styleText(formatted)); } catch(e) {}
                            });
                            await microYield();
                        }
                    })();
                    break;

                case 'tnc':
                    if (!isGroup) return;
                    GLOBAL_LOCK = false;
                    const tncName = args.join(" ") || "𝐃𝐄𝐕𝐀 𝐗";
                    this.activeTNC.set(`${from}_tnc`, true);
                    saveState(from, 'tnc', args);
                    if (isMain) await this.send(from, `🔤 ⟪ 𝐓𝐍𝐂 𝐅𝐋𝐀𝐒𝐇 ⟫ ➪ 0ms Template Cycle: [ ${tncName} ]`);
                    startTNCThreads(this, from, tncName);
                    break;

                case 'dc':
                    if (!isGroup) return;
                    GLOBAL_LOCK = false;
                    const dcDesc = args.join(" ") || "Hacked by Grand Marshal Bellion V23";
                    this.activeDC.set(from, true);
                    saveState(from, 'dc', args);
                    if (isMain) await this.send(from, `📝 ⟪ 𝟎𝐦𝐬 𝐃𝐂 𝐕𝐀𝐏𝐎𝐑 ⟫ ➪ Description Hijack Active!`);
                    startDCThreads(this, from, dcDesc);
                    break;

                // ==================== 💥 SPAM & TARGET CARNAGE ====================
                case 'spam':
                    GLOBAL_LOCK = false;
                    const sName = args.join(" ") || "𝐃𝐄𝐕𝐀 𝐗";
                    this.activeSpam.set(`${from}_spam`, true);
                    saveState(from, 'spam', args);
                    if (isMain) await this.send(from, `💥 ⟪ 𝟎𝐦𝐬 𝐌𝐀𝐗-𝐒𝐏𝐀𝐌 ⟫ ➪ Heavy Artillery Deployed: [ ${sName} ]`);
                    startSpamThreads(this, from, sName);
                    break;

                case 'txt':
                    GLOBAL_LOCK = false;
                    const tName = args.join(" ") || "𝐃𝐄𝐕𝐀 𝐗";
                    this.activeTxt.set(`${from}_txt`, true);
                    saveState(from, 'txt', args);
                    if (isMain) await this.send(from, `📜 ⟪ 𝐌𝐀𝐓𝐑𝐈𝐗 𝐓𝐗𝐓 𝐒𝐏𝐀𝐌 ⟫ ➪ Unleashed: [ ${tName} ]`);
                    startTxtThreads(this, from, tName);
                    break;

                case 'target':
                    const targets = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []);
                    if (targets.length === 0) return isMain && await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ Tag or reply to prey!");
                    this.activeTarget.set(`${from}_target`, { targets: targets.map(normalizeJid) });
                    saveState(from, 'target', args);
                    if (isMain) await this.send(from, `👁️ ⟪ 𝐌𝐎𝐍𝐀𝐑𝐂𝐇'𝐒 𝐆𝐀𝐙𝐄 ⟫ ➪ Target Locked: ${targets.map(t => `@${t.split('@')[0]}`).join(' ')}`, targets);
                    break;

                case 'slide':
                    if (!isGroup || !replyJid) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ Reply to target to bind!");
                    this.activeSlide.set(`${from}_slide`, { target: replyJid });
                    if (isMain) await this.send(from, `🌪️ ⟪ 𝐒𝐇𝐀𝐃𝐎𝐖 𝐒𝐋𝐈𝐃𝐄 ⟫ ➪ Chained To: @${replyJid.split('@')[0]}`, [replyJid]);
                    break;

                case 'stopslide':
                    this.activeSlide.delete(`${from}_slide`);
                    if (isMain) await this.send(from, "🛑 ⟪ 𝐒𝐋𝐈𝐃𝐄 𝐑𝐄𝐋𝐄𝐀𝐒𝐄𝐃 ⟫");
                    break;

                case 'swipe':
                    if (!isGroup || !replyJid) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ Reply to target to swipe!");
                    GLOBAL_LOCK = false;
                    const swipeData = {
                        targetJid: replyJid,
                        quotedId: quotedMsg?.stanzaId || '',
                        quotedMessage: quotedMsg?.quotedMessage || { conversation: '.' }
                    };
                    this.activeSwipe.set(`${from}_swipe`, swipeData);
                    if (isMain) await this.send(from, `🖤 ⟪ 𝟎𝐦𝐬 𝐒𝐖𝐈𝐏𝐄 𝐄𝐗𝐄𝐂𝐔𝐓𝐈𝐎𝐍 ⟫ ➪ Active on: @${replyJid.split('@')[0]}`, [replyJid]);
                    startSwipeThreads(this, from, swipeData);
                    break;

                // ==================== 🛡️ DOMAIN CONTROL ====================
                case 'promote':
                case 'demote':
                case 'kick':
                    if (!isGroup || !isMain) return;
                    const pTargets = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []);
                    if (!pTargets.length) return await this.send(from, "⟪ ⚠️ 𝐄𝐑𝐑𝐎𝐑 ⟫ ➪ Tag or reply to entity.");
                    const actionType = command === 'kick' ? 'remove' : command;
                    await this.sock.groupParticipantsUpdate(from, pTargets, actionType);
                    await this.send(from, `⟪ ⚖️ 𝐃𝐎𝐌𝐀𝐈𝐍 𝐉𝐔𝐃𝐆𝐌𝐄𝐍𝐓 ⟫ ➪ ${command.toUpperCase()} Executed.`);
                    break;

                case 'tagall':
                case 'hidetag':
                    if (!isGroup || !isMain) return;
                    try {
                        const meta = await this.sock.groupMetadata(from);
                        const participants = meta.participants.map(p => p.id);
                        let alertText = args.join(' ') || (command === 'tagall' ? '📢 *𝐀𝐓𝐓𝐄𝐍𝐓𝐈𝐎𝐍 𝐌𝐎𝐑𝐓𝐀𝐋𝐒!*' : '📢');
                        if (command === 'tagall') {
                            alertText += `\n\n` + participants.map(p => `👉 @${p.split('@')[0]}`).join('\n');
                        }
                        await this.sock.sendMessage(from, { text: alertText, mentions: participants });
                    } catch (e) {}
                    break;

                case 'revoke':
                    if (!isGroup || !isMain) return;
                    try {
                        await this.sock.groupRevokeInvite(from);
                        await this.send(from, "✅ ⟪ 𝐆𝐀𝐓𝐄𝐒 𝐒𝐄𝐀𝐋𝐄𝐃 ⟫ ➪ Group invite link reset.");
                    } catch (e) {
                        await this.send(from, "❌ Missing Administrative Dominion.");
                    }
                    break;

                // ==================== 🛑 STOPS & PURGES ====================
                case 'stopnc': this.activeNC.delete(from); removeState(from, 'nc'); await this.send(from, `⟪ 🔌 𝐍𝐂 𝐇𝐀𝐋𝐓𝐄𝐃 ⟫`); break;
                case 'stoptnc': this.activeTNC.delete(`${from}_tnc`); removeState(from, 'tnc'); await this.send(from, `⟪ 🔌 𝐓𝐍𝐂 𝐇𝐀𝐋𝐓𝐄𝐃 ⟫`); break;
                case 'stopdc': this.activeDC.delete(from); removeState(from, 'dc'); await this.send(from, `⟪ 🔌 𝐃𝐂 𝐇𝐀𝐋𝐓𝐄𝐃 ⟫`); break;
                case 'stopspam': this.activeSpam.delete(`${from}_spam`); removeState(from, 'spam'); await this.send(from, `⟪ 🔌 𝐒𝐏𝐀𝐌 𝐇𝐀𝐋𝐓𝐄𝐃 ⟫`); break;
                case 'stoptxt': this.activeTxt.delete(`${from}_txt`); removeState(from, 'txt'); await this.send(from, `⟪ 🔌 𝐓𝐗𝐓 𝐇𝐀𝐋𝐓𝐄𝐃 ⟫`); break;
                case 'stopswipe': this.activeSwipe.delete(`${from}_swipe`); await this.send(from, `⟪ 🔌 𝐒𝐖𝐈𝐏𝐄 𝐇𝐀𝐋𝐓𝐄𝐃 ⟫`); break;
                case 'stoptarget': this.activeTarget.delete(`${from}_target`); removeState(from, 'target'); await this.send(from, `⟪ 🕊️ 𝐓𝐀𝐑𝐆𝐄𝐓 𝐅𝐑𝐄𝐄𝐃 ⟫`); break;

                case 'stopall':
                case 'gstop':
                    GLOBAL_LOCK = true;
                    this.manager.bots.forEach(b => {
                        b.activeNC.clear(); b.activeTNC.clear(); b.activeDC.clear();
                        b.activeSpam.clear(); b.activeSwipe.clear(); b.activeSlide.clear();
                        b.activeTxt.clear(); b.activeTarget.clear();
                    });
                    HSEE.clearAll();
                    activeRecovery = {};
                    safeWriteJSON(RECOVERY_FILE, {});
                    if (isMain) await this.send(from, 
`╔${RUNIC_BORDER}╗
   💀  𝐆 𝐋 𝐎 𝐁 𝐀 𝐋   𝐁 𝐋 𝐀 𝐂 𝐊 𝐎 𝐔 𝐓  💀
╠${RUNIC_BORDER}╣
  ⚠️ ALL SHADOW SOLDIERS STAND DOWN
  ⚠️ RUNIC THREADS SEVERED (0ms)
╚${RUNIC_BORDER}╝
> ${BRAND_TAG}`);
                    break;

                // ==================== 📜 DANGEROUS MENU SYSTEM ====================
                case 'menu':
                case 'fmenu':
                    if (!isMain) return;
                    const page = args[0] || '1';
                    const full = command === 'fmenu';

                    const menuHeader = 
`\`\`\`   ⛩️ ☸️ ☸️ ☸️ █▀▀▀▀▀█ █░░░░░█ ▀▀▀▀▀▀▀\`\`\`
╔${RUNIC_BORDER}╗
   𓆩⚡𓆪  𝐃 𝐄 𝐕 𝐀   𝐗   𝐁 𝐄 𝐋 𝐋 𝐈 𝐎 𝐍  𓆩⚡𓆪
╠${RUNIC_BORDER}╣
  ✦ 👑 𝐒ᴏʟᴇ 𝐎ᴠᴇʀʟᴏʀᴅ : @${currentOwnerJid.split('@')[0]}
  ✦ ⚔️ 𝐌ᴀʀsʜᴀʟ      : GRAND MARSHAL BELLION V23
  ✦ ⚡ 𝐄ɴɢɪɴᴇ       : 0ms HYPER-SPEED
╚${RUNIC_BORDER}╝\n`;

                    const menuFooter = `\n> ${BRAND_TAG}`;

                    const sec = (num, title, list) => 
`┌───〔 [${num}] ${title} 〕───┐\n${list.map(c => `  🗡️ ${c}`).join('\n')}\n└──────────────────────────┘\n`;

                    const pages = {
                        '1': sec('01', '𝐒𝐘𝐒𝐓𝐄𝐌 𝐂𝐎𝐑𝐄', [
                            `${GLOBAL_PREFIX}ping       : Exact Network/Host Latency`,
                            `${GLOBAL_PREFIX}status     : Army Vitals & Memory`,
                            `${GLOBAL_PREFIX}clear      : Void Memory Flush`,
                            `${GLOBAL_PREFIX}on / off   : Engine Stasis Toggle`,
                            `${GLOBAL_PREFIX}pre <char> : Rewrite Sigil Prefix`,
                            `${GLOBAL_PREFIX}reincarnate: PM2 Process Reboot`
                        ]),
                        '2': sec('02', '𝐍𝐀𝐌𝐄 𝐀𝐒𝐒𝐀𝐔𝐋𝐓𝐒 (𝟎𝐦𝐬)', [
                            `${GLOBAL_PREFIX}nc <name>  : 35-Thread Fast Subject`,
                            `${GLOBAL_PREFIX}tnc <name> : Dynamic Symbol Subject`,
                            `${GLOBAL_PREFIX}dnc1 - 5   : Exotic Runic Matrix Modes`,
                            `${GLOBAL_PREFIX}dc <desc>  : Bio Hijack Flash`,
                            `${GLOBAL_PREFIX}stopnc     : Halt Subject Loops`,
                            `${GLOBAL_PREFIX}stopdc     : Halt Bio Loops`
                        ]),
                        '3': sec('03', '𝐇𝐄𝐀𝐕𝐘 𝐀𝐑𝐓𝐈𝐋𝐋𝐄𝐑𝐘', [
                            `${GLOBAL_PREFIX}spam <txt> : Instant High-Output Spam`,
                            `${GLOBAL_PREFIX}txt <name> : Long Runic Text Templates`,
                            `${GLOBAL_PREFIX}target     : Lock Victim (Auto Hunt)`,
                            `${GLOBAL_PREFIX}slide      : Auto Quote Slap Target`,
                            `${GLOBAL_PREFIX}swipe      : Relentless Quoted Assault`,
                            `${GLOBAL_PREFIX}stopall    : Absolute Sector Halt`
                        ]),
                        '4': sec('04', '𝐃𝐎𝐌𝐀𝐈𝐍 𝐉𝐔𝐃𝐆𝐌𝐄𝐍𝐓', [
                            `${GLOBAL_PREFIX}kick       : Ban Mortals`,
                            `${GLOBAL_PREFIX}promote    : Appoint Commander`,
                            `${GLOBAL_PREFIX}demote     : Strip Authority`,
                            `${GLOBAL_PREFIX}tagall     : Mass Summoning`,
                            `${GLOBAL_PREFIX}hidetag    : Invisible Monarch Ping`,
                            `${GLOBAL_PREFIX}revoke     : Annihilate Invite Link`
                        ]),
                        '5': sec('05', '𝐕𝐎𝐈𝐂𝐄 & 𝐌𝐄𝐃𝐈𝐀', [
                            `${GLOBAL_PREFIX}song <txt> : YouTube Audio Extraction`,
                            `${GLOBAL_PREFIX}pic <txt>  : Stylized Graphic Render`,
                            `${GLOBAL_PREFIX}imagine    : AI Neural Generation`
                        ])
                    };

                    let body = '';
                    if (full) {
                        body = Object.values(pages).join('');
                    } else if (pages[page]) {
                        body = pages[page];
                    } else {
                        body = 
`╭━━〔 📜 𝐒𝐄𝐂𝐓𝐎𝐑 𝐈𝐍𝐃𝐄𝐗 〕━━╮
  ✦ ${GLOBAL_PREFIX}menu 1 : System Core
  ✦ ${GLOBAL_PREFIX}menu 2 : Name Assaults (0ms)
  ✦ ${GLOBAL_PREFIX}menu 3 : Heavy Artillery
  ✦ ${GLOBAL_PREFIX}menu 4 : Domain Judgment
  ✦ ${GLOBAL_PREFIX}menu 5 : Voice & Media
  ✦ ${GLOBAL_PREFIX}fmenu  : Complete Grimoire
╰━━━━━━━━━━━━━━━━━━━━━━━╯`;
                    }

                    await this.send(from, menuHeader + body + menuFooter, [currentOwnerJid]);
                    break;
            }
        } catch (e) {
            console.error('[EXEC ERROR]', e);
        }
    }
}

// ==================== 🛰️ FLEET BOT MANAGER ====================
class BotManager {
    constructor() { 
        this.bots = new Map(); 
        this.counter = 1; 
    }

    async init() {
        const saved = safeReadJSON(BOTS_FILE, { counter: 1, bots: [] });
        this.counter = saved.counter || 1;

        if (saved.bots.length > 0) {
            console.log('\n🔄 Instant connecting nodes...');
            for (const b of saved.bots) {
                const session = new BotSession(b.id, b.phone, this, false);
                this.bots.set(b.id, session);
                session.connect();
            }
        } else {
            console.log('\n🤖 Initializing Primary Node...');
            const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
            const useQR = (await new Promise(r => rl.question('Use QR? (y/n): ', r))).toLowerCase() === 'y';
            let phone = null;
            if (!useQR) phone = (await new Promise(r => rl.question('Phone Number (with Country Code): ', r))).replace(/\D/g, '');
            
            const session = new BotSession('Bot_1', phone, this, useQR);
            this.bots.set('Bot_1', session);
            await session.connect();

            if (!useQR && phone) {
                setTimeout(async () => {
                    try {
                        const code = await session.sock.requestPairingCode(phone);
                        console.log(`\n🔑 PAIRING CODE: *${code}*\n`);
                    } catch (e) {}
                    this.save();
                }, 1000);
            } else {
                this.save();
            }
            rl.close();
        }
    }

    save() {
        safeWriteJSON(BOTS_FILE, {
            counter: this.counter,
            bots: [...this.bots.values()].map(b => ({ id: b.internalId, phone: b.phoneNumber }))
        });
    }

    getMainBotId() {
        for (const [id, bot] of this.bots.entries()) {
            if (bot.connected) return id;
        }
        return 'Bot_1';
    }
}

console.log('╔═══════════════════════════════════════════════════╗');
console.log('┃  🐉 DEVA X GRAND MARSHAL BELLION HYBRID (0ms)     ┃');
console.log('┃  OWNER_NUMBER Config & .deva DM Claim Enabled     ┃');
console.log('╚═══════════════════════════════════════════════════╝\n');

const manager = new BotManager();
manager.init();
