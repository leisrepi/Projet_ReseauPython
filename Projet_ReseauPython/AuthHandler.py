import bcrypt
# from DBHandler import is_user_on_db
def passwd_encrypt(passwd):
    """Chiffre un mot de passe avec bcrypt.
        Args:
            passwd (string) : chaîne de caractères du mot de passe à chiffrer

        Returns:
            return (bytes) : Renvoie le mot de passe hashé
    """
    #bcrypt a besoins d'encode pour fonctionner
    passwdDepart = passwd.encode()

    #salaison du MDP
    saltDepart = bcrypt.gensalt(rounds=16)
    #hashage du MDP
    hashedDepart = bcrypt.hashpw(passwdDepart, saltDepart)

    return hashedDepart

def passwd_verify(passwd, hashed):
    """Vérifie un mot de passe avec son hash bcrypt.
        Args:
            passwd (string) : chaîne de caractères du mot de passe à vérifier
            hashed (bytes) : hash du mot de passe à vérifier

        Returns:
            return (bool) : Renvoie True si le mot de passe est correct, False sinon
    """
    passwdVerif = passwd.encode()

    #comparaison des 2 mots de passes
    if(bcrypt.checkpw(passwdVerif, hashed)):
        return True
    else:
        return False

# Permet de se connecter à un compte utilisateur
def can_login(pseudo, passwd):
    """Vérifie les identifiants d'un utilisateur.
        Args:
            pseudo (string) : chaîne de caractères du pseudo de l'utilisateur
            passwd (bytes) : mot de passe hashé de l'utilisateur

        Returns:
            return (bool) : Renvoie True si les identifiants sont corrects, False sinon
    """
    #TODO : si ajout de session, code supplémentaire possible dans cette fonction
    return is_user_on_db(pseudo, passwd)

print(passwd_encrypt("1234")) #1234 => b'$2b$16$W.Z8/R3Gu9p6RUWmqMmhSeJSyF2JiHOwpupW4lsCVDKrRJes8XioS'

print(passwd_verify("1234", b'$2b$16$W.Z8/R3Gu9p6RUWmqMmhSeJSyF2JiHOwpupW4lsCVDKrRJes8XioS')) #True

