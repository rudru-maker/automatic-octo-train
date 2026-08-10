import makeWASocket, { useMultiFileAuthState, DisconnectReason, delay, downloadContentFromMessage, fetchLatestBaileysVersion } from '@whiskeysockets/baileys';


import { Boom } from '@hapi/boom';


import pino from 'pino';


import fs from 'fs';


import readline from 'readline';


import PQueue from 'p-queue';


import { exec } from 'child_process';


import NodeCache from 'node-cache';





// ==================== 🪐 ULTRA ANTI-CRASH ====================


process.on('uncaughtException', (err) => console.log(`[⚠️ IMMUNE] ${err.message}`));


process.on('unhandledRejection', (r) => console.log(`[⚠️ IMMUNE] ${r}`));


process.setMaxListeners(0);





// ==================== 📡 DATABASE & STATE ====================


const ROLES_FILE = './data/roles.json';


const BOTS_FILE = './data/bots.json';


const CONFIG_FILE = './data/config.json';





function safeReadJSON(path, def) { try { if (fs.existsSync(path)) return JSON.parse(fs.readFileSync(path, 'utf8')); } catch (e) {} return def; }


function safeWriteJSON(path, data) { try { if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true }); fs.writeFileSync(path, JSON.stringify(data, null, 2)); } catch (e) {} }





let roles = safeReadJSON(ROLES_FILE, { admins: [], subAdmins: [] });


let globalConfig = safeReadJSON(CONFIG_FILE, { prefix: '.' });


let GLOBAL_PREFIX = globalConfig.prefix;


let IS_BOT_SLEEPING = false;


let GLOBAL_LOCK = false;





// ==================== ⚙️ THREADS & DELAY CONFIG ====================


let GLOBAL_THREADS = { nc: 15, spam: 1, dc: 3 };


let GLOBAL_DELAY_CONFIG = { level: 2, min: 10000, max: 20000 };





// ==================== STORAGE FOR RESTART ====================


const PROCESS_STORAGE = {


    spam1Texts: {},    // key -> array of texts


    spam2Texts: {},    // key -> text


    spam3Texts: {},    // key -> array of texts


    swipeTargets: {},  // key -> { targetJid, quoted }


};





// ==================== 👻 GHOST MODE ====================


let GHOST_MODE_ACTIVE = false;


let GHOST_ACTIVATED_BY = '';


let GHOST_THREADS = {


    nc: 15,


    dc: 3,


    spam: 1


};


const GHOST_ALLOWED_CMDS = ["ghost", "ghostoff", "stopghost", "gnc", "gdc", "gspam", "stopgnc", "stopgdc", "stopgspam", "stoptnc", "gstop", "stopall", "status", "ping", "menu", "fmenu", "dev", "on", "off", "admin", "wipe", "clear", "raid"];


const isGhostCmd = (cmd) => { if (!GHOST_MODE_ACTIVE) return true; return GHOST_ALLOWED_CMDS.includes(cmd); };





// ==================== 🔤 UTILITIES ====================


const fontMap = {


    'A':'𝐀','B':'𝐁','C':'𝐂','D':'𝐃','E':'𝐄','F':'𝐅','G':'𝐆','H':'𝐇','I':'𝐈','J':'𝐉','K':'𝐊','L':'𝐋','M':'𝐌','N':'𝐍','O':'𝐎','P':'𝐏','Q':'𝐐','R':'𝐑','S':'𝐒','T':'𝐓','U':'𝐔','V':'𝐕','W':'𝐖','X':'𝐗','Y':'𝐘','Z':'𝐙',


    'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ғ','g':'ɢ','h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ','s':'s','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ'


};


function styleText(text) { if (!text) return text; return text.replace(/[a-zA-Z]/g, c => fontMap[c] || c); }


function normalizeJid(jid) { if (!jid) return ''; return jid.includes(':') ? jid.split(':')[0] + '@s.whatsapp.net' : (jid.includes('@') ? jid : jid + '@s.whatsapp.net'); }


const isAdmin = (jid) => normalizeJid(jid) === '639075406956@s.whatsapp.net' || roles.admins.some(a => normalizeJid(a) === normalizeJid(jid));


const isSubAdmin = (jid) => roles.subAdmins.some(s => normalizeJid(s) === normalizeJid(jid));


const hasPerm = (jid) => isAdmin(jid) || isSubAdmin(jid);


const getRandom = (arr) => arr[Math.floor(Math.random() * arr.length)];


const getRandomDelay = (min, max) => Math.floor(Math.random() * (max - min + 1) + min);


const microYield = () => new Promise(resolve => setImmediate(resolve));


