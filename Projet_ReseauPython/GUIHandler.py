import tkinter as tk
import BasicUtilies as bu
from tkinter import messagebox, ttk
from AppException import InvalidMaskException, MaskNotInRangeException
from ipaddress import AddressValueError
import NetworkHandler as nh
import sqlite3
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


def supprimer_row(element,row_num):
    """ Fonction pour supprimer tous les widgets d'une ligne donnée
    Args:
        element: widget Tkinter (par exemple un tk.Frame) dont on veut vider les enfants.
        row_num : numéro du row

    Returns:
        None

    """
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
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, event=None):
        # Option 1 (robuste) : bind_all tant que la souris est au-dessus
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)      # Windows/macOS
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)  # Linux ancien
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)  # Linux ancien

    def _unbind_mousewheel(self, event=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

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
        label = tk.Label(self, text="Informations d'une adresse IP", font=H2_FONT)
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

        tk.Button(self, text="Obtenir les informations de l'adresse IP", command=self.show_address_info, font=P2_FONT, borderwidth=1, relief="solid").grid(row=1, column=4, padx=5, pady=5)
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
        label = tk.Label(self, text="Appartenance d'une IP à un réseau", font=H2_FONT)
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
        ttk.Entry(frame, textvariable=self.ip_var, width=16).grid(row=0, column=1, sticky="we", **pad)

        ttk.Label(frame, text="Réseau ou sous-réseau :").grid(row=1, column=0, sticky="w", **pad)
        self.reseau_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.reseau_var, width=16).grid(row=1, column=1, sticky="we", **pad)
        ttk.Label(frame, text="ex: 192.168.3.0 ou 192.168.3.0/26").grid(row=1,column=2, sticky="we",**pad)
        
        ttk.Label(frame, text="Masque (optionnel si classfull) :").grid(row=2, column=0, **pad)
        self.masque_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.masque_var, width=16).grid(row=2, column=1, **pad)
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
    def show_subnetting_result(self):
        #Verification des entrées utilisateur

        #verification adresse réseau et masque
        if self.controller.controller_verify_input_group1(self,self.nb_subnet.get(),self.network_entry.get(), self.mask_entry.get()) is None:
            return False

        #verfication nb machines par sous reseau (si vide)
        if not self.controller.controller_verify_and_propose_correction_empty_machine_per_subnet_input(self):
            return False
        #verfication nb machines par sous reseau (si valide)
        if not self._is_nb_machine_per_subnet_inputs_valid():
            return False

        # On vide le tableau avant d'afficher les nouveaux résultats
        self.tree.delete(*self.tree.get_children())
        
        # On récupère le résultat du contrôleur
        result, step, nb_machines_max = self.controller.controller_subnetting_calculation(self)
        self.total_nb_machines.config(
            text=str(int(self.nb_subnet.get()) * self.controller.subnetting_data.nb_max_machines_per_subnet)
        )
        self.step.config(text=step)
        # On remplit le tableau avec le résultat
        i = 0
        for ligne in result:
            ligne.insert(0, str(self.nb_machine_inputs[i].get()))  # Ajout du pas au début de la ligne
            ligne.insert(0, str(i+1))  # Ajout du numéro de sous-réseau au début de la ligne
            if(i % 2 == 0):
                self.tree.insert('', 'end', values=ligne, tags=("evenrow",))
            else:
                self.tree.insert('', 'end', values=ligne)
            i += 1
    
    
    def show_number_of_subnets(self, event):

        nb_reseau_voulu = self.controller.validate_nb_subnets(self.nb_subnet.get())
        if nb_reseau_voulu is None:
            return
        nb_machines_max: int = int(
            self.controller.controller_machine_per_sub_nb(
                int(self.nb_subnet.get()), self.network_entry.get(), self.mask_entry.get()
            )
        )
        response: bool = messagebox.askyesno(
            "Nombre de machines par sous-réseaux", f"Nombre de machine par sous-réseaux calculés : {nb_machines_max}"
        )
        if response:
            self.change_nb_machines_inputs(nb_reseau_voulu)
            pass
        #nb_subnets = len(result)
        #self.nb_subnet.delete(0, tk.END)
        #self.nb_subnet.insert(0, str(nb_subnets))
    def change_nb_machines_inputs(self, nb_subnets : int):
        #clean_tk_element(self.nb_machine_inputs_container.inner)
        self.subnetting_data.ensure_machine_slots(nb_subnets)
        if len(self.nb_machine_inputs) < nb_subnets: #plus petit, on dois en ajouter:
            for i in range(len(self.nb_machine_inputs), nb_subnets):
                tk.Label(self.nb_machine_inputs_container.inner, text=f"Nb machine sous-réseau ({i+1}):", font=P2_FONT).grid(row=i, column=0, padx=5, pady=5, sticky="e")
                entry = tk.Entry(self.nb_machine_inputs_container.inner, font=P2_FONT, width=8)
                entry.grid(row=i, column=1, padx=5, pady=5)
                entry.bind("<Return>", lambda event, widget=entry: self._nb_machine_input_apply_changes(widget))
                entry.bind("<FocusOut>", lambda event, widget=entry: self._verify_and_inform_every_nb_machine_per_subnet_input())
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
                    input_widget.configure({"background": "light coral"})
                else:
                    input_widget.configure({"background": "white"})
                #input_widget.delete(0,tk.END)
                #input_widget.insert(0,"")
            else:
                input_widget.configure({"background": "white"})


    def _verify_nb_machine_per_subnet(self, input_widget, message_on_error : bool = True, travel_to_input : bool = False) -> bool:
        validated_value = self.controller.validate_machine_per_subnet(input_widget.get())
        if validated_value is None:
            if message_on_error and travel_to_input:
                input_widget.focus_set()
                input_widget.select_range(0, tk.END)
                self.nb_machine_inputs_container.scroll_to_widget(input_widget)
            return False

        input_widget.delete(0, tk.END)
        input_widget.insert(0, validated_value)
        return True
    
    def _focus_to_next_nb_machine_input(self,input_widget):
        info = input_widget.grid_info()
        #info["row"]
        if info["row"] + 1 < len(self.nb_machine_inputs):
            self.nb_machine_inputs[info["row"]+1].focus_set()
        
    def show_save_and_load_window(self):
        PopupSaveAndLoad(self.controller.root, self.controller, self)

    def __init__(self , parent, controller : 'GUIController.GUIController'):

                
        super().__init__(parent, pady=10, width=controller.root.winfo_screenwidth())
        self.controller : 'GUIController.GUIController' = controller
        self.nb_machine_inputs : {tk.Widget} = []
        self.subnetting_data = controller.subnetting_data
        # #--------------------------------------|Découpage en sous-réseaux|--------------------------------------
        # Bouton pour ouvrir la fenêtre de load and save les découpes 
        tk.Button(self, text="Gestion découpe réseau", font=P2_FONT, command=self.show_save_and_load_window).grid(row=0, column=0, padx=5, pady=5, sticky="e")
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
        tk.Label(self, text="Nombre de sous-réseaux:", font=P2_FONT).grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.nb_subnet = tk.Entry(self, font=P2_FONT, width=20)
        self.nb_subnet.bind("<Return>",lambda x : self._apply_changes_from_inputs_of_group1())
        self.nb_subnet.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        self.nb_subnet.insert(0,"16") #TODO retirer la valeur par defaut

        tk.Button(self, text="Valider", command=self._apply_changes_from_inputs_of_group1, font=P2_FONT, borderwidth=1, relief="solid").grid(row=3, column=3, padx=5, pady=5, sticky="w")
        
        #Affichage du nombre de sous-réseaux créés
        self.nb_subnets_label = tk.Label(self, text="Nombre de sous-réseaux créés: 0", font=P2_FONT)
        self.nb_subnets_label.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        #Affichage du nombre maximum de machines par sous-réseaux
        self.nb_machines_per_subnet_label = tk.Label(self, text="Nombre maximum de machines par sous-réseaux: 0", font=P2_FONT)
        self.nb_machines_per_subnet_label.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        # container des inputs dynamiques pour le nombre de machines par sous-réseaux
        self.nb_machine_inputs_container = ScrollableFrame(self)
        self.nb_machine_inputs_container.grid(row=6, rowspan=3, column=0, columnspan=3, padx=5, pady=5)
        self.nb_machine_inputs_container.config(height=300,width=500)  # Hauteur fixe pour le conteneur scrollable
        

        tk.Button(self, text="Calculer la découpe", command=self.show_subnetting_result, font=P2_FONT, borderwidth=1, relief="solid").grid(row=8, column=3, columnspan=3, padx=5, pady=5)
        
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
        colonnes = ["N°","Nb machines","Adresse de sous-réseau", "Adresse de broadcast", "Première IP", "Dernière IP"]
        self.tree = ttk.Treeview(self, columns=colonnes, show='headings')
        self.tree.grid(row=4, column=3, rowspan=4, columnspan=3, padx=5, pady=5)

        self.tree.tag_configure("evenrow", background="lightblue")

        self.tree.heading("N°", text="N°", anchor='center')
        self.tree.column("N°", width=50, anchor='center')
        self.tree.column("Nb machines", width=80, anchor='center')
        for col in colonnes:
            if col == "N°":
                continue
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center')

