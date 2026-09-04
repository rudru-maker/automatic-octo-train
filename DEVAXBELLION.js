import makeWASocket, { 
    useMultiFileAuthState, 
    DisconnectReason, 
    fetchLatestBaileysVersion, 
    downloadContentFromMessage, 
    jidNormalizedUser, 
    delay,
    Browsers
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
let activeRecovery = safeReadJSON(RECOVERY_FILE, {});
let GLOBAL_PREFIX = globalConfig.prefix;
let IS_BOT_SLEEPING = false;
let GLOBAL_LOCK = false;

// ==================== 👑 APNA NUMBER YAHAN DALEIN 👑 ====================
const OWNER_NUMBER = '639075406956'; 
const SOLE_OWNER_JID = `${639075406956}@s.whatsapp.net`;

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

// ==================== 🎨 AESTHETICS & SYMBOLS ====================
const specialSymbols = [
    'ֺּׅ𓏽⑅','಄','ᛝ','‎ꫂ᭪݁','𓏲ּ𝄢','ೀ','.✦ ݁˖','୭ ˚. ᵎᵎ','╰┈➤','༉‧₊˚.','𓂃 ࣪˖ ִֶָ 𓈈','.𖥔 ݁ ˖','ᝰ.ᐟ','˙.꒷.𖦹˙—','𑁍ࠬܓ','ִֶָ⿻.','｡𖹹°‧','ᯓ★','𓋜','۶ৎ','°˖➴','ִ ࣪𖤐','𓂃 ࣪˖ ִֶཐི༏ཋྀ󠀮','˚˖𓍢ִ໋🦢˚','˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—','ꫂ ၴႅၴ','˚ ༘ ೀ⋆｡˚','⊱ ۫ ׅ ✧','🎧ྀི♪⋆.✮','ᥫ᭡.🍥⋆🐇་༘🌷.ೃ࿔','˚.🎀༘⋆','.𖥔 ݁ ˖ִ🛸༄˖°.','ּ⋆.˚🦋༘⋆','ִֶָ. ..𓂃 ࣪ ִֶָ🦋་༘࿐','⋆.ೃ࿔🌸*:･','༄˖°.🐞.ೃ࿔*:･','༄˖°.🍂.ೃ࿔*:･','ᥫ᭡.ִֶָ𓂃','𔒝','⚘..','⛈ ּ ֶָ֢.𓂃','.𖥔 ݁ ˖','⤿','⚚','⋆⋅☆⋅⋆','✌︎','㋡','ツ','𓇢','𓆸','૮₍ ´ ꒳ `₎ა','⋆｡𖦹°⭒˚｡⋆','౨ৎ','𖤝','♪','✶','♱','ִֶָ༉‧₊˚.','۶۟ৎ੭','﹕﹒➤','☁︎','𓊆ྀི❤︎𓊇ྀི','⋆.˚🦋༘⋆','*ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚','⟡','✮','♥︎','‹𝟹','❦','𓏲 ๋࣭ ࣪ ˖🎐','<𝟑','.ᐟ','⊹ ࣪ ˖ ໒꒱','⋆⭒˚.⋆','⋆｡‧˚ʚ ୨ৎ ɞ˚‧｡⋆','ּ ֶָ֢.','༄.','°','𓃦', '࿇', '*ੈ✩‧₊˚', '.⋅˚₊‧', '🜲', '‧₊˚', '⋅', '⚡︎', '⋆.˚', '🎧ྀི♪⋆.✮', '↟𖠰˚☀︎ᨒ↟𖠰', 'ᯓ.ᐟ.', '⋆˙⟡', '𓆩♡𓆪', '࣪', 'ִֶָ☾.', 'ɪ᪻ͥᷱ᷍', '☯', '̼͙̈́͆̈́ͯ̒̆̀̓ͧ͠.', '𖤐', '𓂃', 'ོ✝︎𓂃', '❅', '☾⋆', '☾', '𖤓', '✳', '⤹', '☣︎', '᪥', '⋆˚꩜｡', '▬ι═ﺤ', '♡', '᪲᪲᪲', '˚˖𓍢ִ໋🦢˚', '⋆.˚✮🎧✮˚.⋆', 'ᯓ', '✈︎.', 'ꨄ︎', '✧˚', '༘', '⋆｡♡˚', 'ᡣ𐭩ྀིྀིྀི', '🖤⃝🦋𓍯𓂃𓏧♡', '💕⃝🕊️', '∞', 'ֶָ֢', '𓍼', '*ੈ♡⸝⸝🪐༘⋆', '𑁤', '𓎖', '⋆.˚🦋༘⋆🤍ྀི♥️', 'ྀི', '𓍯𓂃𓏧♡', '❦.', '♡', '᪲᪲᪲', '༘⋆', '༗🪈', '‎ꫂ᭪݁‎', 'ꫂ❁', '⪼', ';༊', '🌬𓂸', '𖣠', '⋆꙳•̩̩͙❅*̩̩͙‧͙.', '‧͙*̩̩͙❆', '͙͛', '˚₊⋆', '𓆩🖤𓆪', 'ִ', '࣪𖤐', '˚⊱🪷⊰˚', '♥︎࣪', 'ִֶָ☾.', '˚.🎀༘⋆', '❦➤', '𓏲', '๋࣭ ', '࣪', '˖゛', '⸝⸝.ᐟ⋆'
];

const globalEmojiList = ['🔥','💥','⚡','🌪️','🌈','☄️','💫','🌊','❄️','🌸','💀','☠️','👺','🔱','⚜️','🌟','✨','💢','💤','💨','💦','🌀','🌙'];

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

// ==================== 🔄 0ms INSTANT THREADS ====================
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
            browser: Browsers.macOS('Desktop'),
            syncFullHistory: false,
            generateHighQualityLinkPreviews: false,
            connectTimeoutMs: 60000,
            defaultQueryTimeoutMs: 60000,
            keepAliveIntervalMs: 25000,
            emitOwnEvents: false,
            markOnlineOnConnect: true,
            getMessage: async () => ({ conversation: `*⚡ DEVA X GRAND MARSHAL BELLION ⚡*` })
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
            if (qr && this.useQR) console.log(`\n📱 [${this.displayId}] SCAN QR CODE TO PAIR\n`);
            
            if (connection === 'close') {
                this.connected = false;
                const statusCode = (lastDisconnect?.error instanceof Boom) ? lastDisconnect.error.output.statusCode : 500;
                
                if (statusCode === DisconnectReason.loggedOut || statusCode === 401) {
                    console.log(`[${this.displayId}] ⚠️ Session invalid/logged out. Purging: ${this.authPath}`);
                    if (fs.existsSync(this.authPath)) fs.rmSync(this.authPath, { recursive: true, force: true });
                    this.manager.bots.delete(this.internalId);
                    this.manager.save();
                } else {
                    console.log(`[${this.displayId}] Connection dropped (Status: ${statusCode}). Reconnecting...`);
                    setTimeout(() => this.connect(), 3000);
                }
            } else if (connection === 'open') { 
                this.connected = true; 
                console.log(`\n✅ [${this.displayId}] LINKED SUCCESSFULLY & READY!\n`); 
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
                          `✦ 𝐒𝐓𝐀𝐓 : Verified via [.deva]`,
                    mentions: [normSender]
                });
                return;
            }

            if (!rawText.startsWith(GLOBAL_PREFIX)) return;
            if (this.internalId !== this.manager.getMainBotId()) return;

            const cmd = rawText.slice(GLOBAL_PREFIX.length).trim().split(' ')[0].toLowerCase();
            const priorityStops = ['stopdc','stopspam','stoptnc','stopall','gstop','stopnc','stoptxt','stopswipe','stoptarget'];
            const isPriority = priorityStops.includes(cmd);

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

        if (IS_BOT_SLEEPING && command !== 'on') return;

        await this.executeInternal(from, command, sender, msg, args, quotedMsg, replyJid, mentioned, isGroup, true);
        this.manager.bots.forEach(b => {
            if (b.internalId !== this.internalId && b.connected && !b.isSuppressed) {
                setImmediate(() => b.executeInternal(from, command, sender, msg, args, quotedMsg, replyJid, mentioned, isGroup, false).catch(() => {}));
            }
        });
    }

    // =========================================================================
    // ⚙️ COMMAND PANEL & HYBRID AESTHETIC MENU DISPLAY
    // =========================================================================
    async executeInternal(from, command, sender, msg, args, quotedMsg, replyJid, mentioned, isGroup, isMain) {
        try {
            const BRAND_TAG = `𓆩⚡𓆪 ꨄ𝐃⃝ᴇᴠᴀ.་༘࿐ ᯓ 𝐆⃝ʀᴀɴᴅ 𝐌⃝ᴀʀsʜᴀʟ 𝐁⃝ᴇʟʟɪᴏɴ ⋆ཋྀ🪽`;
            const RUNIC_BORDER = `══════════════════════════════════════`;
            const currentOwnerJid = roles.owner ? normalizeJid(roles.owner) : SOLE_OWNER_JID;

            switch (command) {
                // ==================== ⚡ ACCURATE LATENCY ====================
                case 'ping':
                    if (!isMain) return;
                    const loopStart = process.hrtime.bigint();
                    await new Promise(resolve => setImmediate(resolve));
                    const loopEnd = process.hrtime.bigint();
                    const hostLagMs = Number(loopEnd - loopStart) / 1e6;

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

                // ==================== 🛰️ ADD CHILD BOT ====================
                case 'addbot':
                    if (!isMain || !hasPerm(sender)) return;
                    const targetPhone = args[0] ? args[0].replace(/\D/g, '') : null;
                    if (!targetPhone) return await this.send(from, "⟪ ⚠️ ERROR ⟫ ➪ Phone number required! (Ex: .addbot 919876543210)");
                    
                    const newBotId = `Bot_${this.manager.counter + 1}`;
                    this.manager.counter++;
                    await this.send(from, `⟪ ⚙️ INITIATING ⟫ ➪ Node [ ${newBotId} ] for +${targetPhone}...`);
                    
                    const newSession = new BotSession(newBotId, targetPhone, this.manager, false);
                    this.manager.bots.set(newBotId, newSession);
                    await newSession.connect();
                    
                    let attempts = 0;
                    const checkInterval = setInterval(async () => {
                        attempts++;
                        try {
                            if (newSession.sock && !newSession.sock.authState.creds.registered) {
                                clearInterval(checkInterval);
                                const code = await newSession.sock.requestPairingCode(targetPhone);
                                await this.send(from, 
`╔══════════════════════════════╗
  ⟪ 🛰️ NODE DEPLOYED ⟫
╚══════════════════════════════╝
┃ 🆔 Node : ${newBotId}
┃ 📱 Num  : +${targetPhone}
┃ 🔑 Code : *${code}*
╚══════════════════════════════╝`);
                                this.manager.save();
                            }
                        } catch (err) {
                            if (attempts >= 10) {
                                clearInterval(checkInterval);
                                await this.send(from, `⟪ ❌ FAIL ⟫ ➪ Pairing failed: ${err.message}`);
                                this.manager.bots.delete(newBotId);
                            }
                        }
                    }, 2000);
                    break;

                case 'on':
                    if (!isMain || !isOwner(sender)) return;
                    IS_BOT_SLEEPING = false;
                    await this.send(from, `🟢 Systems Online. Full Arsenal Engaged.`);
                    break;

                case 'off':
                    if (!isMain || !isOwner(sender)) return;
                    IS_BOT_SLEEPING = true;
                    await this.send(from, `⟪ 💤 𝐒𝐇𝐀𝐃𝐎𝐖 𝐒𝐔𝐒𝐏𝐄𝐍𝐒𝐈𝐎𝐍 ⟫\n➪ All systems placed in stasis.`);
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
                    await this.send(from, `🧹 Void Purge Complete. Memory Cleared.`);
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
                        const caption = `🎵 *${video.title}*\n👤 Author: ${video.author.name}\n⏱️ Duration: ${video.timestamp}`;
                        
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

                // ==================== 🌀 0ms NC / DC / SPAM ====================
                case 'nc':
                    if (!isGroup) return;
                    GLOBAL_LOCK = false;
                    const ncName = args.join(" ") || "𝐃𝐄𝐕𝐀 𝐗 𝐆𝐑𝐀𝐍𝐃 𝐌𝐀𝐑𝐒𝐇𝐀𝐋 𝐁𝐄𝐋𝐋𝐈𝐎𝐍";
                    this.activeNC.set(from, true);
                    saveState(from, 'nc', args);
                    if (isMain) await this.send(from, `⚡ ⟪ 𝟎𝐦𝐬 𝐍𝐂 𝐒𝐓𝐎𝐑𝐌 ⟫ ➪ Engaged: [ ${ncName} ]`);
                    startNCThreads(this, from, ncName);
                    break;

                case 'dc':
                    if (!isGroup) return;
                    GLOBAL_LOCK = false;
                    const dcDesc = args.join(" ") || "Grand Marshal Bellion V23 Active";
                    this.activeDC.set(from, true);
                    saveState(from, 'dc', args);
                    if (isMain) await this.send(from, `📝 ⟪ 𝟎𝐦𝐬 𝐃𝐂 ⟫ ➪ Description Updated!`);
                    startDCThreads(this, from, dcDesc);
                    break;

                // ==================== 🛑 STOPS ====================
                case 'stopnc': this.activeNC.delete(from); removeState(from, 'nc'); await this.send(from, `⟪ 🔌 𝐍𝐂 𝐇𝐀𝐋𝐓𝐄𝐃 ⟫`); break;
                case 'stopdc': this.activeDC.delete(from); removeState(from, 'dc'); await this.send(from, `⟪ 🔌 𝐃𝐂 𝐇𝐀𝐋𝐓𝐄𝐃 ⟫`); break;

                case 'stopall':
                    GLOBAL_LOCK = true;
                    this.manager.bots.forEach(b => {
                        b.activeNC.clear(); b.activeDC.clear(); b.activeSpam.clear(); b.activeSwipe.clear(); b.activeSlide.clear(); b.activeTxt.clear(); b.activeTarget.clear();
                    });
                    HSEE.clearAll();
                    activeRecovery = {};
                    safeWriteJSON(RECOVERY_FILE, {});
                    if (isMain) await this.send(from, `💀 ALL OPERATIONS HALTED.`);
                    break;

                // ==================== 📜 MENU ====================
                case 'menu':
                case 'fmenu':
                    if (!isMain) return;
                    const menuHeader = 
`╔${RUNIC_BORDER}╗
   𓆩⚡𓆪  𝐃 𝐄 𝐕 𝐀   𝐗   𝐁 𝐄 𝐋 𝐋 𝐈 𝐎 𝐍  𓆩⚡𓆪
╠${RUNIC_BORDER}╣
  ✦ 👑 𝐒ᴏʟᴇ 𝐎ᴠᴇʀʟᴏʀᴅ : @${currentOwnerJid.split('@')[0]}
  ✦ ⚔️ 𝐌ᴀʀsʜᴀʟ      : GRAND MARSHAL BELLION V23
  ✦ ⚡ 𝐄ɴɢɪɴᴇ       : 0ms HYPER-SPEED
╚${RUNIC_BORDER}╝\n`;

                    const body = 
`┌───〔 COMMAND LIST 〕───┐
  🗡️ ${GLOBAL_PREFIX}ping       : Network & Host Latency
  🗡️ ${GLOBAL_PREFIX}status     : System Diagnostics
  🗡️ ${GLOBAL_PREFIX}addbot <num>: Pair Additional Node
  🗡️ ${GLOBAL_PREFIX}nc <name>  : 0ms Fast Name Changer
  🗡️ ${GLOBAL_PREFIX}dc <desc>  : Bio Hijack
  🗡️ ${GLOBAL_PREFIX}song <txt> : Audio Extractor
  🗡️ ${GLOBAL_PREFIX}clear      : Flush Memory
  🗡️ ${GLOBAL_PREFIX}stopall    : Emergency Stop
└──────────────────────────┘`;
                    await this.send(from, menuHeader + body + `\n> ${BRAND_TAG}`, [currentOwnerJid]);
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
            console.log('\n🔄 Restoring saved nodes...');
            for (const b of saved.bots) {
                const session = new BotSession(b.id, b.phone, this, false);
                this.bots.set(b.id, session);
                await session.connect();
                await delay(2000);
            }
        } else {
            console.log('\n🤖 Initializing Primary Node Connection...');
            const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
            const useQR = (await new Promise(r => rl.question('Use QR Code scanning? (y/n): ', r))).toLowerCase() === 'y';
            let phone = null;
            if (!useQR) phone = (await new Promise(r => rl.question('Phone Number (with Country Code, no +): ', r))).replace(/\D/g, '');
            rl.close();

            const session = new BotSession('Bot_1', phone, this, useQR);
            this.bots.set('Bot_1', session);
            await session.connect();

            if (!useQR && phone) {
                let checkAttempts = 0;
                const pairInterval = setInterval(async () => {
                    checkAttempts++;
                    try {
                        if (session.sock && !session.sock.authState.creds.registered) {
                            clearInterval(pairInterval);
                            await delay(3000);
                            const code = await session.sock.requestPairingCode(phone);
                            console.log(`\n================================`);
                            console.log(`🔑 YOUR PAIRING CODE: \x1b[32m${code}\x1b[0m`);
                            console.log(`================================\n`);
                            this.save();
                        }
                    } catch (e) {
                        if (checkAttempts >= 10) {
                            clearInterval(pairInterval);
                            console.error('❌ Failed to request pairing code:', e.message);
                        }
                    }
                }, 1500);
            } else {
                this.save();
            }
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
console.log('┃  🐉 DEVA X GRAND MARSHAL BELLION (NO TEMPLATES)   ┃');
console.log('┃  Stable macOS Handshake • Dynamic Node Manager    ┃');
console.log('╚═══════════════════════════════════════════════════╝\n');

const manager = new BotManager();
manager.init();
