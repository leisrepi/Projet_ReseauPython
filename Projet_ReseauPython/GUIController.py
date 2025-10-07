
import GUIHandler

class GUIController:
    def __init__(self):
        self.menu = GUIHandler.MenuSimple(self)

    def on_button_click(self):
        print("Bouton cliqué depuis le contrôleur !")

if __name__ == "__main__":
    controller = GUIController()