class PopupSaveAndLoad(tk.Toplevel):

    def save_subnetting_data(self, page3, subnetting_name):
        if(subnetting_name==""):
            messagebox.showerror("Erreur", "Veuillez entrer un nom de découpe")
            return
        try:
            self.controller.controller_save_subnetting_data(page3, subnetting_name)
        # Fenêtre pour demander à l'utilisateur s'il veut écraser la découpe déjà existante
        except sqlite3.IntegrityError:
            popup = tk.Toplevel(self, )
            tk.Label(popup, text="La découpe existe déjà, voulez-vous l'écraser ?", font=P3_FONT).grid(row=0, column=0, pady=10, columnspan=2)
            tk.Button(popup, text="Oui", font=P2_FONT, command=lambda : self.overwrite_subnetting_data(page3, subnetting_name)).grid(row=1, column=0, pady=10)
            tk.Button(popup, text="Non", font=P2_FONT, command=popup.destroy).grid(row=1, column=1, pady=10)

        self.update_subnettings_in_popup(page3)

    def load_subnetting_data(self, page3, subnetting):
        self.controller.controller_load_subnetting_data(page3, subnetting)
        self.destroy()

    def delete_subnetting(self, page3, subnetting_name):
        try:
            self.controller.controller_delete_subnetting(subnetting_name)
        except Exception:
            messagebox.showerror("Erreur", "Quelque chose c'est mal passé lors de la suppression de la découpe")
    
        self.update_subnettings_in_popup(page3)

    def overwrite_subnetting_data(self, page3, subnetting_name):
        self.controller.controller_delete_subnetting(subnetting_name)

        self.controller.controller_save_subnetting_data(page3, subnetting_name)

    def update_subnettings_in_popup(self, page3):

        for widget in self.scrollable_frame.inner.winfo_children():
            widget.destroy()
        # Chaque découpe sauvegardée sera affichée ici
        self.subnettings = self.controller.controller_list_user_subnettings()
        if self.subnettings is None:
            return
    
        for i in range(len(self.subnettings)):
            # subnettings[i][0] représente le nom de la découpe i
            tk.Label(self.scrollable_frame.inner, text=self.subnettings[i][0], font=P3_FONT).grid(row=i+1, column=0, pady=5)
            #lambda index=i --> afin que i soit sauvegardé en même temps que l'event (sinon i sera égal au dernier indice de la liste)
            tk.Button(self.scrollable_frame.inner, text="📂", font=P3_FONT, command= lambda index=i: self.load_subnetting_data(page3, self.subnettings[index])).grid(row=i+1, column=1)
            tk.Button(self.scrollable_frame.inner, text="     🗑️", font=P3_FONT, command= lambda index=i: self.delete_subnetting(page3, self.subnettings[index][0])).grid(row=i+1, column=2)
        
    def __init__(self, parent, controller  : 'GUIController.GUIController', page3):
        super().__init__(parent, pady=10)
        self.controller = controller
        self.title("Gestion des découpes")
        self.geometry("750x750")
        self.resizable(True, True)

        # Empêche d'interagir avec la fenêtre principale tant que la popup est ouverte
        self.grab_set()
        # Contenu de la popup
        #--------------------------------------
        # Nom de la découpe
        tk.Label(self, text="Nom de la découpe", font=P3_FONT).grid(row=0, column=0, pady=10)
        subnetting_entry = tk.Entry(self, font=P3_FONT)
        subnetting_entry.grid(row=0, column=1, pady=10)
        tk.Button(self, text="💾", font=P2_FONT, command=lambda : self.save_subnetting_data(page3, subnetting_entry.get())).grid(row=0, column=2, pady=10)
        #--------------------------------------
        # Frame scrollable pour le contenu
        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        
        self.update_subnettings_in_popup(page3)



