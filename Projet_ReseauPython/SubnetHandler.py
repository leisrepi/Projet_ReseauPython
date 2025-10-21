# --------------------------------------
#             Imports
# --------------------------------------

from ipaddress import IPv4Network, IPv4Address, AddressValueError, NetmaskValueError
from math import log2, ceil
# Exceptions personnalisées
from AppException import TooManyMachinesException, InvalidMaskException

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
        return not ipadress.is_private
    except AddressValueError:
        return False
# Vérification de la validité du masque.
def is_mask_valid(mask):
    """Vérifie si un masque est valide

    Args:
        mask (string): chaîne de caractères du masque
    
    Returns:
        return (boolean): Renvoie true si le masque est valide, false sinon
    """
    if(mask[0] != "/"):
        mask = "/" + mask
    if(mask[1] == "0"):
        return False
    try:
        IPv4Network(("0.0.0.0"+mask), strict=False)   
        return True
    except NetmaskValueError:
        return False
                    
# Création d'une adresse IP à partir d'une chaîne de caractères (renvoie None si l'adresse n'est pas valide)
def create_ip_adress(ip_string):
    """Crée une adresse IP à partir d'une chaîne de caractères

        Args:
            ip_string (string): chaîne de caractères de l'adresse IP

        Returns: 
            return (IPv4Adress) : Renvoie une instance de IPv4Address ou lève une AdressValueError si l'adresse n'est pas valide
    """
    try:
        return IPv4Address(ip_string)
    except AddressValueError:
        raise AddressValueError("Adresse IP non valide")

# Création d'un réseau à partir d'une adresse IP et d'un masque (renvoie None si le masque n'est pas valide)
def create_network(address, mask):
    """Crée un réseau à partir d'une adresse IP et d'un masque

    Args:
        address (string) : chaîne de caractères de l'adresse IP
        mask (string) : chaîne de caractères du masque

    Returns:
        return (IPv4Network) : Renvoie une instance de IPv4Network

    Raises:
        Lève une NetmaskValueError si le masque n'est pas valide
        Lève une AddressValueError si l'adresse IP n'est pas valide
    """ 
    if(mask[0] != "/"):
        mask = "/" + mask
    try:   
        return IPv4Network((address + mask), strict=False)
    except NetmaskValueError:
        raise NetmaskValueError("Masque non valide")
    except AddressValueError:
        raise AddressValueError("Adresse IP non valide")

# Calcul du nombre de machines maximum sur une liste de machines données(par exposant de 2)
def calculate_nb_machines_max(nb_machines_list):
# log2 exemple : log2(32) = 5 car 2^5 = 32
# ceil arrondi à l'entier supérieur donc si log2 = 4.1 -> 5
# puis 2^5 donnera l'exposant nécessaire pour le nombre d'hôtes par sous-réseau
# + 2 pour l'adresse de réseau et de diffusion
    """Calcule et renvoie le nombre de machines maximum sur une liste de machines données(par exposant de 2)

        Args:
            nb_machines_list (list[int]) : liste du nombre de machines par sous-réseau

        Returns:
            return (int) : Renvoie un entier correspondant au nombre de machines maximum        
    """
    return 2 ** ceil(log2(max(nb_machines_list) + 2))
   
# Calcul du pas.
def calculate_step(nb_machines):
    """Calcule et renvoie le pas en fonction du nombre de machines mis en argument
        
        Args:
            nb_machines (int) : entier nombre de machines par sous-réseau

        Returns:
            return (tuple(int, int)) : Renvoie un tuple (pas, octet) où pas est le pas entre chaque sous-réseau et octet est l'octet du masque à modifier
    """
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

# Vérification de la possibilité de faire une découpe classique
def verify_subnetting_possibility(network, nb_machines_list):
    """Vérifie si une découpe classique est possible

        Args: 
            network (IPv4Network) : IPv4Network du réseau parent
            nb_machines_list (list[int]) : liste du nombre de machines par sous-réseau

        Returns: 
            true si une découpe classique est possible, false sinon
    """
    print("Decoupe classique possible ?:",(network.num_addresses)/len(nb_machines_list), ">=", calculate_nb_machines_max(nb_machines_list))
    return (network.num_addresses)/len(nb_machines_list) >= calculate_nb_machines_max(nb_machines_list)

# Vérification de la possibilité de faire une découpe VLSM
def verify_vlsm_possibility(network, nb_machines_list):
    """Vérifie si une découpe VLSM est possible

        Args:
            network : IPv4Network du réseau parent
            nb_machines_list : liste du nombre de machines par sous-réseau

        Returns:
            Renvoie true si une découpe VLSM est possible, false sinon
    """
    # Calcul du nombre total de machines nécessaires (chaque sous-réseau arrondi à la puissance de 2 supérieure)
    tot_machines = 0
    for nb_machines in nb_machines_list:
        tot_machines += 2 ** ceil(log2(nb_machines + 2))
        print(2 ** ceil(log2(nb_machines + 2)))
    print("VSLM possible ?:",network.num_addresses, ">=", tot_machines)
    return network.num_addresses >= tot_machines

