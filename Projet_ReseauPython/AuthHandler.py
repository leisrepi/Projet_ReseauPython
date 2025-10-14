# --- IMPORTS ---
import base64
import hashlib
import hmac  #(Keyed-Hashing for Message Authentication) bibliothèque de hachage avec clé secrète
import secrets
import time

# --- CONFIG ---
SECRET_KEY = secrets.token_bytes(32)  # clé secrète de 32 bytes (32 * 8 = 256 bits) => très grand pour être sûr qu'elle ne soit pas trouvée par force brute
#pour la trouver il faudrait faire 2^256 essais en moyenne, ce qui est infaisable (1,1579208923731619542357098500869e+77 essais) 
# ou si on calcul a un milliard de milliard de possibilite / s (10^15/s) ~3.7×10⁵⁴ ans (≈ 2.7×10⁴⁴ fois l’âge de l’univers).
SESSION_LIFETIME = 10  # durée de vie en secondes (ici 10s pour tester)

# --- Fonctions de signature ---
def sign_session(user_name: str, session_expiration_time: int, random_per_session: str) -> str:
    """
    Crée une signature HMAC-SHA256 sur le payload (user_name|session_expiration_time|random_per_session).
    Args:
        user_name (str) : nom de l'utilisateur 
        session_expiration_time (int) : temps en s depuis 1970 ou la session expirera 
        random_per_session (str) : chaîne aléatoire unique par session
    Returns:
        str : la signature HMAC-SHA256 encodée en Base64
    """
    message = f"{user_name}|{session_expiration_time}|{random_per_session}".encode() #f pour mettre vairable dans la chaine et pipe | sert juste de separateur,
        #on a choisis "|" car c'est un caractere peu utilise dans les noms d'utilisateur
    #TODO : verifier que le nom d'utilisateur ne contient pas de pipe a son instruction
    if "|" in user_name:
        raise ValueError("Le nom d'utilisateur ne doit pas contenir de pipe '|'")
    mac = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()  # creer le hachage avec la cle secrete, le message et l'algorithme sha256
    return base64.urlsafe_b64encode(mac).decode() #Base64 → compact (~+33% de taille) et réversible vers les bytes, il convertit les octets en caractères.
        #urlsafe_b64encode → évite + et /, donc OK pour les URLs/cookies.


def create_session(user_name: str):
    """Crée une session pour un utilisateur donné.
    Args:
        user_name (str) : nom de l'utilisateur
    Returns:
        dict : dictionnaire contenant les informations de la session (user_name, session_expiration_time, random_per_session, signature)
    """
    session_expiration_time = int(time.time()) + SESSION_LIFETIME # temps actuel en secondes depuis 1970 + durée de vie (apres ce temps la session n'est plus valide)
    random_per_session = secrets.token_urlsafe(8) # chaîne aléatoire unique par session (8 bytes encodés en base64 urlsafe (pas de + ou /))
    signature = sign_session(user_name, session_expiration_time, random_per_session)
    return {
        "user_name": user_name,
        "session_expiration_time": session_expiration_time,
        "random_per_session": random_per_session,
        "signature": signature
    }

def verify_session(token: dict) -> bool:
    """
    Vérifie que la session n'est pas expirée et que la signature est valide.
    Args:
        token (dict) : dictionnaire contenant les informations de la session (user_name, session_expiration_time, random_per_session, signature)
    Returns:
        bool : True si la session est valide, False sinon
    """
    now = int(time.time())
    # Vérifie si la session est expirée
    if now >= token["session_expiration_time"]:
        print("❌ Session expirée")
        return False

    # signature attendue
    expected_sig = sign_session(
        token["user_name"],
        token["session_expiration_time"],
        token["random_per_session"]
    )
    if not hmac.compare_digest(expected_sig, token["signature"]): # compare_digest pour éviter les attaques par timing
        #python s'arrête à la première différence, donc on utilise compare_digest pour forcer à comparer toute la chaîne (même temps, donc pas d'info sur la position de la différence)
        print("❌ Signature invalide (token falsifié ?)")
        return False

    print("✅ Session valide")
    return True