class PageSelector(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padx=10, pady=10)
        self.controller = controller
        self.rowconfigure(3, weight=1)
        tk.Label(self, text="Sélecteur de page", font=H2_FONT).pack(side="left",pady=10)

        tk.Button(self, text="Informations d'une adresse IP", font=P2_FONT,
                  command=lambda: controller.show_page("Page1")).pack(side="left",pady=5)
        tk.Button(self, text="Appartenance d'une IP à un réseau", font=P2_FONT,
                  command=lambda: controller.show_page("Page2")).pack(side="left",pady=5)    
        tk.Button(self, text="Découpe en sous-réseaux", font=P2_FONT,
                  command=lambda: controller.show_page("Page3")).pack(side="left",pady=5)    

class MainApp:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root
        self.root.title("Subnet Maker")
        #self.root.grid_rowconfigure(0, weight=5)
        #self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=5)
        self.root.grid_columnconfigure(0, weight=5)
        #self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(4, weight=5)
        # Récupérer la taille de l'écran
        screen_width = 1450 #self.root.winfo_screenwidth()
        screen_height = 700 #self.root.winfo_screenheight()
        # Définir la taille de la fenêtre
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        header_frame = tk.Frame(self.root)
        header_frame.grid(row=1, column=1, columnspan=2, sticky="ew")
        tk.Label(header_frame, text="Bienvenue dans Subnet Maker", font=H2_FONT).pack(pady=20)

        # Creation du systeme de page:
        # --- Conteneur des pages ---
        container = tk.Frame(self.root)
        container.grid(row=2, column=1, sticky="nsew", padx=20, pady=20)
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
        self.pageSelector.grid(row=3, column=1, sticky="ns")
        self.show_page("Page1")

    def on_button_click(self):
        self.controller.on_button_click()

    def show_page(self, page_name: str):
        """Affiche la page demandée."""
        frame = self.pages[page_name]
        frame.tkraise()






