# --------------------------------------
#             Imports
# --------------------------------------

from math import log2, ceil, floor
# Exceptions personnalisées
from AppException import TooManyMachinesException

# --------------------------------------
#             Fonctions
# --------------------------------------
                   
# Calcul du nombre de machines maximum sur une liste de machines données(par exposant de 2)
#TODO : changer machines en hosts dans le nom de la fonction et ses appels
def calculate_nb_hosts_max(nb_hosts_list):
# log2 exemple : log2(32) = 5 car 2^5 = 32
# ceil arrondi à l'entier supérieur donc si log2 = 4.1 -> 5
# puis 2^5 donnera l'exposant nécessaire pour le nombre d'hôtes par sous-réseau
# + 2 pour l'adresse de réseau et de diffusion
    """
        Calcule et renvoie le nombre d'hôtes maximum sur une liste de hôtes données afin de connaitre le nombre d'hôtes nécessaire par sous-réseau
        Args:
            nb_hosts_list (list[int]) : liste du nombre de hôtes par sous-réseau

        Returns:
            return (int) : Renvoie un entier correspondant au nombre de hôtes maximum        
    """
    return 2 ** ceil(log2(max(nb_hosts_list) + 2))
   
# Calcul du pas.
def calculate_step(nb_machines):
    """Calcule et renvoie le pas en fonction du nombre de machines mis en argument
        
        Args:
            nb_machines (int) : entier nombre de machines par sous-réseau

        Returns:
            return (string) : Renvoie un string <[pas] sur l'octet [octet]> où pas est le pas entre chaque sous-réseau et octet est l'octet du masque à modifier
    """

    if(nb_machines < 256):
        return str(nb_machines) + " sur l'octet 4"
    elif(nb_machines < 65536):
        # // pour division entière
        return str(floor(nb_machines / 256)) + " sur l'octet 3"
    elif(nb_machines < 16777216):
        return str(floor(nb_machines / 65536)) + " sur l'octet 2"
    elif(nb_machines < 4294967296):
        return str(floor(nb_machines / 16777216)) + " sur l'octet 1"
    return 

# Vérification de la possibilité de faire une découpe classique
def verify_subnetting_possibility(network, nb_machines_list):
    """Vérifie si une découpe classique est possible

        Args: 
            network (IPv4Network) : IPv4Network du réseau parent
            nb_machines_list (list[int]) : liste du nombre de machines par sous-réseau

        Returns: 
            true si une découpe classique est possible, false sinon
    """
    print("Decoupe classique possible ?:",(network.num_addresses)/len(nb_machines_list), ">=", calculate_nb_hosts_max(nb_machines_list))
    return (network.num_addresses)/len(nb_machines_list) >= calculate_nb_hosts_max(nb_machines_list)

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
            return (list[list[string]]) : Renvoie une liste de liste contenant les informations des sous-réseaux [adresse_sous_reseau, adresse_broadcast, premiere_ip, derniere_ip


        Raises:
            TooManyMachinesException : Lève une exception TooManyMachinesException si le nombre de sous-réseaux dépasse 100
    """
    if(not verify_subnetting_possibility(network, nb_machines_list)):
        raise ValueError("Découpe classique impossible avec les paramètres fournis.")
        
    nb_machines = calculate_nb_hosts_max(nb_machines_list)
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


# address = "18.0.0.0"
# if(not is_ip_valid(address)):
#     print("Adresse IP non valide")
#     exit()
# mask = "255.255.0.0"
# if(not is_mask_valid(mask)):
#     print("Masque non valide")
#     exit()

# # mask = define_mask_by_ip_class(create_ip_adress(adress))
# nb_machines_list = [7, 6, 5, 4, 3, 2, 1, 10, 1, 10, 5, 10, 1, 1, 1, 1, 1, 1]


# network = create_network(address, mask)
# print("Adresse réseau :", network.network_address)
# print("Masque :", network.netmask)
# print("Adresse de diffusion :", network.broadcast_address)
# print("Nombre d'hôtes :", network.num_addresses - 2)
# hosts = list(network.hosts())
# print("Plage d'adresses disponible :", hosts[0], "à", hosts[-1])


# if(verify_subnetting_possibility(network, nb_machines_list)):
#     try:
#         result = calculate_subnetting(network, nb_machines_list)
#         print(result)
#     except TooManyMachinesException as e:
#         print("Erreur :", e)
# elif(verify_vlsm_possibility(network, nb_machines_list)):
#     print("VLSM possible")
#     exit()
# else:
#     print("Découpe impossible")
#     exit()



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