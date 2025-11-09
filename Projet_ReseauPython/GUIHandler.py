import tkinter as tk
from tkinter import messagebox, ttk
from AppException import InvalidMaskException, MaskNotInRangeException
from ipaddress import AddressValueError
import NetworkHandler as nh
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

		#TODO retirer ce debug (valeur de connection par defaut)
		self.pseudonyme_entry.insert(0,"test")
		self.password_entry.insert(0,"test")

		self.validate_information = tk.Button(self.root, text="Se connecter", font=H3_FONT, command=self.on_login)
		
		self.validate_information.pack(pady=20)

	def change_login_button(self, state):
		self.validate_information.config(state=state)

	def on_login(self):
		pseudonyme = self.pseudonyme_entry.get()
		password = self.password_entry.get()
		self.controller.on_login(pseudonyme, password)



class Page1(tk.Frame):
	def show_address_info(self):
		self.network_label.config(text="")
		self.network_broadcast_label.config(text="")
		self.subnetwork_label.config(text="")
		self.subnetwork_broadcast_label.config(text="")

		try:
			network_addr, network_broadcast, subnet_addr, subnet_broadcast = self.controller.controller_get_address_info(self.ip_entry.get(), self.mask_entry.get())
		except InvalidMaskException as e:
			messagebox.showerror("Erreur", str(e))
			return
		except AddressValueError as e:
			messagebox.showerror("Erreur", str(e))
			return
		except MaskNotInRangeException as e:
			messagebox.showerror("Erreur", str(e))
			return
		
		self.network_label.config(text=str(network_addr))
		self.network_broadcast_label.config(text=str(network_broadcast))
		if(subnet_addr is None and subnet_broadcast is None):
			return
		self.subnetwork_label.config(text=str(subnet_addr))
		self.subnetwork_broadcast_label.config(text=str(subnet_broadcast))
	
	def __init__(self, parent, controller):
		super().__init__(parent, pady=10)
		self.controller = controller
		label = tk.Label(self, text="Informations d'une adresse", font=H2_FONT)
		label.grid(row=0, column=0, columnspan=2 , padx=5, pady=5)

		#--------------------------------------
		# Adresse IP
		tk.Label(self, text="Adresse IP:", font=P2_FONT).grid(row=1, column=0, padx=5, pady=5, sticky="e")
		self.ip_entry = tk.Entry(self, font=P2_FONT, width=20)
		self.ip_entry.grid(row=1, column=1, padx=5, pady=5)
		
		# Masque
		tk.Label(self, text="Masque:", font=P2_FONT).grid(row=1, column=2, padx=5, pady=5, sticky="e")
		self.mask_entry = tk.Entry(self, font=P2_FONT, width=20)
		self.mask_entry.grid(row=1, column=3, padx=5, pady=5)

		tk.Button(self, text="Obtenir les informations de l'adresse", command=self.show_address_info, font=P2_FONT, borderwidth=1, relief="solid").grid(row=1, column=4, padx=5, pady=5)
		#--------------------------------------
		# Résultats

		# Address du réseau
		tk.Label(self, text="Adresse du réseau:", font=P2_FONT).grid(row=2, column=0, padx=5, pady=5, sticky="e")
		self.network_label = tk.Label(self, font=P2_FONT, width=20)
		self.network_label.grid(row=2, column=1, padx=5, pady=5)

		# Adresse du sous-réseau
		tk.Label(self, text="Adresse du sous-réseau:", font=P2_FONT).grid(row=2, column=2, padx=5, pady=5, sticky="e")
		self.subnetwork_label = tk.Label(self, font=P2_FONT, width=20)
		self.subnetwork_label.grid(row=2, column=3, padx=5, pady=5)

		# Broadcast du réseau
		tk.Label(self, text="Broadcast du réseau:", font=P2_FONT).grid(row=3, column=0, padx=5, pady=5, sticky="e")
		self.network_broadcast_label = tk.Label(self, font=P2_FONT, width=20)
		self.network_broadcast_label.grid(row=3, column=1, padx=5, pady=5)

		# Broadcast du sous-réseau
		tk.Label(self, text="Broadcast du sous-réseau:", font=P2_FONT).grid(row=3, column=2, padx=5, pady=5, sticky="e")
		self.subnetwork_broadcast_label = tk.Label(self, font=P2_FONT, width=20)
		self.subnetwork_broadcast_label.grid(row=3, column=3, padx=5, pady=5)


		
