import telebot
import os
import json
from datetime import datetime, timedelta
from collections import Counter

# ============= KONFIGURASI =============
# Ambil token dari environment variable
TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    print("❌ ERROR: Token tidak ditemukan!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# 🔴 GANTI DENGAN ID TELEGRAM ANDA!
ADMIN_CHAT_ID = "8650707421"  # Contoh: "123456789"

# File untuk menyimpan data (simpan di repository)
PROJECTS_FILE = 'projects.json'
ABSEN_FILE = 'absen.json'

# ============= FUNGSI BANTUAN =============
def load_data():
    """Load data dari file JSON"""
    projects = {}
    absen = []
    
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            projects = json.load(f)
    
    if os.path.exists(ABSEN_FILE):
        with open(ABSEN_FILE, 'r') as f:
            absen = json.load(f)
    
    return projects, absen

def save_data(projects, absen):
    """Simpan data ke file JSON"""
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects, f, indent=2)
    
    with open(ABSEN_FILE, 'w') as f:
        json.dump(absen, f, indent=2)
    
    print("✅ Data tersimpan")

def get_current_date():
    """Dapatkan tanggal sekarang format DD/MM/YYYY"""
    return datetime.now().strftime("%d/%m/%Y")

def get_wib_time():
    """Dapatkan waktu WIB"""
    wib = datetime.now() + timedelta(hours=7)
    return wib.strftime("%H:%M")

def format_rupiah(angka):
    """Format angka ke Rupiah"""
    try:
        return f"Rp {int(angka):,}".replace(",", ".")
    except:
        return "Rp 0"

# ============= FUNGSI REKAP =============
def get_rekap_project(projects, absen):
    """Buat rekap semua project"""
    if not projects:
        return "📁 *Belum ada project*"
    
    text = "📊 *REKAP SEMUA PROJECT*\n\n"
    
    for pid, p in projects.items():
        # Hitung jumlah absen untuk project ini
        jml_absen = sum(1 for a in absen if a['project_id'] == pid)
        
        text += f"`{pid}` - *{p['nama']}*\n"
        text += f"   💰 {format_rupiah(p['nilai'])}\n"
        text += f"   📊 Total absen: {jml_absen}\n"
        
        # Hitung absen per status untuk project ini
        project_absen = [a for a in absen if a['project_id'] == pid]
        if project_absen:
            status_count = Counter(a['status'] for a in project_absen)
            text += f"   ✅ Hadir: {status_count.get('Hadir', 0)}\n"
            text += f"   🤒 Sakit: {status_count.get('Sakit', 0)}\n"
            text += f"   📝 Izin: {status_count.get('Izin', 0)}\n"
            text += f"   🏖️ Cuti: {status_count.get('Cuti', 0)}\n"
        
        text += "\n"
    
    return text

def get_rekap_absen_harian(absen):
    """Buat rekap absen hari ini"""
    today = get_current_date()
    
    # Filter absen hari ini
    absen_hari_ini = [a for a in absen if a.get('tanggal') == today]
    
    if not absen_hari_ini:
        return f"📝 *REKAP ABSEN HARI INI*\n🗓️ {today}\n\nBelum ada absen hari ini."
    
    # Hitung per status
    status_count = Counter(a['status'] for a in absen_hari_ini)
    
    # Kelompokkan per project
    per_project = {}
    for a in absen_hari_ini:
        pid = a['project_id']
        if pid not in per_project:
            per_project[pid] = []
        per_project[pid].append(a)
    
    text = f"📝 *REKAP ABSEN HARI INI*\n🗓️ {today}\n"
    text += f"📊 Total: {len(absen_hari_ini)} orang\n\n"
    
    # Statistik global
    text += "📈 *Statistik Global:*\n"
    text += f"✅ Hadir: {status_count.get('Hadir', 0)}\n"
    text += f"🤒 Sakit: {status_count.get('Sakit', 0)}\n"
    text += f"📝 Izin: {status_count.get('Izin', 0)}\n"
    text += f"🏖️ Cuti: {status_count.get('Cuti', 0)}\n\n"
    
    # Rincian per project
    text += "📋 *Rincian Per Project:*\n"
    for pid, daftar in per_project.items():
        text += f"\n`{pid}` - {len(daftar)} orang:\n"
        for a in daftar:
            text += f"   • {a['nama']} ({a['status']}) - {a.get('jam', '')}\n"
    
    return text

