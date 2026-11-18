from faulthandler import register
import tkinter as tk
from tkinter import messagebox

from backend.auth import login 

#Untuk membuat halaman login
window = tk.Tk()
window.title("Login SIAKAD")
window.geometry("400x300")
window.configure(bg="#f0f0f0")



#creating wwidgets
login_label= tk.Label(window, text="Login", font=("Arial", 20), bg="#f0f0f0")
username_label= tk.Label(window, text="Username:", font=("Arial", 12), bg="#f0f0f0")
username_entry= tk.Entry(window, font=("Arial", 12))
nim_entry= tk.Entry(window, font=("Arial", 12))
nim_label= tk.Label(window, text="NIM:", font=("Arial", 12), bg="#f0f0f0")
login_button= tk.Button(window, text="Login", font=("Arial", 12), command=lambda: login(username_entry.get(), nim_entry.get()))
register_button= tk.Button(window, text="Register", font=("Arial", 12), command=lambda: register(username_entry.get(), nim_entry.get()))


#placing widgets onn the window
login_label.pack(pady=20)
username_label.pack()
username_entry.pack(pady=5)
nim_label.pack()
nim_entry.pack(pady=5)
login_button.pack(pady=20)
register_button.pack(pady=5)






window.mainloop()