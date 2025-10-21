import tkinter as tk
import GUIHandler
from SubnetHandler import calculate_subnetting
from NetworkHandler import create_network
from ipaddress import NetmaskValueError, AddressValueError


class GUIController:
    _controller = None
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
        self.root.title("NO_NAME_SET")
        self.view = GUIHandler.LoginMenu(self)
        self.run()

    def on_button_click(self):
        print("Bouton cliqué depuis le contrôleur !")

    def on_login(self, email, password):
        #TODO RETIRER CE DEBUG !!!!!!
        print(f"Login avec Email: {email}, Mot de passe: {password}")
        #TODO : verifier si les identifiants sont corrects avant d'ouvrir la fenetre principale
        #TODO : ouvrir la fenetre en lui fournissant l'id de l'utilisateur
        self.clean_view()
        self.view = GUIHandler.MainApp(self)
       
    
    def clean_view(self):
        self.root.destroy()
        self.root = tk.Tk()
        self.root.title("NO_NAME_SET")

    def run(self):
        self.root.mainloop()

    def show_page(self, page_name):
        self.view.show_page(page_name)

    #TODO : vérifier les entrées utilisateur avant de lancer le calcul (si elles ne sont pas vides et sont valides)
    def controller_subnetting_calculation(self, page3):
        try:
            network = create_network(page3.network_entry.get(), page3.mask_entry.get())
        except NetmaskValueError as e:
            tk.messagebox.showerror("Erreur", f"Erreur lors de la création du réseau : {e}")
            return
        except AddressValueError as e:
            tk.messagebox.showerror("Erreur", f"Erreur lors de la création du réseau : {e}")
            return
        
        combobox_list = list(page3.nb_machines_combobox["values"])

        # On ignore le premier élément qui est une chaîne vide
        list_nb_machines = list(map(int, combobox_list[1:]))
        return calculate_subnetting(network, list_nb_machines)


'''
if __name__ == "__main__":
    controller = GUIController()
    controller.run()
'''