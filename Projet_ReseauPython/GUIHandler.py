import tkinter as tk
from tkinter import messagebox, ttk
# Constantes de taille de police
H1_FONT = ("Arial", 24, "bold")
H2_FONT = ("Arial", 20, "bold")
H3_FONT = ("Arial", 16, "bold")
P_FONT = ("Arial", 16)
P2_FONT = ("Arial", 14)
P3_FONT = ("Arial", 12)


class LoginMenu:
	def __init__(self, controller):
		self.controller = controller
		self.root = controller.root
		self.root.title("Connexion")
		self.root.geometry("400x250")

		tk.Label(self.root, text="Pseudonyme:", font=H3_FONT).pack(pady=(20, 0))
		self.pseudonyme_entry = tk.Entry(self.root, font=P_FONT, width=30)
		self.pseudonyme_entry.pack(pady=5)

		tk.Label(self.root, text="Mot de passe:", font=H3_FONT).pack(pady=(10, 0))
		self.password_entry = tk.Entry(self.root, show="*", font=P_FONT, width=30)
		self.password_entry.pack(pady=5)

		tk.Button(self.root, text="Se connecter", font=H3_FONT, command=self.on_login).pack(pady=20)


	def on_login(self):
		pseudonyme = self.pseudonyme_entry.get()
		password = self.password_entry.get()
		self.controller.on_login(pseudonyme, password)



class Page1(tk.Frame):
	def __init__(self, parent, controller):
		super().__init__(parent, pady=10)
		self.controller = controller
		label = tk.Label(self, text="Calcul réseau", font=H2_FONT)
		label.grid(row=0, column=0, columnspan=2 , padx=5, pady=5)

		


		#--------------------------------------|Point 1 (gauche)|--------------------------------------
		framePoint1 = tk.Frame(self)
		framePoint1.grid(row=1, column=0, padx=5, pady=5)
		#--------------------------------------
		#IPV4
		tk.Label(framePoint1, text="Adresse IP:", font=P2_FONT).grid(row=0, column=0, padx=5, pady=5, sticky="e")
		self.ip_entry = tk.Entry(framePoint1, font=P2_FONT, width=20)
		self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
		
		#MASK
		tk.Label(framePoint1, text="Masque:", font=P2_FONT).grid(row=0, column=2, padx=5, pady=5, sticky="e")
		self.mask_entry = tk.Entry(framePoint1, font=P2_FONT, width=20)
		self.mask_entry.grid(row=0, column=3, padx=5, pady=5)

		#--------------------------------------
		#Output Adresse reseau
		tk.Label(framePoint1, text="Adresse Reseau:", font=P2_FONT).grid(row=1, column=0, padx=5, pady=5, sticky="e")
		self.network_output= tk.Entry(framePoint1, font=P2_FONT, width=20, state="readonly")
		self.network_output.grid(row=1, column=1, padx=5, pady=5)
		#Output Adresse broadcast
		tk.Label(framePoint1, text="Adresse Broadcast:", font=P2_FONT).grid(row=1, column=2, padx=5, pady=5, sticky="e")
		self.broadcast_output= tk.Entry(framePoint1, font=P2_FONT, width=20, state="readonly")
		self.broadcast_output.grid(row=1, column=3, padx=5, pady=5)

		#--------------------------------------
		#Output adresse sous reseau
		tk.Label(framePoint1, text="Adresse Sous-Réseau:", font=P2_FONT).grid(row=2, column=0, padx=5, pady=5, sticky="e")
		self.subnet_output= tk.Entry(framePoint1, font=P2_FONT, width=20, state="readonly")
		self.subnet_output.grid(row=2, column=1, padx=5, pady=5)
		#Output Adresse broadcast sous reseau
		tk.Label(framePoint1, text="Adresse Broadcast Sous-Réseau:", font=P2_FONT).grid(row=2, column=2, padx=5, pady=5, sticky="e")
		self.subnet_broadcast_output= tk.Entry(framePoint1, font=P2_FONT, width=20, state="readonly")
		self.subnet_broadcast_output.grid(row=2, column=3, padx=5, pady=5)


		#--------------------------------------|Point 2 (droite)|--------------------------------------
		framePoint2 = tk.Frame(self)
		framePoint2.grid(row=1, column=1, padx=5, pady=5)
		#--------------------------------------
		#IPV4
		tk.Label(framePoint2, text="Adresse IP:", font=P2_FONT).grid(row=0, column=0, padx=5, pady=5, sticky="e")
		self.ip_entry2 = tk.Entry(framePoint2, font=P2_FONT, width=20)
		self.ip_entry2.grid(row=0, column=1, padx=5, pady=5)
		#Adresse reseau
		tk.Label(framePoint2, text="Adresse Reseau:", font=P2_FONT).grid(row=0, column=2, padx=5, pady=5, sticky="e")
		self.network_output2= tk.Entry(framePoint2, font=P2_FONT, width=20, state="readonly")
		self.network_output2.grid(row=0, column=3, padx=5, pady=5)
		#--------------------------------------
		#Output 1ere adresse réseau/sous réseau
		tk.Label(framePoint2, text="1ère Adresse Utilisable:", font=P2_FONT).grid(row=1, column=0, padx=5, pady=5, sticky="e")
		self.first_usable_output= tk.Entry(framePoint2, font=P2_FONT, width=20, state="readonly")
		self.first_usable_output.grid(row=1, column=1, padx=5, pady=5)
		#Output Derniere adresse réseau/sous réseau
		tk.Label(framePoint2, text="Dernière Adresse Utilisable:", font=P2_FONT).grid(row=1, column=2, padx=5, pady=5, sticky="e")
		self.last_usable_output= tk.Entry(framePoint2, font=P2_FONT, width=20, state="readonly")
		self.last_usable_output.grid(row=1, column=3, padx=5, pady=5)
		#---------------------------------------
		#Bare appartien au réseau ?
		self.belongs_output = tk.Label(framePoint2,
		    text="L'adresse IP appartient-elle au réseau ?",
			font=P2_FONT,
			background="lightgrey"
			).grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="e")
		


