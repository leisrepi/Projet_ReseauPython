import tkinter as tk
import GUIHandler
import AuthHandler
import DBHandler as db
import DBHandler
import time
import threading
#TODO : importer le import au complet vue que on ce sert de toutes les fonctions
from SubnetHandler import calculate_subnetting, calculate_step, calculate_nb_hosts_max
import AddressHandler
from ipaddress import NetmaskValueError, AddressValueError
from SubnetHandler import calculate_subnetting, calculate_step, calculate_nb_hosts_max
from NetworkHandler import create_network, define_mask_by_ip_class, validate_mask_format
import NetworkHandler
from AppException import InvalidMaskException, MaskNotInRangeException
import AppException

import BasicUtilies as bu
import tkinter.messagebox as msg

from ipaddress import IPv4Address
from typing import TYPE_CHECKING #pour avoir la docu sans import du module a l'execution (car pas besoin et importation circulaire)
if TYPE_CHECKING:
	import GUIHandler

from AppException import InvalidMaskException, MaskNotInRangeException


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
        if time_left <= 595:
            self.session = AuthHandler.refresh_session(self.session)
            print("refreshed")
    #TODO : vérifier les entrées utilisateur avant de lancer le calcul (si elles ne sont pas vides et sont valides)
    #FIXME: modifier calculate_step pour qu'il affiche le bon pas
    def controller_subnetting_calculation(self, page3 : GUIHandler.Page3):
        try:
            network = create_network(page3.network_entry.get(), page3.mask_entry.get())
        except InvalidMaskException as e:
            tk.messagebox.showerror("Erreur", f"Erreur lors de la création du réseau : {e}")
            return
        except AddressValueError as e:
            tk.messagebox.showerror("Erreur", f"Erreur lors de la création du réseau : {e}")
            return
        
        
        # on transforme les input en liste d'entiers
        list_nb_machines = []
        for input in page3.nb_machine_inputs:
            if bu.to_int(input.get()) is None or bu.to_int(input.get()) < 0:
                #TODO : mettre la bonne exception   
                raise AppException.InvalidInputException("Invalid number of machines input.")
                #tk.messagebox.showerror("Erreur", "Veuillez entrer des entiers positifs pour le nombre de machines par sous-réseau.")
            list_nb_machines.append(bu.to_int(input.get()))

        #list_nb_machines = list(map(int, combobox_list[1:]))
        #TODO : recyclage de fonction, CE n'est PAS DU TOUT PROPRE VOIR SOLIDE !!!!!
        print(page3.data['nb_max_machines_per_subnet'], page3.nb_subnet.get())
        return calculate_subnetting(network, page3.data['nb_max_machines_per_subnet'], int(page3.nb_subnet.get())), calculate_step(page3.data['nb_max_machines_per_subnet']), network.num_addresses - 2



    #----------------------------------------fonction page3--------------------------------------------
    
    def controller_verify_input_group1(self, page3 : GUIHandler.Page3, nb_subnet_voulue, subnet, mask):
        print(page3)
        print("----------------------------------------------------------------------")
        #verification du nombre de sous réseau
        nb_subnet_voulue : int = bu.to_int(nb_subnet_voulue) #c'est normal si c'est deja présent a certain endroit avant l'appel de cette fonction, certain appelant ne le font pas
        if nb_subnet_voulue is None or nb_subnet_voulue <= 0 or nb_subnet_voulue > 100:
            msg.showerror("Erreur", "Le nombre de sous-réseaux doit être un entier positif et inférieur ou égal à 100.")
            return None
        
        #verification du mask
        try:
            NetworkHandler.validate_mask_format(mask)
        except Exception as e:
            msg.showerror("Erreur", str(e))
            return None

        try:
            validate_mask_format(mask, classful=True)
            if(not NetworkHandler.is_classful_network_address(subnet, mask)):
                msg.showerror("Erreur","Le masque classfull introduit ne correspond pas au masque de classe de l'adresse IP")
                return None
        except Exception:
            pass

        #verification du subnet
          #verif de la validité de l'adresse IP
        if not AddressHandler.is_ip_valid(subnet):
            msg.showerror("Erreur", "Le format de l'adresse IP du sous-réseau est invalide.")
            return None

        max_machine_per_subnet = AddressHandler.calculate_max_host_per_subnet(nb_subnet_voulue, subnet, mask)
        if max_machine_per_subnet < 2:
            msg.showerror("Erreur", "Le nombre de sous-réseaux demandé est trop élevé pour le réseau donné.")
            return None
        page3.data['nb_max_machines_per_subnet'] = max_machine_per_subnet
        
        return max_machine_per_subnet

    def controller_create_number_of_subnets_input(self, page3 : GUIHandler.Page3, nb_subnet_voulue, subnet, mask):
        print(nb_subnet_voulue, subnet, mask)
        #TODO : verifier les entrers utilisateur, retour si erreur, et création des champs
        nb_subnet_voulue : int = bu.to_int(nb_subnet_voulue)
        max_machine_per_subnet  = self.controller_verify_input_group1(page3, nb_subnet_voulue, subnet, mask)
        if max_machine_per_subnet is None:
            return None
        
        page3.data['nb_max_machines_per_subnet'] = max_machine_per_subnet
        #Demander a l'utilisateur si ce nombre de machine maximal lui convient
        if msg.askyesno("Confirmation", f"Le nombre de machine par sous réseau maximal sera de: {max_machine_per_subnet}. Voulez-vous continuer ?") == False:
            return None

        #TODO : hardcoder
        page3.change_nb_machines_inputs(nb_subnet_voulue)


        page3.nb_machines_per_subnet_label["text"] = "Nombre maximum de machines par sous-réseaux: " + str(max_machine_per_subnet)
        page3.nb_subnets_label["text"] = "Nombre de sous-réseaux créés: " + str(nb_subnet_voulue)
        page3._verify_and_inform_every_nb_machine_per_subnet_input()
        return nb_subnet_voulue #SubnetHandler.calculate_number_of_subnets(nb_subnet, subnet, mask);

    def controller_machine_per_sub_nb(self, nb_subnet, subnet, mask):
        #13 suposont 16 ->
        return AddressHandler.calculate_max_host_per_subnet(nb_subnet, subnet, mask)
    
    
    def controller_fill_empty_machine_per_subnet_input_with_0(self, page3 : GUIHandler.Page3):
        for input in page3.nb_machine_inputs:
            if input.get() == "":
                input.delete(0, tk.END)
                input.insert(0, "0")

    #oauis c'est long mais au moin je me comprend
    #va verifier que tout les champs sont remplis, si ce n'est pas le cas il va proposer a l'utilisateur de les remplir avec des 0
    def controller_verify_and_propose_correction_empty_machine_per_subnet_input(self, page3 : GUIHandler.Page3):
        if page3.nb_machine_inputs is None or len(page3.nb_machine_inputs) == 0:
            msg.showerror("Erreur", "Merci de dabord valider le nombre de sous-réseaux avant de lancer la découpe.")
            return False
        for input in page3.nb_machine_inputs:
            if input.get() == "":
                user_answer = msg.askyesno("Champs vide détecté", "Un ou plusieurs champs de nombre de machines par sous-réseau sont vides. Voulez-vous les remplir avec '0' ? (non vous amenèra au premier champ vide pour correction)")
                if user_answer:
                    self.controller_fill_empty_machine_per_subnet_input_with_0(page3)
                    return True
                else:
                    input.focus_set()
                    return False
        return True
    

    def controller_get_address_info(self, ip : str, mask):
        try:
            validate_mask_format(mask)
            subnet = create_network(ip, mask)
        except AddressValueError as e:
            raise AddressValueError(str(e))
        except InvalidMaskException as e:
            raise InvalidMaskException(str(e))
        except MaskNotInRangeException as e:
            raise MaskNotInRangeException(str(e))
        
        mask = mask.strip()
        if int(ip.split(".")[0]) > 223:
            raise AddressValueError("Il n'est pas possible d'obtenir les informations du réseau d'une adresse de classe D ou E")
           

        if(mask[0] == "/"):
             return subnet.network_address, subnet.broadcast_address, None, None
            
        
        #gestion erreur classe D et E
       
        classfull_mask = define_mask_by_ip_class(subnet.network_address)
       
        if(classfull_mask is None or str(subnet.netmask) < classfull_mask):
            raise InvalidMaskException("Masque de sous-réseau supérieur au masque de réseau (masque de classe)")

        print("classfull mask : ", classfull_mask)
        print("subnet mask : ", str(subnet.netmask))
        if(str(subnet.netmask) == classfull_mask):
            return subnet.network_address, subnet.broadcast_address, None, None
        
        network = create_network(ip, classfull_mask)
        return network.network_address, network.broadcast_address, subnet.network_address, subnet.broadcast_address 
    
    def controller_load_subnetting_data(self, page3 : GUIHandler.Page3, data):
        """
        Charge les données de découpage en sous-réseaux dans la page 3 de l'interface graphique.
        Args:
            page3 (GUIHandler.Page3): La page 3 de l'interface graphique.
            data (tuple): Un tuple contenant les données de découpage en sous-réseaux.
                data[0] : nom de la découpe
                data[1] : nom d'utilisateur (speudo)
                data[2] : adresse réseau
                data[3] : masque réseau
                
        Returns:
            None
        """
        page3.data['subneting_name'] = data[0]
        page3.network_entry.delete(0, tk.END)
        page3.network_entry.insert(0, data[2])
        page3.mask_entry.delete(0, tk.END) 
        page3.mask_entry.insert(0, data[3])

        #on demande les découpes a la db
        #TODO : bon nom de la fonction a mettre au lieux de valeur hardcode ex : DBHandler.get_all_subnetting_of_user(self.session, data[0])
        """subnetting_data = [["découpe de test", 5 , 1 , "Kevin"],
                           ["découpe de test", 10 , 2 , "Kevin"],
                           ["découpe de test", 2 , 3 , "Kevin"],
                           ["découpe de test", 6 , 4 , "Kevin"],
                           ["découpe de test", 8 , 5 , "Kevin"],
                           ] """
        subnetting_data = DBHandler.get_all_subnets_of_a_subnetting(self.session, data[0])
        
        if subnetting_data is None:
            msg.showerror("Erreur", "La découpe que vous essayez de charger n'existe pas ou une erreur est survenue lors de la récupération des données.")
            return
        #on remplit les champs
        page3.nb_subnet.delete(0, tk.END)
        page3.nb_subnet.insert(0, str(len(subnetting_data)))
        page3.change_nb_machines_inputs(len(subnetting_data))
        for i in range (len(subnetting_data)):
            page3.nb_machine_inputs[i].delete(0, tk.END)
            page3.nb_machine_inputs[i].insert(0, str(subnetting_data[i][1])) #le 1 c'est le nb de machine du sous réseau

        #on lance la découpe pour réobtenir le résultat:
        page3.show_subnetting_result()

    def controller_save_subnetting_data(self, page3 : GUIHandler.Page3, subneting_name):
        """
        Sauvegarde les données de découpage en sous-réseaux dans la base de données.
        Args:
            page3 (GUIHandler.Page3): La page 3 de l'interface graphique.
            subneting_name (str): Le nom de la découpe en sous-réseaux.
        Returns:
            None (ou False en cas d'erreur)
        """
        #TODO : retourner des erreurs ou juste un boolean ?

        #verification adresse réseau et masque
        if self.controller_verify_input_group1(page3,page3.nb_subnet.get(),page3.network_entry.get(), page3.mask_entry.get()) is None:
            return False

        #Vérification que tous les champs sont remplis
        if not self.controller_verify_and_propose_correction_empty_machine_per_subnet_input(page3):
            return False
        
        #verfication nb machines par sous reseau (si valide)
        if not page3._is_nb_machine_per_subnet_inputs_valid():
            return False
        
        #Récupération des données a sauvegarder
        subnet_address = page3.network_entry.get()
        subnet_mask = page3.mask_entry.get()
        list_nb_machines = []
        for input in page3.nb_machine_inputs:
            list_nb_machines.append(bu.to_int(input.get()))
        
        #+-----------------------+
        #| Sauvegarde dans la db |
        #+-----------------------+

        #sauvegarde de la découpe réseau
        #TODO : a modifier, le pseudo sera retirer au merge
        DBHandler.insert_decoupe(self.session, subneting_name, subnet_address, subnet_mask)
        
        #sauvegarde des sous-réseaux
        try:
            
            for i in range(len(list_nb_machines)):
                DBHandler.insert_sous_reseau(self.session, i+1, list_nb_machines[i], subneting_name)
        except Exception as e:
            msg.showerror("Erreur", f"Une erreur est survenue lors de la sauvegarde des sous-réseaux : {e}")
            #erreur de sauvegarde des sous-réseaux, on supprime la découpe réseau créée précédemment
            try:
                DBHandler.delete_Subnetting(self.session, subneting_name)
            except Exception as e2:
                msg.showerror("Erreur critique", f"Une erreur critique est survenue lors de la sauvegarde des sous-réseaux et la suppression de la découpe réseau a échoué : {e2}")
            return
        msg.showinfo("Succès", "Les données de découpage en sous-réseaux ont été sauvegardées avec succès.")
    
        
    
    def controller_delete_subnetting(self, subnetting_id):
        db.delete_subnetting(self.session, subnetting_id)
        
    
'''
if __name__ == "__main__":
    controller = GUIController()
    controller.run()
'''