class Page2(tk.Frame):
	def effacer(self):
		self.ip_var.set("")
		self.reseau_var.set("")
		self.masque_var.set("")
		self._set_status("", ok=None)
		self._set_details("")
    
	def _set_status(self, text, ok: bool | None):
		#Couleurs simples selon état
		if ok is True:
			fg = "#0a7d2b"  # vert
		elif ok is False:
			fg = "#b00020" #Rouge
		else:
			fg = ""
		self.result_appartenance.configure(text=text, foreground=fg)

	def _set_details(self, text):
		self.result_details.configure(state="normal")
		self.result_details.delete("1.0","end")
		self.result_details.insert("1.0",text)
		self.result_details.configure(state="disabled")

	def show_ip_checking_results(self):
		try:
			nh.check_ip_network(self)
		except AddressValueError as e:
			messagebox.showerror("Erreur", str(e))
		except InvalidMaskException as e:
			messagebox.showerror("Erreur", str(e))
		except MaskNotInRangeException as e:
			messagebox.showerror("Erreur", str(e))
		
	def __init__(self, parent, controller):
		super().__init__(parent, pady=10)
		self.controller = controller
		label = tk.Label(self, text="Page 2", font=H2_FONT)
		label.pack(pady=10, padx=10)

		#Styles
		style = ttk.Style(self)
		# try:
        #     style.theme_use("clam")
        # except Exception:
        #     pass

		pad = {'padx' : 8, 'pady' : 6}
	
		frame = ttk.Frame(self)
		frame.pack(fill="both", expand=True, padx=12, pady=12)

		#Entrées
		ttk.Label(frame, text="Adresse IP à vérifier :").grid(row=0, column=0, stick="w", **pad)
		self.ip_var = tk.StringVar()
		ttk.Entry(frame, textvariable=self.ip_var, width=28).grid(row=0, column=1, sticky="we", **pad)

		ttk.Label(frame, text="Réseau ou sous-réseau :").grid(row=1, column=0, sticky="w", **pad)
		self.reseau_var = tk.StringVar()
		ttk.Entry(frame, textvariable=self.reseau_var, width=28).grid(row=1, column=1, sticky="we", **pad)
		ttk.Label(frame, text="ex: 192.168.3.0 ou 192.168.3.0/26").grid(row=1,column=2, sticky="we",**pad)
		
		ttk.Label(frame, text="Masque (optionnel si CIDR) :").grid(row=2, column=0, **pad)
		self.masque_var = tk.StringVar()
		ttk.Entry(frame, textvariable=self.masque_var, width=28).grid(row=2, column=1, **pad)
		ttk.Label(frame, text="ex: 255.255.255.192 ou /26").grid(row=2,column=2,sticky="w")

		#Boutons
		btns = ttk.Frame(frame)
		btns.grid(row=3, column=0, columnspan=3, sticky="we",**pad)
		ttk.Button(btns, text="Vérifier", command=self.show_ip_checking_results).pack(side="left", padx=4)
		ttk.Button(btns, text="Effacer", command=self.effacer).pack(side="left",padx=4)

		#Résultats
		sep = ttk.Separator(frame)
		sep.grid(row=4, column=0, columnspan=3, sticky="we", pady=(10,6))

		self.result_appartenance = ttk.Label(frame, text="",font=("TkDefaultFont",11,"bold"))
		self.result_appartenance.grid(row=5, column=0, columnspan=3, sticky="w", **pad)

		self.result_details = tk.Text(frame, height=9, width=72, wrap="word")
		self.result_details.grid(row=6, column=0, columnspan=3, sticky="nsew", **pad)
		self.result_details.configure(state="disabled")

		#Grille responsive
		frame.columnconfigure(1, weight=1)
		frame.rowconfigure(6, weight=1)