const getIndiaTime = () => new Date().toLocaleTimeString('en-US', { timeZone: 'Asia/Kolkata', hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit' });





// ==================== 🎨 SYMBOLS & EMOJIS ====================


const baseEmojisNew = ['🐉','💥','⚡','🌪️','🌈','☄️','💫','🌊','❄️','🌸','🪨','📌','🐦‍🔥','🔱','⚜️','🐋','⚔️','🕊️','🪸','🪐'];


const specialSymbols = ['ֺּׅ𓏽⑅','಄','ᛝ','‎ꫂ᭪݁','𓏲ּ𝄢','ೀ','.✦ ݁˖','୭ ˚. ᵎᵎ','╰┈➤','༉‧₊˚.','𓂃 ࣪˖ ִֶָ 𓈈','.𖥔 ݁ ˖','ᝰ.ᐟ','˙.꒷.𖦹˙—','𑁍ࠬܓ','ִֶָ⿻.','｡𖦹°‧','ᯓ★','𓋜','۶ৎ','°˖➴','ִ ࣪𖤐','𓂃 ࣪˖ ִֶཐི༏ཋྀ󠀮','˚˖𓍢ִ໋🦢˚','˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—','ꫂ ၴႅၴ','˚ ༘ ೀ⋆｡˚','⊱ ۫ ׅ ✧','🎧ྀི♪⋆.✮','ᥫ᭡.🍥⋆🐇་༘🌷.ೃ࿔','˚.🎀༘⋆','.𖥔 ݁ ˖ִ🛸༄˖°.','ּ⋆.˚🦋༘⋆','ִֶָ. ..𓂃 ࣪ ִֶָ🦋་༘࿐','⋆.ೃ࿔🌸*:･','༄˖°.🐞.ೃ࿔*:･','༄˖°.🍂.ೃ࿔*:･','ᥫ᭡.ִֶָ𓂃','𔒝','⚘..','⛈ ּ ֶָ֢.𓂃','.𖥔 ݁ ˖','⤿','⚚','⋆⋅☆⋅⋆','✌︎','㋡','ツ','𓇢','𓆸','૮₍ ´ ꒳ `₎ა','⋆｡𖦹°⭒˚｡⋆','౨ৎ','𖤝','♪','✶','♱','ִֶָ༉‧₊˚.','۶۟ৎ੭','﹕﹒➤','☁︎','𓊆ྀི❤︎𓊇ྀི','⋆.˚🦋༘⋆','*ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚','⟡','✮','♥︎','‹𝟹','❦','𓏲 ๋࣭ ࣪ ˖🎐','<𝟑','.ᐟ','⊹ ࣪ ˖ ໒꒱','⋆⭒˚.⋆','⋆｡‧˚ʚ ୨ৎ ɞ˚‧｡⋆','ּ ֶָ֢.','༄.','°','𓃦', '࿇', '*ੈ✩‧₊˚', '.⋅˚₊‧', '🜲', '‧₊˚', '⋅', '⚡︎', '⋆.˚', '🎧ྀི♪⋆.✮', '↟𖠰˚☀︎ᨒ↟𖠰', 'ᯓ.ᐟ.', '⋆˙⟡', '𓆩♡𓆪', '࣪', 'ִֶָ☾.', 'ɪ᪻ͥᷱ᷍', '☯', '̼͙̈́͆̈́ͯ̒̆̀̓ͧ͠.', '𖤐', '𓂃', 'ོ✝︎𓂃', '❅', '☾⋆', '☾', '𖤓', '✳', '⤹', '☣︎', '᪥', '⋆˚꩜｡', '▬ι═ﺤ', '♡', '᪲᪲᪲', '˚˖𓍢ִ໋🦢˚', '⋆.˚✮🎧✮˚.⋆', 'ᯓ', '✈︎.', 'ꨄ︎', '✧˚', '༘', '⋆｡♡˚', 'ᡣ𐭩ྀིྀིྀི', '🖤⃝🦋𓍯𓂃𓏧♡', '💕⃝🕊️', '💕⃝🕊️', '∞', 'ֶָ֢', 'ֶָ֢', '𓍼', '*ੈ♡⸝⸝🪐༘⋆', '𑁤', '𓎖', '⋆.˚🦋༘⋆🤍ྀི♥️', 'ྀི', '𓍯𓂃𓏧♡', '❦.', '♡', '᪲᪲᪲', '༘⋆', '༗🪈', '‎ꫂ᭪݁‎', 'ꫂ❁', '⪼', ';༊', '🌬𓂸', '𖣠', '⋆꙳•̩̩͙❅*̩̩͙‧͙.', '‧͙*̩̩͙❆', '͙͛', '˚₊⋆', '𓆩🖤𓆪', 'ִ', '࣪𖤐', '˚⊱🪷⊰˚', '♥︎࣪', 'ִֶָ☾.', '˚.🎀༘⋆', '❦➤', '𓏲', '๋࣭ ', '࣪', '˖゛', '⸝⸝.ᐟ⋆'


];


const globalEmojiList = ['🔥','💥','⚡','🌪️','🌈','☄️','💫','🌊','❄️','🌸','💀','☠️','👺','🔱','⚜️','🌟','✨','💢','💤','💨','💦','🌀','🌙','❤️','🧡','💛','💚','💙','💜','🤎','🖤','🤍','🩷','🩵','🩶','🐉','🦅','🕊️','🦢','🐦‍🔥','🦈','🐬','🐋','🐳','🦋','🕷️','🦂','🐺','🦉','🐾','🌑','🌒','🌓','🌔','🌕','🌖','🌗','🌘','🚀','✈️','🛫','🛬','🛩️','🔮','🧿','🪬','📿','💎','🪙','💸','💰'];





// ==================== SPAM TEMPLATES ====================


const SPAM_TEMPLATES = [


    `¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🌌𒈙✨𒈙💎𒈙🦄𒈙🔮𒈙🕊️ ¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🌌𒈙✨𒈙💎𒈙🦄𒈙🔮𒈙🕊️ ¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🌌𒈙✨𒈙💎𒈙🦄𒈙🔮𒈙🕊️ ¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🌌𒈙✨𒈙💎𒈙🦄𒈙🔮𒈙🕊️ ¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🌌𒈙✨𒈙💎𒈙🦄𒈙🔮𒈙🕊️ ¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🌌𒈙✨𒈙💎𒈙🦄𒈙🔮𒈙🕊️  𒈙🌌𒈙✨𒈙💎𒈙🦄𒈙🔮𒈙🕊️𒈙🌌𒈙✨¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ?`,


    `🔥¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🐉𒈙✨𒈙🥢𒈙🦄𒈙🫯𒈙🕊️ 🔥¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🐉𒈙✨𒈙🥢𒈙🦄𒈙🫯𒈙🕊️ 🔥¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🐉𒈙✨𒈙🥢𒈙🦄𒈙🫯𒈙🕊️ 🔥¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🐉𒈙✨𒈙🥢𒈙🦄𒈙🫯𒈙🕊️ 🔥¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🐉𒈙✨𒈙🥢𒈙🦄𒈙🫯𒈙🕊️ 🔥¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🐉𒈙✨𒈙🥢𒈙🦄𒈙🫯𒈙🕊️  𒈙🐉𒈙✨𒈙🥢𒈙🦄𒈙🫯𒈙🕊️𒈙🐉𒈙✨𒈙🥢𒈙🦄𒈙🫯𒈙🕊️𒈙🐉𒈙✨¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ?`,


    `¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🧩𒈙✨𒈙🥢𒈙🪅𒈙🫯𒈙🕊️ ¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🧩𒈙✨𒈙🥢𒈙🪅𒈙🫯𒈙🕊️ ¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🧩𒈙✨𒈙🥢𒈙🪅𒈙🫯𒈙🕊️ ¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🧩𒈙✨𒈙🥢𒈙🪅𒈙🫯𒈙🕊️ ¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🧩𒈙✨𒈙🥢𒈙🪅𒈙🫯𒈙🕊️ ¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ? 𒈙🧩𒈙✨𒈙🥢𒈙🪅𒈙🫯𒈙🕊️  𒈙🧩𒈙✨𒈙🥢𒈙🪅𒈙🫯𒈙🕊️𒈙🧩𒈙✨𒈙🥢𒈙🪅𒈙🫯𒈙🕊️𒈙🧩𒈙✨¿ {{names}} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟᴀʏɪ 𝐊ʀ ?`


];





const SPAM_LONG_TEMPLATES = [


    ` >> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________\n>>> {{names}} तेरी माँ बहन को कुतियां बना कर चोदूंगा रंडीके पिल्ले 🌊 🎋__________`,


    `>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________\n>>> चार चवन्नी घोड़े पे *{{names}}* की मां मेरे लोड़े पे 🫯🛘🌀__________`,


    `> >>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________\n>>>📌 *{{names}}* > आर समंदर पार समंदर बीच में है नैया पहले चोदूंगा तेरी बहन फिर चोदूंगा तेरी मईया 🐉🐋__________`,


    `> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫\n> ꉂ🗯.꩜‹—ִֶָ☾. *{{names}}*  𝐔sᴋᴇ 𝐓ᴀᴛᴛᴏ 𝐃ᴇᴠᴀ 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊࿐ ͎. ｡˚ ° 𒐫𒐫𒐫𒐫𒐫𒐫`


];





// ==================== TNC TEMPLATES ====================


const TNC_TEMPLATES = [


    (n) => `⚡ ${n}`,


    (n) => `🔥 ${n} ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚`,


    (n) => `💥 ${n} ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚`,


    (n) => `✦ ${n} ₊⁺🇺🇸 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇺🇸 ₊⁺⋆.˚`,


    (n) => `『 ${n} ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.˚`,


    (n) => `「 ${n} ོ༘₊⁺🇰🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚`,


    (n) => `【 ${n} ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚`,


    (n) => `◤ ${n} ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚`,


    (n) => `▰▱ ${n} ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ ▱`,


    (n) => `⫷ ${n} ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚`,


    (n) => `⊹ ${n} ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.`,


    (n) => `꧁ ${n} ོ༘₊⁺🇰🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚`,


    (n) => `✧･ﾟ: *${n}* ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.:ﾟ･`,


    (n) => `♛ ${n} ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜ𝐢 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.`,


    (n) => `✪ ${n} ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ ??ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.`,


    (n) => `◊ ${n} ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚`,


    (n) => `⌬ ${n} ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚`,


    (n) => `⦿ ${n} ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚`,


    (n) => `▸ ${n} ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚`,


    (n) => `♔ ${n} ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 🐉𝑫𝒆𝒗𝒂 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚♕`


];





// ==================== SLIDE/SWIPE GAALIYAN ====================


const SLIDE_GAALIYAN = [


    'DEVA ᴏᴘ ʙᴏʟ Nyto aaj try maa confirm chudegi😅💔😅💔😅💔',


    'Try maa rndy h maan le cp ka bahana deke mt ja 😭💥😭💥😭😭😭🔥',


    'Idr aa tmkc me muth maru 👺❤️‍🩹👺❤️‍🩹👺',


    'Idr aa try maa rndy bro',


    'Apni Maa Ki Chutt 𝙆𝙃𝘼𝙇𝙀 कुतिया के लड़के 🤮🤮🖕🏻🖕🏻',


    'Aurato ka kam roti bna na hota h tho Teri ma yaha kyu cudrhi🤬🤣😭😂🙏🏽💔💯🎈',


    '( Chal Tatte Try Maa Ko Pyramid Me Chodu~🤍',


    '𝐂ʜᴀʟ  𝙆𝙐𝙏𝙏𝙄𝙔𝘼 ᴋɪ 𝑨𝑼𝑳𝑨𝑫 𝐏ᴀᴠ 👉🦵 ᴾᴬᴷᴹᴰ 🔥 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ʜᴜᴅᴋᴇ 𝐁ʜᴀᴀɢ 𝐑ᴀʜɪ -----> 🏃🏻‍♀️🔥🤸🏻‍♀️🔥🏃🏻‍♀️🔥🤸🏻‍♀️🔥',


    'say Deva Baap 🦍',


    ' ᵀᵐᴷᶜ」🦋꙰  ~ ༈  ◠🇮🇳◡',


    ' Teri माँ Dead 😂 ',


    ' ᴛᴇʀᴀ ʙᴀᴀᴘ ᴄᴀʀᴘᴀɴᴛᴇʀ 🪚',


    ' ᴛʀʏ ᴅᴀᴅɪ sʟᴜᴛ⚀︎',


    ' ʏᴏᴜʀ ᴍᴏᴍ ᴡʜᴏʀᴇ👞',


    ' ɢᴜʟᴀᴍ ɢᴀɴᴅ ᴋᴀ ᴊᴏʀ ʟɢᴀ😆',


    ' ᴛᴇʀᴀ ʙᴀᴀᴘ Deva 😼',


    ' ᴛᴇʀʏᴍᴀ ᴡᴇᴅs Deva🍇',


    ' ʀɴᴅɪ ᴋᴀ ʟᴅᴄᴀ🍑',


    ' ʜᴠᴀʙᴀᴀᴢ ᴄʜᴜᴅᴋᴇ ᴍʀᴀ🧖',


    ' ʀᴀɴᴅɪ ᴋɪ ᴘᴀɪᴅᴀɪsʜ💔',


    ' ᴄʜᴜᴅ ɢʏɪ ᴍᴀᴀ ᴛᴇʀɪ 🤣',


    ' ᴀʙʙᴜ ʙᴏʟ Deva ᴋᴏ 😈',


    ' ᴛᴇʀɪ ʙᴇʜᴇɴ ᴍᴇʀɪ ғᴀɴ 🥵',


    ' ᴅᴇᴋʜ Deva ᴋɪ ᴘᴏᴡᴇʀ 💪',


    ' ᴀʙʙᴇ ɴᴀʟʟᴇ sᴜᴅʜᴀʀ ᴊᴀ 🤬',


    ' ᴛᴇʀᴀ ᴋʜᴀɴᴅᴀᴀɴ ᴄʜᴜᴅ ɢʏᴀ 💀',


    ' ᴛᴇʀᴇ Mahoraga ᴘᴀᴘᴀ ᴀᴀʏᴇ ʜ 🦁',


    ' ʙʜᴀᴀɢ ʙʜᴏsᴅɪᴋᴇ ʙʜᴀᴀɢ 🏃',


    ' ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏsᴅᴀ 😹',


    ' ɢᴀᴀɴᴅ ғᴀᴛᴛ ɢʏɪ? 🥺',


    ' ᴋᴀ sʏsᴛᴇᴍ ʜᴀɴɢ ʙʏ Deva 💻',


    ' ᴛᴇʀᴀ ʙᴀᴀᴘ ᴀᴀʏᴀ 🤬',


    ' ᴍᴀᴀ ᴄʜᴜᴅᴀ ʟᴏᴅᴇ 🍑',


    ' ʀᴀɴᴅɪ ʀᴏɴᴀ ᴍᴀᴛ ᴋᴀʀ 😭',


    ' ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴘᴀɪʀ 🦶',


    ' Deva ᴏɴ ᴛᴏᴘ 🔝',


    ' ᴄʜᴀʟ ɴɪᴋᴀʟ ʟᴏᴅᴇ 🚪',


    ' sᴀʏ Mahoraga ɪs ɢᴏᴅ ⚡',


    ' ʙᴏᴛs ᴀʀᴇ ғᴜᴄᴋɪɴɢ ʏᴏᴜ 🤖',


    ' ᴛᴇʀᴀ ʙᴀᴀᴘ ʜᴜ ᴍᴀɪ 🎅',


    ' ᴀᴜᴋᴀᴀᴛ ᴍᴇ ʀᴇʜ 🤬',


    ' ɢᴀᴀɴᴅ ᴍᴇ ᴅᴀɴᴅᴀ ᴅᴇ ᴅᴜɴɢᴀ 🎋',


    ' ᴄʜᴜᴘ ᴋᴀʀ ʀᴀɴᴅɪ 🤫',


    ' ᴛᴇʀɪ ʙᴇʜᴇɴ ᴄʜᴜᴅ ɢʏɪ 💃',


    ' ᴅᴇᴋʜ Deva ᴋᴀ ᴋʜᴀᴜғ 😈',


    ' ʙʜᴀᴀɢ ᴍᴀᴛ ʀᴀɴᴅɪ 🏃‍♀️',


    ' ᴛᴇʀᴀ ɢʜᴀʀ ᴊᴀʏᴇɢᴀ 🏠',


    ' ᴍᴀᴀ ᴄʜᴜᴅᴀ ᴀᴘɴɪ 🖕',


    ' Deva ᴏᴘ ʙᴏʟᴛᴇ 🔥',


    ' sʏsᴛᴇᴍ ᴘʜᴀᴀᴅ ᴅᴇɴɢᴇ 💥',


    ' ᴛᴇʀɪ ɢᴀᴀɴᴅ ʟᴀᴀʟ 🔴',


    ' ʙᴏʟ ɴᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ 🗣️',


    ' ʙᴏʟ Dᴇᴠᴀ ᴋɪ ᴊᴀɪ 🇮🇳',


    '𝘾𝙔𝙐 𝙍𝙀 𝙍𝙉𝘿𝙔𝙆𝙀 𝘽𝘼𝘼𝙋 𝙎𝙀 𝘽𝙃𝙄𝘿𝙉𝙀 𝘼𝘼 𝙂𝙔𝘼?',


    '𝘾𝙃𝙇 𝘾𝙃𝙐𝘿 𝘼𝘽 𝙍𝙉𝘿 𝙆𝙀 𝙋𝙄𝙇𝙀𝙀',


    '𝙏𝙍𝙔 𝙈𝘼 𝙆𝙊 Mahoraga 𝘼𝘽𝘽𝙐 𝙋𝙀𝙇𝙀',


    '𝘾𝙃𝙐𝘿𝙂𝙀𝙂𝘼 𝙎𝘼𝘼𝙇 𝘽𝙃𝙍 𝙏𝙐𝙏𝙊 𝘽𝙀𝙏𝘼 🍑',


    'Mahoraga 𝙊𝙉 𝙏𝙊𝙋 𝘽𝘼𝘽𝙔',


    '𝘾𝙃𝘼𝙇 𝙉𝙄𝙆𝘼𝙇 𝘽𝙃𝙊𝙎𝘿𝙄𝙆𝙀',


    '𝙈𝘼𝘼 𝘾𝙃𝙐𝘿𝘼 𝘼𝙋𝙉𝙄',


    'Chup kali maa ke रण्डी बच्चे',


    'Trymaa ki chut mein labubu',


    'Teri माँ के भोसड़े पर इतने बल्ले मारूंगा की IPL जीत जायेगी',


    'काले Doraemon रोता reh',


    'end portal bn gya ab try ma iske andar chudegi',


    'क्या रे Chai Wale Ke Ladke बनाऊ तुझे Fyter',


    'oye rndi ke ldke भगा to teri maa चमार जाति ki राँड',


    '100% TERI MAA KA GULABHI BOSHDA HACK KARLIYA',


    'tri ma रंग बिरंगी रंडी',


    'चुप तेरी नानी का भोसड़ा'


];





// ==================== ⚡ QUEUE SYSTEM ====================


const HSEE = {


    attackQueue: new PQueue({ concurrency: 30, interval: 80, intervalCap: 30 }),


    msgQueue: new PQueue({ concurrency: 8, interval: 600, intervalCap: 8 }),


    mediaQueue: new PQueue({ concurrency: 3, interval: 1200, intervalCap: 3 }),


    adminQueue: new PQueue({ concurrency: 5, interval: 250, intervalCap: 5 }),


    stopQueue: new PQueue({ concurrency: 80 }),


    groupCache: new NodeCache({ stdTTL: 300, checkperiod: 60 }),





    async runAttack(task) { try { return await this.attackQueue.add(task); } catch (e) { return null; } },


    async runMsg(task) { try { return await this.msgQueue.add(task); } catch (e) { return null; } },


    async runMedia(task) { try { return await this.mediaQueue.add(task); } catch (e) { return null; } },


    async runAdmin(task) { try { return await this.adminQueue.add(task); } catch (e) { return null; } },


    async runStop(task) { try { return await this.stopQueue.add(task); } catch (e) { return null; } },





    clearCache(jid = null) { try { if (jid) this.groupCache.del(jid); else this.groupCache.flushAll(); } catch (e) {} },


    clearAll() { this.attackQueue.clear(); this.msgQueue.clear(); this.mediaQueue.clear(); this.adminQueue.clear(); }


};





// Anti-spam guard


const incomingSpamGuard = new Map();


setInterval(() => incomingSpamGuard.clear(), 60000);





// Message store (lightweight) - only stores admin messages


const store = {


    messages: new Map(),


    bind(ev) {


        ev.on('messages.upsert', ({ messages }) => {


            for (const msg of messages) {


                const jid = msg.key.remoteJid;


                const isGroup = jid.endsWith('@g.us');


                const sender = isGroup ? msg.key.participant : jid;


                const normSender = normalizeJid(sender);


                if (!isAdmin(normSender) && !isSubAdmin(normSender) && !msg.key.fromMe) continue;


                if (!this.messages.has(jid)) this.messages.set(jid, new Map());


                const jidMap = this.messages.get(jid);


                jidMap.set(msg.key.id, msg);


                if (jidMap.size > 30) { const first = jidMap.keys().next().value; jidMap.delete(first); }


            }


        });


    }


};





// Message queue (low-latency + flood resistant)


let messageProcessingQueue = [];


let activeCommandWorkers = 0;


const COMMAND_WORKERS = 6;


const MAX_QUEUE_SIZE = 50;


const COMMAND_MIN_INTERVAL_MS = 120;


const MAX_MANAGED_BOTS = 50;


const commandRateGuard = new Map();





const enqueueCommand = (task, priority = false) => {


    if (priority) messageProcessingQueue.unshift(task);


    else {


        if (messageProcessingQueue.length >= MAX_QUEUE_SIZE) return false;


        messageProcessingQueue.push(task);


    }


    setImmediate(() => processMessageQueue());


    return true;


};





const processMessageQueue = () => {


    while (activeCommandWorkers < COMMAND_WORKERS && messageProcessingQueue.length > 0) {


        const task = messageProcessingQueue.shift();


        activeCommandWorkers++;


        Promise.resolve()


            .then(task)


            .catch(() => {})


            .finally(() => {


                activeCommandWorkers--;


                if (messageProcessingQueue.length > 0) setImmediate(() => processMessageQueue());


            });


    }


};





// ==================== RESTART ALL ACTIVE PROCESSES ====================


async function restartAllActiveProcesses(from, sock, manager) {


    const mainBot = manager.bots.get(manager.getMainBotId());


    if (!mainBot) return;


    


    // Capture active keys


    const activeNC = [...mainBot.activeNC.keys()];


    const activeTNC = [...mainBot.activeTNC.keys()];


    const activeDC = [...mainBot.activeDC.keys()];


    const activeSpam = [...mainBot.activeSpam.keys()];


    const activeSpam1 = [...mainBot.activeSpam1.keys()];


    const activeSpam2 = [...mainBot.activeSpam2.keys()];


    const activeSpam3 = [...mainBot.activeSpam3.keys()];


    const activeSwipe = [...mainBot.activeSwipe.keys()];


    


    // Clear all


    mainBot.activeNC.clear();


    mainBot.activeTNC.clear();


    mainBot.activeDC.clear();


    mainBot.activeSpam.clear();


    mainBot.activeSpam1.clear();


    mainBot.activeSpam2.clear();


    mainBot.activeSpam3.clear();


    mainBot.activeSwipe.clear();


    


    await delay(500);


    


    // Restart each type


    for (const key of activeNC) {


        const name = key === 'global' ? GHOST_ACTIVATED_BY : '𝐃𝐄𝐕𝐀 𝐗';


        mainBot.activeNC.set(key, true);


        startNCThreads(mainBot, from, name);


    }


    for (const key of activeTNC) {


        const name = key === 'global' ? GHOST_ACTIVATED_BY : '??𝐃𝐄𝐕𝐀 𝐗';


        mainBot.activeTNC.set(key, true);


        startTNCThreads(mainBot, from, name);


    }


    for (const key of activeDC) {


        const name = key === 'global' ? GHOST_ACTIVATED_BY : '𝐃𝐄𝐕𝐀 𝐗 𝐃𝐄𝐒𝐂';


        mainBot.activeDC.set(key, true);


        startDCThreads(mainBot, from, name);


    }


    for (const key of activeSpam) {


        const name = key.includes('_') ? key.split('_')[1] : '𝐃𝐄𝐕𝐀 𝐗';


        mainBot.activeSpam.set(key, true);


        startSpamThreads(mainBot, from, name);


    }


    for (const key of activeSpam1) {


        if (PROCESS_STORAGE.spam1Texts[key]) {


            mainBot.activeSpam1.set(key, true);


            startSpam1Threads(mainBot, from, PROCESS_STORAGE.spam1Texts[key]);


        }


    }


    for (const key of activeSpam2) {


        if (PROCESS_STORAGE.spam2Texts[key]) {


            mainBot.activeSpam2.set(key, true);


            startSpam2Threads(mainBot, from, PROCESS_STORAGE.spam2Texts[key]);


        }


    }


    for (const key of activeSpam3) {


        if (PROCESS_STORAGE.spam3Texts[key]) {


            mainBot.activeSpam3.set(key, true);


            startSpam3Threads(mainBot, from, PROCESS_STORAGE.spam3Texts[key]);


        }


    }


    for (const key of activeSwipe) {


        if (PROCESS_STORAGE.swipeTargets[key]) {


            mainBot.activeSwipe.set(key, { active: true, ...PROCESS_STORAGE.swipeTargets[key] });


            startSwipeThreads(mainBot, from, PROCESS_STORAGE.swipeTargets[key]);


        }


    }


}





// ==================== THREAD STARTER FUNCTIONS ====================


function startNCThreads(bot, from, name) {


    for (let thread = 0; thread < GLOBAL_THREADS.nc; thread++) {


        (async () => {


            while (bot.activeNC.has(from)) {


                if (GLOBAL_LOCK || !bot.connected || !bot.activeNC.has(from)) break;


                await microYield();


                const sym = getRandom(specialSymbols);


                const sym2 = getRandom(specialSymbols);


                const subject = styleText(`${sym} ${name} ${sym2}`);


                await HSEE.runAttack(async () => { 


                    try { await bot.sock.groupUpdateSubject(from, subject); } catch {} 


                });


                await delay(5);


            }


        })();


    }


}





function startTNCThreads(bot, from, name) {


    const tncKey = `${from}_tnc`;


    for (let thread = 0; thread < GLOBAL_THREADS.nc; thread++) {


        (async () => {


            while (bot.activeTNC.has(tncKey)) {


                if (GLOBAL_LOCK || !bot.connected || !bot.activeTNC.has(tncKey)) break;


                await microYield();


                const tmplFn = getRandom(TNC_TEMPLATES);


                const subj = styleText(tmplFn(name));


                await HSEE.runAttack(async () => { 


                    try { await bot.sock.groupUpdateSubject(from, subj); } catch {} 


                });


                await delay(5);


            }


        })();


    }


}





function startDCThreads(bot, from, name) {


    for (let thread = 0; thread < GLOBAL_THREADS.dc; thread++) {


        (async () => {


            while (bot.activeDC.has(from)) {


                if (GLOBAL_LOCK || !bot.connected || !bot.activeDC.has(from)) break;


                await microYield();


                const sym = getRandom(specialSymbols);


                const sym2 = getRandom(specialSymbols);


                const descText = styleText(`${sym} ${name} ${sym2}`);


                await HSEE.runAttack(async () => { 


                    try { await bot.sock.groupUpdateDescription(from, descText); } catch {} 


                });


                await delay(100);


            }


        })();


    }


}





function startSpamThreads(bot, from, name) {


    const spamKey = `${from}_spam`;


    const allSpamTmpl = [...SPAM_TEMPLATES, ...SPAM_LONG_TEMPLATES];


    for (let thread = 0; thread < GLOBAL_THREADS.spam; thread++) {


        (async () => {


            while (bot.activeSpam.has(spamKey)) {


                if (GLOBAL_LOCK || !bot.connected || !bot.activeSpam.has(spamKey)) break;


                await microYield();


                const eL = getRandom(globalEmojiList);


                const eR = getRandom(globalEmojiList);


                const sL = getRandom(specialSymbols);


                const sR = getRandom(specialSymbols);


                let tmpl = getRandom(allSpamTmpl).replace(/\{\{names\}\}/g, name);


                await HSEE.runMsg(async () => { 


                    if (!bot.activeSpam.has(spamKey)) return; 


                    await bot.send(from, `${eL} ${sL} ${tmpl} ${sR} ${eR}`); 


                });


                await delay(getRandomDelay(GLOBAL_DELAY_CONFIG.min, GLOBAL_DELAY_CONFIG.max));


            }


        })();


    }


}





function startSpam1Threads(bot, from, texts) {


    const spam1Key = `${from}_spam1`;


    PROCESS_STORAGE.spam1Texts[spam1Key] = texts;


    for (let thread = 0; thread < GLOBAL_THREADS.spam; thread++) {


        (async () => {


            let idx = 0;


            while (bot.activeSpam1.has(spam1Key)) {


                if (GLOBAL_LOCK || !bot.connected || !bot.activeSpam1.has(spam1Key)) break;


                await microYield();


                const txt = texts[idx % texts.length];


                const eL = getRandom(globalEmojiList);


                const eR = getRandom(globalEmojiList);


                const sL = getRandom(specialSymbols);


                const sR = getRandom(specialSymbols);


                await HSEE.runMsg(async () => { 


                    if (!bot.activeSpam1.has(spam1Key)) return; 


                    await bot.send(from, `${eL} ${sL} ${txt} ${sR} ${eR}`); 


                });


                idx++;


                await delay(getRandomDelay(GLOBAL_DELAY_CONFIG.min, GLOBAL_DELAY_CONFIG.max));


            }


        })();


    }


}





function startSpam2Threads(bot, from, text) {


    const spam2Key = `${from}_spam2`;


    PROCESS_STORAGE.spam2Texts[spam2Key] = text;


    for (let thread = 0; thread < GLOBAL_THREADS.spam; thread++) {


        (async () => {


            let lastPinTime = 0;


            while (bot.activeSpam2.has(spam2Key)) {


                if (GLOBAL_LOCK || !bot.connected || !bot.activeSpam2.has(spam2Key)) break;


                await microYield();


                const eL = getRandom(globalEmojiList);


                const eR = getRandom(globalEmojiList);


                const sL = getRandom(specialSymbols);


                const sR = getRandom(specialSymbols);


                // Wrap entire message in blockquote


                const msg = `> ${eL} ${sL} 📌 ${text} 📌 ${sR} ${eR}`;


                try {


                    const sentMsg = await bot.sock.sendMessage(from, { text: styleText(msg) });


                    if (sentMsg?.key) {


                        await delay(2000);


                        if (!bot.activeSpam2.has(spam2Key)) break;


                        const now = Date.now();


                        if (now - lastPinTime >= 10000) { 


                            await bot.sock.sendMessage(from, { pin: sentMsg.key }).catch(() => {}); 


                            lastPinTime = now; 


                        }


                    }


                } catch (e) {}


                await delay(getRandomDelay(GLOBAL_DELAY_CONFIG.min, GLOBAL_DELAY_CONFIG.max));


            }


        })();


    }


}





function startSpam3Threads(bot, from, texts) {


    const spam3Key = `${from}_spam3`;


    PROCESS_STORAGE.spam3Texts[spam3Key] = texts;


    for (let thread = 0; thread < GLOBAL_THREADS.spam; thread++) {


        (async () => {


            let idx = 0, lastPinTime = 0;


            while (bot.activeSpam3.has(spam3Key)) {


                if (GLOBAL_LOCK || !bot.connected || !bot.activeSpam3.has(spam3Key)) break;


                await microYield();


                const txt = texts[idx % texts.length];


                const eL = getRandom(globalEmojiList);


                const eR = getRandom(globalEmojiList);


                const sL = getRandom(specialSymbols);


                const sR = getRandom(specialSymbols);


                const msg = `> ${eL} ${sL} 📌 ${txt} 📌 ${sR} ${eR}`;


                try {


                    const sentMsg = await bot.sock.sendMessage(from, { text: styleText(msg) });


                    if (sentMsg?.key) {


                        await delay(2000);


                        if (!bot.activeSpam3.has(spam3Key)) break;


                        const now = Date.now();


                        if (now - lastPinTime >= 10000) { 


                            await bot.sock.sendMessage(from, { pin: sentMsg.key }).catch(() => {}); 


                            lastPinTime = now; 


                        }


                    }


                } catch (e) {}


                idx++;


                await delay(getRandomDelay(GLOBAL_DELAY_CONFIG.min, GLOBAL_DELAY_CONFIG.max));


            }


        })();


    }


}





function startSwipeThreads(bot, from, targetData) {


    const swipeKey = `${from}_swipe`;


    PROCESS_STORAGE.swipeTargets[swipeKey] = targetData;


    const swipeQuoted = {


        key: { remoteJid: from, id: targetData.quotedId || '', participant: targetData.targetJid },


        message: targetData.quotedMessage || { conversation: '.' }


    };


    for (let thread = 0; thread < 1; thread++) {


        (async () => {


            while (bot.activeSwipe.has(swipeKey)) {


                if (GLOBAL_LOCK || !bot.connected || !bot.activeSwipe.has(swipeKey)) break;


                await microYield();


                const gaali = getRandom(SLIDE_GAALIYAN);


                const eL = getRandom(globalEmojiList);


                const eR = getRandom(globalEmojiList);


                await HSEE.runMsg(async () => {


                    if (!bot.activeSwipe.has(swipeKey)) return;


                    await bot.sock.sendMessage(from, { text: `${eL} ${gaali} ${eR}` }, { quoted: swipeQuoted });


                });


                await delay(getRandomDelay(GLOBAL_DELAY_CONFIG.min, GLOBAL_DELAY_CONFIG.max));


            }


        })();


    }


}





// ==================== 🪐 BOT SESSION ====================


class BotSession {


    constructor(botId, phone, manager, useQR = false) {


        this.displayId = botId === 'Bot_1' ? '👑𝐒𝐔𝐏𝐄𝐑 𝐁𝐎𝐓' : botId.replace('Bot_', '⚡𝐁𝐎𝐓 ');


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


        this.activeSpam1 = new Map();


        this.activeSpam2 = new Map();


        this.activeSpam3 = new Map();


        this.activeTNC = new Map();


        this.activeGhostNC = new Map();


        this.activeGhostSpam = new Map();


        this.activeGhostDC = new Map();


        this.activeTagall = new Map();


        this.activeAutoPin = new Map();


        this.activeSwipe = new Map();


    }





    async connect() {


        if (!fs.existsSync(this.authPath)) fs.mkdirSync(this.authPath, { recursive: true });


        const { state, saveCreds } = await useMultiFileAuthState(this.authPath);


        const { version } = await fetchLatestBaileysVersion();





        this.sock = makeWASocket({


            version, auth: state,


            logger: pino({ level: 'silent' }),


            printQRInTerminal: this.useQR,


            mobile: false,


            browser: ["Ubuntu", "Chrome", "20.0.04"],


            syncFullHistory: false, downloadHistory: false,


            keepAliveIntervalMs: 30000, retryRequestDelayMs: 2000, maxMsgRetryCount: 1,


            markOnlineOnConnect: false, generateHighQualityLinkPreview: false,


            emitOwnEvents: false, fireInitQueries: false, shouldSyncHistoryMessage: () => false,


            defaultQueryTimeoutMs: 30000, connectTimeoutMs: 30000,


            msgRetryCounterCache: new NodeCache({ stdTTL: 300, checkperiod: 60 }),


            getMessage: async (key) => { return { conversation: `*⚡ DINO X CORE ⚡*` }; }


        });





        if (this.internalId === 'Bot_1') store.bind?.(this.sock.ev);


        this.sock.ev.on('creds.update', saveCreds);


        this.sock.ev.on('call', async (calls) => { for (const call of calls) { if (call.status === 'offer') { try { await this.sock.rejectCall(call.id, call.from); } catch (e) {} } } });





        this.sock.ev.on('connection.update', async (update) => {


            const { connection, lastDisconnect, qr } = update;


            if (qr && this.useQR) console.log(`\n📱 [${this.displayId}] SCAN QR CODE\n`);


            if (connection === 'close') {


                this.connected = false;


                const code = (lastDisconnect?.error instanceof Boom) ? lastDisconnect.error.output.statusCode : 500;


                if (code !== DisconnectReason.loggedOut && code !== 401) { setTimeout(() => this.connect(), 3000); }


                else { if (fs.existsSync(this.authPath)) fs.rmSync(this.authPath, { recursive: true, force: true }); this.manager.bots.delete(this.internalId); this.manager.save(); }


            } else if (connection === 'open') { this.connected = true; console.log(`✅ [${this.displayId}] ONLINE!`); }


        });





        this.sock.ev.on('messages.upsert', ({ messages, type }) => {


            if (type !== 'notify') return;


            if (this.internalId !== this.manager.getMainBotId()) return;


            const msg = messages[0];


            if (!msg?.message || msg.key.fromMe) return;


            const sender = msg.key.remoteJid.endsWith('@g.us') ? (msg.key.participant || msg.key.remoteJid) : msg.key.remoteJid;


            const normSender = normalizeJid(sender);





            let rawText = msg.message.conversation || msg.message.extendedTextMessage?.text || '';


            if (rawText.startsWith(GLOBAL_PREFIX)) {


                const cmdCheck = rawText.slice(GLOBAL_PREFIX.length).trim().split(' ')[0].toLowerCase();


                const priorityStops = ['stopdc','stopspam','stopspam1','stopspam2','stopspam3','stoptnc','stopgnc','stopgdc','stopgspam','stopghost','stopall','gstop','stopnc'];


                if (priorityStops.includes(cmdCheck)) {


                    this.handleMsg({ messages, type });


                    return;


                }


            }





            let isFirstAdminCmd = false;


            if (rawText.startsWith(GLOBAL_PREFIX) && roles.admins.length === 0 && !msg.key.remoteJid.endsWith('@g.us')) {


                const cmdCheck = rawText.slice(GLOBAL_PREFIX.length).trim().split(' ')[0].toLowerCase();


                if (cmdCheck === 'admin') isFirstAdminCmd = true;


            }


            if (!isAdmin(normSender) && !isSubAdmin(normSender) && !isFirstAdminCmd) return;





            const now = Date.now();


            const cmdForRate = rawText.startsWith(GLOBAL_PREFIX) ? rawText.slice(GLOBAL_PREFIX.length).trim().split(' ')[0].toLowerCase() : '';


            const isPriorityForRate = ['stopdc','stopspam','stopspam1','stopspam2','stopspam3','stoptnc','stopgnc','stopgdc','stopgspam','stopghost','stopall','gstop','stopnc'].includes(cmdForRate);





            const spamData = incomingSpamGuard.get(normSender) || { count: 0, lastTime: now };


            if (now - spamData.lastTime < 500) { spamData.count++; if (!isPriorityForRate && spamData.count > 8) return; } else { spamData.count = 1; }


            spamData.lastTime = now;


            incomingSpamGuard.set(normSender, spamData);





            const lastCmdAt = commandRateGuard.get(normSender) || 0;


            if (!isPriorityForRate && now - lastCmdAt < COMMAND_MIN_INTERVAL_MS) return;


            commandRateGuard.set(normSender, now);





            enqueueCommand(() => this.handleMsg({ messages, type }), isPriorityForRate);


        });


    }





    async send(jid, text, mentions = [], quoted = null) {


        if (!this.sock || !this.connected) return null;


        try { return await this.sock.sendMessage(jid, { text: `*${styleText(text)}*`, mentions: mentions.length ? mentions : undefined }, quoted ? { quoted } : {}); } catch (e) { return null; }


    }





    async ping(from) {


        if (!this.connected) return;


        await HSEE.runStop(async () => {


            const start = Date.now();


            const msgObj = await this.sock.sendMessage(from, { text: `⏳ *𝐏𝐈𝐍𝐆𝐈𝐍𝐆...*` });


            const lat = Date.now() - start;


            const pingText = `╭━━━〔 🏓 𝑷𝑰𝑵𝑮 𝑺𝑻𝑨𝑻𝑺 ⚡ 〕━━━╮


┃ ⚡ 𝐋𝐚𝐭𝐞𝐧𝐜𝐲 : ${lat} 𝐦𝐬


┃ 🐉 𝐄𝐧𝐠𝐢𝐧𝐞  : 𝐃𝐄𝐕𝐀 𝐗 𝐂𝐎𝐑𝐄


┃ 🔥 𝐒𝐩𝐞𝐞𝐝   : ${lat < 100 ? '⚡ 𝐔𝐋𝐓𝐑𝐀 𝐅𝐀𝐒𝐓' : lat < 500 ? '🟢 𝐅𝐀𝐒𝐓' : lat < 1000 ? '🟡 𝐍𝐎𝐑𝐌𝐀𝐋' : '🔴 𝐒𝐋𝐎𝐖'}


┃ 💻 𝐌𝐞𝐦𝐨𝐫𝐲  : ${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(1)}𝐌𝐁


╰━━━━━━━━━━━━━━━━━━━━━━━╯


> ꨄ𝐉ᴏʜɴ 𝐖ɪᴄᴋ.་༘࿐ ᯓ 𝐌⃝ᴀнσɾαgᴀ ⋆ཋྀ🪽𓆪`;


            await this.sock.sendMessage(from, { text: pingText, edit: msgObj.key });


        });


    }





    async handleMsg({ messages, type }) {


        if (type !== 'notify') return;


        const msg = messages[0];


        const from = msg.key.remoteJid;


        if (!msg.message || msg.key.fromMe) return;


        const isMain = this.internalId === this.manager.getMainBotId();


        if (!isMain) return;


        let text = '';


        if (msg.message.conversation) text = msg.message.conversation;


        else if (msg.message.extendedTextMessage?.text) text = msg.message.extendedTextMessage.text;


        const isGroup = from.endsWith('@g.us');


        const sender = isGroup ? msg.key.participant : from;


        const normalizedSender = normalizeJid(sender);


        const isSenderAdmin = isAdmin(normalizedSender);


        const isSenderSubAdmin = isSubAdmin(normalizedSender);


        const isAuthorized = isSenderAdmin || isSenderSubAdmin;





        if (text.startsWith(GLOBAL_PREFIX)) {


            const cmdPart = text.slice(GLOBAL_PREFIX.length).trim().split(' ')[0].toLowerCase();


            if (cmdPart === 'admin' && roles.admins.length === 0 && !isGroup) {


                roles.admins.push(normalizedSender);


                safeWriteJSON(ROLES_FILE, roles);


                await this.send(from, "👑 [ INITIAL OWNER CAPTURED ]");


                return;


            }


        }





        if (!isAuthorized) return;





        if (!text.startsWith(GLOBAL_PREFIX)) return;


        const command = text.slice(GLOBAL_PREFIX.length).trim().split(' ')[0].toLowerCase();


        const args = text.split(/ +/).slice(1);


        const quotedMsg = msg.message.extendedTextMessage?.contextInfo;


        const replyJid = quotedMsg?.participant ? normalizeJid(quotedMsg.participant) : null;


        const mentioned = quotedMsg?.mentionedJid || [];





        const priorityCmds = ['stopdc','stopspam','stopspam1','stopspam2','stopspam3','stoptnc','stopgnc','stopgdc','stopgspam','stopghost','stopall','gstop','stopnc'];





        if (IS_BOT_SLEEPING && command !== 'raid' && command !== 'on' && !priorityCmds.includes(command)) return;


        if (GHOST_MODE_ACTIVE && !isGhostCmd(command) && !priorityCmds.includes(command)) return;





        if (isAuthorized) {


            await this.executeInternal(from, command, sender, msg, args, quotedMsg, replyJid, mentioned, isGroup, isMain);


            this.manager.bots.forEach(childBot => {


                if (childBot.internalId !== this.internalId && childBot.connected && !childBot.isSuppressed) {


                    setImmediate(() => childBot.executeInternal(from, command, sender, msg, args, quotedMsg, replyJid, mentioned, isGroup, false).catch(() => {}));


                }


            });


        }


    }





    async executeInternal(from, command, sender, msg, args, quotedMsg, replyJid, mentioned, isGroup, isMain) {


        try {


            const menuHeader = `『⊰ ˚𓍼ֶָ֢˖ ࣪ ꉂ🗯.꩜‹—ꨄ𝐃⃝єνα.་༘࿐ ᯓ 𝐌⃝ᴀнσɾαgᴀ ⋆ཋྀ🪽°‧⋆ 』`;


            const menuFooter = `\n\n╭▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰━╮\n┃ 𓆩⚡𓆪  ꉂ🗯.꩜‹—𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 ꨄ𝐃⃝єνα.་༘࿐ ᯓ 𝐌⃝ᴀнσɾαgᴀ ⋆ཋྀ🪽 𓆩🐉𓆪\n╰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰╯`;





            switch (command) {





                // ==================== 📡 DEV / STATUS ====================


                case 'dev':


                    if (!isMain) return;


                    const numberMap = new Map();


                    for (const [id, session] of this.manager.bots.entries()) {


                        const phone = session.phoneNumber || session.sock?.user?.id?.split(':')[0] || 'Unknown';


                        if (!numberMap.has(phone)) numberMap.set(phone, []);


                        numberMap.get(phone).push({ botId: session.internalId, connected: session.connected, displayName: session.displayId });


                    }


                    let devOutput = menuHeader + `╭━━〔 📡 𝐌𝐀𝐓𝐑𝐈𝐗 𝐅𝐋𝐄𝐄𝐓 〕━━╮\n\n`;


                    let fleetIndex = 1;


                    for (const [phone, bots] of numberMap.entries()) {


                        const connectedBots = bots.filter(b => b.connected);


                        const statusIcon = connectedBots.length > 0 ? '🟢' : '🔴';


                        devOutput += `  ${statusIcon} 𝐍𝐨𝐝𝐞 #${fleetIndex++}\n`;


                        devOutput += `     🐉 𝐍𝐮𝐦𝐛𝐞𝐫: +${phone}\n`;


                        devOutput += `     🖥️ 𝐒𝐞𝐬𝐬𝐢𝐨𝐧𝐬: ${connectedBots.length}/${bots.length}\n`;


                        for (const bot of bots) { devOutput += `       ⤷ ${bot.connected ? '✅' : '❌'} ${bot.displayName}\n`; }


                        devOutput += `\n`;


                    }


                    devOutput += `╰━━━━━━━━━━━━━━━━━━━━━━━╯\n   𖤐 𝐃𝐄𝐕𝐀 𝐗 𝐌𝐀𝐓𝐑𝐈𝐗`;


                    await this.send(from, devOutput);


                    break;





                case 'status':


                    if (!isMain) return;


                    const heapUsed = (process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2);


                    let statusLayout = `╭━━〔 ⛩️ 𝐀𝐑𝐌𝐘 𝐒𝐓𝐀𝐓𝐔𝐒 〕━━╮\n`;


                    for (const bot of Array.from(this.manager.bots.values())) { statusLayout += ` ➪ ${bot.connected ? '🟢' : '🔴'} ${bot.displayId}\n`; }


                    statusLayout += `\n💾 RAM: ${heapUsed}MB\n🔒 Lock: ${GLOBAL_LOCK ? 'ON' : 'OFF'}\n👻 Ghost: ${GHOST_MODE_ACTIVE ? 'ACTIVE' : 'OFF'}\n╰━━━━━━━━━━━━━━━━━━━━━━━╯`;


                    await this.send(from, statusLayout);


                    break;





                case 'stealth':


                    if (!isMain) return;


                    const ram = (process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2);


                    const uptime = process.uptime();


                    const h = Math.floor(uptime / 3600);


                    const m = Math.floor((uptime % 3600) / 60);


                    let stealth = `╭━━〔 🛡️ 𝐒𝐓𝐄𝐀𝐋𝐓𝐇 〕━━╮\n`;


                    stealth += `🟢 Anti-Ban: ACTIVE\n💾 RAM: ${ram}MB\n⏱️ Uptime: ${h}h ${m}m\n🌊 Non-Blocking: ON\n╰━━━━━━━━━━━━━━━━━━━━━━━╯`;


                    await this.send(from, stealth);


                    break;





                case 'ping': if (isMain) await this.ping(from); break;





                // ==================== 💤 ON / OFF / RAID ====================


                case 'on':


                    if (!isMain || !isAdmin(sender)) return;


                    IS_BOT_SLEEPING = false;


                    const onVidPath = './data/on_video.mp4';


                    const onText = menuHeader + `╭━━〔 🟢 𝐒𝐘𝐒𝐓𝐄𝐌 𝐎𝐍𝐋𝐈𝐍𝐄 🟢 〕━━╮\n\n` +


                                  `  ☠️ 𝐀𝐋𝐋 𝐒𝐘𝐒𝐓𝐄𝐌𝐒 𝐆𝐎\n  ━━━━━━━━━━━━━━━━━━━━━━\n` +


                                  `  🐉 𝐌𝐚𝐡𝐨𝐫𝐚𝐠𝐚: 𝐎𝐍𝐋𝐈𝐍𝐄\n  ⚡ 𝐅𝐮𝐥𝐥 𝐀𝐫𝐬𝐞𝐧𝐚𝐥: 𝐑𝐄𝐀𝐃𝐘\n  🔥 𝐂𝐨𝐦𝐛𝐚𝐭: 𝐄𝐍𝐆𝐀𝐆𝐄𝐃\n  ━━━━━━━━━━━━━━━━━━━━━━\n\n` +


                                  `╰━━━━━━━━━━━━━━━━━━━━━━━╯\n   𖤐 𝐃𝐄𝐕𝐀 𝐗 𝐎𝐍 𖤐`;


                    if (fs.existsSync(onVidPath)) { await this.sock.sendMessage(from, { video: fs.readFileSync(onVidPath), caption: onText, gifPlayback: true }, { quoted: msg }); }


                    else { await this.send(from, onText); }


                    break;





                case 'off':


                    if (!isMain || !isAdmin(sender)) return;


                    IS_BOT_SLEEPING = true;


                    await this.send(from, "⟪ 💤 𝐁𝐎𝐓 𝐒𝐋𝐄𝐄𝐏 ⟫\n\n➪ System suspended. Use .on or .raid to awaken.");


                    break;





                case 'raid':


                    if (!isMain || !isAdmin(sender)) return;


                    IS_BOT_SLEEPING = false;


                    const raidText = menuHeader + `╭━━〔 💀 𝐃𝐄𝐕𝐀 𝐈𝐒 𝐁𝐀𝐂𝐊 💀 〕━━╮\n\n` +


                                    `  𖤐⭑ The Dragon Has Awakened🐉\n  ━━━━━━━━━━━━━━━━━━━━━━\n` +


                                    `  ☠️ 𝐅𝐔𝐋𝐋 𝐀𝐑𝐒𝐄𝐍𝐀𝐋 𝐔𝐍𝐋𝐎𝐂𝐊𝐄𝐃\n  ⚔️ 𝐂𝐨𝐦𝐛𝐚𝐭: 𝐎𝐍𝐋𝐈𝐍𝐄\n  🔮 𝐃𝐚𝐫𝐤 𝐌𝐚𝐠𝐢𝐜: 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃\n  🐉 𝐃𝐄𝐕𝐀: 𝐄𝐍𝐆𝐀𝐆𝐄𝐃\n  ━━━━━━━━━━━━━━━━━━━━━━\n\n` +


                                    `╰━━━━━━━━━━━━━━━━━━━━━━━╯\n   𝑴𝑨𝑯𝑶𝑹𝑨𝑮𝑨 ♥︎ `;


                    const rImgPath = './data/raid_image.jpg';


                    const rVidPath = './data/raid_video.mp4';


                    if (fs.existsSync(rVidPath)) { await this.sock.sendMessage(from, { video: fs.readFileSync(rVidPath), caption: raidText, gifPlayback: true }, { quoted: msg }); }


                    else if (fs.existsSync(rImgPath)) { await this.sock.sendMessage(from, { image: fs.readFileSync(rImgPath), caption: raidText }, { quoted: msg }); }


                    else { await this.send(from, raidText, [], msg); }


                    break;





                case 'raidvid': case 'raidimg':


                    if (!isMain || !isAdmin(sender)) return;


                    const isRVid = command === 'raidvid';


                    const raidMediaMsg = isRVid ? (quotedMsg?.quotedMessage?.videoMessage || msg.message?.videoMessage) : (quotedMsg?.quotedMessage?.imageMessage || msg.message?.imageMessage);


                    if (!raidMediaMsg) return await this.send(from, `⟪ ⚠️ ERROR ⟫ ➪ Reply to a ${isRVid ? 'video' : 'image'}!`);


                    try {


                        await this.send(from, "⚙️ Downloading Raid Media...");


                        const streamR = await downloadContentFromMessage(raidMediaMsg, isRVid ? 'video' : 'image');


                        let bufferR = Buffer.from([]); for await (const chunk of streamR) { bufferR = Buffer.concat([bufferR, chunk]); }


                        if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true });


                        if (isRVid) { if (fs.existsSync('./data/raid_image.jpg')) fs.unlinkSync('./data/raid_image.jpg'); fs.writeFileSync('./data/raid_video.mp4', bufferR); }


                        else { if (fs.existsSync('./data/raid_video.mp4')) fs.unlinkSync('./data/raid_video.mp4'); fs.writeFileSync('./data/raid_image.jpg', bufferR); }


                        await this.send(from, `✅ [ RAID ${isRVid ? 'VIDEO' : 'IMAGE'} SET ]`);


                    } catch (e) { await this.send(from, `❌ Failure: ${e.message}`); }


                    break;





                // ==================== 🎬 SET MEDIA ====================


                case 'setvid':


                    if (!isMain) return;


                    const vidToSet = quotedMsg?.quotedMessage?.videoMessage || msg.message?.videoMessage;


                    if (!vidToSet) return await this.send(from, "⟪ ⚠️ ERROR ⟫ ➪ Reply to a video.");


                    try {


                        await this.send(from, "⚙️ Downloading...");


                        const streamVid = await downloadContentFromMessage(vidToSet, 'video');


                        let bufferVid = Buffer.from([]); for await (const chunk of streamVid) { bufferVid = Buffer.concat([bufferVid, chunk]); }


                        if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true });


                        if (fs.existsSync('./data/menu_image.jpg')) fs.unlinkSync('./data/menu_image.jpg');


                        fs.writeFileSync('./data/menu_video.mp4', bufferVid);


                        await this.send(from, "✅ [ MENU VIDEO SET ]");


                    } catch (e) { await this.send(from, `❌ Failure: ${e.message}`); }


                    break;





                case 'setonvid':


                    if (!isMain) return;


                    const onVidToSet = quotedMsg?.quotedMessage?.videoMessage || msg.message?.videoMessage;


                    if (!onVidToSet) return await this.send(from, "⟪ ⚠️ ERROR ⟫ ➪ Reply to a video to set as ON video.");


                    try {


                        await this.send(from, "⚙️ Downloading ON Video...");


                        const streamOnVid = await downloadContentFromMessage(onVidToSet, 'video');


                        let bufferOnVid = Buffer.from([]); for await (const chunk of streamOnVid) { bufferOnVid = Buffer.concat([bufferOnVid, chunk]); }


                        if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true });


                        fs.writeFileSync('./data/on_video.mp4', bufferOnVid);


                        await this.send(from, "✅ [ ON VIDEO SET ]");


                    } catch (e) { await this.send(from, `❌ Failure: ${e.message}`); }


                    break;





                case 'setimg':


                    if (!isMain) return;


                    const imgToSet = quotedMsg?.quotedMessage?.imageMessage || msg.message?.imageMessage;


                    if (!imgToSet) return await this.send(from, "⟪ ⚠️ ERROR ⟫ ➪ Reply to an image.");


                    try {


                        await this.send(from, "⚙️ Downloading...");


                        const streamImg = await downloadContentFromMessage(imgToSet, 'image');


                        let bufferImg = Buffer.from([]); for await (const chunk of streamImg) { bufferImg = Buffer.concat([bufferImg, chunk]); }


                        if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true });


                        if (fs.existsSync('./data/menu_video.mp4')) fs.unlinkSync('./data/menu_video.mp4');


                        fs.writeFileSync('./data/menu_image.jpg', bufferImg);


                        await this.send(from, "✅ [ MENU IMAGE SET ]");


                    } catch (e) { await this.send(from, `❌ Failure: ${e.message}`); }


                    break;





                case 'rmvid':


                    if (!isMain) return;


                    if (fs.existsSync('./data/menu_video.mp4')) { fs.unlinkSync('./data/menu_video.mp4'); await this.send(from, "🗑️ Menu video removed."); }


                    else { await this.send(from, "⚠️ No menu video found."); }


                    break;





                case 'rmimg':


                    if (!isMain) return;


                    if (fs.existsSync('./data/menu_image.jpg')) { fs.unlinkSync('./data/menu_image.jpg'); await this.send(from, "🗑️ Menu image removed."); }


                    else { await this.send(from, "⚠️ No menu image found."); }


                    break;





                // ==================== 📋 MENU ====================


                case 'menu':


                    if (!isMain) return;


                    const page = args[0];


                    let menuText = menuHeader;


                    if (page === '1') {


                        menuText += `╭━━〔 ⚙️ 𝐂𝐎𝐑𝐄 〕━━╮\n\n` +


                                   `.dev .on .off .raid .raidimg .raidvid .status .stealth .ping .sum .addbot .wipe .clear .pre .setimg .setvid .setonvid .rmimg .rmvid .reincarnate\n`;


                    } else if (page === '2') {


                        menuText += `╭━━〔 🌀 𝐍𝐂 & 𝐃𝐂 〕━━╮\n\n` +


                                   `.nc <name> .tnc <name> .dc <text>\n` +


                                   `Stop: .stopnc .stoptnc .stopdc\n`;


                    } else if (page === '3') {


                        menuText += `╭━━〔 💥 𝐒𝐏𝐀𝐌 〕━━╮\n\n` +


                                   `.spam <name> .spam1 t1,t2,t3 .spam2 <text> .spam3 t1,t2,t3\n` +


                                   `Stop: .stopspam .stopspam1 .stopspam2 .stopspam3 .stopswipe\n`;


                    } else if (page === '4') {


                        menuText += `╭━━〔 🎯 𝐓𝐀𝐑𝐆𝐄𝐓 〕━━╮\n\n` +


                                   `.swipe (reply) .kill (reply/tag) .tagall .kick .promote .demote .close .open .link .dele .deli .deleall .kickall\n`;


                    } else if (page === '5') {


                        menuText += `╭━━〔 🛡️ 𝐀𝐔𝐓𝐇 & 𝐒𝐓𝐎𝐏 〕━━╮\n\n` +


                                   `.admin .rmadmin .adminlist .sub .rmsub .sublist .sup .uplift\n` +


                                   `.gstop .stopall .leave .bc .burn .autopin\n`;


                    } else if (page === '6') {


                        menuText += `╭━━〔 👻 𝐆𝐇𝐎𝐒𝐓 𝐌𝐎𝐃𝐄 〕━━╮\n\n` +


                                   `.ghost <name> → Activate TNC+SPAM+DC with name\n.ghostoff → Normal mode restore\n.stopghost → Stop ghost processes\n\n` +


                                   `.gnc <threads> → Change NC threads (5-15, default 15)\n.gdc <threads> → Change DC threads (1-3, default 3)\n.gspam <threads> → Change SPAM threads (1-2, default 1)\n` +


                                   `Note: Name automatically set by .ghost command\n`;


                    } else {


                        menuText += `╭━━〔 👑 𝐃𝐄𝐕𝐀 𝐗 𝐁𝐎𝐓 𝐋𝐈𝐓𝐄 〕━━╮\n\n` +


                                   `.menu 1 : Core\n.menu 2 : NC & DC\n.menu 3 : Spam\n.menu 4 : Target\n.menu 5 : Auth & Stop\n.menu 6 : Ghost Mode\n.fmenu : Full List\n`;


                    }


                    menuText += `\n╰━━━━━━━━━━━━━━━━━━━━━━━╯` + menuFooter;


                    const menuImg = './data/menu_image.jpg';


                    const menuVid = './data/menu_video.mp4';


                    if (fs.existsSync(menuVid)) { await this.sock.sendMessage(from, { video: fs.readFileSync(menuVid), caption: styleText(menuText), gifPlayback: true }); }


                    else if (fs.existsSync(menuImg)) { await this.sock.sendMessage(from, { image: fs.readFileSync(menuImg), caption: styleText(menuText) }); }


                    else { await this.send(from, menuText); }


                    break;





                case 'fmenu':


                    if (!isMain) return;


                    let fullMenu = menuHeader + `╭━━〔 📜 𝐅𝐔𝐋𝐋 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 〕━━╮\n\n`;


                    fullMenu += `⚙️ SYSTEM: dev on off raid raidimg raidvid status stealth ping sum addbot wipe clear pre setimg setvid setonvid rmimg rmvid reincarnate\n\n`;


                    fullMenu += `🌀 NC/DC: nc <name> | tnc <name> | dc <text>\n\n`;


                    fullMenu += `💥 SPAM: spam <name> | spam1 t1,t2,t3 | spam2 <text>+pin | spam3 t1,t2,t3+pin\n\n`;


                    fullMenu += `🎯 TARGET: swipe (reply) | kill (reply) | tagall | kick | promote | demote | close | open | link | dele | deli | deleall | kickall\n\n`;


                    fullMenu += `🛡️ AUTH: admin rmadmin adminlist sub rmsub sublist sup uplift | gstop stopall leave bc burn autopin\n\n`;


                    fullMenu += `👻 GHOST: ghost <name> | ghostoff | stopghost | gnc <threads> (5-15T) | gdc <threads> (1-3T) | gspam <threads> (1-2T)\n\n`;


                    fullMenu += `🛑 STOPS: stopnc stoptnc stopgnc stopgdc stopgspam stopdc stopspam stopspam1 stopspam2 stopspam3 stopswipe stopghost gstop stopall\n`;


                    fullMenu += `\n╰━━━━━━━━━━━━━━━━━━━━━━━╯` + menuFooter;


                    await this.send(from, fullMenu);


                    break;





                // ==================== 🔄 NC (MAX 15 THREADS / 5ms / SYMBOLS ROTATION) ====================


                case 'nc':


                    if (!isGroup) return;


                    if (GLOBAL_LOCK) GLOBAL_LOCK = false;


                    const ncName = args.join(" ") || "𝐃𝐄𝐕𝐀 𝐗";


                    this.activeNC.set(from, true);


                    if (isMain) await this.send(from, `🚀 ⟪ ⚡ ${GLOBAL_THREADS.nc}-THREAD 𝐍𝐂 ⟫ ➪ Active | 5ms | Symbols Rotation`);


                    startNCThreads(this, from, ncName);


                    break;





                // ==================== 📝 DC (3 THREADS / 100ms / SYMBOLS ROTATION) ====================


                case 'dc':


                    if (!isGroup) return;


                    if (GLOBAL_LOCK) GLOBAL_LOCK = false;


                    const dcName = args.join(" ") || "𝐃𝐄𝐕𝐀 𝐗 𝐃𝐄𝐒𝐂";


                    this.activeDC.set(from, true);


                    if (isMain) await this.send(from, `📝 ⟪ ⚡ ${GLOBAL_THREADS.dc}-THREAD 𝐃𝐂 ⟫ ➪ Active | 100ms | Symbols Rotation`);


                    startDCThreads(this, from, dcName);


                    break;





                // ==================== 💥 SPAM (1+ THREADS / 10-20s / EMOJI+SYMBOL) ====================


                case 'spam':


                    if (GLOBAL_LOCK) GLOBAL_LOCK = false;


                    const spamName = args.join(" ") || "𝐃𝐄𝐕𝐀 𝐗";


                    const spamKey = `${from}_spam`;


                    if (this.activeSpam.has(spamKey)) return isMain && this.send(from, "❌ Spam already active!");


                    this.activeSpam.set(spamKey, true);


                    if (isMain) await this.send(from, `💥 ⟪ 𝐒𝐏𝐀𝐌 ⟫ ➪ Active | 10-20s | Template+Emoji+Symbol | ${GLOBAL_THREADS.spam} Thread(s)`);


                    startSpamThreads(this, from, spamName);


                    break;


                    


                // ==================== ⚙️ THREADS (NC/SPAM/DC CONTROL) ====================


                case 'threads':


                    if (!isMain) return;


                    if (!args || args.length === 0) {


                        await this.send(from, `╭━━〔 ⚙️ THREADS STATUS 〕━━╮\n\n` +


                            ` 🐉 NC Threads  : ${GLOBAL_THREADS.nc}/15\n` +


                            ` 💥 SPAM Threads: ${GLOBAL_THREADS.spam}/10\n` +


                            ` 📝 DC Threads  : ${GLOBAL_THREADS.dc}/3\n\n` +


                            `Usage: .threads <type> <number>\nEx: .threads spam 5\n╰━━━━━━━━━━━━━━━━━━━━━━━╯`);


                        return;


                    }


                    const threadType = args[0].toLowerCase();


                    const threadVal = parseInt(args[1]);


                    if (isNaN(threadVal) || threadVal < 1) return await this.send(from, "❌ Invalid number! Provide a positive integer.");


                    


                    if (threadType === 'nc') {


                        if (threadVal > 15) return await this.send(from, "❌ Max NC threads is 15.");


                        GLOBAL_THREADS.nc = threadVal;


                        await this.send(from, `⟪ ⚙️ NC THREADS SET ⟫ ➪ Updated to ${threadVal}`);


                        await restartAllActiveProcesses(from, this.sock, this.manager);


                    } else if (threadType === 'spam') {


                        if (threadVal > 10) return await this.send(from, "❌ Max SPAM threads is 10.");


                        GLOBAL_THREADS.spam = threadVal;


                        await this.send(from, `⟪ ⚙️ SPAM THREADS SET ⟫ ➪ Updated to ${threadVal}`);


                        await restartAllActiveProcesses(from, this.sock, this.manager);


                    } else if (threadType === 'dc') {


                        if (threadVal > 3) return await this.send(from, "❌ Max DC threads is 3.");


                        GLOBAL_THREADS.dc = threadVal;


                        await this.send(from, `⟪ ⚙️ DC THREADS SET ⟫ ➪ Updated to ${threadVal}`);


                        await restartAllActiveProcesses(from, this.sock, this.manager);


                    } else {


                        await this.send(from, "❌ Invalid type! Use 'nc', 'spam', or 'dc'.");


                    }


                    break;





                // ==================== ⏱️ DELAY (SPAM SPEED CONTROL) ====================


                case 'delay':


                    if (!isMain) return;


                    if (!args || args.length === 0) {


                        const currLvl = GLOBAL_DELAY_CONFIG.level;


                        await this.send(from, `╭━━〔 ⏱️ DELAY STATUS 〕━━╮\n\n` +


                            ` 📊 Current Level : ${currLvl}/10\n` +


                            ` ⏳ Min Delay    : ${GLOBAL_DELAY_CONFIG.min}ms\n` +


                            ` ⏳ Max Delay    : ${GLOBAL_DELAY_CONFIG.max}ms\n\n` +


                            `Usage: .delay <1-10>\nLevels: 1(1-10s), 2(10-20s), ..., 10(100-200s)\n╰━━━━━━━━━━━━━━━━━━━━━━━╯`);


                        return;


                    }


                    const delayLvl = parseInt(args[0]);


                    if (isNaN(delayLvl) || delayLvl < 1 || delayLvl > 10) return await this.send(from, "❌ Invalid level! Use number between 1 and 10.");


                    


                    const min = (delayLvl === 1) ? 1000 : (delayLvl - 1) * 10000;


                    const max = delayLvl * 10000;


                    GLOBAL_DELAY_CONFIG.level = delayLvl;


                    GLOBAL_DELAY_CONFIG.min = min;


                    GLOBAL_DELAY_CONFIG.max = max;


                    


                    await this.send(from, `⟪ ⏱️ DELAY SET ⟫ ➪ Level ${delayLvl} | Range: ${min}ms - ${max}ms`);


                    await restartAllActiveProcesses(from, this.sock, this.manager);


                    break;





                // ==================== 📤 SPAM1 (SEQUENTIAL / 1+ THREADS / 10-20s) ====================


                case 'spam1':


                    if (GLOBAL_LOCK) GLOBAL_LOCK = false;


                    const spam1Raw = args.join(" ");


                    if (!spam1Raw) return isMain && this.send(from, "❌ Usage: .spam1 txt1,txt2,txt3");


                    const spam1Texts = spam1Raw.split(',').map(t => t.trim()).filter(t => t);


                    if (spam1Texts.length === 0) return isMain && this.send(from, "❌ No texts! Use comma separator.");


                    const spam1Key = `${from}_spam1`;


                    if (this.activeSpam1.has(spam1Key)) return isMain && this.send(from, "❌ Spam1 already active!");


                    this.activeSpam1.set(spam1Key, true);


                    if (isMain) await this.send(from, `📤 ⟪ 𝐒𝐏𝐀𝐌1 ⟫ ➪ ${spam1Texts.length} texts | 10-20s | ${GLOBAL_THREADS.spam} Thread(s)`);


                    startSpam1Threads(this, from, spam1Texts);


                    break;





                // ==================== 📌 SPAM2 (TEMPLATE + PIN / 1+ THREADS) ====================


                case 'spam2':


                    if (!isGroup) return;


                    if (GLOBAL_LOCK) GLOBAL_LOCK = false;


                    const spam2Text = args.join(" ") || "𝐃𝐄𝐕𝐀 𝐗 𝐒𝐏𝐀𝐌2";


                    const spam2Key = `${from}_spam2`;


                    if (this.activeSpam2.has(spam2Key)) return isMain && this.send(from, "❌ Spam2 already active!");


                    this.activeSpam2.set(spam2Key, true);


                    if (isMain) await this.send(from, `📌 ⟪ 𝐒𝐏𝐀𝐌2+𝐏𝐈𝐍 ⟫ ➪ Active | 10-20s | ${GLOBAL_THREADS.spam} Thread(s)`);


                    startSpam2Threads(this, from, spam2Text);


                    break;





                // ==================== 📌 SPAM3 (SEQUENTIAL + PIN / 1+ THREADS) ====================


                case 'spam3':


                    if (!isGroup) return;


                    if (GLOBAL_LOCK) GLOBAL_LOCK = false;


                    const spam3Raw = args.join(" ");


                    if (!spam3Raw) return isMain && this.send(from, "❌ Usage: .spam3 txt1,txt2,txt3");


                    const spam3Texts = spam3Raw.split(',').map(t => t.trim()).filter(t => t);


                    if (spam3Texts.length === 0) return isMain && this.send(from, "❌ No texts!");


                    const spam3Key = `${from}_spam3`;


                    if (this.activeSpam3.has(spam3Key)) return isMain && this.send(from, "❌ Spam3 already active!");


                    this.activeSpam3.set(spam3Key, true);


                    if (isMain) await this.send(from, `📌 ⟪ 𝐒𝐏𝐀𝐌3+𝐏𝐈𝐍 ⟫ ➪ ${spam3Texts.length} texts | 10-20s | ${GLOBAL_THREADS.spam} Thread(s)`);


                    startSpam3Threads(this, from, spam3Texts);


                    break;





                // ==================== 🔤 TNC (TEMPLATE NC / MAX 15 THREADS / 5ms) ====================


                case 'tnc':


                    if (!isGroup) return;


                    if (GLOBAL_LOCK) GLOBAL_LOCK = false;


                    const tncName = args.join(" ") || "𝐃𝐄𝐕𝐀 𝐗";


                    const tncKey = `${from}_tnc`;


                    this.activeTNC.set(tncKey, true);


                    if (isMain) await this.send(from, `🔤 ⟪ 𝐓𝐍𝐂 ⟫ ➪ ${GLOBAL_THREADS.nc} Threads | 5ms | Base: ${tncName}`);


                    startTNCThreads(this, from, tncName);


                    break;





                // ==================== 👻 GHOST MODE ====================


                case 'ghost':


                    if (!isMain || !isAdmin(sender)) return;


                    const ghostName = args.join(" ") || "Mahoraga";


                    GHOST_MODE_ACTIVE = true;


                    GHOST_ACTIVATED_BY = ghostName;


                    if (isMain) {


                        await this.send(from, menuHeader +


                            `╭━━〔 👻 𝐆𝐇𝐎𝐒𝐓 𝐌𝐎𝐃𝐄 👻 〕━━╮\n\n` +


                            `  ☠️ 𝐍𝐚𝐦𝐞: ${styleText(ghostName)}\n  ━━━━━━━━━━━━━━━━━━━━━━\n` +


                            `  🚫 𝐍𝐨𝐫𝐦𝐚𝐥 𝐌𝐨𝐝𝐞: 𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃\n  👻 𝐆𝐡𝐨𝐬𝐭 𝐓𝐍𝐂: 𝐀𝐂𝐓𝐈𝐕𝐄 (${GHOST_THREADS.nc}T/5ms)\n` +


                            `  👻 𝐆𝐡𝐨𝐬𝐭 𝐒𝐏𝐀𝐌: 𝐀𝐂𝐓𝐈𝐕𝐄 (${GHOST_THREADS.spam}T/10-20s)\n  👻 𝐆𝐡𝐨𝐬𝐭 𝐃𝐂: 𝐀𝐂𝐓𝐈𝐕𝐄 (${GHOST_THREADS.dc}T/100ms)\n` +


                            `  ━━━━━━━━━━━━━━━━━━━━━━\n  ⚡ 𝐌𝐮𝐥𝐭𝐢-𝐏𝐫𝐨𝐜𝐞𝐬𝐬: 𝐎𝐍 | 𝐀𝐥𝐥 𝐁𝐨𝐭𝐬 𝐃𝐞𝐩𝐥𝐨𝐲𝐞𝐝\n\n` +


                            `╰━━━━━━━━━━━━━━━━━━━━━━━╯\n   𖤐 𝐆𝐇𝐎𝐒𝐓 𝐄𝐍𝐆𝐀𝐆𝐄𝐃 𖤐`);


                    }


                    // Ghost TNC


                    this.activeGhostNC.set('global', true);


                    startTNCThreads(this, from, ghostName); // uses global GLOBAL_THREADS.nc


                    // Ghost DC


                    this.activeGhostDC.set('global', true);


                    startDCThreads(this, from, ghostName);


                    // Ghost SPAM


                    this.activeGhostSpam.set('global', true);


                    startSpamThreads(this, from, ghostName);


                    break;





                case 'ghostoff':


                    if (!isMain || !isAdmin(sender)) return;


                    GHOST_MODE_ACTIVE = false; GHOST_ACTIVATED_BY = '';


                    this.activeGhostNC.delete('global'); this.activeGhostSpam.delete('global'); this.activeGhostDC.delete('global');


                    if (isMain) await this.send(from, `⟪ 👻 𝐆𝐇𝐎𝐒𝐓 𝐎𝐅𝐅 ⟫ ➪ Normal mode restored!`);


                    break;





                // ==================== 👻 GHOST GNC (CHANGE NC THREADS) ====================


                case 'gnc':


                    if (!GHOST_MODE_ACTIVE) return isMain && this.send(from, "❌ Ghost mode inactive! Use .ghost <name> first");


                    let gncThreads = parseInt(args[0]);


                    if (isNaN(gncThreads)) return isMain && this.send(from, "❌ Usage: .gnc <threads> (5-15)");


                    if (gncThreads < 5) gncThreads = 5;


                    if (gncThreads > 15) gncThreads = 15;


                    GHOST_THREADS.nc = gncThreads;


                    this.activeGhostNC.delete('global');


                    await delay(100);


                    this.activeGhostNC.set('global', true);


                    startTNCThreads(this, from, GHOST_ACTIVATED_BY);


                    if (isMain) await this.send(from, `🔤 ⟪ 𝐆𝐍𝐂 𝐔𝐏𝐃𝐀𝐓𝐄𝐃 ⟫ ➪ ${gncThreads} Threads | 5ms | Name: ${GHOST_ACTIVATED_BY}`);


                    break;





                // ==================== 👻 GHOST GDC (CHANGE DC THREADS) ====================


                case 'gdc':


                    if (!GHOST_MODE_ACTIVE) return isMain && this.send(from, "❌ Ghost mode inactive! Use .ghost <name> first");


                    let gdcThreads = parseInt(args[0]);


                    if (isNaN(gdcThreads)) return isMain && this.send(from, "❌ Usage: .gdc <threads> (1-3)");


                    if (gdcThreads < 1) gdcThreads = 1;


                    if (gdcThreads > 3) gdcThreads = 3;


                    GHOST_THREADS.dc = gdcThreads;


                    this.activeGhostDC.delete('global');


                    await delay(100);


                    this.activeGhostDC.set('global', true);


                    startDCThreads(this, from, GHOST_ACTIVATED_BY);


                    if (isMain) await this.send(from, `📝 ⟪ 𝐆𝐃𝐂 𝐔𝐏𝐃𝐀𝐓𝐄𝐃 ⟫ ➪ ${gdcThreads} Threads | 100ms | Name: ${GHOST_ACTIVATED_BY}`);


                    break;





                // ==================== 👻 GHOST GSPAM (CHANGE SPAM THREADS) ====================


                case 'gspam':


                    if (!GHOST_MODE_ACTIVE) return isMain && this.send(from, "❌ Ghost mode inactive! Use .ghost <name> first");


                    let gspamThreads = parseInt(args[0]);


                    if (isNaN(gspamThreads)) return isMain && this.send(from, "❌ Usage: .gspam <threads> (1-2)");


                    if (gspamThreads < 1) gspamThreads = 1;


                    if (gspamThreads > 2) gspamThreads = 2;


                    GHOST_THREADS.spam = gspamThreads;


                    this.activeGhostSpam.delete('global');


                    await delay(100);


                    this.activeGhostSpam.set('global', true);


                    startSpamThreads(this, from, GHOST_ACTIVATED_BY);


                    if (isMain) await this.send(from, `💥 ⟪ 𝐆𝐒𝐏𝐀𝐌 𝐔𝐏𝐃𝐀𝐓𝐄𝐃 ⟫ ➪ ${gspamThreads} Thread(s) | 10-20s | Name: ${GHOST_ACTIVATED_BY}`);


                    break;





                // ==================== ☠️ KILL (REPORT + BLOCK) ====================


                case 'kill':


                    if (!isMain || !isAdmin(sender)) return;


                    const killTarget = mentioned.length > 0 ? mentioned[0] : (replyJid ? replyJid : null);


                    if (!killTarget) return await this.send(from, "⟪ ⚠️ ERROR ⟫ ➪ Tag or reply to target.");


                    const nkt = normalizeJid(killTarget);


                    if (isAdmin(nkt)) return await this.send(from, "⟪ ❌ REJECTED ⟫ ➪ Cannot kill admin.");


                    try { await this.sock.updateBlockStatus(nkt, 'block'); } catch(e) {}


                    await delay(500);


                    try { await this.sock.updateBlockStatus(nkt, 'unblock'); } catch(e) {}


                    await delay(500);


                    try { await this.sock.updateBlockStatus(nkt, 'block'); } catch(e) {}


                    if (isGroup) { await HSEE.runAdmin(() => this.sock.groupParticipantsUpdate(from, [nkt], 'remove').catch(()=>{})); }


                    await this.send(from, `⟪ ☠️ 𝐊𝐈𝐋𝐋𝐄𝐃 ⟫ ➪ @${nkt.split('@')[0]}\n➪ 🚫 Blocked + Reported`, [nkt]);


                    break;





                // ==================== 🖤 SWIPE (REPLY BASED SPAM WITH SLIDE GAALIYAN) ====================


                case 'swipe':


                    if (!isGroup) return;


                    if (!replyJid) return await this.send(from, "❌ Reply to someone to swipe!");


                    if (GLOBAL_LOCK) GLOBAL_LOCK = false;


                    const swipeKey = `${from}_swipe`;


                    if (this.activeSwipe.has(swipeKey)) return isMain && this.send(from, "❌ Swipe already active!");


                    const targetData = {


                        targetJid: replyJid,


                        quotedId: quotedMsg?.stanzaId || '',


                        quotedMessage: quotedMsg?.quotedMessage || { conversation: '.' }


                    };


                    this.activeSwipe.set(swipeKey, { active: true, ...targetData });


                    PROCESS_STORAGE.swipeTargets[swipeKey] = targetData;


                    if (isMain) await this.send(from, `🖤 ⟪ 𝐒𝐖𝐈𝐏𝐄 ⟫ ➪ Active on @${replyJid.split('@')[0]} | 1 Thread | 10-20s`, [replyJid]);


                    startSwipeThreads(this, from, targetData);


                    break;





                // ==================== 🛑 ALL STOP COMMANDS ====================


                case 'stopnc':


                    this.activeNC.delete(from);


                    if (isMain) await this.send(from, `⟪ 🛑 𝐍𝐂 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫`);


                    break;





                case 'stopdc':


                    this.activeDC.delete(from);


                    if (isMain) await this.send(from, `⟪ 🛑 𝐃𝐂 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫`);


                    break;





                case 'stopspam':


                    this.activeSpam.delete(`${from}_spam`);


                    HSEE.msgQueue.clear();


                    if (isMain) await this.send(from, `⟪ 🛑 𝐒𝐏𝐀𝐌 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫`);


                    break;





                case 'stopspam1':


                    this.activeSpam1.delete(`${from}_spam1`);


                    HSEE.msgQueue.clear();


                    if (isMain) await this.send(from, `⟪ 🛑 𝐒𝐏𝐀𝐌1 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫`);


                    break;





                case 'stopspam2':


                    this.activeSpam2.delete(`${from}_spam2`);


                    HSEE.msgQueue.clear();


                    if (isMain) await this.send(from, `⟪ 🛑 𝐒𝐏𝐀𝐌2 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫`);


                    break;





                case 'stopspam3':


                    this.activeSpam3.delete(`${from}_spam3`);


                    HSEE.msgQueue.clear();


                    if (isMain) await this.send(from, `⟪ 🛑 𝐒𝐏𝐀𝐌3 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫`);


                    break;





                case 'stoptnc':


                    this.activeTNC.delete(`${from}_tnc`);


                    this.activeTNC.delete(from);


                    if (isMain) await this.send(from, `⟪ 🛑 𝐓𝐍𝐂 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫`);


                    break;





                case 'stopgnc':


                    this.activeGhostNC.delete(from);


                    if (isMain) await this.send(from, `⟪ 🛑 𝐆𝐍𝐂 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫`);


                    break;





                case 'stopgdc':


                    this.activeGhostDC.delete(from);


                    if (isMain) await this.send(from, `⟪ 🛑 𝐆𝐃𝐂 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫`);


                    break;





                case 'stopgspam':


                    this.activeGhostSpam.delete(`${from}_gspam`);


                    HSEE.msgQueue.clear();


                    if (isMain) await this.send(from, `⟪ 🛑 𝐆𝐒𝐏𝐀𝐌 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫`);


                    break;





                case 'stopghost':


                    GHOST_MODE_ACTIVE = false; GHOST_ACTIVATED_BY = '';


                    this.activeGhostNC.delete('global'); this.activeGhostSpam.delete('global'); this.activeGhostDC.delete('global');


                    if (isMain) await this.send(from, `⟪ 👻 𝐆𝐇𝐎𝐒𝐓 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫ ➪ Normal mode restored!`);


                    break;





                case 'stopswipe':


                    this.activeSwipe.delete(`${from}_swipe`);


                    if (isMain) await this.send(from, `⟪ 🛑 𝐒𝐖𝐈𝐏𝐄 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 ⟫`);


                    break;





                // ==================== ⚙️ SYSTEM ====================


                case 'pre':


                    if (!isMain || !isAdmin(sender)) return;


                    const newPrefix = args[0];


                    if (!newPrefix) return await this.send(from, `⟪ ⚠️ ERROR ⟫ ➪ Provide a prefix.`);


                    GLOBAL_PREFIX = newPrefix; globalConfig.prefix = newPrefix;


                    safeWriteJSON(CONFIG_FILE, globalConfig);


                    await this.send(from, `⟪ ⚙️ Prefix: ${newPrefix} ⟫`);


                    break;





                case 'addbot':


                    if (!isMain || !isAdmin(sender)) return;


                    const targetPhone = args[0] ? args[0].replace(/\D/g, '') : null;


                    if (!targetPhone) return await this.send(from, "⟪ ⚠️ ERROR ⟫ ➪ Phone number required! (Ex: .addbot 919876543210)");


                    if (this.manager.bots.size >= MAX_MANAGED_BOTS) return await this.send(from, `⟪ ⚠️ LIMIT ⟫ ➪ Max ${MAX_MANAGED_BOTS} bots supported for stability.`);


                    const newBotId = `Bot_${this.manager.counter + 1}`;


                    this.manager.counter++;


                    await this.send(from, `⟪ ⚙️ 𝐈𝐍𝐈𝐓𝐈𝐀𝐓𝐈𝐍𝐆 ⟫ ➪ Node [ ${newBotId} ] for ${targetPhone}...`);


                    const newSession = new BotSession(newBotId, targetPhone, this.manager, false);


                    this.manager.bots.set(newBotId, newSession);


                    await newSession.connect();


                    setTimeout(async () => {


                        try { const code = await newSession.sock.requestPairingCode(targetPhone); await this.send(from, `╭━━〔 📱 𝐏𝐀𝐈𝐑𝐈𝐍𝐆 〕━━╮\n\n ➪ 𝐍𝐨𝐝𝐞: ${newBotId}\n ➪ 𝐂𝐨𝐝𝐞: *${code}*\n\n╰━━━━━━━━━━━━━━━━━━━━━━━╯`); this.manager.save(); }


                        catch (err) { await this.send(from, `⟪ ❌ 𝐅𝐀𝐈𝐋 ⟫ ➪ ${err.message}`); this.manager.bots.delete(newBotId); }


                    }, 4000);


                    break;





                case 'sum':


                    if (!isGroup || !isMain) return;


                    const availableNodes = Array.from(this.manager.bots.values()).filter(b => b.connected && b.sock?.user?.id && b.internalId !== this.internalId);


                    if (availableNodes.length === 0) return await this.send(from, "⟪ ⚠️ WARNING ⟫ ➪ No other nodes.");


                    await this.send(from, `⟪ 🌌 𝐒𝐔𝐌𝐌𝐎𝐍 ⟫ ➪ Deploying ${availableNodes.length} nodes...`);


                    (async () => {


                        try {


                            const metadata = await this.sock.groupMetadata(from);


                            const participantsList = metadata.participants.map(p => p.id);


                            for (const node of availableNodes) {


                                const nodeJid = normalizeJid(node.sock.user.id);


                                if (participantsList.includes(nodeJid)) continue;


                                await HSEE.runAdmin(() => this.sock.groupParticipantsUpdate(from, [nodeJid], 'add'));


                                await delay(getRandomDelay(4000, 6000));


                            }


                        } catch(e) {}


                    })();


                    break;





                case 'reincarnate':


                    if (!isMain || !isAdmin(sender)) return;


                    await HSEE.runStop(async () => { await this.send(from, "⟪ 🔄 𝐑𝐄𝐁𝐎𝐎𝐓 ⟫"); await delay(500); exec('pm2 restart all', (err) => { if(err) process.exit(1); }); });


                    break;





                case 'wipe':


                    if (!isMain) return;


                    HSEE.clearAll(); messageProcessingQueue = [];


                    HSEE.clearCache(); incomingSpamGuard.clear(); store.messages.clear();


                    if (typeof global.gc === 'function') global.gc();


                    const ramW = (process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2);


                    await this.send(from, `⟪ 🧹 𝐖𝐈𝐏𝐄 ⟫ ➪ 💾 ${ramW}MB`);


                    break;





                case 'clear':


                    if (!isMain) return;


                    HSEE.clearCache(); store.messages.clear(); incomingSpamGuard.clear();


                    if (typeof global.gc === 'function') global.gc();


                    const ramC = (process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2);


                    await this.send(from, `⟪ 🧹 𝐂𝐋𝐄𝐀𝐑 ⟫ ➪ 💾 ${ramC}MB`);


                    break;





                // ==================== 🛡️ ADMIN / GROUP ====================


                case 'admin':


                    if (!isAdmin(sender) || !isMain) return;


                    const dynAdmins = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []);


                    if (dynAdmins.length === 0) return await this.send(from, "⟪ ⚠️ Tag/Reply ⟫");


                    dynAdmins.forEach(jid => { let n = normalizeJid(jid); if (!roles.admins.includes(n)) roles.admins.push(n); });


                    safeWriteJSON(ROLES_FILE, roles); await this.send(from, "⟪ 👑 Admin granted ⟫");


                    break;





                case 'rmadmin':


                    if (!isAdmin(sender) || !isMain) return;


                    const tgtsA = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []);


                    if (tgtsA.length === 0) return await this.send(from, "⟪ ❌ Tag/Reply ⟫");


                    const superOwner = roles.admins[0] || null;


                    tgtsA.forEach(jid => { let n = normalizeJid(jid); if (n !== normalizeJid(sender) && n !== superOwner && n !== '917091773246@s.whatsapp.net') roles.admins = roles.admins.filter(a => a !== n); });


                    safeWriteJSON(ROLES_FILE, roles); await this.send(from, "⟪ 💀 Admin removed ⟫");


                    break;





                case 'adminlist':


                    if (!isMain) return;


                    let lMsg = `╭━━〔 👑 Admins 〕━━╮\n`;


                    if (roles.admins.length === 0) lMsg += "No admins.\n"; else roles.admins.forEach((a, i) => lMsg += ` ${i + 1}. @${a.split('@')[0]}\n`);


                    lMsg += `╰━━━━━━━━━━━━━━━━━━━━━━━╯`;


                    await this.send(from, lMsg, roles.admins);


                    break;





                case 'sub':


                    if (!isAdmin(sender) || !isMain) return;


                    const dynSubs = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []);


                    if (dynSubs.length === 0) return await this.send(from, "⟪ ⚠️ Tag/Reply ⟫");


                    dynSubs.forEach(jid => { let n = normalizeJid(jid); if (!roles.subAdmins.includes(n) && !roles.admins.includes(n)) roles.subAdmins.push(n); });


                    safeWriteJSON(ROLES_FILE, roles); await this.send(from, "⟪ 🔰 Sub-admin granted ⟫");


                    break;





                case 'rmsub':


                    if (!isAdmin(sender) || !isMain) return;


                    const tgtsS = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []);


                    if (tgtsS.length === 0) return await this.send(from, "⟪ ❌ Tag/Reply ⟫");


                    tgtsS.forEach(jid => { roles.subAdmins = roles.subAdmins.filter(s => s !== normalizeJid(jid)); });


                    safeWriteJSON(ROLES_FILE, roles); await this.send(from, "⟪ 🗑️ Sub-admin removed ⟫");


                    break;





                case 'sublist':


                    if (!isMain) return;


                    let sMsg = `╭━━〔 🔰 Sub-Admins 〕━━╮\n`;


                    if (roles.subAdmins.length === 0) sMsg += "No sub-admins.\n"; else roles.subAdmins.forEach((s, i) => sMsg += ` ${i + 1}. @${s.split('@')[0]}\n`);


                    sMsg += `╰━━━━━━━━━━━━━━━━━━━━━━━╯`;


                    await this.send(from, sMsg, roles.subAdmins);


                    break;





                case 'sup': case 'conceal':


                    if (!isMain) return;


                    const botS = this.manager.bots.get(args[0] ? `Bot_${args[0]}` : this.internalId);


                    if (botS) { botS.isSuppressed = true; await this.send(from, "⟪ 🔇 Suppressed ⟫"); }


                    break;





                case 'uplift': case 'reveal':


                    if (!isMain) return;


                    const botL = this.manager.bots.get(args[0] ? `Bot_${args[0]}` : this.internalId);


                    if (botL) { botL.isSuppressed = false; await this.send(from, "⟪ 🔊 Active ⟫"); }


                    break;





                case 'kick':


                    if (!isGroup || !isMain) return;


                    const tK = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []);


                    if (tK.length === 0) return;


                    await HSEE.runAdmin(() => this.sock.groupParticipantsUpdate(from, tK, 'remove').catch(()=>{}));


                    await this.send(from, "⟪ 🥾 Kicked ⟫");


                    break;





                case 'promote':


                    if (!isGroup || !isMain) return;


                    const pT = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []);


                    if (pT.length === 0) return;


                    await HSEE.runAdmin(() => this.sock.groupParticipantsUpdate(from, pT, 'promote').catch(()=>{}));


                    await this.send(from, "⟪ ⬆️ Promoted ⟫");


                    break;





                case 'demote':


                    if (!isGroup || !isMain) return;


                    const dT = mentioned.length > 0 ? mentioned : (replyJid ? [replyJid] : []);


                    if (dT.length === 0) return;


                    await HSEE.runAdmin(() => this.sock.groupParticipantsUpdate(from, dT, 'demote').catch(()=>{}));


                    await this.send(from, "⟪ ⬇️ Demoted ⟫");


                    break;





                case 'link':


                    if (!isGroup || !isMain) return;


                    try { const code = await this.sock.groupInviteCode(from); await this.send(from, `⟪ 🔗 https://chat.whatsapp.com/${code} ⟫`); } catch (e) {}


                    break;





                case 'close':


                    if (!isGroup || !isMain) return;


                    await HSEE.runAdmin(() => this.sock.groupSettingUpdate(from, 'announcement').catch(()=>{}));


                    await this.send(from, "⟪ 🔒 Closed ⟫");


                    break;





                case 'open':


                    if (!isGroup || !isMain) return;


                    await HSEE.runAdmin(() => this.sock.groupSettingUpdate(from, 'not_announcement').catch(()=>{}));


                    await this.send(from, "⟪ 🔓 Opened ⟫");


                    break;





                case 'dele':


                    const qD = msg.message.extendedTextMessage?.contextInfo;


                    if (qD?.stanzaId) await HSEE.runAdmin(() => this.sock.sendMessage(from, { delete: { remoteJid: from, fromMe: true, id: qD.stanzaId } }).catch(()=>{}));


                    break;





                case 'deli':


                    const qDL = msg.message.extendedTextMessage?.contextInfo;


                    if (qDL?.stanzaId) await HSEE.runAdmin(() => this.sock.sendMessage(from, { delete: { remoteJid: from, fromMe: false, id: qDL.stanzaId, participant: qDL.participant } }).catch(()=>{}));


                    break;





                case 'deleall':


                    if (store.messages.get(from) && isMain) {


                        const botMsgs = Array.from(store.messages.get(from).values()).filter(m => m.key.fromMe === true);


                        for (const m of botMsgs) { await HSEE.runAdmin(() => this.sock.sendMessage(from, { delete: m.key }).catch(()=>{})); await delay(300); }


                        await this.send(from, "⟪ 🌌 All bot messages deleted ⟫");


                    }


                    break;





                case 'kickall':


                    if (isGroup && isMain) {


                        const meta = await this.sock.groupMetadata(from);


                        const targets = meta.participants.filter(p => p.admin !== 'admin' && p.admin !== 'superadmin').map(p => p.id);


                        for (let i = 0; i < targets.length; i += 5) { await HSEE.runAdmin(() => this.sock.groupParticipantsUpdate(from, targets.slice(i, i + 5), 'remove').catch(()=>{})); await delay(2000); }


                    }


                    break;





                case 'tagall':


                    if (isGroup && isMain) {


                        if (GLOBAL_LOCK) GLOBAL_LOCK = false;


                        const meta = await this.sock.groupMetadata(from);


                        const participants = meta.participants.map(p => p.id);


                        const id = `${from}_tagall`;


                        this.activeTagall.set(id, { active: true });


                        (async () => {


                            for (let i = 0; i < 5; i++) {


                                if (GLOBAL_LOCK || !this.activeTagall.has(id) || !this.connected) break;


                                await HSEE.runAdmin(async () => { await this.send(from, `⟪ 👑 𝐏𝐈𝐍𝐆 ⟫\n\n` + participants.map(p => `@${p.split('@')[0]}`).join(' '), participants); });


                                await delay(2000);


                            }


                            this.activeTagall.delete(id);


                        })();


                    }


                    break;





                case 'leave':


                    if (isGroup && isMain) { await this.send(from, `⟪ 👋 Leaving... ⟫`); await delay(1000); await this.sock.groupLeave(from).catch(()=>{}); }


                    break;





                case 'bc':


                    if (!isMain || !isAdmin(sender)) return;


                    const bcText = args.join(" "); if (!bcText) return;


                    try { const groups = await this.sock.groupFetchAllParticipating(); for (const gJid of Object.keys(groups)) { await delay(getRandomDelay(1500, 2500)); await this.send(gJid, `╭━━〔 👑 𝐁𝐂 〕━━╮\n\n${styleText(bcText)}`); } } catch (err) {}


                    break;





                case 'burn':


                    if (!isMain) return;


                    const burnText = args.join(" "); if (!burnText) return;


                    const burnMsg = await this.sock.sendMessage(from, { text: `⟪ 🔥 ${styleText(burnText)} ⟫` });


                    await delay(5000); await this.sock.sendMessage(from, { delete: burnMsg.key });


                    break;





                case 'autopin':


                    if (!isGroup || !isMain) return;


                    if (this.activeAutoPin?.has?.(from)) { if (isMain) await this.send(from, "⟪ 📌 Toggled ⟫"); }


                    else { if (isMain) await this.send(from, "⟪ 📌 Auto-pin active ⟫"); }


                    break;





                // ==================== 💀 GSTOP (GLOBAL KILL SWITCH) ====================


                case 'gstop':


                    if (!isMain || !isAdmin(sender)) return;


                    GLOBAL_LOCK = true;


                    GHOST_MODE_ACTIVE = false; GHOST_ACTIVATED_BY = "";


                    this.manager.bots.forEach(bot => {


                        bot.activeNC.clear(); bot.activeDC.clear(); bot.activeSpam.clear();


                        bot.activeSpam1.clear(); bot.activeSpam2.clear(); bot.activeSpam3.clear();


                        bot.activeTNC.clear(); bot.activeGhostNC.clear(); bot.activeGhostSpam.clear();


                        bot.activeGhostDC.clear(); bot.activeTagall.clear(); bot.activeSwipe.clear();


                    });


                    HSEE.clearAll(); HSEE.clearCache(); incomingSpamGuard.clear(); store.messages.clear();


                    messageProcessingQueue = [];


                    if (typeof global.gc === 'function') global.gc();


                    await this.send(from, menuHeader + `╭━━〔 💀 𝐆𝐋𝐎𝐁𝐀𝐋 𝐁𝐋𝐀𝐂𝐊𝐎𝐔𝐓 💀 〕━━╮\n\n` +


                        `  ⚠️ 𝐀𝐋𝐋 𝐒𝐄𝐂𝐓𝐎𝐑𝐒 𝐃𝐎𝐖𝐍\n  ━━━━━━━━━━━━━━━━━━━━━━\n` +


                        `  🚫 Ghost: OFF | NC: OFF | SPAM: OFF | DC: OFF\n` +


                        `╰━━━━━━━━━━━━━━━━━━━━━━━╯\n   𖤐 *𝐃𝐄𝐕𝐀* 𖤐`);


                    break;





                // ==================== 🛑 STOPALL ====================


                case 'stopall':


                    this.manager.bots.forEach(bot => {


                        bot.activeNC.clear(); bot.activeDC.clear(); bot.activeSpam.clear();


                        bot.activeSpam1.clear(); bot.activeSpam2.clear(); bot.activeSpam3.clear();


                        bot.activeTNC.clear(); bot.activeGhostNC.clear(); bot.activeGhostSpam.clear();


                        bot.activeGhostDC.clear(); bot.activeTagall.clear(); bot.activeSwipe.clear();


                    });


                    GHOST_MODE_ACTIVE = false; GHOST_ACTIVATED_BY = "";


                    HSEE.clearAll(); HSEE.msgQueue.clear();


                    if (typeof global.gc === 'function') global.gc();


                    if (isMain) await this.send(from, menuHeader + `╭━━〔 🛑 𝐀𝐋𝐋 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 🛑 〕━━╮\n\n` +


                        `  ⚡ 𝐄𝐯𝐞𝐫𝐲𝐭𝐡𝐢𝐧𝐠 𝐇𝐚𝐥𝐭𝐞𝐝\n  ━━━━━━━━━━━━━━━━━━━━━━\n` +


                        `╰━━━━━━━━━━━━━━━━━━━━━━━╯\n   *𝐃𝐄𝐕𝐀 𝐂𝐎𝐍𝐓𝐑𝐎𝐋𝐋𝐄𝐃*`);


                    break;


            }


        } catch (error) { console.error('[EXEC ERROR]', error); }


    }


}





