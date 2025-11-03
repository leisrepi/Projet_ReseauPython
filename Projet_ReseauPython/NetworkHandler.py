# --------------------------------------
#             Imports
# --------------------------------------

from ipaddress import IPv4Network, AddressValueError, NetmaskValueError
from AppException import InvalidMaskException, MaskNotInRangeException

import re
# --------------------------------------
#             Fonctions
# --------------------------------------

# Vérification de la validité du masque.
def validate_mask_format(mask, *, classful: bool = None):
    """Vérifie le format d'un masque (classful ou classless ou indifférent)

    Args:
        mask (string): chaîne de caractères du masque
        classful (bool, optional): Indique si le masque doit être vérifié en classful (True), classless (False) ou indifférent (None). Par défaut à None.

    Raises:
        InvalidMaskException : Si le masque est invalide
        MaskNotInRangeException : Si le masque n'est pas dans les bornes autorisées (/8 à /29 = 255.0.0.0 à 255.255.255.248)
    """

    # Vérification du format du masque (peut importe si classful ou classless)
    if(classful is None):
        if(mask[0] != "/"):
            mask = "/" + mask
        try:
            network = IPv4Network(("0.0.0.0"+mask), strict=False) 
            if(not network.num_addresses in range(8, 16777217)): # entre /8 et /29
                raise MaskNotInRangeException("Masque ne se trouve pas entre /8 et /29")
        except NetmaskValueError:
            raise InvalidMaskException("Masque invalide")  
        
    # Vérification du classful    
    elif(classful):
    
        # Vérification du format du masque (par regex)
        if(not re.search(r"^((255|254|252|248|240|224|192|128|0)\.){3}(255|254|252|248|240|224|192|128|0)$", mask)):
            raise InvalidMaskException("Masque invalide")
        
        # Vérification des bornes du masque (entre le /8 et le /29)
        if(mask < "255.0.0.0" or mask > "255.255.255.248"):
            raise MaskNotInRangeException("Masque ne se trouve pas entre 255.0.0.0 et 255.255.255.248")
        
        # Vérification des octets du masque (par exemple refuser 255.0.128.0)
        mask_parts = [int(part) for part in mask.split(".")]
        for i in range(4):
            # S'il s'agit du premier octet, on vérifie s'il est différent de 255 (car 255.0.0.0 est le masque minimal), 
            # sinon on initialise la variable previous_byte
            if(i == 0):
                if(mask_parts[i] != 255):
                    raise InvalidMaskException("Masque invalide")
                else:
                    previous_byte = mask_parts[i]
                    continue
            
            # Pour les octets suivants, on vérifie si l'octet précédent n'est pas égal à 255, 
            # que l'octet actuel soit égal à 0 (car 255.x.0.x n'est pas valide)
            if(previous_byte != 255 and mask_parts[i] != 0):
                raise InvalidMaskException("Masque invalide")
            
            previous_byte = mask_parts[i]

    # Vérification du classless
    else:   
        if(mask[0] != "/"):
            raise InvalidMaskException("Masque invalide")
        try:
            prefix_length = int(mask[1:])
            if(prefix_length < 0 or prefix_length > 32):
                raise InvalidMaskException("Masque invalide")
            if(prefix_length < 8 or prefix_length > 29):
                raise MaskNotInRangeException("Masque ne se trouve pas entre /8 et /29")
        except ValueError:
            raise InvalidMaskException("Masque invalide")


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