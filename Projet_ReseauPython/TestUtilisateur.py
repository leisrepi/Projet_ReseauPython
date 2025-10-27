import DBHandler

if (__name__ == "__main__"):
    pseudo = input("Insérer un nom d'utilisateur : ")
    mdp = input("Insérer un mot de passe : ")

    DBHandler.insert_user(pseudo, mdp)
    print("Etat de l'utilisateur dans la db : " + ("existant" if DBHandler.is_user_on_db(pseudo, mdp) else "non-existant"))