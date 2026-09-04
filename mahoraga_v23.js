import {
    makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    delay,
    jidNormalizedUser
} from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import pino from 'pino';
import os from 'os';
import yts from 'yt-search';
import PQueue from 'p-queue';
import axios from 'axios';

// ==========================================
// ⚙️ CONFIGURATION & GLOBALS
// ==========================================
const PREFIX = '.';

const activeTasks = {
    nc: new Map(),
    dc: new Map(),
    spam: new Map(),
    attack: new Map(),
    slide: new Map(),
    swipe: new Map()
};

const taskQueues = {
    nc: new PQueue({ concurrency: 2 }),
    spam: new PQueue({ concurrency: 3 }),
    dc: new PQueue({ concurrency: 1 })
};

const EMOJIS = ['💀', '🔥', '👑', '⚡', '🐉', '🌪️', '🖤', '☠️', '🩸', '🪐', '💫', '🦅', '🕸️'];

// SEX TEXT BY Deva)
const SPAM_TEXTS = ["LUND LE", "CHUDAI KHAA", "kaise ho", "TMKC RYNDYKE", "DEVA is here 💀", "System Hacked 🔥"];
const TXT_MESSAGES = [
    " ᴅᴇᴋʜ Deva ᴋɪ ᴘᴏᴡᴇʀ 💪",
    " ᴀʙʙᴇ ɴᴀʟʟᴇ sᴜᴅʜᴀʀ ᴊᴀ 🤬",
    " ᴛᴇʀᴀ ᴋʜᴀɴᴅᴀᴀɴ ᴄʜᴜᴅ ɢʏᴀ 💀",
    " ᴛᴇʀᴇ Deva ᴘᴀᴘᴀ ᴀᴀʏᴇ ʜ 🦁",
    " ʙʜᴀᴀɢ ʙʜᴏsᴅɪᴋᴇ ʙʜᴀᴀɢ 🏃",
    " ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏsᴅᴀ 😹",
    " ɢᴀᴀɴᴅ ғᴀᴛᴛ ɢʏɪ? 🥺",
    " ᴋᴀ sʏsᴛᴇᴍ ʜᴀɴɢ ʙʏ Deva 💻",
    " ᴛᴇʀᴀ ʙᴀᴀᴘ ᴀᴀʏᴀ 🤬",
    " ᴍᴀᴀ ᴄʜᴜᴅᴀ ʟᴏᴅᴇ 🍑",
    " ʀᴀɴᴅɪ ʀᴏɴᴀ ᴍᴀᴛ ᴋᴀʀ 😭",
    " ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴘᴀɪʀ 🦶",
    " Deva ᴏɴ ᴛᴏᴘ 🔝",
    " ᴄʜᴀʟ ɴɪᴋᴀʟ ʟᴏᴅᴇ 🚪",
    " ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴀᴘᴇ 🔞"
];

// Admin System Setup
const rolesFile = './roles_Deva.json';
let roles = { owner: null, admins: [], subAdmins: [] };
if (fs.existsSync(rolesFile)) {
    roles = JSON.parse(fs.readFileSync(rolesFile, 'utf8'));
}
const saveRoles = () => fs.writeFileSync(rolesFile, JSON.stringify(roles, null, 2));

// ==========================================
// 🛡️ ANTI-CRASH & MEMORY OPTIMIZATION
// ==========================================
process.on('uncaughtException', (err) => console.error('[ANTI-CRASH]', err.message));
process.on('unhandledRejection', (err) => console.error('[ANTI-CRASH]', err?.message));

// Auto Garbage Collection (Clears unused RAM every 60 seconds)
setInterval(() => {
    if (typeof global.gc === 'function') {
        global.gc();
    }
}, 60000);

function formatUptime(uptime) {
    let seconds = Math.floor(uptime % 60);
    let minutes = Math.floor((uptime / 60) % 60);
    let hours = Math.floor((uptime / (60 * 60)) % 24);
    let days = Math.floor(uptime / (60 * 60 * 24));
    return `${days}d ${hours}h ${minutes}m ${seconds}s`;
}

// ==========================================
// 📱 WHATSAPP ENGINE (Deva V23)
// ==========================================
class DevaEngine {
    constructor() {
        this.sock = null;
        this.botNumber = '';
        this.connected = false;
        this.startTime = Date.now();
    }