class Page2(tk.Frame):
	def __init__(self, parent, controller):
		super().__init__(parent, pady=10)
		self.controller = controller
		label = tk.Label(self, text="Page 2", font=H2_FONT)
		label.pack(pady=10, padx=10)

class Page3(tk.Frame):
	def __init__(self, parent, controller):

		#TODO : ajouter une vérification pour ne pas ajouter du texte
		#TODO : renommer get_text
		def add_to_combobox():
			current_values = list(self.nb_machines_combobox['values'])
			if(self.nb_machines_combobox.get() == ""):
				self.nb_machines_combobox['values'] = current_values + [self.nb_machines_per_subnet.get()]
			else:
				print("Il est écrit : ", self.nb_machines_combobox.get())
			self.nb_machines_per_subnet.delete(0, tk.END)

		def remove_of_combobox():
			# current est l'index de l'élément sélectionné
			# le premier élément est une chaîne vide lorsqu'aucun élément n'est sélectionné
			if self.nb_machines_combobox.current() == 0:
				return
			
			combobox_list = list(self.nb_machines_combobox['values'])
			combobox_list.pop(self.nb_machines_combobox.current())
			self.nb_machines_combobox['values'] = combobox_list
			print("Valeur supprimée : ", self.nb_machines_combobox.get())
			print("Index supprimé : ", self.nb_machines_combobox.current())
			self.nb_machines_combobox.set("")
				
		super().__init__(parent, pady=10, width=controller.root.winfo_screenwidth())
		self.controller = controller
		# #--------------------------------------|Découpage en sous-réseaux|--------------------------------------
		label = tk.Label(self, text="Découpe en sous-réseaux", font=H2_FONT).grid(row=0, column=0, padx=5, pady=5, sticky="e", columnspan=5)
		
		
		# #-----------------------------------------------------------------------------------------------
		# Adresse réseau
		tk.Label(self, text="Adresse réseau:", font=P2_FONT).grid(row=1, column=0, padx=5, pady=5, sticky="e")
		self.network_entry = tk.Entry(self, font=P2_FONT, width=20)
		self.network_entry.grid(row=1, column=1, padx=5, pady=5)

		nb_machines_tab = [""]
		# Nombre de machines par sous-réseau
		tk.Label(self, text="Nombre de machines par sous-réseau:", font=P2_FONT).grid(row=1, column=2, padx=5, pady=5, sticky="e")
		self.nb_machines_per_subnet = tk.Entry(self, font=P2_FONT, width=5, )
		self.nb_machines_per_subnet.grid(row=1, column=3, padx=5, pady=5, sticky="w")
		tk.Button(self, text="ajouter", command= add_to_combobox, borderwidth=1, relief="solid").grid(row=1, column=4, padx=5, pady=5, sticky="w")
		self.nb_machines_combobox = ttk.Combobox(self, values=nb_machines_tab, font=P2_FONT, width=5)
		self.nb_machines_combobox.grid(row=1, column=5, padx=5, pady=5, sticky="w")
		tk.Button(self, text="supprimer", command=remove_of_combobox, borderwidth=1, relief="solid").grid(row=1, column=6, padx=5, pady=5, sticky="w")

		# #-----------------------------------------------------------------------------------------------

		# Masque
		tk.Label(self, text="Masque:", font=P2_FONT).grid(row=2, column=0, padx=5, pady=5, sticky="e")
		self.mask_entry = tk.Entry(self, font=P2_FONT, width=20)
		self.mask_entry.grid(row=2, column=1, padx=5, pady=5)

		# Nombre de sous-réseaux
		tk.Label(self, text="Nombre de sous-réseaux:", font=P2_FONT).grid(row=2, column=2, padx=5, pady=5, sticky="e")
		self.nb_subnet = tk.Entry(self, font=P2_FONT, width=5)
		self.nb_subnet.grid(row=2, column=3, padx=5, pady=5, sticky="w")

		tk.Button(self, text="Calucler la découpe", command=print("Button Clicked"), font=P2_FONT, borderwidth=1, relief="solid").grid(row=2, column=4, columnspan=3, padx=5, pady=5)

		# #-----------------------------------------------------------------------------------------------

		# Tableau des sous-réseaux
		colonnes = ["Adresse de sous-réseau", "Adresse de broadcast", "Première IP", "Dernière IP"]
		tree = ttk.Treeview(self, columns=colonnes, show='headings')
		tree.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

		for col in colonnes:
			tree.heading(col, text=col)
			tree.column(col, anchor='center')

