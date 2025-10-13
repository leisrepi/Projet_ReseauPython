# --------------------------------------
#             Imports
# --------------------------------------

from ipaddress import IPv4Address, AddressValueError
# Exceptions personnalisées
from AppException import TooManyMachinesException

# --------------------------------------
#             Fonctions
# --------------------------------------

# Vérification de la validité de l'adresse IP. 
def is_ip_valid(address):  
    """Vérifie si une adresse IP est valide"""
    """Renvoie true si valide, false sinon"""
    """address : chaîne de caractères de l'adresse IP"""
    try:
        ipadress = IPv4Address(address)
        return not ipadress.is_private
    except AddressValueError:
        return False