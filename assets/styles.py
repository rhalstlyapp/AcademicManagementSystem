"""Style ttk terpusat — Tema "Coffee Shop".

Panggil `terapkan_style(root)` sekali di main_window sebelum layar dibangun.
Idempoten: aman dipanggil berulang.
"""
from tkinter import ttk

from assets import colors as c

_SUDAH = {"ok": False}


def terapkan_style(root):
    if _SUDAH["ok"]:
        return
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # ---- Entry dengan focus ring caramel ----
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
        bordercolor=[("focus", c.INPUT_BORDER_FOCUS)],
        lightcolor=[("focus", c.INPUT_BORDER_FOCUS)],
        darkcolor=[("focus", c.INPUT_BORDER_FOCUS)],
    )

    # ---- Combobox ----
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
        bordercolor=[("focus", c.INPUT_BORDER_FOCUS)],
        fieldbackground=[("readonly", c.SURFACE_ELEVATED)],
        selectbackground=[("readonly", c.SURFACE_ELEVATED)],
        selectforeground=[("readonly", c.TEXT_DARK)],
    )

    # ---- Tombol Primary (caramel) ----
    style.configure(
        "Primary.TButton",
        background=c.PRIMARY_ACCENT_SOFT,
        foreground="#FFF8F0",
        font=("Segoe UI", 11, "bold"),
        padding=(18, 12),
        borderwidth=0,
        focuscolor=c.PRIMARY_ACCENT,
    )
    style.map(
        "Primary.TButton",
        background=[("active", c.PRIMARY_ACCENT), ("disabled", c.SURFACE_MUTED)],
        foreground=[("disabled", c.TEXT_MUTED)],
    )

    # ---- Tombol Secondary ----
    style.configure(
        "Secondary.TButton",
        background=c.SURFACE_MUTED,
        foreground=c.TEXT_DARK,
        font=("Segoe UI", 10, "bold"),
        padding=(16, 10),
        borderwidth=0,
    )
    style.map("Secondary.TButton", background=[("active", c.INPUT_BORDER)])

    # ---- Link ----
    style.configure(
        "Link.TButton",
        background=c.CARD_BG,
        foreground=c.PRIMARY_ACCENT_SOFT,
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
        padding=(4, 2),
    )
    style.map("Link.TButton", foreground=[("active", c.PRIMARY_DARK)])

    # ---- Checkbutton ----
    style.configure(
        "Form.TCheckbutton",
        background=c.CARD_BG,
        foreground=c.TEXT_MUTED,
        font=("Segoe UI", 9),
        padding=(0, 4),
    )
    style.map("Form.TCheckbutton", background=[("active", c.CARD_BG)])

    _SUDAH["ok"] = True