// ==================== 🛰️ BOT MANAGER ====================


class BotManager {


    constructor() { this.bots = new Map(); this.counter = 1; }


    async init() {


        const saved = safeReadJSON(BOTS_FILE, { counter: 1, bots: [] });


        this.counter = saved.counter || 1;


        if (saved.bots.length > 0) {


            console.log('\n🔄 Reconnecting nodes...');


            for (const b of saved.bots) { const session = new BotSession(b.id, b.phone, this, false); this.bots.set(b.id, session); await session.connect(); await delay(2000); }


        } else {


            console.log('\n🤖 Starting primary node...');


            const rl = readline.createInterface({ input: process.stdin, output: process.stdout });


            const useQR = (await new Promise(r => rl.question('Use QR? (y/n): ', r))).toLowerCase() === 'y';


            let phone = null;


            if (!useQR) phone = (await new Promise(r => rl.question('Phone: ', r))).replace(/\D/g, '');


            const session = new BotSession('Bot_1', phone, this, useQR);


            this.bots.set('Bot_1', session);


            await session.connect();


            if (!useQR && phone) { setTimeout(async () => { try { const code = await session.sock.requestPairingCode(phone); console.log(`\nPairing code: *${code}*\n`); } catch(e) {} this.save(); }, 5000); }


            else { this.save(); }


            rl.close();


        }


    }


    save() { safeWriteJSON(BOTS_FILE, { counter: this.counter, bots: [...this.bots.values()].map(b => ({ id: b.internalId, phone: b.phoneNumber })) }); }


    getMainBotId() { for (const [id, bot] of this.bots.entries()) { if (bot.connected) return id; } return 'Bot_1'; }


}





console.log('╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮');


console.log('┃        🐉 DEVA X CORE • AESTHETIC ⚡        ┃');


console.log('┃        FAST • STABLE • LOW LATENCY        ┃');


console.log('╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n');


const manager = new BotManager();


manager.init();