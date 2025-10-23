# --------------------------------------
#             Imports
# --------------------------------------

from ipaddress import IPv4Network, AddressValueError, NetmaskValueError
from AppException import InvalidMaskException

# --------------------------------------
#             Fonctions
# --------------------------------------

# Vérification de la validité du masque.
def is_mask_valid(mask):
    """Vérifie si un masque est valide

    Args:
        mask (string): chaîne de caractères du masque
    
    Returns:
        return (boolean): Renvoie true si le masque est valide, false sinon

    Raises:
        InvalidMaskException : Si le masque est invalide
    """
    if (mask == "" or mask is None):
        return False
    if(mask[0] != "/"):
        mask = "/" + mask
    if(mask[1] == "0"):
        return False
    try:
        IPv4Network(("0.0.0.0"+mask), strict=False)   
        return True
    except NetmaskValueError:
        return False
    
# Création d'un réseau à partir d'une adresse IP et d'un masque (renvoie None si le masque n'est pas valide)
def create_network(address, mask):
    """Crée un réseau à partir d'une adresse IP et d'un masque

        Args:
            address (string) : chaîne de caractères de l'adresse IP
            mask (string) : chaîne de caractères du masque

        Returns:
            return (IPv4Network) : Renvoie une instance de IPv4Network

        Raises:
            NetmaskValueError : si le masque n'est pas valide
            AddressValueError : si l'adresse IP n'est pas valide
    """ 
    if(not is_mask_valid(mask)):
        raise NetmaskValueError("Masque non valide ou vide")
    if(mask[0] != "/"):
        mask = "/" + mask
    try:   
        return IPv4Network((address + mask), strict=False)
    except AddressValueError:
        raise AddressValueError("Adresse IP non valide")
    except NetmaskValueError:
        raise NetmaskValueError("Masque non valide")

# Définition du masque en fonction de la classe d'adresse IP classfull (renvoie None si l'adresse ne peut pas avoir de masque)
def define_mask_by_ip_class(ip_address):
    """Définit le masque en fonction de la classe d'adresse IP classfull mise en argument
        Args:
            ip_address (string) : IPv4Address à partir de laquelle on déduit la classe
        Returns:
            return (string) : masque sous forme de chaîne de caractères
        Raises:
            InvalidMaskException : si l'adresse ne peut pas avoir de masque (classe D ou E)
    """
    #IPV4Network reprend la première adresse et le masque
    CLASS_A = IPv4Network(("0.0.0.0", "128.0.0.0"))
    CLASS_B = IPv4Network(("128.0.0.0", "192.0.0.0"))
    CLASS_C = IPv4Network(("192.0.0.0", "224.0.0.0"))

    # Renvoie le masque adéquat en fonction de si l'adresse se trouve dans la plage d'adresses de la classe
    if ip_address in CLASS_A:
        return "255.0.0.0"
    elif ip_address in CLASS_B:
        return '255.255.0.0'
    elif ip_address in CLASS_C:
        return "255.255.255.0"
    else:
        raise InvalidMaskException("L'adresse IP ne peut pas avoir de masque (classe D ou E)")