# Calcul des sous-réseaux (renvoie une liste de liste contenant les informations des sous-réseaux [adresse_sous_reseau, adresse_broadcast, premiere_ip, derniere_ip])
def calculate_subnetting(network, nb_machines_list):
    """Calcule les sous-réseaux en fonction du réseau et de la liste du nombre de machines par sous-réseau

        Args:
            network (IPv4Network) : IPv4Network du réseau parent
            nb_machines_list (list[int]) : liste du nombre de machines par sous-réseau

        Returns:
            Renvoie une liste de liste contenant les informations des sous-réseaux [adresse_sous_reseau, adresse_broadcast, premiere_ip, derniere_ip

        Raises:
            Lève une exception TooManyMachinesException si le nombre de sous-réseaux dépasse 100
    """
    nb_machines = calculate_nb_machines_max(nb_machines_list)
    nb_subnet = len(nb_machines_list)

    # Liste des hôtes et du nombre d'adresses pour éviter de recalculer à chaque itération
    hosts = list(network.hosts())
    # Nombre d'adresses total dans le réseau
    num_addresses = network.num_addresses
    # Pas entre chaque sous-réseau
    step = nb_machines - 1

    # Si le nombre de sous-réseaux est trop grand, on arrête l'opération et on renvoie une exception
    if(nb_subnet > 100):
        raise TooManyMachinesException("Le nombre de machines par sous-réseau a dépassé la limite (100). Opération annulée.")


    increment = 0
    result = []
    # Boucle d'affichage des sous-réseaux
    for i in range(nb_subnet):
        print("Sous-réseau", i+1)
        result.append([])
        # S'il s'agit du premier sous-réseau, l'adresse de sous-réseau est l'adresse réseau (list(network.hosts()) ne prends que les adresses utilisables)
        if(i == 0):
            print("Adresse de sous-réseau :", network.network_address)
            result[i].append(str(network.network_address))
        else:
            print("Adresse de sous-réseau :", hosts[i + increment - 1])
            result[i].append(str(hosts[i + increment - 1]))

        # S'il s'agit du dernier sous-réseau, l'adresse de broadcast est l'adresse de broadcast du réseau (list(hosts) ne prends que les adresses utilisables)
        if((i + increment + nb_machines - 2)  == num_addresses - 2):
            print("Adresse de broadcast :", network.broadcast_address)
            result[i].append(str(network.broadcast_address))
        else:
            print("Adresse de broadcast :", hosts[(i + increment + nb_machines - 2)])
            result[i].append(str(hosts[(i + increment + nb_machines - 2)]))
        # Première IP
        print("Première IP :", hosts[i + increment])
        result[i].append(str(hosts[i + increment]))
        # Dernière IP
        print("Dernière IP :", hosts[(i + increment + nb_machines - 3)])
        result[i].append(str(hosts[(i + increment + nb_machines - 3)]))

        # Mise à jour de l'incrément pour le prochain sous-réseau
        increment += step
        print()
    return result
        
# --------------------------------------
#               Tests
# --------------------------------------

# Tests peut être supprimé une fois le module terminé


address = "18.0.0.0"
if(not is_ip_valid(address)):
    print("Adresse IP non valide")
    exit()
mask = "255.255.0.0"
if(not is_mask_valid(mask)):
    print("Masque non valide")
    exit()

# mask = define_mask_by_ip_class(create_ip_adress(adress))
nb_machines_list = [7, 6, 5, 4, 3, 2, 1, 10, 1, 10, 5, 10, 1, 1, 1, 1, 1, 1]


network = create_network(address, mask)
print("Adresse réseau :", network.network_address)
print("Masque :", network.netmask)
print("Adresse de diffusion :", network.broadcast_address)
print("Nombre d'hôtes :", network.num_addresses - 2)
hosts = list(network.hosts())
print("Plage d'adresses disponible :", hosts[0], "à", hosts[-1])


if(verify_subnetting_possibility(network, nb_machines_list)):
    try:
        result = calculate_subnetting(network, nb_machines_list)
        print(result)
    except TooManyMachinesException as e:
        print("Erreur :", e)
elif(verify_vlsm_possibility(network, nb_machines_list)):
    print("VLSM possible")
    exit()
else:
    print("Découpe impossible")
    exit()



# root = tk.Tk()
# root.title("Tableau de données")
# root.title("Tableau de données")

# colonnes = ["Adresse de sous-réseau", "Adresse de broadcast", "Première IP", "Dernière IP"]
# # result.append(colonnes)
# tree = ttk.Treeview(root, columns=colonnes, show='headings')
# for col in colonnes:
#     tree.heading(col, text=col)
#     tree.column(col, width=100, anchor='center')

# # Ajouter les lignes
# for ligne in result:
#     tree.insert('', 'end', values=ligne)

# tree.pack(expand=True, fill='both')
# root.mainloop()

# Question : J'ai oublié mais faut-il afficher un sous-réseau si la dernière adresse de celui-ci est l'adresse de broadcast du réseau parent (en référence au dernier sr mis en rouge dans le powerpoint)?