class Page3(tk.Frame):
	def add_to_combobox(self):
			if(self.list_machines_entry.get() == ""):
				messagebox.showwarning("Attention", "Veuillez entrer un nombre de machines avant d'ajouter.")
				return

			if((not self.list_machines_entry.get().isnumeric())):
				messagebox.showwarning("Attention", "Veuillez entrer un nombre valide.")
				return
			
			if(int(self.list_machines_entry.get()) < 2):
				messagebox.showwarning("Attention", "Le nombre de machines doit être au moins de 2.")
				return
			
			current_values = list(self.list_machines_combobox['values'])
			if(self.list_machines_combobox.get() == ""):
				self.list_machines_combobox['values'] = current_values + [self.list_machines_entry.get()]
			else:
				print("Il est écrit : ", self.list_machines_combobox.get())
			self.list_machines_entry.delete(0, tk.END)

	def remove_of_combobox(self):
		# current est l'index de l'élément sélectionné
		# le premier élément est une chaîne vide lorsqu'aucun élément n'est sélectionné
		if self.list_machines_combobox.current() == 0:
			return
		combobox_list = list(self.list_machines_combobox['values'])
		combobox_list.pop(self.list_machines_combobox.current())
		self.list_machines_combobox['values'] = combobox_list
		print("Valeur supprimée : ", self.list_machines_combobox.get())
		print("Index supprimé : ", self.list_machines_combobox.current())
		self.list_machines_combobox.set("")

	# Choix entre nombre de machines ou nombre de sous-réseaux pour la découpe
	def choose_subnetting_method(self):
		if(self.subnetting_choice.get() == "1"):
			self.nb_machines_subnet.config(state="normal")
			self.nb_subnet.delete(0, tk.END)
			self.nb_subnet.config(state="disabled")
		else:
			self.nb_subnet.config(state="normal")
			self.nb_machines_subnet.delete(0, tk.END)
			self.nb_machines_subnet.config(state="disabled")
	
	def show_subnetting_result(self):

		# On vide le tableau avant d'afficher les nouveaux résultats
		self.tree.delete(*self.tree.get_children())
		
		# On récupère le résultat du contrôleur
		result, step, nb_machines_max = self.controller.controller_subnetting_calculation(self)
		print("Resultat de la découpe : ", result)
		self.total_nb_machines.config(text=str(nb_machines_max))
		self.step.config(text=step)
		# On remplit le tableau avec le résultat
		i = 0
		for ligne in result:
			ligne.insert(0, str(i+1))  # Ajout du numéro de sous-réseau au début de la ligne
			if(i % 2 == 0):
				self.tree.insert('', 'end', values=ligne, tags=("evenrow",))
			else:
				self.tree.insert('', 'end', values=ligne)
			i += 1
		
			
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
		self.network_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

		# Masque
		tk.Label(self, text="Masque:", font=P2_FONT).grid(row=2, column=0, padx=5, pady=5, sticky="e")
		self.mask_entry = tk.Entry(self, font=P2_FONT, width=20)
		self.mask_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
		
		# Liste des machines du sous-réseau
		tk.Label(self, text="Liste des machines du sous-réseau:", font=P2_FONT).grid(row=3, column=0, padx=5, pady=5, sticky="e")
		self.list_machines_entry = tk.Entry(self, font=P2_FONT, width=5)
		self.list_machines_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

		# Liste déroulante des nombres de machines
		self.list_machines_combobox = ttk.Combobox(self, values=[""], font=P2_FONT, width=5, state="readonly")
		self.list_machines_combobox.grid(row=3, column=2, padx=5, pady=5, sticky="w")

		tk.Button(self, text="ajouter", command=self.add_to_combobox, borderwidth=1, relief="solid").grid(row=4, column=1, padx=5, pady=5, sticky="w")
		tk.Button(self, text="supprimer", command=self.remove_of_combobox, borderwidth=1, relief="solid").grid(row=4, column=2, padx=5, pady=5, sticky="w")

		# Choix entre nombre de machines ou nombre de sous-réseaux
		self.subnetting_choice = tk.StringVar(value="1")
		tk.Radiobutton(self, text = "Nb machines", variable=self.subnetting_choice, value = "1", command=self.choose_subnetting_method).grid(row=5, column=1, padx=5, pady=5, sticky="e")
		tk.Radiobutton(self, text = "Nb sous-réseaux", variable=self.subnetting_choice, value = "2", command=self.choose_subnetting_method).grid(row=5, column=2, padx=5, pady=5, sticky="e")

		# Nombre machines par sous-réseau
		tk.Label(self, text="Nombre machines maximum des sous-réseau:", font=P2_FONT).grid(row=6, column=0, padx=5, pady=5, sticky="e")
		self.nb_machines_subnet = tk.Entry(self, font=P2_FONT, width=20)
		self.nb_machines_subnet.grid(row=6, column=1, columnspan=2, padx=5, pady=5, sticky="w")

		# Nombre de sous-réseaux
		tk.Label(self, text="Nombre de sous-réseau:", font=P2_FONT).grid(row=7, column=0, padx=5, pady=5, sticky="e")
		self.nb_subnet = tk.Entry(self, font=P2_FONT, width=20, state="disabled")
		self.nb_subnet.grid(row=7, column=1, columnspan=2, padx=5, pady=5, sticky="w")

		tk.Button(self, text="Calculer la découpe", command=self.show_subnetting_result, font=P2_FONT, borderwidth=1, relief="solid").grid(row=8, column=0, padx=5, pady=5)

		#-----------------------------------------------------------------------------------------------

		# Pas
		tk.Label(self, text="Pas:", font=P2_FONT).grid(row=1, column=4, padx=5, pady=5, sticky="e")
		self.step = tk.Label(self, font=P2_FONT, width=20, anchor="w")
		self.step.grid(row=1, column=5, padx=5, pady=5, sticky="w")

		# Nombre de machines total du réseau
		tk.Label(self, text="Nombre de machines total du réseau:", font=P2_FONT).grid(row=2, column=4, padx=5, pady=5, sticky="e")
		self.total_nb_machines = tk.Label(self, font=P2_FONT, width=20, anchor="w")
		self.total_nb_machines.grid(row=2, column=5, padx=5, pady=5, sticky="w")

		#-----------------------------------------------------------------------------------------------

		# Tableau des sous-réseaux
		colonnes = ["N°","Adresse de sous-réseau", "Adresse de broadcast", "Première IP", "Dernière IP"]
		self.tree = ttk.Treeview(self, columns=colonnes, show='headings')
		self.tree.grid(row=3, column=4, rowspan=4, columnspan=2, padx=5, pady=5)

		self.tree.tag_configure("evenrow", background="lightblue")

		self.tree.heading("N°", text="N°", anchor='center')
		self.tree.column("N°", width=50, anchor='center')
		for col in colonnes:
			if col == "N°":
				continue
			self.tree.heading(col, text=col)
			self.tree.column(col, anchor='center')



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
			frame = PageClass(container, self.controller)
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






