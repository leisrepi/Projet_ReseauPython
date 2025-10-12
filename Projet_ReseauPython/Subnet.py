# --------------------------------------
#             Imports
# --------------------------------------

from ipaddress import IPv4Network, IPv4Address
from math import log2, ceil, floor
# --------------------------------------
#             Fonctions
# --------------------------------------

# Vérification de la validité de l'adresse IP.
def is_ip_valid(ip_string):
    try:
        IPv4Address(ip_string)
        return True
    except ValueError:
        return False

# Création d'une adresse IP à partir d'une chaîne de caractères (renvoie None si l'adresse n'est pas valide)
def create_ip_adress(ip_string):
    try:
        return IPv4Address(ip_string)
    except ValueError:
        return None
    
# Calcul du pas.
def calculate_pas(nb_machines):
    if(nb_machines <= 256):
        return nb_machines, 4
    elif(nb_machines <= 65536):
        return nb_machines // 256, 3
    elif(nb_machines <= 16777216):
        return nb_machines // 65536, 2
    elif(nb_machines <= 4294967296):
        return nb_machines // 16777216, 1
    return 

# Définition du masque en fonction de la classe d'adresse IP classfull (renvoie None si l'adresse ne peut pas avoir de masque)
def define_mask_by_ip_class(adresse_ip):
    #IPV4Network reprend la première adresse et le masque
    CLASS_A = IPv4Address(("0.0.0.0", "128.0.0.0"))
    CLASS_B = IPv4Address(("128.0.0.0", "192.0.0.0"))
    CLASS_C = IPv4Address(("192.0.0.0", "224.0.0.0"))
    #CLASS_D = IPv4Network(("224.0.0.0", "240.0.0.0"))
    if adresse_ip in CLASS_A:
        return "255.0.0.0"
    elif adresse_ip in CLASS_B:
        return '255.255.0.0'
    elif adresse_ip in CLASS_C:
        return "255.255.255.0"
    else:
        return None

def verify_subnetting_possibility(network, nb_sr, nb_machines):
    #Vérification que le nombre de sous-réseaux est possible
    # Vérification que le nombre de machines par sous-réseau est possible
    if(nb_machines > floor((network.num_addresses) / nb_sr)):
        return False
    return True

def calculate_subnetting(network, nb_sr, nb_machines):

    if(nb_sr > 100):
        print("Le nombre de machines par sous-réseau a dépassé la limite (100). Opération annulée.")
        return None
    increment = 0

    result = []
    # Boucle d'affichage des sous-réseaux
    for i in range(nb_sr):
        print("Sous-réseau", i+1)
        result.append([])
        # S'il s'agit du premier sous-réseau, l'adresse de sous-réseau est l'adresse réseau (list(network.hosts()) ne prends que les adresses utilisables)
        if(i == 0):
            print("Adresse de sous-réseau :", network.network_address)
            result[i].append(str(network.network_address))
        else:
            print("Adresse de sous-réseau :", list(network.hosts())[i + increment - 1])
            result[i].append(str(list(network.hosts())[i + increment - 1]))

        # S'il s'agit du dernier sous-réseau, l'adresse de broadcast est l'adresse de broadcast du réseau (list(network.hosts()) ne prends que les adresses utilisables)
        if((i + increment + nb_machines - 2)  == network.num_addresses - 2):
            print("Adresse de broadcast :", network.broadcast_address)
            result[i].append(str(network.broadcast_address))
        else:
            print("Adresse de broadcast :", str(list(network.hosts())[(i + increment + nb_machines - 2)]))
            result[i].append(str(list(network.hosts())[(i + increment + nb_machines - 2)]))

        print("Première IP :", list(network.hosts())[i + increment])
        result[i].append(str(list(network.hosts())[i + increment]))
        print("Dernière IP :", str(list(network.hosts())[(i + increment + nb_machines - 3)]))
        result[i].append(str(list(network.hosts())[(i + increment + nb_machines - 3)]))

        increment += nb_machines - 1
        print()
    return result
        
# --------------------------------------
#               Tests
# --------------------------------------
'''
adress = IPv4Address("168.192.0.0")
mask = define_mask_by_ip_class(adress)
print("Masque défini :", mask, "\n")

network = IPv4Network((adress, mask), strict=False)
print("Adresse réseau :", network.network_address)
print("Masque :", network.netmask)
print("Adresse de diffusion :", network.broadcast_address)
print("Nombre d'hôtes :", network.num_addresses - 2)
print("Plage d'adresses disponible :", list(network.hosts())[0], "à", list(network.hosts())[-1])
print()
result = calculate_subnetting(network, 4, 50)
print(result)'''