class PageSelector(tk.Frame):
	def __init__(self, parent, controller):
		super().__init__(parent, padx=10, pady=10)
		self.controller = controller
		self.rowconfigure(3, weight=1)
		tk.Label(self, text="Sélecteur de page", font=H2_FONT).pack(side="left",pady=10)

		tk.Button(self, text="Aller à la Page 1", font=P2_FONT,
				  command=lambda: controller.show_page("Page1")).pack(side="left",pady=5)

		tk.Button(self, text="Aller à la Page 2", font=P2_FONT,
				  command=lambda: controller.show_page("Page2")).pack(side="left",pady=5)	
		tk.Button(self, text="Aller à la Page 3", font=P2_FONT,
				  command=lambda: controller.show_page("Page3")).pack(side="left",pady=5)	

class MainApp:
	def __init__(self, controller):
		self.controller = controller
		self.root = controller.root
		self.root.title("Application Principale")
		self.root.geometry(str(self.root.winfo_screenwidth())+"x"+str(self.root.winfo_screenheight()))

		# Frame pour le label de bienvenue
		header_frame = tk.Frame(self.root)
		header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
		tk.Label(header_frame, text="Bienvenue dans l'application principale!", font=H2_FONT).pack(pady=20)

		# Creation du systeme de page:
		# --- Conteneur des pages ---
		container = tk.Frame(self.root)
		container.grid(row=1, column=0, sticky="nsew")
		container.rowconfigure(0, weight=1)
		container.columnconfigure(0, weight=1)

		self.pages = {}
		for PageClass in (Page1, Page2, Page3):
			page_name = PageClass.__name__
			frame = PageClass(container, self)
			self.pages[page_name] = frame
			# Toutes les pages occupent la même cellule
			frame.grid(row=0, column=0, sticky="nsew")

		self.pageSelector = PageSelector(self.root, self)
		self.pageSelector.grid(row=2, column=0, sticky="ns")
		self.show_page("Page1")
		self.test_button = tk.Button(self.root, text="Test Bouton", font=P2_FONT, command=self.on_button_click)
		self.test_button.grid(row=1, column=1, padx=10, pady=10, sticky="ne")

	def on_button_click(self):
		self.controller.on_button_click()

	def show_page(self, page_name: str):
		"""Affiche la page demandée."""
		frame = self.pages[page_name]
		frame.tkraise()






