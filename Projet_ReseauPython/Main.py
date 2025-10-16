import GUIHandlerOld
import GUIController
import AuthHandler


#Important ! permet au sous processus "_sign_process" de "AuthHandler" de se lancer correctement sous Windows
if (__name__ == "__main__"):
    print ("Hello World !")
    print ("test version 0.0.3")
    print ("voici ce que j'ai ajouter dans le main")
    print ("voici ce que j'ai ajouter depuis la branche 2")
    print ("il ne reste que la branche nouvelle fonctionnalité")
    print ("j'ai refussioner avec la branche main")

    #GUIHandlerOld.init_GUI()


    guiController = GUIController.GUIController.get_instance()


