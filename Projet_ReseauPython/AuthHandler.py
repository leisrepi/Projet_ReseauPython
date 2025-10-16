# --- IMPORTS ---
import DBHandler
import bcrypt

import base64
import hashlib
import hmac  #(Keyed-Hashing for Message Authentication) bibliothèque de hachage avec clé secrète
import secrets
import time
import atexit
from multiprocessing import Process, Pipe



# --- sous service (pour sécuriser le stockage de la clé secrète en mémoire) ---
# --- Processus gardien : possède les secrets et ne les renvoie jamais ---
_parent = None #parti du pipe dans le processus principal
_child = None #parti du pipe dans le processus enfant
_sign_process : Process = None #processus de signature



def _signer(connexion):
    # --- CONFIG ---
    SECRET_KEY = secrets.token_bytes(32)  # clé secrète de 32 bytes (32 * 8 = 256 bits) => très grand pour être sûr qu'elle ne soit pas trouvée par force brute
    #pour la trouver il faudrait faire 2^256 essais en moyenne, ce qui est infaisable (1,1579208923731619542357098500869e+77 essais) 
    # ou si on calcul a un milliard de milliard de possibilite / s (10^15/s) ~3.7×10⁵⁴ ans (≈ 2.7×10⁴⁴ fois l’âge de l’univers).
    
    while True:
        commande, args = connexion.recv()
        print(commande, args)
        if commande == "sign":
            user_name, session_expiration_time, random_per_session = args
            if "|" in user_name:
                #TODO : crée une exception personnalisée
                raise ValueError("Le nom d'utilisateur ne doit pas contenir de pipe '|'")
            
            message = f"{user_name}|{session_expiration_time}|{random_per_session}".encode() #f pour mettre vairable dans la chaine et pipe | sert juste de separateur,
                #on a choisis "|" car c'est un caractere peu utilise dans les noms d'utilisateur

            mac = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()  # creer le hachage avec la cle secrete, le message et l'algorithme sha256
            signature = base64.urlsafe_b64encode(mac).decode() #Base64 → compact (~+33% de taille) et réversible vers les bytes, il convertit les octets en caractères.
                #urlsafe_b64encode → évite + et /, donc OK pour les URLs/cookies.
            connexion.send(signature)
        elif commande == "exit":
            connexion.send(True)
            connexion.close()
            break

def _shutdown():
    """Ferme proprement le processus de signature"""
    try:
        _parent.send(("exit",))
        _parent.recv()
    except Exception:
        pass

atexit.register(_shutdown)


SESSION_LIFETIME = 10  # durée de vie en secondes (ici 10s pour tester)



def _verify_sign_process_launch(self):
    """Vérifie que le processus de signature est lancé, sinon le lance."""
    global _parent, _child, _sign_process      

    if _sign_process is None or not _sign_process.is_alive():
        _parent, _child = Pipe(duplex=True) #crée un pipe de communication bi-directionnel
        _sign_process = Process(target=_signer, args=(_child,), daemon=True) #crée un processus enfant qui exécute la fonction _signer avec l'extrémité enfant du pipe
        _sign_process.start() #démarre le processus enfant





class session:
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.session_expiration_time = int(time.time()) + SESSION_LIFETIME # temps actuel en secondes depuis 1970 + durée de vie (apres ce temps la session n'est plus valide)
        self.random_per_session = secrets.token_urlsafe(8) # chaîne aléatoire unique par session (8 bytes encodés en base64 urlsafe (pas de + ou /))
        print(self.random_per_session)
        self.signature = sign_session(user_name, self.session_expiration_time, self.random_per_session)

# --- Fonctions de signature ---
def sign_session(self,user_name: str, session_expiration_time: int, random_per_session: str) -> str:
    """
    Crée une signature HMAC-SHA256 sur le payload (user_name|session_expiration_time|random_per_session).
    Args:
        user_name (str) : nom de l'utilisateur 
        session_expiration_time (int) : temps en s depuis 1970 ou la session expirera 
        random_per_session (str) : chaîne aléatoire unique par session
    Returns:
        str : la signature HMAC-SHA256 encodée en Base64
    """
    _verify_sign_process_launch()
    _parent.send(("sign", (user_name, session_expiration_time, random_per_session,)))
    return _parent.recv()

    '''
    if "|" in user_name:
        #TODO : crée une exception personnalisée
        raise ValueError("Le nom d'utilisateur ne doit pas contenir de pipe '|'")
    
    message = f"{user_name}|{session_expiration_time}|{random_per_session}".encode() #f pour mettre vairable dans la chaine et pipe | sert juste de separateur,
        #on a choisis "|" car c'est un caractere peu utilise dans les noms d'utilisateur

    mac = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()  # creer le hachage avec la cle secrete, le message et l'algorithme sha256
    return base64.urlsafe_b64encode(mac).decode() #Base64 → compact (~+33% de taille) et réversible vers les bytes, il convertit les octets en caractères.
        #urlsafe_b64encode → évite + et /, donc OK pour les URLs/cookies.
    '''

def verify_session(session: session) -> bool:
    """
    Vérifie que la session n'est pas expirée et que la signature est valide.
    Args:
        token (dict) : dictionnaire contenant les informations de la session (user_name, session_expiration_time, random_per_session, signature)
    Returns:
        bool : True si la session est valide, False sinon
    """
    now = int(time.time())
    # Vérifie si la session est expirée
    if now >= session.session_expiration_time:
        print("❌ Session expirée")
        return False

    # signature attendue
    expected_signature = sign_session(
        session.user_name,
        session.session_expiration_time,
        session.random_per_session,
    )
    if not hmac.compare_digest(expected_signature, session.signature): # compare_digest pour éviter les attaques par timing
        #python s'arrête à la première différence, donc on utilise compare_digest pour forcer à comparer toute la chaîne (même temps, donc pas d'info sur la position de la différence)
        print("❌ Signature invalide (token falsifié ?)")
        return False

    print("✅ Session valide")
    return True


def password_encrypt(password):
    """Chiffre un mot de passe avec bcrypt.
        Args:
            passwd (string) : mot de passe en blanc à chiffrer

        Returns:
            return (bytes) : Renvoie le mot de passe hashé
    """
    #bcrypt a besoins d'encode pour fonctionner
    passwordDepart = password.encode()

    #salaison du MDP
    saltDepart = bcrypt.gensalt(rounds=16)
    #hashage du MDP
    hashedDepart = bcrypt.hashpw(passwordDepart, saltDepart)

    return hashedDepart

#TODO : renommer en is_password_correct
def password_verification(password, hashed):
    """Vérifie un mot de passe avec son hash bcrypt.
        Args:
            passwd (string) : mot de passe en blanc à vérifier
            hashed (bytes) : hash du mot de passe à vérifier

        Returns:
            return (bool) : Renvoie True si le mot de passe est correct, False sinon
    """
    passwordVerif = password.encode()

    #comparaison des 2 mots de passes
    if(bcrypt.checkpw(passwordVerif, hashed)):
        return True
    else:
        return False

# Permet de se connecter à un compte utilisateur
def login(pseudo, password):
    """Vérifie les identifiants d'un utilisateur.
        Args:
            pseudo (string) : chaîne de caractères du pseudo de l'utilisateur
            password (bytes) : mot de passe en blanc

        Returns:
            return (bool) : Renvoie True si les identifiants sont corrects, False sinon
    """
    #
    if DBHandler.is_user_on_db(pseudo, password):
        return session(pseudo)
    return None