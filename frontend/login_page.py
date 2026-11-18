import tkinter as tk

from assets.colors import (
    BG_COLOR,
    CARD_BG,
    TEXT_DARK,
    PRIMARY_COLOR,
    ACCENT_COLOR
)
from tkinter import messagebox

from backend.auth import login, register

#Untuk membuat halaman login
window = tk.Tk()
window.title("Login SIAKAD")
window.geometry("400x300")
window.configure(bg=BG_COLOR)



# Creating widgets
login_label = tk.Label(
    window,
    text="Login",
    font=("Arial", 20),
    bg=BG_COLOR,
    fg=TEXT_DARK
)

username_label = tk.Label(
    window,
    text="Username:",
    font=("Arial", 12),
    bg=CARD_BG,
    fg=TEXT_DARK
)

username_entry = tk.Entry(
    window,
    font=("Arial", 12)
)

nim_label = tk.Label(
    window,
    text="NIM:",
    font=("Arial", 12),
    bg=CARD_BG,
    fg=TEXT_DARK
)

nim_entry = tk.Entry(
    window,
    font=("Arial", 12)
)

login_button = tk.Button(
    window,
    text="Login",
    font=("Arial", 12),
    command=lambda: login(
        username_entry.get(),
        nim_entry.get()
    )
)

# Teks "Anda belum punya akun?"
register_text = tk.Label(
    window,
    text="Anda belum punya akun?",
    font=("Arial", 10),
    bg=CARD_BG,
    fg=TEXT_DARK
)

# Tombol Register
register_button = tk.Button(
    window,
    text="Register",
    font=("Arial", 10),
    fg="blue",
    relief="flat",
    bd=0,
    cursor="hand2",
    command=lambda: register(
        username_entry.get(),
        nim_entry.get()
    )
)


# Placing widgets on the window
login_label.pack(pady=20)

username_label.pack()
username_entry.pack(pady=5)

nim_label.pack()
nim_entry.pack(pady=5)

login_button.pack(pady=20)

register_text.pack(pady=(5, 0))
register_button.pack(pady=(0, 10))




window.mainloop()