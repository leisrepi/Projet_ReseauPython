import ipaddress
from ipaddress import IPv4Address, IPv4Network
import Subnet

IpAddress = "192.168.3.55"
SNMask = "255.255.128.0"

#Retourne l'Ip du réseau et son adresse broadcast et le sous réseaux si possible
def get_network_information_from_ip_address(IpAdress, SNMask):
    IpClient = IPv4Address(IpAddress)
    netMask = Subnet.define_mask_by_ip_class(IpClient)
    IpNetwork = IPv4Network(IpAddress+"/"+netMask, strict=False)
    #vérification de l'appartenance du masque dde sous réseaux par rapport a celui du réseaux (vérification que celui-ci n'est pas plus grand)
    if(IpNetwork.netmask < SNMask):
        return None
    if(IpNetwork.netmask == SNMask):
        return IpNetwork.network_address, IpNetwork.broadcast_address
    

#si masque == classe -->affiche reseau broadcast