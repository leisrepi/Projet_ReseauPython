import tkinter as tk
import BasicUtilies as bu
import DBHandler as db
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


#TODO : faire la documentation
# Fonction pour supprimer tous les widgets d'une ligne donnée
def supprimer_row(element,row_num):
    for widget in element.grid_slaves():  # Récupère tous les widgets gérés par grid
        info = widget.grid_info()
        if info["row"] == row_num:
            widget.grid_forget()  # ou widget.destroy() pour les supprimer définitivement

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

	#FIXME : correction scroll to widget
	def scroll_to_widget(self, widget, margin=5):
		"""Scroll le minimum nécessaire pour que le widget soit entièrement visible."""

		self.update_idletasks()

		# Position du widget dans le frame interne
		widget_top = widget.winfo_y()
		widget_bottom = widget_top + widget.winfo_height()

		# Zone visible actuelle dans les coords du frame interne
		visible_top = self.canvas.canvasy(0)
		viewport_height = self.canvas.winfo_height()
		visible_bottom = visible_top + viewport_height

		# Si déjà entièrement visible -> rien à faire
		if widget_top >= visible_bottom and widget_bottom <= visible_top:
			return

		# Calcul du nouveau top souhaité
		if widget_top < visible_bottom:
			# Trop haut -> on remonte juste assez pour coller le haut du widget en haut
			new_top = widget_top - margin
		elif widget_bottom > visible_top:
			# Trop bas -> on descend juste assez pour voir le bas du widget
			new_top = widget_bottom + margin - viewport_height
		else:
			return

		# Récupérer la scrollregion
		bbox = self.canvas.bbox("all")
		if not bbox:
			return

		region_top = bbox[1]
		region_bottom = bbox[3]
		total_height = region_bottom - region_top

		# Si tout tient dans la vue -> pas de scroll
		if total_height <= viewport_height:
			return

		# Clamp new_top dans les bornes réelles
		if new_top < region_top:
			new_top = region_top

		max_top = region_bottom - viewport_height
		if new_top > max_top:
			new_top = max_top

		# Conversion en fraction en tenant compte de region_top
		fraction = (new_top - region_top) / total_height
		if fraction < 0:
			fraction = 0
		elif fraction > 1:
			fraction = 1

		self.canvas.yview_moveto(fraction)




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
	
	
	#TODO : deplacer cela dans le controller
	def show_subnetting_result(self):
		#Verification des entrées utilisateur

		#verification adresse réseau et masque
		if self.controller.controller_verify_input_group1(self,self.nb_subnet.get(),self.network_entry.get(), self.mask_entry.get()) is None:
			return

		#verfication nb machines par sous reseau (si vide)
		if not self.controller.controller_verify_and_propose_correction_empty_machine_per_subnet_input(self):
			return
		#verfication nb machines par sous reseau (si valide)
		if not self._is_nb_machine_per_subnet_inputs_valid():
			return

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
	def change_nb_machines_inputs(self, nb_subnets, nb_subnets_voulu : int):
		#clean_tk_element(self.nb_machine_inputs_container.inner)
		if len(self.nb_machine_inputs) < nb_subnets: #plus petit, on dois en ajouter:
			for i in range(len(self.nb_machine_inputs), nb_subnets):
				tk.Label(self.nb_machine_inputs_container.inner, text=f"Nb machine sous-réseau ({i+1}):", font=P2_FONT).grid(row=i, column=0, padx=5, pady=5, sticky="e")
				entry = tk.Entry(self.nb_machine_inputs_container.inner, font=P2_FONT, width=20)
				entry.grid(row=i, column=1, padx=5, pady=5)
				entry.bind("<Return>", lambda event, widget=entry: self._nb_machine_input_apply_changes(widget))
				entry.bind("<FocusOut>", lambda event, widget=entry: self._verify_and_inform_every_nb_machine_per_subnet_input())
				if i >= nb_subnets_voulu:
					entry.insert(0,"0") 
				self.nb_machine_inputs.append(entry)
		else: #plus grand, on dois en retirer:
			for i in range(nb_subnets, len(self.nb_machine_inputs)):
				supprimer_row(self.nb_machine_inputs_container.inner, i)
				#self.nb_machine_inputs[i].destroy() #detruit l'element tk
			self.nb_machine_inputs = self.nb_machine_inputs[:nb_subnets] #retire les references
	
	def _apply_changes_from_inputs_of_group1(self):
		return self.controller.controller_create_number_of_subnets_input(
			self,self.nb_subnet.get(),
			self.network_entry.get(),
			self.mask_entry.get()
		)

	def _nb_machine_input_apply_changes(self, input_widget : tk.Widget):
		if self._verify_nb_machine_per_subnet(input_widget):
			self._focus_to_next_nb_machine_input(input_widget)
			self.nb_machine_inputs_container.scroll_to_widget(input_widget)
		else:
			input_widget.focus_set()
			input_widget.select_range(0, tk.END)
		self._verify_and_inform_every_nb_machine_per_subnet_input()
		

	def _is_nb_machine_per_subnet_inputs_valid(self) -> bool:
		for input_widget in self.nb_machine_inputs:
			if not self._verify_nb_machine_per_subnet(input_widget, message_on_error=True, travel_to_input=True):
				return False
		return True
	def _verify_and_inform_every_nb_machine_per_subnet_input(self):
		for input_widget in self.nb_machine_inputs:
			if not self._verify_nb_machine_per_subnet(input_widget, message_on_error=False):
				if input_widget.get() != "":
					#TODO: utiliser des couleurs plus douces
					input_widget.configure({"background": "red"})
				else:
					input_widget.configure({"background": "white"})
				#input_widget.delete(0,tk.END)
				#input_widget.insert(0,"")
			else:
				input_widget.configure({"background": "white"})


	#pour respecter le mvc, cela devrais etre dans le controller
	def _verify_nb_machine_per_subnet(self, input_widget, message_on_error : bool = True, travel_to_input : bool = False) -> bool:
		input_widget_value : int = bu.to_int(input_widget.get())
		if input_widget_value is None or input_widget_value < 0:
			if message_on_error:
				messagebox.showerror("Erreur", "Le nombre de machines par sous-réseau doit être un entier positif.")
				if travel_to_input:
					input_widget.focus_set()
					input_widget.select_range(0, tk.END)
					self.nb_machine_inputs_container.scroll_to_widget(input_widget)
			return False
		if input_widget_value > self.data['nb_max_machines_per_subnet']:
			if message_on_error:	
				messagebox.showerror("Erreur", f"Le nombre de machines par sous-réseau ne doit pas dépasser {self.data['nb_max_machines_per_subnet']}.")
				if travel_to_input:
					input_widget.focus_set()
					input_widget.select_range(0, tk.END)
					self.nb_machine_inputs_container.scroll_to_widget(input_widget)
			return False
		return True
	
	def _focus_to_next_nb_machine_input(self,input_widget):
		info = input_widget.grid_info()
		#info["row"]
		if info["row"] + 1 < len(self.nb_machine_inputs):
			self.nb_machine_inputs[info["row"]+1].focus_set()
    	
	def _show_save_and_load_window(self):
		PopupSaveAndLoad(self.controller.root, self.controller)

	def __init__(self , parent, controller : 'GUIController.GUIController'):

				
		super().__init__(parent, pady=10, width=controller.root.winfo_screenwidth())
		self.controller : 'GUIController.GUIController' = controller
		self.nb_machine_inputs : {tk.Widget} = []
		self.data = {}
		self.data['nb_subnets'] = 0
		self.data['nb_max_machines_per_subnet'] = 0
		self.data['nb_machines_per_subnet'] = []
		self.data['network'] = None
		self.data['mask'] = None
		# #--------------------------------------|Découpage en sous-réseaux|--------------------------------------
		# Bouton pour ouvrir la fenêtre de load and save les découpes 
		tk.Button(self, text="Sauvegarder ou charger une découpe", font=P2_FONT, command=self._show_save_and_load_window).grid(row=0, column=0, padx=5, pady=5, sticky="e")
		label = tk.Label(self, text="Découpe en sous-réseaux", font=H2_FONT).grid(row=0, column=1, padx=5, pady=5, sticky="e", columnspan=4)
		
		
		# #-----------------------------------------------------------------------------------------------
		# ============== Inputs groupe 1 ==================
		# Adresse réseau
		tk.Label(self, text="Adresse réseau:", font=P2_FONT).grid(row=1, column=0, padx=5, pady=5, sticky="e")
		self.network_entry = tk.Entry(self, font=P2_FONT, width=20)
		self.network_entry.bind("<Return>",lambda x : self._apply_changes_from_inputs_of_group1())
		self.network_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
		self.network_entry.insert(0,"192.168.1.0") #TODO retirer la valeur par defaut

		# Masque
		tk.Label(self, text="Masque:", font=P2_FONT).grid(row=2, column=0, padx=5, pady=5, sticky="e")
		self.mask_entry = tk.Entry(self, font=P2_FONT, width=20)
		self.mask_entry.bind("<Return>",lambda x : self._apply_changes_from_inputs_of_group1())
		self.mask_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
		self.mask_entry.insert(0,"/24") #TODO retirer la valeur par defaut
		
		

		# Nombre de sous-réseaux
		tk.Label(self, text="Nombre de sous-réseau:", font=P2_FONT).grid(row=3, column=0, padx=5, pady=5, sticky="e")
		self.nb_subnet = tk.Entry(self, font=P2_FONT, width=20)
		self.nb_subnet.bind("<Return>",lambda x : self._apply_changes_from_inputs_of_group1())
		self.nb_subnet.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="w")
		self.nb_subnet.insert(0,"16") #TODO retirer la valeur par defaut

		tk.Button(self, text="Valider", command=self._apply_changes_from_inputs_of_group1, font=P2_FONT, borderwidth=1, relief="solid").grid(row=3, column=3, padx=5, pady=5)
		
		#Affichage du nombre de sous-réseaux créés
		self.nb_subnets_label = tk.Label(self, text="Nombre de sous-réseaux créés: 0", font=P2_FONT)
		self.nb_subnets_label.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

		#Affichage du nombre maximum de machines par sous-réseaux
		self.nb_machines_per_subnet_label = tk.Label(self, text="Nombre maximum de machines par sous-réseaux: 0", font=P2_FONT)
		self.nb_machines_per_subnet_label.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

		# container des inputs dynamiques pour le nombre de machines par sous-réseaux
		self.nb_machine_inputs_container = ScrollableFrame(self)
		self.nb_machine_inputs_container.grid(row=6, column=0, columnspan=3, padx=5, pady=5)
		self.nb_machine_inputs_container.config(height=300,width=500)  # Hauteur fixe pour le conteneur scrollable
		

		tk.Button(self, text="Calculer la découpe", command=self.show_subnetting_result, font=P2_FONT, borderwidth=1, relief="solid").grid(row=7, column=0, columnspan=2, padx=5, pady=5)

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

