import DBHandler as db
import AppException as ap

value = input("Ajouter un utilisateur ? y/n")

if value == 'y' or  value == 'Y':
    i = 0
    while i != 1:
        user_name = input("Entrer un nom d'utilisateur : ")
        user_password = input("Entrer son mot de passe : ")

        try:
            i = i+1
            db.insert_user(user_name, user_password)
        except(ap.UserAlreadyInDBException):
            i = i-1