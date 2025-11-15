import GUIController
import AuthHandler
import DBHandler
import NetworkHandler

#Important ! permet au sous processus "_sign_process" de "AuthHandler" de se lancer correctement sous Windows
if (__name__ == "__main__"):
    print ("test version 0.1.0")
    print(AuthHandler.DUMMY_HASH)
    
    #GUIHandlerOld.init_GUI()
    
    DBHandler.create_db()
    #DBHandler.insert_user("test", "test")
    guiController = GUIController.GUIController.get_instance()