def get_laporan_lengkap():
    """Gabungan rekap project dan absen harian"""
    projects, absen = load_data()
    
    rekap_project = get_rekap_project(projects, absen)
    rekap_absen = get_rekap_absen_harian(absen)
    
    wib = get_wib_time()
    tanggal = get_current_date()
    
    header = f"""
📋 *LAPORAN LENGKAP BOT*
🗓️ {tanggal} | ⏰ {wib} WIB
✅ Status: Aktif di GitHub Actions
    """
    
    return f"{header}\n\n{rekap_project}\n\n{rekap_absen}"

# ============= FUNGSI UNTUK TEST =============
def test_kirim_pesan():
    """Kirim pesan test sederhana"""
    try:
        pesan = f"""
✅ *TEST BOT GITHUB ACTIONS*
Waktu: {get_current_date()} {get_wib_time()} WIB

Bot berhasil terhubung ke Telegram!
Menunggu data untuk rekap lengkap...
        """
        bot.send_message(ADMIN_CHAT_ID, pesan, parse_mode="Markdown")
        print("✅ Pesan test terkirim")
        return True
    except Exception as e:
        print(f"❌ Error test: {e}")
        return False

def kirim_laporan_lengkap():
    """Kirim laporan lengkap ke admin"""
    try:
        laporan = get_laporan_lengkap()
        
        # Kirim laporan (bisa dipecah kalau terlalu panjang)
        if len(laporan) > 4000:
            # Kirim rekap project dulu
            projects, _ = load_data()
            bot.send_message(ADMIN_CHAT_ID, get_rekap_project(projects, []), parse_mode="Markdown")
            
            # Kirim rekap absen
            _, absen = load_data()
            bot.send_message(ADMIN_CHAT_ID, get_rekap_absen_harian(absen), parse_mode="Markdown")
        else:
            bot.send_message(ADMIN_CHAT_ID, laporan, parse_mode="Markdown")
        
        print(f"✅ Laporan lengkap terkirim ke {ADMIN_CHAT_ID}")
        return True
    except Exception as e:
        print(f"❌ Error kirim laporan: {e}")
        return False

# ============= HANDLER UNTUK PESAN MASUK =============
@bot.message_handler(commands=['start', 'help'])
def start(message):
    help_text = """
👋 *Halo! Ini Bot Rekap Kerja*

Bot ini berjalan di *GitHub Actions* dan akan mengirim:
✅ Rekap semua project
✅ Rekap absen harian
✅ Laporan lengkap setiap hari

📅 *Jadwal:*
• 08:00 WIB - Pengingat
• 17:00 WIB - Laporan lengkap

Untuk test, tunggu jadwal berikutnya.
    """
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['rekap'])
def manual_rekap(message):
    """Perintah manual untuk rekap"""
    bot.reply_to(message, "📊 Menyiapkan laporan...")
    laporan = get_laporan_lengkap()
    bot.send_message(message.chat.id, laporan, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, "Gunakan /start atau /rekap")

# ============= MAIN PROGRAM =============
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 BOT REKAP GITHUB ACTIONS")
    print("=" * 60)
    print(f"Waktu: {get_current_date()} {get_wib_time()} WIB")
    print(f"Admin ID: {ADMIN_CHAT_ID}")
    print(f"Token: {TOKEN[:10]}...")
    
    # Load data
    projects, absen = load_data()
    print(f"📁 Project: {len(projects)}")
    print(f"📝 Absen: {len(absen)}")
    print("-" * 60)
    
    # Tentukan mode berdasarkan waktu atau parameter
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Mode test: kirim pesan sederhana
        print("📌 Mode: TEST")
        test_kirim_pesan()
    
    elif len(sys.argv) > 1 and sys.argv[1] == "rekap":
        # Mode rekap: kirim laporan lengkap
        print("📌 Mode: REKAP LENGKAP")
        kirim_laporan_lengkap()
    
    else:
        # Mode default: kirim laporan lengkap
        print("📌 Mode: DEFAULT")
        kirim_laporan_lengkap()
    
    print("=" * 60)

