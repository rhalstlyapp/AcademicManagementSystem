
"""Palet warna & tipografi aplikasi — Tema "Academic Forest (POLNES)".

Prinsip:
- Profesional, bersih, & menenangkan mata saat membaca data IPK/tugas.
- Terinspirasi langsung dari hijau utama logo POLNES (#36592D) & putih bersih.
- Kontras teks-latar >= 4.5:1 (WCAG AA).
- Nama konstanta lama dipertahankan agar halaman lain tidak rusak.
"""

# ------------------------------------------------------------------ Brand
PRIMARY_COLOR       = "#36592D"   # hijau utama logo POLNES (aksen & tombol utama)
PRIMARY_DARK        = "#223A1C"   # deep forest green (brand gelap / header)
PRIMARY_HOVER       = "#2B4824"   # hijau POLNES lebih gelap saat hover
PRIMARY_LIGHT       = "#D7E6D2"   # sage muda — teks/ikon di atas latar gelap
PRIMARY_ACCENT      = "#4A773E"   # hijau daun segar untuk sorotan sekunder
PRIMARY_ACCENT_SOFT = "#36592D"   # hijau utama untuk tombol primary bg

# Gradasi brand panel (misal untuk halaman Login / Banner)
PRIMARY_GRADIENT_TOP = "#36592D"  # hijau logo POLNES
PRIMARY_GRADIENT_BOT = "#192B14"  # dark evergreen

# ------------------------------------------------------------------ Surface
BG_COLOR         = "#F4F6F3"      # putih keabuan dengan hint hijau sangat tipis (nyaman di mata)
CARD_BG          = "#FFFFFF"      # putih bersih (mengikuti aksen putih di logo)
SURFACE_ELEVATED = "#FFFFFF"      # alias CARD_BG
SURFACE_MUTED    = "#E6ECE4"      # sage pucat — untuk tombol sekunder / header tabel
BORDER_COLOR     = "#CBD5C8"      # garis tepi abu-hijau lembut

# ------------------------------------------------------------------ Input
INPUT_BORDER       = "#BFCBB9"
INPUT_BORDER_FOCUS = "#36592D"
FOCUS_RING         = "#4A773E"

# ------------------------------------------------------------------ Tab
TAB_ACTIVE_BG = "#36592D"
TAB_IDLE_BG   = "#E2E9DF"

# ------------------------------------------------------------------ Teks
TEXT_DARK  = "#182216"   # charcoal kehijauan sangat gelap (kontras tinggi, tidak kaku)
TEXT_MUTED = "#556452"   # abu-hijau untuk label/keterangan sekunder (kontras >= 5.5:1)

# ------------------------------------------------------------------ Status (Sangat penting untuk IPK & Tugas)
SUCCESS_COLOR = "#246A3B"   # hijau emerald (IPK cumlaude / tugas sudah dikumpulkan)
SUCCESS_BG    = "#E3F3E8"   # latar hijau lembut
WARNING_COLOR = "#9A6700"   # amber/emas gelap (mendekati deadline tugas / IPK cukup)
WARNING_BG    = "#FDF3D7"   # latar kuning hangat lembut
DANGER_COLOR  = "#B42318"   # merah tegas (terlambat kumpul tugas / nilai mengulang)
DANGER_BG     = "#FEECEB"   # latar merah lembut
INFO_COLOR    = "#1D5B79"   # biru akademik (pengumuman / status dosen)
INFO_BG       = "#E3F0F7"   # latar biru lembut

# ------------------------------------------------------------------ Role Badge (Opsional - pembeda Admin, Dosen, Mahasiswa)
ROLE_ADMIN_BG   = "#223A1C" # dark forest
ROLE_DOSEN_BG   = "#1D5B79" # academic blue
ROLE_MHS_BG     = "#4A773E" # leaf green

# ------------------------------------------------------------------ Sidebar
SIDEBAR_BG     = "#1B2E16"   # hijau tua gelap (elegan & kontras dengan konten putih)
SIDEBAR_ACTIVE = "#4A773E"   # hijau terang POLNES — menu aktif
SIDEBAR_HOVER  = "#274020"   # hijau medium — saat kursor diarahkan
SIDEBAR_TEXT   = "#DCE5D9"   # putih kehijauan lembut — teks menu idle

# ------------------------------------------------------------------ Font
FONT_FAMILY  = "Segoe UI"
FONT_BRAND   = ("Segoe UI", 26, "bold")
FONT_TITLE   = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 14, "bold")
FONT_BOLD    = ("Segoe UI", 10, "bold")
FONT_BODY    = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_BUTTON  = ("Segoe UI", 10, "bold")
FONT_LINK    = ("Segoe UI", 10, "bold")

# ------------------------------------------------------------------ Versi Dictionary Singkat
ACADEMIC_COLOR_PALETTE = {
    "bg_color": "#F4F6F3",        # Latar utama putih-sage lembut
    "card_bg": "#FFFFFF",         # Kartu putih bersih (seperti detail logo)
    "alt_bg": "#E6ECE4",          # Latar sekunder / baris tabel selang-seling
    "text_dark": "#182216",       # Teks utama gelap
    "primary_color": "#36592D",   # Hijau POLNES untuk CTA/Heading
    "accent_color": "#4A773E",    # Hijau aksen untuk hover/highlight
    "sidebar_bg": "#1B2E16"       # Hijau gelap untuk navigasi samping
}

# Palet Warna Website Bertema Kopi (Versi Singkat)

BG_COLOR = "#F7F3EE"
CARD_BG = "#EFE8DD"
TEXT_DARK = "#1A120B"
PRIMARY_COLOR = "#0F382C"
ACCENT_COLOR = "#7A3E36"

