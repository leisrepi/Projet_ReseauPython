import tkinter as tk
import GUIHandler



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
        self.root.title("Application")
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
        self.view = GUIHandler.MenuSimple(self)
        self.start()
    
    def clean_view(self):
        self.view.root.destroy()

    def run(self):
        self.root.mainloop()


'''
if __name__ == "__main__":
    controller = GUIController()
    controller.run()
'''