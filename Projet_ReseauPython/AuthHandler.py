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

#INFO : la sécuriter sarette au moment ou il est possible d'ecraser le sous procéssus
#il faudrait faire un service windows séparer avec clé publique et priver pour correctement tout securiser
#mais cela est overkill dans le cadre du projet

# --- sous service (pour sécuriser le stockage de la clé secrète en mémoire) ---
# --- Processus gardien : possède les secrets et ne les renvoie jamais ---
_parent = None #parti du pipe dans le processus principal
_child = None #parti du pipe dans le processus enfant
_sign_process : Process = None #processus de signature



def _create_session(connexion):
    # --- CONFIG ---
    SESSION_LIFETIME = 10  # durée de vie en secondes (ici 10s pour tester)
    SECRET_KEY = secrets.token_bytes(32)  # clé secrète de 32 bytes (32 * 8 = 256 bits) => très grand pour être sûr qu'elle ne soit pas trouvée par force brute
    #pour la trouver il faudrait faire 2^256 essais en moyenne, ce qui est infaisable (1,1579208923731619542357098500869e+77 essais) 
    # ou si on calcul a un milliard de milliard de possibilite / s (10^15/s) ~3.7×10⁵⁴ ans (≈ 2.7×10⁴⁴ fois l’âge de l’univers).
    
    #sous fonction pour signer (plus sécurisé)

    # --- Fonctions de signature ---
    def _sign_session(user_name: str, session_expiration_time: int, random_per_session: str) -> str:
        """
        Crée une signature HMAC-SHA256 sur le payload (user_name|session_expiration_time|random_per_session).
        Args:
            user_name (str) : nom de l'utilisateur 
            session_expiration_time (int) : temps en s depuis 1970 ou la session expirera 
            random_per_session (str) : chaîne aléatoire unique par session
        Returns:
            str : la signature HMAC-SHA256 encodée en Base64
        """
        
        if "|" in user_name:
            #raise ValueError("Le nom d'utilisateur ne doit pas contenir de pipe '|'")
            return None
        if user_name is None:
            #raise ValueError("le nom d'utilisateur ne peut pas être vide!")
            return None
        
        message = f"{user_name}|{session_expiration_time}|{random_per_session}".encode() #f pour mettre vairable dans la chaine et pipe | sert juste de separateur,
            #on a choisis "|" car c'est un caractere peu utilise dans les noms d'utilisateur

        mac = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()  # creer le hachage avec la cle secrete, le message et l'algorithme sha256
        return base64.urlsafe_b64encode(mac).decode() #Base64 → compact (~+33% de taille) et réversible vers les bytes, il convertit les octets en caractères.
            #urlsafe_b64encode → évite + et /, donc OK pour les URLs/cookies.
        
    def _verify_session(old_session : session) -> bool:
        #TODO faire la documentation
        if old_session is None:
            return False #la session ne peut pas être vide
        now = int(time.time())
        if now >= old_session.session_expiration_time:
            print("❌ Session expirée")
            return False

        # signature attendue
        expected_signature = _sign_session(
            old_session.user_name,
            old_session.session_expiration_time,
            old_session.random_per_session,
        )
        return hmac.compare_digest(expected_signature, old_session.signature)
            
    try:
        while True:
            commande, args = connexion.recv()
            print(commande, args)
            if commande == "create_session":
                user_name: str = None
                password: str = None
                old_session : session = None
                user_name, password, old_session = args

                if user_name is None and old_session is not None:
                    #rafraîchissement de session
                    user_name = old_session.user_name
                if "|" in user_name:
                    #TODO : crée une exception personnalisée
                    #raise ValueError("Le nom d'utilisateur ne doit pas contenir de pipe '|'")
                    connexion.send(None)
                    continue
                
                if password is not None:
                    #vérification du mot de passe
                    if not DBHandler.is_user_on_db(user_name, password):
                        connexion.send(None)
                        continue
                elif old_session is not None:
                    #vérification de l'ancienne session
                    
                    if not _verify_session(old_session=old_session):
                        print("❌ Signature invalide (token falsifié ?)")
                        connexion.send(None)
                        continue
                else:
                    # neither password nor old_session provided
                    connexion.send(None)
                    continue

                new_session = session(user_name)
                new_session.session_expiration_time = int(time.time()) + SESSION_LIFETIME # temps actuel en secondes depuis 1970 + durée de vie (apres ce temps la session n'est plus valide)
                
                message = f"{new_session.user_name}|{new_session.session_expiration_time}|{new_session.random_per_session}".encode() #f pour mettre vairable dans la chaine et pipe | sert juste de separateur,
                    #on a choisis "|" car c'est un caractere peu utilise dans les noms d'utilisateur
                mac = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()  # creer le hachage avec la cle secrete, le message et l'algorithme sha256
                new_session.signature = base64.urlsafe_b64encode(mac).decode() #Base64 → compact (~+33% de taille) et réversible vers les bytes, il convertit les octets en caractères.
                    #urlsafe_b64encode → évite + et /, donc OK pour les URLs/cookies.
                
                connexion.send(new_session)
            elif commande == "verify_session":
                old_session : session = args
                connexion.send(_verify_session(old_session))
            elif commande == "exit":
                connexion.send(False) #on renvoie false au lieux de truc pour eviter les attaques par timing 
                #(tu fait une demande au sous procéssus sans jamais la récuperer, en espérant que la fonction de sécu)
                #la récupère et accepte ta demande.
                break
    finally:
        try:
            connexion.close()
        except Exception:
            pass

