"""Entry point aplikasi desktop SIAKAD."""
import tkinter as tk

from assets.colors import BG_COLOR, TEXT_DARK
from frontend.login_page import tampilkan_login


def main():
    root = tk.Tk()
    root.title("Academic Management System")
    root.geometry("1000x680")
    root.minsize(820, 560)
    root.configure(bg=BG_COLOR)
    root.option_add("*Font", ("Segoe UI", 10))
    root.option_add("*Foreground", TEXT_DARK)
    tampilkan_login(root)
    root.mainloop()


if __name__ == "__main__":
    main()
