# --------------------------------------
#             Imports
# --------------------------------------

import AppException
import math
from ipaddress import IPv4Address, IPv4Network, AddressValueError

# --------------------------------------
#             Fonctions
# --------------------------------------

# Vérification de la validité de l'adresse IP. 
def is_ip_valid(address):  
    """Vérifie si une adresse IP est valide

        Args:
            address (IPv4Adress) : chaîne de caractères de l'adresse IP

        Returns:
            return (boolean) : Renvoie true si valide, false sinon
    """
    try:
        ipadress = IPv4Address(address)
        return not ipadress.is_multicast and not ipadress.is_reserved
    except AddressValueError:
        return False
    
# Création d'une adresse IP à partir d'une chaîne de caractères (renvoie None si l'adresse n'est pas valide)
def create_ip_address(ip_string):
    """Crée une adresse IP à partir d'une chaîne de caractères

        Args:
            ip_string (string) : chaîne de caractères de l'adresse IP

        Returns: 
            return (IPv4Adress) : Renvoie une instance de IPv4Address 

        Raises:  
            AdressValueError si l'adresse n'est pas valide
    """
    try:
        return IPv4Address(ip_string)
    except AddressValueError:
        raise AddressValueError("Adresse IP non valide")
    
import math
from ipaddress import IPv4Network

def calculate_max_host_per_subnet(subnetNumber, subnet, mask):

    subnetNumber = int(subnetNumber)
    if(mask[0] == "/"):
        net = IPv4Network(f"{subnet}{mask}", strict=False)
    else:
        net = IPv4Network(f"{subnet}/{mask}", strict=False)
 

    i=1
    while True:
        x = 2 ** math.ceil(math.log2(i))
        if(x >= subnetNumber):
            i = x
            break
        i = i+1

    addresses_per_subnet = net.num_addresses / i

    return int(addresses_per_subnet) - 2