#XXX : attaque possible par timing, faire une demande qui renvera

def _shutdown():
    """Ferme proprement le processus de signature"""
    try:
        if _parent is not None:
            try:
                _parent.send(("exit", None))
                # attendre l'ack
                _parent.recv()
            except (BrokenPipeError, EOFError, OSError):
                pass
            try:
                _parent.close()
            except Exception:
                pass

        if _sign_process is not None:
            _sign_process.join(timeout=2)
            if _sign_process.is_alive():
                # arrêt doux
                _sign_process.terminate()
                _sign_process.join(timeout=2)
            # en tout dernier recours :
            if _sign_process.is_alive():
                _sign_process.kill()
                _sign_process.join(timeout=2)
    except Exception:
        pass
    finally:
        _sign_process = None

atexit.register(_shutdown)






def _verify_sign_process_launch():
    """Vérifie que le processus de signature est lancé, sinon le lance."""
    global _parent, _child, _sign_process      

    if _sign_process is None or not _sign_process.is_alive():
        _parent, _child = Pipe(duplex=True) #crée un pipe de communication bi-directionnel
        _sign_process = Process(target=_create_session, args=(_child,), daemon=True) #crée un processus enfant qui exécute la fonction _signer avec l'extrémité enfant du pipe
        _sign_process.start() #démarre le processus enfant


#XXXTODO : lock la création de session au sein du sous-processus ainsi que la verification du mdp
# lock la verification de signaturue au sein du sous-processus
# -> impossible d'obtenir un hash de signature, sois on crée une sessions depuis le
# pseudo (string aléatoire générer en interne), qui renvera une signature mais avec le texte aléatoire
# signature obtenue uniquement si le mdp correct est fourni ou si une signature valide est fournie

# attaque lier au changement d'heure windows ?

#XXX peu etre appeler de l'extérieux, la sécuriter saute donc!!!
class session:
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.session_expiration_time = 0 # temps actuel en secondes depuis 1970 + durée de vie (apres ce temps la session n'est plus valide)
        self.random_per_session = secrets.token_urlsafe(8) # chaîne aléatoire unique par session (8 bytes encodés en base64 urlsafe (pas de + ou /))
        print(self.random_per_session)
        self.signature = None



def verify_session(session: session) -> bool:
    #TODO mettre a jour la documentation
    """
    Vérifie que la session n'est pas expirée et que la signature est valide.
    Args:
        token (dict) : dictionnaire contenant les informations de la session (user_name, session_expiration_time, random_per_session, signature)
    Returns:
        bool : True si la session est valide, False sinon
    """
    
    return _verify_sign_process_launch() or _parent.send(("verify_session", session)) or _parent.recv()

def create_session(user_name: str, password: str = None) -> session:
    """Crée une nouvelle session pour un utilisateur donné.
        Args:
            user_name (string) : chaîne de caractères du pseudo de l'utilisateur
            password (string) : mot de passe en blanc

        Returns:
            return (session) : Renvoie un objet session si la création a réussi, None sinon
    """
    _verify_sign_process_launch()
    _parent.send(("create_session", (user_name, password, None)))
    return _parent.recv()

def refresh_session(old_session : session) -> session:
    """Rafraîchit une session existante.
        Args:
            old_session (session) : objet session à rafraîchir

        Returns:
            return (session) : Renvoie un nouvel objet session si le rafraîchissement a réussi, None sinon
    """
    _verify_sign_process_launch()
    _parent.send(("create_session", (None, None, old_session)))
    return _parent.recv()

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