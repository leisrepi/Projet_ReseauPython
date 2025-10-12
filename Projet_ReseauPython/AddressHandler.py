import ipaddress
from ipaddress import IPv4Address, IPv4Network
import Subnet

IpAddress = "192.168.3.55"
IpMask = "255.255.128.0"

Ipclient = IPv4Network(IpAddress, strict=False)
maskRes = Subnet.define_mask_by_ip_class(IpAddress)
IpNetwork = IPv4Network(IpAddress, maskRes)

#Retourne l'Ip du réseau et son adresse broadcast
def get_network_information_from_ip_address():
    return IpNetwork.network_address, IpNetwork.broadcast_address


interface = ipaddress.ip_interface(IpAddress)


print(IpAddress, IpMask,IpNetwork.network_address, IpNetwork.netmask)

#si masque == classe -->affiche reseau broadcast