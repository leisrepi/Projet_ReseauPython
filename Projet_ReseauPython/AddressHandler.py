import ipaddress
from ipaddress import IPv4Address, IPv4Network
import Subnet

IpAddress = "192.168.3.55"
SNMask = "255.255.128.0"

#Retourne l'Ip du réseau et son adresse broadcast et le sous réseaux si possible
def get_network_information_from_ip_address(IpAddress, SNMask):
    """Retourne l'adresse du réseaux et son broadcast et aussi le sous-réseaux avec son broadcast.
        Si le sous réseaux est impossible il renverra 'None' pour le sous réseaux et son broadcast"""
    IpClient = IPv4Address(IpAddress)
    netMask = Subnet.define_mask_by_ip_class(IpClient)
    IpNetwork = IPv4Network(IpAddress+"/"+netMask, strict=False)
    #vérification de l'appartenance du masque dde sous réseaux par rapport a celui du réseaux (vérification que celui-ci n'est pas plus grand)
    if(str(IpNetwork.netmask) < SNMask):
        return None #gérer l'erreur dans le cas ou le sous réseaux est plus grand que le réseaux lui meme
    if(IpNetwork.netmask == SNMask): #Vérification de la possibilité de sous-réseaux
        return IpNetwork.network_address, IpNetwork.broadcast_address, None, None
    for SNIp in IpNetwork.hosts(): #boucle de recherche du sous réseaux dans lequel se trouve l'adresse Ip du client
        SNIpAddress = SNIp
    
    SNBroadcast = IPv4Network(str(SNIpAddress)+"/"+SNMask, strict=False).broadcast_address
    return IpNetwork.network_address, IpNetwork.broadcast_address, SNIpAddress, SNBroadcast

print(get_network_information_from_ip_address(IpAddress, SNMask))