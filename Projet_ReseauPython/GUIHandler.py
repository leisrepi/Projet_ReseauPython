
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
