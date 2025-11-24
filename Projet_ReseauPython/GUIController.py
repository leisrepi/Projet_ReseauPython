"""Contrôleur de l'interface graphique.

Ce module centralise la logique métier et les interactions entre la vue
(`GUIHandler`) et les couches d'authentification/base de données. Il vise à
clarifier la séparation MVC en évitant que les vues ne manipulent directement
les modèles ou la base.
"""

from __future__ import annotations

import threading
import time
import tkinter as tk
import tkinter.messagebox as msg
from typing import TYPE_CHECKING, List, Optional

import AddressHandler
import AppException
import AuthHandler
import BasicUtilies as bu
import DBHandler
import NetworkHandler
from AppException import InvalidMaskException, MaskNotInRangeException
from NetworkHandler import create_network, define_mask_by_ip_class, validate_mask_format
from SubnetHandler import calculate_step, calculate_subnetting
from ipaddress import AddressValueError

if TYPE_CHECKING:  # Importation différée pour éviter les cycles
    import GUIHandler


class GUIController:
    """Singleton qui orchestre les évènements de l'interface Tkinter."""

    _controller: Optional["GUIController"] = None

    def __new__(cls):
        raise RuntimeError("Use get_instance() to get the singleton instance.")

    @classmethod
    def get_instance(cls) -> "GUIController":
        if cls._controller is None:
            instance = super().__new__(cls)
            instance.__init__()
            cls._controller = instance
        return cls._controller

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self.root = tk.Tk()
        self._initialized = True
        self._events: List[str] = []
        self.session = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("NO_NAME_SET")

        # Vue initiale
        self.view: "GUIHandler.LoginMenu | GUIHandler.MainApp" = GUIHandler.LoginMenu(self)
        self.run()

    # ------------------------------------------------------------------
    # Gestion de la fenêtre principale
    # ------------------------------------------------------------------
    def set_cursor_loading(self) -> None:
        self.root.configure(cursor="wait")

    def set_cursor_default(self) -> None:
        self.root.configure(cursor="")

    def bind_all_event_to_root(self, event: str, function) -> None:
        self.root.bind_all(event, function)
        self._events.append(event)

    def unbind_all_events(self) -> None:
        for sequence in self._events:
            self.root.unbind_all(sequence)
        self._events.clear()

    def clean_view(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("NO_NAME_SET")
        for widget in self.root.winfo_children():
            widget.destroy()
        self.unbind_all_events()

    def show_login(self) -> None:
        self.clean_view()
        self.view = GUIHandler.LoginMenu(self)

    def show_main(self) -> None:
        self.clean_view()
        self.view = GUIHandler.MainApp(self)
        self.bind_all_event_to_root("<Key>", self.refresh_key)
        self.bind_all_event_to_root("<Motion>", self.refresh_key)

    def run(self) -> None:
        self.root.mainloop()

    # ------------------------------------------------------------------
    # Session et authentification
    # ------------------------------------------------------------------
    def on_login(self, pseudonyme: str, password: str) -> None:
        """Tente une connexion et bascule sur l'application principale."""

        self.set_cursor_loading()
        self.view.change_login_button(tk.DISABLED)

        is_verification_done = tk.BooleanVar(self.root, value=False)
        result_box: dict[str, object | Exception | None] = {"result": None, "error": None}

        def worker() -> None:
            try:
                result_box["result"] = AuthHandler.create_session(pseudonyme, password=password)
            except Exception as exc:  # type: ignore[except-type]
                result_box["error"] = exc
            finally:
                self.root.after(0, lambda: is_verification_done.set(True))

        threading.Thread(target=worker, daemon=True).start()
        # Attente non bloquante pour Tk
        self.root.wait_variable(is_verification_done)

        error = result_box["error"]
        if error is not None:
            msg.showerror("Erreur de connexion", str(error))
            self.set_cursor_default()
            self.view.change_login_button(tk.ACTIVE)
            return

        self.session = result_box["result"]
        self.set_cursor_default()
        self.view.change_login_button(tk.ACTIVE)

        if self.session is not None and AuthHandler.verify_session(self.session):
            self.show_main()
        else:
            msg.showerror("Erreur de connexion", "Email ou mot de passe incorrect.")

    def refresh_key(self, _event) -> None:
        if self.session is None:
            self.disconnect()
            return
        time_left = self.session.session_expiration_time - time.time()
        if time_left <= 595:
            self.session = AuthHandler.refresh_session(self.session)

    def disconnect(self) -> None:
        self.session = None
        self.show_login()

    def on_close(self) -> None:
        self.root.destroy()
        AuthHandler._shutdown()

    # ------------------------------------------------------------------
    # Fonctions destinées aux vues (Page1/Page3/Popup...)
    # ------------------------------------------------------------------
    def controller_subnetting_calculation(self, page3: "GUIHandler.Page3"):
        try:
            network = create_network(page3.network_entry.get(), page3.mask_entry.get())
        except (InvalidMaskException, AddressValueError) as exc:
            msg.showerror("Erreur", f"Erreur lors de la création du réseau : {exc}")
            return None

        list_nb_machines = []
        for input_widget in page3.nb_machine_inputs:
            value = bu.to_int(input_widget.get())
            if value is None or value < 0:
                raise AppException.InvalidInputException("Invalid number of machines input.")
            list_nb_machines.append(value)

        return (
            calculate_subnetting(network, page3.data["nb_max_machines_per_subnet"], int(page3.nb_subnet.get())),
            calculate_step(page3.data["nb_max_machines_per_subnet"]),
            network.num_addresses - 2,
        )

    def controller_verify_input_group1(self, page3: "GUIHandler.Page3", nb_subnet_voulue, subnet, mask):
        nb_subnet_voulue: int = bu.to_int(nb_subnet_voulue)
        if nb_subnet_voulue is None or nb_subnet_voulue <= 0 or nb_subnet_voulue > 100:
            msg.showerror("Erreur", "Le nombre de sous-réseaux doit être un entier positif et inférieur ou égal à 100.")
            return None

        try:
            NetworkHandler.validate_mask_format(mask)
        except Exception as exc:  # type: ignore[except-type]
            msg.showerror("Erreur", str(exc))
            return None

        try:
            validate_mask_format(mask, classful=True)
            if not NetworkHandler.is_classful_network_address(subnet, mask):
                msg.showerror("Erreur", "Le masque classfull introduit ne correspond pas au masque de classe de l'adresse IP")
                return None
        except Exception:  # Validation facultative
            pass

        if not AddressHandler.is_ip_valid(subnet):
            msg.showerror("Erreur", "Le format de l'adresse IP du sous-réseau est invalide.")
            return None

        max_machine_per_subnet = AddressHandler.calculate_max_host_per_subnet(nb_subnet_voulue, subnet, mask)
        if max_machine_per_subnet < 2:
            msg.showerror("Erreur", "Le nombre de sous-réseaux demandé est trop élevé pour le réseau donné.")
            return None
        page3.data["nb_max_machines_per_subnet"] = max_machine_per_subnet
        return max_machine_per_subnet

    def controller_create_number_of_subnets_input(self, page3: "GUIHandler.Page3", nb_subnet_voulue, subnet, mask, confirmation=True):
        nb_subnet_voulue: int = bu.to_int(nb_subnet_voulue)
        max_machine_per_subnet = self.controller_verify_input_group1(page3, nb_subnet_voulue, subnet, mask)
        if max_machine_per_subnet is None:
            return None

        page3.data["nb_max_machines_per_subnet"] = max_machine_per_subnet
        if confirmation:
            if not msg.askyesno(
                "Confirmation",
                f"Le nombre de machine par sous réseau maximal sera de: {max_machine_per_subnet}. Voulez-vous continuer ?",
            ):
                return None

        page3.change_nb_machines_inputs(nb_subnet_voulue)
        page3.nb_machines_per_subnet_label["text"] = (
            "Nombre maximum de machines par sous-réseaux: " + str(max_machine_per_subnet)
        )
        page3.nb_subnets_label["text"] = "Nombre de sous-réseaux créés: " + str(nb_subnet_voulue)
        page3._verify_and_inform_every_nb_machine_per_subnet_input()
        return nb_subnet_voulue

    def controller_machine_per_sub_nb(self, nb_subnet, subnet, mask):
        return AddressHandler.calculate_max_host_per_subnet(nb_subnet, subnet, mask)

    def controller_fill_empty_machine_per_subnet_input_with_0(self, page3: "GUIHandler.Page3"):
        for input_widget in page3.nb_machine_inputs:
            if input_widget.get() == "":
                input_widget.delete(0, tk.END)
                input_widget.insert(0, "0")

    def controller_verify_and_propose_correction_empty_machine_per_subnet_input(self, page3: "GUIHandler.Page3") -> bool:
        if page3.nb_machine_inputs is None or len(page3.nb_machine_inputs) == 0:
            msg.showerror("Erreur", "Merci de dabord valider le nombre de sous-réseaux avant de lancer la découpe.")
            return False
        for input_widget in page3.nb_machine_inputs:
            if input_widget.get() == "":
                user_answer = msg.askyesno(
                    "Champs vide détecté",
                    "Un ou plusieurs champs de nombre de machines par sous-réseau sont vides. Voulez-vous les remplir avec '0' ? (Non vous amènera au premier champ vide pour correction)",
                )
                if user_answer:
                    self.controller_fill_empty_machine_per_subnet_input_with_0(page3)
                    return True
                input_widget.focus_set()
                return False
        return True

    def controller_get_address_info(self, ip: str, mask):
        try:
            validate_mask_format(mask)
            subnet = create_network(ip, mask)
        except AddressValueError as exc:
            raise AddressValueError(str(exc))
        except InvalidMaskException as exc:
            raise InvalidMaskException(str(exc))
        except MaskNotInRangeException as exc:
            raise MaskNotInRangeException(str(exc))

        mask = mask.strip()
        if int(ip.split(".")[0]) > 223:
            raise AddressValueError("Il n'est pas possible d'obtenir les informations du réseau d'une adresse de classe D ou E")

        if mask[0] == "/":
            return subnet.network_address, subnet.broadcast_address, None, None

        classfull_mask = define_mask_by_ip_class(subnet.network_address)
        if classfull_mask is None or str(subnet.netmask) < classfull_mask:
            raise InvalidMaskException("Masque de sous-réseau supérieur au masque de réseau (masque de classe)")

        if str(subnet.netmask) == classfull_mask:
            return subnet.network_address, subnet.broadcast_address, None, None

        network = create_network(ip, classfull_mask)
        return network.network_address, network.broadcast_address, subnet.network_address, subnet.broadcast_address

    def controller_load_subnetting_data(self, page3: "GUIHandler.Page3", data):
        page3.data["subneting_name"] = data[0]
        page3.network_entry.delete(0, tk.END)
        page3.network_entry.insert(0, data[2])
        page3.mask_entry.delete(0, tk.END)
        page3.mask_entry.insert(0, data[3])

        subnetting_data = DBHandler.get_all_subnets_of_a_subnetting(self.session, data[0])
        if subnetting_data is None:
            msg.showerror(
                "Erreur",
                "La découpe que vous essayez de charger n'existe pas ou une erreur est survenue lors de la récupération des données.",
            )
            return

        page3.nb_subnet.delete(0, tk.END)
        page3.nb_subnet.insert(0, str(len(subnetting_data)))
        self.controller_create_number_of_subnets_input(
            page3,
            page3.nb_subnet.get(),
            page3.network_entry.get(),
            page3.mask_entry.get(),
            confirmation=False,
        )
        page3.change_nb_machines_inputs(len(subnetting_data))
        for i in range(len(subnetting_data)):
            page3.nb_machine_inputs[i].delete(0, tk.END)
            page3.nb_machine_inputs[i].insert(0, str(subnetting_data[i][1]))

        page3.show_subnetting_result()

    def controller_save_subnetting_data(self, page3: "GUIHandler.Page3", subneting_name):
        if self.controller_verify_input_group1(page3, page3.nb_subnet.get(), page3.network_entry.get(), page3.mask_entry.get()) is None:
            return False

        if not self.controller_verify_and_propose_correction_empty_machine_per_subnet_input(page3):
            return False

        if not page3._is_nb_machine_per_subnet_inputs_valid():
            return False

        subnet_address = page3.network_entry.get()
        subnet_mask = page3.mask_entry.get()
        list_nb_machines = [bu.to_int(input_widget.get()) for input_widget in page3.nb_machine_inputs]

        DBHandler.insert_decoupe(self.session, subneting_name, subnet_address, subnet_mask)

        try:
            for i, nb_machines in enumerate(list_nb_machines):
                DBHandler.insert_sous_reseau(self.session, i + 1, nb_machines, subneting_name)
        except Exception as exc:  # type: ignore[except-type]
            msg.showerror("Erreur", f"Une erreur est survenue lors de la sauvegarde des sous-réseaux : {exc}")
            try:
                DBHandler.delete_Subnetting(self.session, subneting_name)
            except Exception as cleanup_exc:  # type: ignore[except-type]
                msg.showerror(
                    "Erreur critique",
                    f"Une erreur critique est survenue lors de la sauvegarde des sous-réseaux et la suppression de la découpe réseau a échoué : {cleanup_exc}",
                )
            return False

        msg.showinfo("Succès", "Les données de découpage en sous-réseaux ont été sauvegardées avec succès.")
        return True

    def controller_delete_subnetting(self, subnetting_id):
        DBHandler.delete_subnetting(self.session, subnetting_id)

    def controller_list_user_subnettings(self):
        return DBHandler.get_all_subnettings_of_user(self.session)

