"""Entry point aplikasi Academic Management System."""

import ctypes
import tkinter as tk

from frontend import main_window


def aktifkan_dpi_awareness():
    """Membuat aplikasi mengikuti DPI Windows dengan lebih tajam."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


def main():
    aktifkan_dpi_awareness()

    root = tk.Tk()
    main_window.mulai(root)
    root.mainloop()


if __name__ == "__main__":
    main()