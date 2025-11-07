import tkinter as tk
import GUIHandler
import AuthHandler
import DBHandler  
import time
import threading
#TODO : importer le import au complet vue que on ce sert de toutes les fonctions
import AppException
from SubnetHandler import calculate_subnetting, calculate_step, calculate_nb_machines_max
import SubnetHandler
import AddressHandler
from NetworkHandler import create_network
from ipaddress import NetmaskValueError, AddressValueError
import NetworkHandler

import BasicUtilies as bu
import tkinter.messagebox as msg

from typing import TYPE_CHECKING #pour avoir la docu sans import du module a l'execution (car pas besoin et importation circulaire)
if TYPE_CHECKING:
	import GUIHandler

class GUIController:
    _controller = None
    _event = []
    def __new__(cls):
        raise RuntimeError("Use get_instance() to get the singleton instance.")

    @classmethod
    def get_instance(cls):
        if cls._controller is None:
            cls._controller = super().__new__(cls)
            cls._controller.__init__()
        return cls._controller

    def __init__(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("NO_NAME_SET")
        self.view = GUIHandler.LoginMenu(self)
        self.session = None
        self.run()
    
    def set_cursor_loading(self):
        GUIController.get_instance().root.configure(cursor="wait")
    def set_cursor_default(self):
        GUIController.get_instance().root.configure(cursor="")

    def on_button_click(self):
        print(self)
        print("Bouton cliqué depuis le contrôleur !")
        if (AuthHandler.verify_session(self.session)):
            print("Session valide.")
        else:
            print("Session expirée, veuillez vous reconnecter.")
            self.disconnect()

    def on_login(self, pseudonyme, password):
        #XXX RETIRER CE DEBUG !!!!!!
        print(f"Login avec Email: {pseudonyme}, Mot de passe: {password}")

        #XXX : verifier si les identifiants sont corrects avant d'ouvrir la fenetre principale
        
        self.set_cursor_loading()
        self.view.change_login_button(tk.DISABLED)
        
        is_verification_done = tk.BooleanVar(self.root, value=False)
        #FIXME : refaire cela au propre
        box = {"result": None, "error": None}
        def worker():
            try:
                box["result"] = AuthHandler.create_session(pseudonyme, password=password)
            except Exception as e:
                box["error"] = e
            finally:
                # réveiller le wait_variable dans le thread UI
                self.root.after(0, lambda: is_verification_done.set(True))

        threading.Thread(target=worker, daemon=True).start()
        self.root.wait_variable(is_verification_done) #attente que le thread est fini, mais fonction propre a tk qui ne va pas freeze le reste de l'appli
        if box["error"] is not None:
            print(box["error"])
            return
        self.session = box["result"]

        self.set_cursor_default()
        self.view.change_login_button(tk.ACTIVE)
        print("session créée : ", self.session)
        if self.session != None and AuthHandler.verify_session(self.session):
            print("Login réussi !")
            self.clean_view()
            self.view = GUIHandler.MainApp(self)
            # self.root.bind_all("<Key>", self.refresh_key)
            # self.root.bind_all("<Motion>", self.refresh_key)
            self.bind_all_event_to_root("<Key>",self.refresh_key)
            self.bind_all_event_to_root("<Motion>", self.refresh_key)
        else:
            print("Échec du login !")
            tk.messagebox.showerror("Erreur de connexion", "Email ou mot de passe incorrect.")
            return

    def disconnect(self):
        self.clean_view()
        self.view = GUIHandler.LoginMenu(self)
       
    def on_close(self):
        print("Fermeture de l'application...")
        self.root.destroy()
        AuthHandler._shutdown()


    def bind_all_event_to_root(self, event, function):
        self.root.bind_all(event,function)
        self._event.append(event)

    def unbind_all_events(self):
        for sequence in self._event:
            self.root.unbind_all(sequence)
        self._event.clear()

    def clean_view(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("NO_NAME_SET")
        print("cleaned view")
        #FIXME unbind les fonctionn qui actualise la key sinon réactualisation du menu en boucle
        for w in self.root.winfo_children():
            w.destroy()
        self.unbind_all_events()

    def run(self):
        self.root.mainloop()

    def show_page(self, page_name):
        self.view.show_page(page_name)

    def refresh_key(self, c):
        if self.session is None:
            self.disconnect()
            return
        time_left = self.session.session_expiration_time - time.time()
        if time_left <= 95:
            self.session = AuthHandler.refresh_session(self.session)
            print("refreshed")
    #TODO : vérifier les entrées utilisateur avant de lancer le calcul (si elles ne sont pas vides et sont valides)
    #FIXME: modifier calculate_step pour qu'il affiche le bon pas
    def controller_subnetting_calculation(self, page3):
        try:
            network = create_network(page3.network_entry.get(), page3.mask_entry.get())
        except NetmaskValueError as e:
            tk.messagebox.showerror("Erreur", f"Erreur lors de la création du réseau : {e}")
            return
        except AddressValueError as e:
            tk.messagebox.showerror("Erreur", f"Erreur lors de la création du réseau : {e}")
            return
        
        combobox_list = list(page3.list_machines_combobox["values"])
        if(len(combobox_list) < 3): # 3 car le premier élément est une chaîne vide
            tk.messagebox.showerror("Erreur", "Veuillez ajouter au moins 2 nombre de machines.")
            return
        # On ignore le premier élément qui est une chaîne vide
        list_nb_machines = list(map(int, combobox_list[1:]))
        return calculate_subnetting(network, list_nb_machines), calculate_step(calculate_nb_machines_max(list_nb_machines)), network.num_addresses - 2



    #----------------------------------------fonction page3--------------------------------------------
    #TODO : auto générer, a verifier
    def controller_subnetting_calculation(self, page3):
        try:
            network = create_network(page3.network_entry.get(), page3.mask_entry.get())
        except NetmaskValueError as e:
            tk.messagebox.showerror("Erreur", f"Erreur lors de la création du réseau : {e}")
            return
        except AddressValueError as e:
            tk.messagebox.showerror("Erreur", f"Erreur lors de la création du réseau : {e}")
            return

        combobox_list = list(page3.list_machines_combobox["values"])
        if(len(combobox_list) < 3): # 3 car le premier élément est une chaîne vide
            tk.messagebox.showerror("Erreur", "Veuillez ajouter au moins 2 nombre de machines.")
            return
        # On ignore le premier élément qui est une chaîne vide
        list_nb_machines = list(map(int, combobox_list[1:]))
        return calculate_subnetting(network, list_nb_machines), calculate_step(calculate_nb_machines_max(list_nb_machines)), network.num_addresses - 2

    def controller_create_number_of_subnets_input(self, page3 : GUIHandler.Page3, nb_subnet_voulue, subnet, mask):
        print(nb_subnet_voulue, subnet, mask)
        #TODO : verifier les entrers utilisateur, retour si erreur, et création des champs

        #verification du nombre de sous réseau
        nb_subnet_voulue : int = bu.to_int(nb_subnet_voulue)
        if nb_subnet_voulue is None or nb_subnet_voulue <= 0 or nb_subnet_voulue > 128:
            msg.showerror("Erreur", "Le nombre de sous-réseaux doit être un entier positif et inférieur ou égal à 128.")
            return None
        
        real_nb_subnet : int = nb_subnet_voulue
        #verification du mask
        try:
            NetworkHandler.validate_mask_format(mask)
        except Exception as e:
            msg.showerror("Erreur", str(e))
            return None

        #verification du subnet


        max_machine_per_subnet = AddressHandler.calculate_max_host_per_subnet(nb_subnet_voulue, subnet, mask)
        #Demander a l'utilisateur si ce nombre de machine maximal lui convient
        if msg.askyesno("Confirmation", f"Le nombre de machine par sous réseau maximal sera de: {max_machine_per_subnet}. Voulez-vous continuer ?") == False:
            return None

        #TODO : hardcoder
        page3.change_nb_machines_inputs(real_nb_subnet, nb_subnet_voulue)

        #TODO : stocker quelque part le nombre max de machine par sous réseau ? ou le recalculer?
        # faire en sorte que quand l'utilisateur appuer sur "return" sur un champs, sa le verifie et passe au suivant si correct

        return real_nb_subnet #SubnetHandler.calculate_number_of_subnets(nb_subnet, subnet, mask);

    def controller_machine_per_sub_nb(self, nb_subnet, subnet, mask):
        #13 suposont 16 ->
        return AddressHandler.calculate_max_host_per_subnet(nb_subnet, subnet, mask)
'''
if __name__ == "__main__":
    controller = GUIController()
    controller.run()
'''