
import GUIHandler

class GUIController:
    def __init__(self):
        self.menu = GUIHandler.LoginMenu(self)

    def on_button_click(self):
        print("Bouton cliqué depuis le contrôleur !")

    def on_login(self, email, password):
        print(f"Login avec Email: {email}, Mot de passe: {password}")
        #TODO : verifier si les identifiants sont corrects avant d'ouvrir la fenetre principale
        #TODO : ouvrir la fenetre en lui fournissant l'id de l'utilisateur
        self.menu.root.destroy()
        self.menu = GUIHandler.MenuSimple(self)

if __name__ == "__main__":
    controller = GUIController()
