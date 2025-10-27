# --------------------------------------
#             Imports
# --------------------------------------

from ipaddress import IPv4Address, AddressValueError
import AppException
from ipaddress import IPv4Address, IPv4Network
from NetworkHandler import define_mask_by_ip_class

# --------------------------------------
#             Fonctions
# --------------------------------------

#Retourne l'Ip du réseau et son adresse broadcast et le sous réseaux si possible
def get_network_information_from_ip_address_and_mask(IpAddress, SNMask):

    """ Retourne les infos du réseaux.

        Args:
            IpAddress (String) : adresse ip en format string
            SNMask (String) : masque lier à l'adresse ip en format string
        Returns :
            Adresse du réseaux et son broadcast. Adresse sous-réseaux et son broadcast.
            Si le sous réseaux est impossible il renverra 'None' pour le sous réseaux et son broadcast.

        Raise :
            SNMaskErrorException si le masque n'est pas correcte."""
    
    IpClient = IPv4Address(IpAddress)
    netMask = define_mask_by_ip_class(IpClient)
    IpNetwork = IPv4Network(IpAddress+"/"+netMask, strict=False)

    #vérification de l'appartenance du masque dde sous réseaux par rapport a celui du réseaux (vérification que celui-ci n'est pas plus grand)
    if(str(IpNetwork.netmask) < SNMask):
        raise AppException.SNMaskErrorException 

    if(IpNetwork.netmask == SNMask): #Vérification de la possibilité de sous-réseaux
        return IpNetwork.network_address, IpNetwork.broadcast_address, None, None
    
    for SNIp in IpNetwork.hosts(): #boucle de recherche du sous réseaux dans lequel se trouve l'adresse Ip du client
        SNIpAddress = SNIp
    
    SNBroadcast = IPv4Network(str(SNIpAddress)+"/"+SNMask, strict=False).broadcast_address
    return IpNetwork.network_address, IpNetwork.broadcast_address, SNIpAddress, SNBroadcast

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
        return not ipadress.is_private
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
    
