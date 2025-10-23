import tkinter as tk
import GUIHandler
import AuthHandler
import DBHandler  
import time
import threading

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
        if time_left <= 5:
            self.session = AuthHandler.refresh_session(self.session)
            print("refreshed")

'''
if __name__ == "__main__":
    controller = GUIController()
    controller.run()
'''