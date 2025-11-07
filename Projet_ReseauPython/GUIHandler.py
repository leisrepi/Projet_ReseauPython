import tkinter as tk
import BasicUtilies as bu
from tkinter import messagebox, ttk

from typing import TYPE_CHECKING #pour avoir la docu sans import du module a l'execution (car pas besoin et importation circulaire)
if TYPE_CHECKING:
	import GUIController

# Constantes de taille de police
H1_FONT = ("Arial", 24, "bold")
H2_FONT = ("Arial", 20, "bold")
H3_FONT = ("Arial", 16, "bold")
P_FONT = ("Arial", 16)
P2_FONT = ("Arial", 14)
P3_FONT = ("Arial", 12)


def clean_tk_element(element):
	"""Supprime tous les widgets enfants d'un widget Tkinter.

	Args:
		element: widget Tkinter (par exemple un tk.Frame) dont on veut vider les enfants.

	Returns:
		None

	Exemple:
		clean_tk_element(mon_frame)
	"""
	
	for w in element.winfo_children():
		w.destroy()

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


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # 1. Canvas + Scrollbar verticale
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.v_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # 2. Frame interne qui contiendra TON contenu
        self.inner = ttk.Frame(self.canvas)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        # 3. Ajuster automatiquement la zone scrollable quand le contenu change de taille
        self.inner.bind("<Configure>", self._on_frame_configure)

        # 4. Ajuster la largeur du frame interne quand le canvas change de taille (responsive)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # 5. Molette souris (Windows/Linux). Pour macOS on adapte un tout petit peu.
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)        # Windows / Linux
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)    # Linux old
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)    # Linux old

    def _on_frame_configure(self, event):
        # Met à jour la scrollregion = la zone totale scrollable
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # Force la largeur de inner à suivre la largeur visible du canvas (sinon ça fait une 2e scrollbar horizontale moche)
        canvas_width = event.width
        self.canvas.itemconfig(self.inner_id, width=canvas_width)

    def _on_mousewheel(self, event):
        # delta est négatif quand tu scrolles vers le bas
        # Sur Windows : event.delta est par pas de 120
        # Sur X11 récent : pareil mais parfois différent, on normalise un peu
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _on_mousewheel_linux(self, event):
        # Ancien bindings Linux (<Button-4>/<Button-5>)
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

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
	#TODO : verifier la validité des entrées utilisateur avant de lancer le calcul
	#TODO : bouton pour mettre les champs (non remplis) nb_machines a 0 (si on voulais 13 réseau, 16 serons crée )
	
	
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
	
	def verify_nb_subnet_inputs(self):
		
		nb : int = bu.to_int(self.nb_subnet.get())
		if nb is None or nb <= 0 or nb > 128:
			messagebox.showerror("Erreur", "Le nombre de sous-réseaux doit être positif et inférieur ou égal à 128.")
			return False
		return True

	def show_number_of_subnets(self, event):

		# On récupère le résultat du contrôleur
		#TODO : arrondir le nombre de subnet a l'exposant 2 le plus proche (haut)
		#TODO : verifier les entrers utilisateur
		if not self.verify_nb_subnet_inputs():
			return
		nb_reseau_voulu : int = int(self.nb_subnet.get())
		nb_reseau : int = 16 #TODO hardcoder pour les test
		nb_machines_max : int = int(self.controller.controller_machine_per_sub_nb(int(self.nb_subnet.get()), self.network_entry.get(), self.mask_entry.get()))
		response : bool = messagebox.askyesno("Nombre de machines par sous-réseaux", f"Nombre de machine par sous-réseaux calculés : {nb_machines_max}")
		if response:
			print("user said yes")
			self.change_nb_machines_inputs(nb_reseau,nb_reseau_voulu)
			pass
		#nb_subnets = len(result)
		#self.nb_subnet.delete(0, tk.END)
		#self.nb_subnet.insert(0, str(nb_subnets))
	def change_nb_machines_inputs(self, nb_subnets, nb_subnets_voulu):
		clean_tk_element(self.nb_machine_inputs_container.inner)
		self.nb_machine_inputs = []
		for i in range(nb_subnets):
			tk.Label(self.nb_machine_inputs_container.inner, text=f"Nb machine sous-réseau ({i+1}):", font=P2_FONT).grid(row=i, column=0, padx=5, pady=5, sticky="e")
			entry = tk.Entry(self.nb_machine_inputs_container.inner, font=P2_FONT, width=20)
			entry.grid(row=i, column=1, padx=5, pady=5)
			if i >= nb_subnets_voulu:
				entry.insert(0,"0") #TODO retirer la valeur par defaut
			self.nb_machine_inputs.append(entry)
		pass
			
	def __init__(self , parent, controller : 'GUIController.GUIController'):

				
		super().__init__(parent, pady=10, width=controller.root.winfo_screenwidth())
		self.controller : 'GUIController.GUIController' = controller
		# #--------------------------------------|Découpage en sous-réseaux|--------------------------------------
		label = tk.Label(self, text="Découpe en sous-réseaux", font=H2_FONT).grid(row=0, column=0, padx=5, pady=5, sticky="e", columnspan=5)
		
		
		# #-----------------------------------------------------------------------------------------------
		# Adresse réseau
		tk.Label(self, text="Adresse réseau:", font=P2_FONT).grid(row=1, column=0, padx=5, pady=5, sticky="e")
		self.network_entry = tk.Entry(self, font=P2_FONT, width=20)
		self.network_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
		self.network_entry.insert(0,"192.168.1.0") #TODO retirer la valeur par defaut

		# Masque
		tk.Label(self, text="Masque:", font=P2_FONT).grid(row=2, column=0, padx=5, pady=5, sticky="e")
		self.mask_entry = tk.Entry(self, font=P2_FONT, width=20)
		self.mask_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
		self.mask_entry.insert(0,"/24") #TODO retirer la valeur par defaut
		
		

		# Nombre de sous-réseaux
		tk.Label(self, text="Nombre de sous-réseau:", font=P2_FONT).grid(row=3, column=0, padx=5, pady=5, sticky="e")
		self.nb_subnet = tk.Entry(self, font=P2_FONT, width=20)
		self.nb_subnet.bind("<Return>",lambda x : self.controller.controller_create_number_of_subnets_input(self,self.nb_subnet.get(),self.network_entry.get(),self.mask_entry.get()))# .show_number_of_subnets)
		self.nb_subnet.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="w")
		self.nb_subnet.insert(0,"16") #TODO retirer la valeur par defaut

		tk.Button(self, text="Calculer la découpe", command=self.show_subnetting_result, font=P2_FONT, borderwidth=1, relief="solid").grid(row=4, column=0, padx=5, pady=5)

		# container des inputs dynamiques pour le nombre de machines par sous-réseaux
		self.nb_machine_inputs_container = ScrollableFrame(self)
		self.nb_machine_inputs_container.grid(row=5, column=0, columnspan=3, padx=5, pady=5)
		self.nb_machine_inputs_container.config(height=300,width=500)  # Hauteur fixe pour le conteneur scrollable
		#self.nb_machine_inputs_container.grid_propagate(False)

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






