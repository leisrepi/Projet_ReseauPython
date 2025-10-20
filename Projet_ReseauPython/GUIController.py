import tkinter as tk
import GUIHandler
import AuthHandler
import DBHandler  


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
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("NO_NAME_SET")
        self.view = GUIHandler.LoginMenu(self)
        self.session = None
        self.run()


    def on_button_click(self):
        print("Bouton cliqué depuis le contrôleur !")
        if (AuthHandler.verify_session(self.session)):
            print("Session valide.")
        else:
            print("Session expirée, veuillez vous reconnecter.")
            self.disconnect()

    def on_login(self, pseudonyme, password):
        #XXX RETIRER CE DEBUG !!!!!!
        print(f"Login avec Email: {pseudonyme}, Mot de passe: {password}")

        #TODO : verifier si les identifiants sont corrects avant d'ouvrir la fenetre principale
        if AuthHandler.login(pseudonyme, password):
            print("Login réussi !")
            self.session = AuthHandler.session(pseudonyme)
            self.clean_view()
            self.view = GUIHandler.MainApp(self)
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

    def clean_view(self):
        self.root.destroy()
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("NO_NAME_SET")

    def run(self):
        self.root.mainloop()

    def show_page(self, page_name):
        self.view.show_page(page_name)


'''
if __name__ == "__main__":
    controller = GUIController()
    controller.run()
'''