    async connect(sessionName = 'session_Deva') {
        const { state, saveCreds } = await useMultiFileAuthState(`./${sessionName}`);
        
        this.sock = makeWASocket({
            auth: state,
            printQRInTerminal: true,
            logger: pino({ level: 'silent' }),
            browser: ['Deva Ultra', 'Chrome', '23.0.0'],
            syncFullHistory: false, // RAM Optimization: Stops massive history loading
            generateHighQualityLinkPreviews: false, // Saves RAM/CPU
            retryRequestDelayMs: 10,
            keepAliveIntervalMs: 30000,
            getMessage: async () => { return { conversation: 'Deva' }; } // Prevents store crash
        });

        this.sock.ev.on('creds.update', saveCreds);

        this.sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            
            if (qr) console.log('SCAN QR CODE TO LINK WHATSAPP');

            if (connection === 'close') {
                this.connected = false;
                
                // FLUSH MEMORY ON DISCONNECT (Prevents RAM Leak)
                taskQueues.nc.clear();
                taskQueues.spam.clear();
                taskQueues.dc.clear();
                activeTasks.nc.clear();
                activeTasks.dc.clear();
                activeTasks.spam.clear();
                activeTasks.attack.clear();
                activeTasks.slide.clear();
                activeTasks.swipe.clear();
                if (typeof global.gc === 'function') global.gc();
                
                const reason = new Boom(lastDisconnect?.error)?.output?.statusCode;
                if (reason !== DisconnectReason.loggedOut) {
                    console.log('Connection closed, reconnecting...');
                    setTimeout(() => this.connect(sessionName), 3000);
                } else {
                    console.log('Logged out. Please delete session folder and restart.');
                }
            } else if (connection === 'open') {
                this.connected = true;
                this.botNumber = jidNormalizedUser(this.sock.user.id);
                console.log(`✅ Deva V23 Connected: ${this.botNumber}`);
            }
        });

        this.sock.ev.on('messages.upsert', async (m) => {
            if (m.type !== 'notify') return;
            const msg = m.messages[0];
            if (!msg.message) return;

            const from = msg.key.remoteJid;
            const sender = msg.key.participant || msg.key.remoteJid;
            const isGroup = from.endsWith('@g.us');
            const isFromMe = msg.key.fromMe;

            let text = msg.message.conversation || 
                       msg.message.extendedTextMessage?.text || 
                       msg.message.imageMessage?.caption || '';
            
            // ===== SLIDE INTERCEPTOR =====
            if (isGroup && !isFromMe) {
                const slideKey = `${from}_slide`;
                if (activeTasks.slide.has(slideKey)) {
                    const slideData = activeTasks.slide.get(slideKey);
                    if (slideData.target === sender) {
                        const replyTxt = SPAM_TEXTS[Math.floor(Math.random() * SPAM_TEXTS.length)];
                        await this.sock.sendMessage(from, { text: `🌪️ ${replyTxt}` }, { quoted: msg });
                    }
                }
            }

            if (!text.startsWith(PREFIX)) return;

            const args = text.slice(PREFIX.length).trim().split(/ +/);
            const command = args.shift().toLowerCase();
            const query = args.join(' ');
            
            const quotedMsg = msg.message.extendedTextMessage?.contextInfo;
            const replyJid = quotedMsg?.participant;
            const mentioned = quotedMsg?.mentionedJid || [];

            await this.handleCommand(command, query, args, from, sender, isGroup, msg, replyJid, mentioned);
        });
    }

    // ==========================================
    // ⚙️ COMMAND HANDLER
    // ==========================================
    async handleCommand(cmd, query, args, from, sender, isGroup, msg, replyJid, mentioned) {
        
        // 🔐 ROLE AUTHORIZATION
        const isOwner = sender === roles.owner;
        const isAdmin = isOwner || roles.admins.includes(sender);
        const isSubAdmin = isAdmin || roles.subAdmins.includes(sender);
        const isAuthorized = isSubAdmin || msg.key.fromMe;

        // 🛡️ ADMIN MANAGEMENT COMMANDS
        if (cmd === 'admin') {
            if (!roles.owner) {
                roles.owner = sender;
                if (!roles.admins.includes(sender)) roles.admins.push(sender);
                saveRoles();
                return this.reply(from, '👑 You have claimed OWNER status for Deva V23!', msg);
            }
            if (isOwner) {
                const target = replyJid || (mentioned.length > 0 ? mentioned[0] : null);
                if (!target) return this.reply(from, '❌ Tag or reply to a user to make them ADMIN.', msg);
                if (!roles.admins.includes(target)) roles.admins.push(target);
                saveRoles();
                return this.reply(from, `✅ @${target.split('@')[0]} is now an ADMIN!`, msg, [target]);
            }
        }

        if (cmd === 'rmadmin') {
            if (!isOwner) return this.reply(from, '❌ Only Owner can remove Admins.', msg);
            const target = replyJid || (mentioned.length > 0 ? mentioned[0] : null);
            if (!target) return this.reply(from, '❌ Tag or reply to a user.', msg);
            roles.admins = roles.admins.filter(a => a !== target);
            saveRoles();
            return this.reply(from, `🗑️ @${target.split('@')[0]} has been removed from ADMINS.`, msg, [target]);
        }

        if (cmd === 'sub') {
            if (!isAdmin) return this.reply(from, '❌ Only Admins can add Sub-Admins.', msg);
            const target = replyJid || (mentioned.length > 0 ? mentioned[0] : null);
            if (!target) return this.reply(from, '❌ Tag or reply to a user.', msg);
            if (!roles.subAdmins.includes(target)) roles.subAdmins.push(target);
            saveRoles();
            return this.reply(from, `✅ @${target.split('@')[0]} is now a SUB-ADMIN!`, msg, [target]);
        }

        if (cmd === 'rmsub') {
            if (!isAdmin) return this.reply(from, '❌ Only Admins can remove Sub-Admins.', msg);
            const target = replyJid || (mentioned.length > 0 ? mentioned[0] : null);
            if (!target) return this.reply(from, '❌ Tag or reply to a user.', msg);
            roles.subAdmins = roles.subAdmins.filter(a => a !== target);
            saveRoles();
            return this.reply(from, `🗑️ @${target.split('@')[0]} has been removed from SUB-ADMINS.`, msg, [target]);
        }

        // 🛑 Un-authorized block for restricted commands
        const restrictedCommands = ['nc', 'stopnc', 'n1', 'n10', 'n100', 'dc', 'stopdc', 'spam', 'txt', 'dtx', 'stopspam', 'stoptxt', 'stopdtx', 'attack', 'stopattack', 'slide', 'stopslide', 'swipe', 'stopswipe', 'promote', 'demote', 'kick', 'tagall', 'hidetag', 'link', 'revoke'];
        if (restrictedCommands.some(rc => cmd.startsWith(rc)) && !isAuthorized) {
            // Do not reply to unauthorized users to prevent spam
            return;
        }

        // 🛡️ SYSTEM & INFO COMMANDS
        if (cmd === 'ping') {
            const start = Date.now();
            await this.reply(from, '🏓 Pinging...', msg);
            const latency = Date.now() - start;
            this.reply(from, `*『 🏓 𝐏𝐎𝐍𝐆 』*\n⚡ Latency: ${latency}ms\n𓆩⚡𓆪 𝐌ᴀʜᴏʀᴀɢᴀ 𝐕𝟐𝟑`, msg);
            return;
        }

        if (cmd === 'status') {
            const ramUsage = (process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2);
            const totalRam = (os.totalmem() / 1024 / 1024 / 1024).toFixed(2);
            const uptime = formatUptime((Date.now() - this.startTime) / 1000);
            
            const stats = `*『⊰ ˚𓍼 ꨄ𝐌⃝ᴀʜᴏʀᴀɢᴀ ᯓ 𝐔⃝ʟᴛʀᴀ 🪽』*\n\n` +
                          `⏱️ *Uptime:* ${uptime}\n` +
                          `💾 *RAM:* ${ramUsage} MB / ${totalRam} GB\n` +
                          `⚡ *Active NCs:* ${activeTasks.nc.size}\n` +
                          `🚀 *Active Spams:* ${activeTasks.spam.size}\n` +
                          `🎯 *Active Slides:* ${activeTasks.slide.size}\n` +
                          `🌪️ *Active Swipes:* ${activeTasks.swipe.size}\n\n` +
                          `*𓆩⚡𓆪 𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ 𝐌ᴀʜᴏʀᴀɢᴀ 𝐕𝟐𝟑*`;
            this.reply(from, stats, msg);
            return;
        }

        if (cmd === 'clear') {
            taskQueues.nc.clear();
            taskQueues.spam.clear();
            taskQueues.dc.clear();
            activeTasks.nc.clear();
            activeTasks.dc.clear();
            activeTasks.spam.clear();
            activeTasks.attack.clear();
            activeTasks.slide.clear();
            activeTasks.swipe.clear();
            if (typeof global.gc === 'function') global.gc();
            this.reply(from, `✅ *SYSTEM CLEARED*\nAll loops, arrays, and queues have been flushed. Memory is optimized.`, msg);
            return;
        }

        if (cmd === 'arise') {
            this.reply(from, `*『 👑 𝐌𝐀𝐇𝐎𝐑𝐀𝐆𝐀 𝐇𝐀𝐒 𝐀𝐖𝐀𝐊𝐄𝐍𝐄𝐃 👑 』*\n\nTremble before the ultimate engine. All systems online and ready to strike. ⚡`, msg);
            return;
        }

        // 👑 GROUP ADMIN COMMANDS
        if (['promote', 'demote', 'kick'].includes(cmd)) {
            if (!isGroup) return this.reply(from, '❌ Only for groups!', msg);
            const target = replyJid || (mentioned.length > 0 ? mentioned[0] : null);
            if (!target) return this.reply(from, '❌ Tag or reply to someone.', msg);
            
            const action = cmd === 'kick' ? 'remove' : cmd;
            try {
                await this.sock.groupParticipantsUpdate(from, [target], action);
                this.reply(from, `✅ Action *${cmd}* executed on @${target.split('@')[0]}`, msg, [target]);
            } catch (e) {
                this.reply(from, '❌ Failed! Am I admin?', msg);
            }
            return;
        }

        if (cmd === 'link') {
            if (!isGroup) return;
            try {
                const code = await this.sock.groupInviteCode(from);
                this.reply(from, `🔗 *Group Link:*\nhttps://chat.whatsapp.com/${code}`, msg);
            } catch (e) {
                this.reply(from, '❌ Failed. Make me admin first.', msg);
            }
            return;
        }

        if (cmd === 'revoke') {
            if (!isGroup) return;
            try {
                await this.sock.groupRevokeInvite(from);
                this.reply(from, '✅ Group link revoked and updated!', msg);
            } catch (e) {
                this.reply(from, '❌ Failed. Make me admin first.', msg);
            }
            return;
        }

        if (cmd === 'tagall' || cmd === 'hidetag') {
            if (!isGroup) return;
            try {
                const groupMeta = await this.sock.groupMetadata(from);
                const participants = groupMeta.participants.map(p => p.id);
                let text = query || (cmd === 'tagall' ? '📢 *ATTENTION EVERYONE!*' : '📢');
                
                if (cmd === 'tagall') {
                    text += `\n\n` + participants.map(p => `👉 @${p.split('@')[0]}`).join('\n');
                }
                
                await this.sock.sendMessage(from, { text, mentions: participants });
            } catch (e) {
                this.reply(from, '❌ Failed to fetch members.', msg);
            }
            return;
        }

        // 🎯 TARGET COMMANDS (SLIDE / SWIPE)
        if (cmd === 'slide') {
            if (!isGroup) return;
            if (!replyJid) return this.reply(from, '❌ Reply to someone to slide!', msg);
            
            const slideKey = `${from}_slide`;
            activeTasks.slide.set(slideKey, { target: replyJid });
            this.reply(from, `⟪ 🌪️ 𝐒𝐔𝐏𝐄𝐑 𝐒𝐋𝐈𝐃𝐄 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃 ⟫\n🎯 Target: @${replyJid.split('@')[0]}\n(Will reply to every msg they send)`, msg, [replyJid]);
            return;
        }

        if (cmd === 'stopslide') {
            activeTasks.slide.delete(`${from}_slide`);
            this.reply(from, '🛑 Slide Stopped.', msg);
            return;
        }

        if (cmd === 'swipe') {
            if (!isGroup) return;
            if (!replyJid) return this.reply(from, '❌ Reply to someone to swipe!', msg);
            
            const swipeKey = `${from}_swipe`;
            if (activeTasks.swipe.has(swipeKey)) return this.reply(from, 'Swipe already running!', msg);
            
            activeTasks.swipe.set(swipeKey, true);
            this.reply(from, `⟪ 🖤 𝐒𝐔𝐏𝐄𝐑 𝐒𝐖𝐈𝐏𝐄 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃 ⟫\n🎯 Target: @${replyJid.split('@')[0]}\n🛑 Stop: ${PREFIX}stopswipe`, msg, [replyJid]);

            (async () => {
                while (activeTasks.swipe.has(swipeKey) && this.connected) {
                    const txt = SPAM_TEXTS[Math.floor(Math.random() * SPAM_TEXTS.length)];
                    await taskQueues.spam.add(async () => {
                        try {
                            await this.sock.sendMessage(from, { text: `@${replyJid.split('@')[0]} ${txt}`, mentions: [replyJid] });
                        } catch (e) {}
                    });
                    await delay(Math.floor(Math.random() * (2500 - 1000 + 1)) + 1000); // 1s to 2.5s delay
                }
            })();
            return;
        }

        if (cmd === 'stopswipe') {
            activeTasks.swipe.delete(`${from}_swipe`);
            this.reply(from, '🛑 Swipe Stopped.', msg);
            return;
        }

        // 🌀 NORMAL NAME CHANGER (NC & n1-n100)
        if (cmd === 'nc' || /^n([1-9]|[1-9][0-9]|100)$/.test(cmd)) {
            if (!isGroup) return;
            const ncKey = `${from}_nc`;
            if (activeTasks.nc.has(ncKey)) return this.reply(from, 'NC is already running!', msg);
            
            const name = query || '𝐌𝐀𝐇𝐎𝐑𝐀𝐆𝐀 𝐕𝟐𝟑';
            activeTasks.nc.set(ncKey, true);
            this.reply(from, `⟪ 🌀 𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃 ⟫\n🎯 Target: ${name}\n⚡ Speed: Slow/Safe\n🛑 Stop: ${PREFIX}stopnc`, msg);

            (async () => {
                while (activeTasks.nc.has(ncKey) && this.connected) {
                    const e1 = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
                    const e2 = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
                    const e3 = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
                    const e4 = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
                    const subject = `${e1}${e2} ${name} ${e3}${e4}`;
                    
                    await taskQueues.nc.add(async () => {
                        try { await this.sock.groupUpdateSubject(from, subject); } catch (e) {}
                    });
                    await delay(Math.floor(Math.random() * 1500) + 3500);
                }
            })();
            return;
        }

        if (cmd === 'stopnc') {
            activeTasks.nc.delete(`${from}_nc`);
            this.reply(from, '🛑 NC Stopped.', msg);
            return;
        }

        // 📝 DESCRIPTION CHANGER (DC)
        if (cmd === 'dc') {
            if (!isGroup) return;
            const dcKey = `${from}_dc`;
            if (activeTasks.dc.has(dcKey)) return this.reply(from, 'DC is already running!', msg);
            
            const desc = query || 'Hacked by Deva V23';
            activeTasks.dc.set(dcKey, true);
            this.reply(from, `⟪ 📝 𝐃𝐂 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃 ⟫\n🛑 Stop: ${PREFIX}stopdc`, msg);

            (async () => {
                while (activeTasks.dc.has(dcKey) && this.connected) {
                    const e1 = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
                    const description = `${e1} ${desc} ${e1}\n\n𓆩⚡𓆪 𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ 𝐌ᴀʜᴏʀᴀɢᴀ 𝐕𝟐𝟑 𓆩🪽𓆪`;
                    
                    await taskQueues.dc.add(async () => {
                        try { await this.sock.groupUpdateDescription(from, description); } catch (e) {}
                    });
                    await delay(4500);
                }
            })();
            return;
        }

        if (cmd === 'stopdc') {
            activeTasks.dc.delete(`${from}_dc`);
            this.reply(from, '🛑 DC Stopped.', msg);
            return;
        }

        // 🚀 SPAM COMMANDS (spam, txt, dtx)
        if (cmd === 'spam' || cmd === 'txt' || cmd === 'dtx') {
            const spamKey = `${from}_spam`;
            if (activeTasks.spam.has(spamKey)) return this.reply(from, 'Spam is already running!', msg);
            
            const hasQuery = query.length > 0;
            activeTasks.spam.set(spamKey, true);
            this.reply(from, `⟪ 🚀 𝐒𝐏𝐀𝐌 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃 ⟫\n🛑 Stop: ${PREFIX}stopspam`, msg);

            (async () => {
                let msgIndex = 0;
                while (activeTasks.spam.has(spamKey) && this.connected) {
                    const e1 = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
                    let spamMsg = '';
                    if (hasQuery) {
                        spamMsg = `${e1} ${query} ${e1}`;
                    } else {
                        spamMsg = `${e1} ${TXT_MESSAGES[msgIndex % TXT_MESSAGES.length]} ${e1}`;
                        msgIndex++;
                    }

                    await taskQueues.spam.add(async () => {
                        try { await this.sock.sendMessage(from, { text: spamMsg }); } catch (e) {}
                    });
                    await delay(3000);
                }
            })();
            return;
        }

        if (cmd === 'stopspam' || cmd === 'stoptxt' || cmd === 'stopdtx') {
            activeTasks.spam.delete(`${from}_spam`);
            this.reply(from, '🛑 Spam Stopped.', msg);
            return;
        }

        // ⚔️ ATTACK COMMAND (God Mode but Slower)
        if (cmd === 'attack') {
            if (!isGroup) return;
            const atkKey = `${from}_attack`;
            if (activeTasks.attack.has(atkKey)) return this.reply(from, 'Attack already running!', msg);
            
            const name = query || '𝐌𝐀𝐇𝐎𝐑𝐀𝐆𝐀';
            activeTasks.attack.set(atkKey, true);
            this.reply(from, `⟪ ⚔️ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃 ⟫\n💀 Target: ${name}\n🛑 Stop: ${PREFIX}stopattack`, msg);

            (async () => {
                while (activeTasks.attack.has(atkKey) && this.connected) {
                    const e = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
                    await taskQueues.nc.add(async () => {
                        try { await this.sock.groupUpdateSubject(from, `${e}${e} ${name} ${e}${e}`); } catch (e) {}
                    });
                    await delay(4000);
                }
            })();
            (async () => {
                while (activeTasks.attack.has(atkKey) && this.connected) {
                    await taskQueues.dc.add(async () => {
                        try { await this.sock.groupUpdateDescription(from, `🔥 ${name} 🔥\n𓆩⚡𓆪 𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ 𝐌ᴀʜᴏʀᴀɢᴀ 𝐕𝟐𝟑`); } catch (e) {}
                    });
                    await delay(5000);
                }
            })();
            (async () => {
                while (activeTasks.attack.has(atkKey) && this.connected) {
                    await taskQueues.spam.add(async () => {
                        try { await this.sock.sendMessage(from, { text: `🚨 ${name} IS RULING THIS CHAT 🚨` }); } catch (e) {}
                    });
                    await delay(2500);
                }
            })();
            return;
        }

        if (cmd === 'stopattack') {
            activeTasks.attack.delete(`${from}_attack`);
            this.reply(from, '🛑 Attack Stopped.', msg);
            return;
        }

        // 🎵 SONG DOWNLOADER
        if (cmd === 'song') {
            if (!query) return this.reply(from, `Usage: ${PREFIX}song <song name>`, msg);
            this.reply(from, `🔍 Searching for: *${query}*...`, msg);
            
            try {
                const search = await yts(query);
                if (!search || !search.videos.length) return this.reply(from, '❌ Song not found.', msg);
                
                const video = search.videos[0];
                const caption = `🎵 *${video.title}*\n👤 Author: ${video.author.name}\n⏱️ Duration: ${video.timestamp}\n\n*𓆩⚡𓆪 𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ 𝐌ᴀʜᴏʀᴀɢᴀ 𝐕𝟐𝟑 𓆩🪽𓆪*`;
                
                let audioUrl = '';
                try {
                    const res = await axios.get(`https://api.vreden.web.id/api/ytplaymp3?url=${video.url}`);
                    audioUrl = res.data.result?.download?.url;
                } catch (e) {
                    audioUrl = `https://aemt.me/youtube?url=${video.url}&filter=audioandvideo`;
                }

                if (!audioUrl) return this.reply(from, '❌ Failed to extract audio.', msg);

                await this.sock.sendMessage(from, { image: { url: video.thumbnail }, caption: caption }, { quoted: msg });
                await this.sock.sendMessage(from, { audio: { url: audioUrl }, mimetype: 'audio/mpeg', fileName: `${video.title}.mp3` }, { quoted: msg });

            } catch (err) {
                console.error(err);
                this.reply(from, '❌ Error downloading song.', msg);
            }
            return;
        }

        // 📜 PAGINATED MENU SYSTEM
        if (cmd === 'menu' || cmd === 'fmenu') {
            const page = args[0] || '1';
            const full = cmd === 'fmenu';

            const header = `*『⊰ ˚𓍼 ꨄ𝐌⃝ᴀʜᴏʀᴀɢᴀ ᯓ 𝐔⃝ʟᴛʀᴀ 🪽』 ── 𝐕𝟐𝟑 ⚡*\n\n`;
            const footer = `\n╰─┈┈┈┈┈┈┈┈┈╯\n\n*𓆩⚡𓆪 𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ 𝐌ᴀʜᴏʀᴀɢᴀ 𝐕𝟐𝟑 𓆩🪽𓆪*`;

            const formatSection = (num, title, cmds) => `*${PREFIX}ᴍᴇɴᴜ ${num} : ${title}*\n${cmds.map(c => `│ ✦ ${c}`).join('\n')}\n`;

            const pages = {
                '1': formatSection('1', '𝐂ᴏʀᴇ', ['.ping', '.status', '.arise', '.off']),
                '2': formatSection('2', '𝐍𝐂 & 𝐓ʀɪᴘʟᴇ', ['.nc', '.n1 to .n100', '.stopnc', '.dc', '.stopdc']),
                '3': formatSection('3', '𝐕ᴏɪᴄᴇ & 𝐌ᴇᴅɪᴀ', ['.song', '.tts', '.audio', '.video', '.pic']),
                '4': formatSection('4', '𝐆ʀᴏᴜᴘ & 𝐓ᴀʀɢᴇᴛ', ['.attack', '.stopattack', '.spam', '.txt', '.dtx', '.stopspam']),
                '5': formatSection('5', '𝐀ᴅᴍɪɴ & 𝐁ᴏᴛ', ['.promote', '.demote', '.kick', '.tagall', '.hidetag', '.link', '.revoke']),
                '6': formatSection('6', '𝐒ʏsᴛᴇᴍ', ['.slide', '.stopslide', '.swipe', '.stopswipe', '.performance']),
                '7': formatSection('7', '𝐏ʀᴏ 𝐓ᴏᴏʟs', ['.autopin', '.kickall', '.bc']),
                '8': formatSection('8', '𝐃ɪᴀɢɴᴏsᴛɪᴄs', ['.ping', '.net', '.logs', '.db']),
                '9': formatSection('9', '📱 𝐍ᴜᴍʙᴇʀ 𝐏ᴀɴᴇʟ', ['.pair', '.session', '.unlink']),
                '10': formatSection('10', '𝐒ᴇᴄᴜʀɪᴛʏ & 𝐀ᴅᴍɪɴ', ['.lock', '.mute', '.protect', '.antispam']),
                '11': formatSection('11', '🛠 𝐃ᴇᴠᴇʟᴏᴘᴇʀ 𝐓ᴏᴏʟs', ['.eval', '.exec', '.update']),
                '12': formatSection('12', '🔌 𝐀𝐏𝐈 𝐓ᴏᴏʟs', ['.api', '.checkkey', '.renew']),
                '13': formatSection('13', '𝐔𝐗 & 𝐈ɴғᴏ', ['.about', '.creator', '.theme'])
            };

            let content = '';
            if (full) {
                content = Object.values(pages).join('\n');
            } else if (pages[page]) {
                content = pages[page];
            } else {
                content = `*📜 𝐃𝐄𝐕𝐀 𝐌𝐄𝐍𝐔 𝐈𝐍𝐃𝐄𝐗*\n\n` +
                          Object.keys(pages).map(k => `│ ✦ .ᴍᴇɴᴜ ${k} : ${pages[k].split('\n')[0].split(':')[1].trim()}`).join('\n') +
                          `\n│ ✦ .ғᴍᴇɴᴜ : 𝐅ᴜʟʟ 𝐋ɪsᴛ\n`;
            }

            this.reply(from, header + content + footer, msg);
            return;
        }
    }

    async reply(jid, text, msg, mentions = []) {
        try {
            await this.sock.sendMessage(jid, { text, mentions }, { quoted: msg });
        } catch (e) {}
    }
}

// ==========================================
// 🚀 INITIATE Deva ENGINE
// ==========================================
console.log('╔══════════════════════════════════════╗');
console.log('║  𓆩⚡𓆪 Deva ULTRA V23 ENGINE 𓆩⚡𓆪 ║');
console.log('╚══════════════════════════════════════╝\n');

const DevaBot = new DevaEngine();
DevaBot.connect();