class PopupSaveAndLoad(tk.Toplevel):

	def __init__(self, parent, controller):
		super().__init__(parent, pady=10)
		self.controller = controller
		self.title("Gestion des découpes")
		self.geometry("450x450")
		self.resizable(True, True)

		# Empêche d'interagir avec la fenêtre principale tant que la popup est ouverte
		self.grab_set()
		# Contenu de la popup
		#--------------------------------------
		# Nom de la découpe
		tk.Label(self, text="Nom de la découpe", font=P3_FONT).grid(row=0, column=0, pady=10)
		tk.Entry(self, font=P3_FONT).grid(row=0, column=1, pady=10)
		#--------------------------------------
		# Frame scrollable pour le contenu
		self.scrollable_frame = ScrollableFrame(self)
		self.scrollable_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
		tk.Button(self, text="💾", font=P2_FONT).grid(row=0, column=2, pady=10)

		# Chaque découpe sauvegardée sera affichée ici
		#TODO : remplacer par le contenu dynamique des découpes sauvegardées
		subnettings = db.get_all_subnettings_of_user(self.controller.session)
		for i in range(len(subnettings)):
			# subnettings[i][0] représente le nom de la découpe i
			tk.Label(self.scrollable_frame.inner, text=subnettings[i][0], font=P3_FONT).grid(row=i+1, column=0, pady=5)
			#lambda index=i --> afin que i soit sauvegardé en même temps que l'event (sinon i sera égal au dernier indice de la liste)
			tk.Button(self.scrollable_frame.inner, text="     🗑️", font=P3_FONT, command= lambda index=i: self.controller.controller_delete_subnetting(subnettings[index][0])).grid(row=i+1, column=1)

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
		self.root.geometry("1600x800")#str(self.root.winfo_screenwidth())+"x"+str(self.root.winfo_screenheight()))
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






