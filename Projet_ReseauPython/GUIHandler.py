class LoginMenu:
	def __init__(self, controller):
		self.controller = controller
		self.root = tk.Tk()
		self.root.title("Connexion")
		self.root.geometry("400x250")

		tk.Label(self.root, text="Email:", font=H3_FONT).pack(pady=(20, 0))
		self.email_entry = tk.Entry(self.root, font=P_FONT, width=30)
		self.email_entry.pack(pady=5)

		tk.Label(self.root, text="Mot de passe:", font=H3_FONT).pack(pady=(10, 0))
		self.password_entry = tk.Entry(self.root, show="*", font=P_FONT, width=30)
		self.password_entry.pack(pady=5)

		tk.Button(self.root, text="Se connecter", font=H3_FONT, command=self.on_login).pack(pady=20)

		self.root.mainloop()

	def on_login(self):
		email = self.email_entry.get()
		password = self.password_entry.get()
		self.controller.on_login(email, password)

class MenuSimple:
	def __init__(self, controller):
		self.controller = controller
		self.root = tk.Tk()
		self.root.title("Menu Simple")
		self.root.geometry("400x200")
		btn = tk.Button(self.root, text="Cliquez-moi", font=H2_FONT, command=self.on_button_click)
		btn.pack(expand=True)
		self.root.mainloop()

	def on_button_click(self):
		self.controller.on_button_click()

        

import tkinter as tk
from tkinter import messagebox

# Constantes de taille de police
H1_FONT = ("Arial", 24, "bold")
H2_FONT = ("Arial", 20, "bold")
H3_FONT = ("Arial", 16, "bold")
P_FONT = ("Arial", 16)
P2_FONT = ("Arial", 14)
P3_FONT = ("Arial", 12)
