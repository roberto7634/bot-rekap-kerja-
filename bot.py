import telebot
import os
from datetime import datetime

# ============= KONFIGURASI =============
# Ambil token dari environment variable
TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    print("❌ ERROR: Token tidak ditemukan!")
    exit(1)

print(f"✅ Token: {TOKEN[:10]}...")
bot = telebot.TeleBot(TOKEN)

# 🔴 GANTI DENGAN ID TELEGRAM ANDA!
# Cara dapat ID: kirim pesan ke @userinfobot di Telegram (pinjam HP teman)
ADMIN_CHAT_ID = "7232671831"  # Contoh: "123456789"

# ============= FUNGSI BANTUAN =============
def get_current_date():
    """Dapatkan tanggal dan waktu sekarang"""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def get_wib_time():
    """Dapatkan waktu WIB"""
    from datetime import timedelta
    # UTC ke WIB (+7 jam)
    wib_time = datetime.now() + timedelta(hours=7)
    return wib_time.strftime("%H:%M")

def kirim_rekap():
    """Kirim rekap ke admin"""
    try:
        jam = get_wib_time()
        tanggal = get_current_date()
        
        pesan = f"""
📊 *REKAP OTOMATIS BOT*
🗓️ {tanggal}
⏰ {jam} WIB

✅ Bot BERHASIL berjalan di GitHub Actions!
📈 Ini adalah pesan test.

📌 *Informasi:*
• Platform: GitHub Actions
• Status: ✅ Aktif
• Library: pyTelegramBotAPI

—
_Bot Rekap Kerja v1.0 (Tanpa Schedule)_
        """
        
        bot.send_message(ADMIN_CHAT_ID, pesan, parse_mode="Markdown")
        print(f"✅ [{tanggal}] Pesan berhasil dikirim ke {ADMIN_CHAT_ID}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR kirim pesan: {e}")
        return False

# ============= HANDLER UNTUK PESAN MASUK =============
@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, 
        "👋 Halo! Bot ini berjalan di GitHub Actions.\n"
        "Bot akan mengirim rekap otomatis setiap jam 08:00 dan 17:00 WIB.\n\n"
        "Untuk test, tunggu jadwal berikutnya."
    )

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, f"Pesan diterima: {message.text}")

# ============= MAIN PROGRAM =============
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 BOT GITHUB ACTIONS")
    print("=" * 50)
    print(f"Waktu: {get_current_date()}")
    print(f"Admin ID: {ADMIN_CHAT_ID}")
    print(f"Token: {TOKEN[:10]}...")
    print("-" * 50)
    
    # Kirim rekap
    if kirim_rekap():
        print("✅ Bot berhasil mengirim pesan!")
    else:
        print("❌ Bot gagal mengirim pesan!")
        exit(1)
    
    print("=" * 50)
