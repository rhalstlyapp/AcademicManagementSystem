"""Style ttk terpusat untuk tema Academic Forest.

Panggil `terapkan_style(root)` sekali pada saat aplikasi
pertama kali dibuat.

File ini hanya menangani styling widget ttk.
Warna utama tetap mengambil dari assets.colors.
"""

from tkinter import ttk

from assets import colors as c


# ============================================================
# STATUS
# ============================================================

_SUDAH = {
    "ok": False
}


# ============================================================
# FUNGSI UTAMA
# ============================================================

def terapkan_style(root):
    """Menerapkan seluruh style ttk aplikasi."""

    if _SUDAH["ok"]:
        return

    style = ttk.Style(root)

    # Gunakan tema clam agar konfigurasi border,
    # background, dan foreground lebih konsisten
    # pada Windows.
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # ========================================================
    # ENTRY
    # ========================================================

    style.configure(
        "Form.TEntry",
        fieldbackground=c.SURFACE_ELEVATED,
        foreground=c.TEXT_DARK,
        bordercolor=c.INPUT_BORDER,
        lightcolor=c.INPUT_BORDER,
        darkcolor=c.INPUT_BORDER,
        insertcolor=c.TEXT_DARK,
        padding=(12, 10),
        relief="flat",
    )

    style.map(
        "Form.TEntry",
        bordercolor=[
            (
                "focus",
                c.INPUT_BORDER_FOCUS,
            ),
        ],
        lightcolor=[
            (
                "focus",
                c.INPUT_BORDER_FOCUS,
            ),
        ],
        darkcolor=[
            (
                "focus",
                c.INPUT_BORDER_FOCUS,
            ),
        ],
    )

    # ========================================================
    # COMBOBOX
    # ========================================================

    style.configure(
        "Form.TCombobox",
        fieldbackground=c.SURFACE_ELEVATED,
        background=c.SURFACE_ELEVATED,
        foreground=c.TEXT_DARK,
        bordercolor=c.INPUT_BORDER,
        arrowcolor=c.TEXT_MUTED,
        padding=(10, 8),
    )

    style.map(
        "Form.TCombobox",
        bordercolor=[
            (
                "focus",
                c.INPUT_BORDER_FOCUS,
            ),
        ],
        fieldbackground=[
            (
                "readonly",
                c.SURFACE_ELEVATED,
            ),
        ],
        selectbackground=[
            (
                "readonly",
                c.SURFACE_ELEVATED,
            ),
        ],
        selectforeground=[
            (
                "readonly",
                c.TEXT_DARK,
            ),
        ],
    )

    # ========================================================
    # PRIMARY BUTTON
    # ========================================================

    style.configure(
        "Primary.TButton",
        background=c.PRIMARY_COLOR,
        foreground="#FFFFFF",
        font=c.FONT_BUTTON,
        padding=(18, 12),
        borderwidth=0,
        focuscolor=c.FOCUS_RING,
    )

    style.map(
        "Primary.TButton",
        background=[
            (
                "active",
                c.PRIMARY_HOVER,
            ),
            (
                "pressed",
                c.PRIMARY_DARK,
            ),
            (
                "disabled",
                c.SURFACE_MUTED,
            ),
        ],
        foreground=[
            (
                "disabled",
                c.TEXT_MUTED,
            ),
        ],
    )

    # ========================================================
    # SECONDARY BUTTON
    # ========================================================

    style.configure(
        "Secondary.TButton",
        background=c.SURFACE_MUTED,
        foreground=c.TEXT_DARK,
        font=c.FONT_BOLD,
        padding=(16, 10),
        borderwidth=0,
        focuscolor=c.FOCUS_RING,
    )

    style.map(
        "Secondary.TButton",
        background=[
            (
                "active",
                c.INPUT_BORDER,
            ),
            (
                "pressed",
                c.BORDER_COLOR,
            ),
        ],
    )

    # ========================================================
    # LINK BUTTON
    # ========================================================

    style.configure(
        "Link.TButton",
        background=c.CARD_BG,
        foreground=c.PRIMARY_COLOR,
        font=c.FONT_LINK,
        borderwidth=0,
        padding=(4, 2),
        focuscolor=c.CARD_BG,
    )

    style.map(
        "Link.TButton",
        foreground=[
            (
                "active",
                c.PRIMARY_DARK,
            ),
        ],
    )

    # ========================================================
    # CHECKBUTTON
    # ========================================================

    style.configure(
        "Form.TCheckbutton",
        background=c.CARD_BG,
        foreground=c.TEXT_MUTED,
        font=c.FONT_SMALL,
        padding=(0, 4),
        focuscolor=c.CARD_BG,
    )

    style.map(
        "Form.TCheckbutton",
        background=[
            (
                "active",
                c.CARD_BG,
            ),
        ],
    )

    # ========================================================
    # LABEL
    # ========================================================

    style.configure(
        "Form.TLabel",
        background=c.CARD_BG,
        foreground=c.TEXT_DARK,
        font=c.FONT_BODY,
    )

    style.configure(
        "Muted.TLabel",
        background=c.CARD_BG,
        foreground=c.TEXT_MUTED,
        font=c.FONT_SMALL,
    )

    # ========================================================
    # TREEVIEW
    # ========================================================

    style.configure(
        "Treeview",
        background=c.CARD_BG,
        foreground=c.TEXT_DARK,
        fieldbackground=c.CARD_BG,
        bordercolor=c.BORDER_COLOR,
        rowheight=30,
        font=c.FONT_BODY,
    )

    style.configure(
        "Treeview.Heading",
        background=c.SURFACE_MUTED,
        foreground=c.TEXT_DARK,
        font=c.FONT_BOLD,
        bordercolor=c.BORDER_COLOR,
    )

    style.map(
        "Treeview",
        background=[
            (
                "selected",
                c.PRIMARY_LIGHT,
            ),
        ],
        foreground=[
            (
                "selected",
                c.TEXT_DARK,
            ),
        ],
    )

    # ========================================================
    # NOTEBOOK / TAB
    # ========================================================

    style.configure(
        "TNotebook",
        background=c.BG_COLOR,
        borderwidth=0,
    )

    style.configure(
        "TNotebook.Tab",
        background=c.TAB_IDLE_BG,
        foreground=c.TEXT_DARK,
        padding=(14, 8),
        font=c.FONT_BOLD,
    )

    style.map(
        "TNotebook.Tab",
        background=[
            (
                "selected",
                c.TAB_ACTIVE_BG,
            ),
        ],
        foreground=[
            (
                "selected",
                "#FFFFFF",
            ),
        ],
    )

    # Tandai bahwa style sudah diterapkan.
    _SUDAH["ok"] = True
