# --------------------------------------
#             Imports
# --------------------------------------

from ipaddress import IPv4Network, IPv4Address
from math import log2, ceil, floor

# --------------------------------------
#             Imports
# --------------------------------------

from ipaddress import IPv4Network, IPv4Address
from math import log2, ceil, floor
import tkinter as tk
from tkinter import ttk
# --------------------------------------
#             Fonctions
# --------------------------------------

# Vérification de la validité de l'adresse IP.
def is_ip_valide(ip):
    try:
        IPv4Address(ip)
        return True
    except ValueError:
        return False

# Calcul du pas.
def pas_calculation(nb_machines):
    if(nb_machines <= 256):
        return nb_machines, 4
    elif(nb_machines <= 65536):
        return nb_machines // 256, 3
    elif(nb_machines <= 16777216):
        return nb_machines // 65536, 2
    elif(nb_machines <= 4294967296):
        return nb_machines // 16777216, 1
    return 
    
            
    
# --------------------------------------
#             Variables
# --------------------------------------

# Définition des classes d'adresses IP (première et dernière adresse de chaque classe)
classeA = IPv4Network(("0.0.0.0", "128.0.0.0"))
classeB = IPv4Network(("128.0.0.0", "192.0.0.0"))
classeC = IPv4Network(("192.0.0.0", "224.0.0.0"))
classeD = IPv4Network(("224.0.0.0", "240.0.0.0"))

adresse_ip_string = "224.168.0.0"

classfull = True
nb_sr = 5
nb_machines = 10

# --------------------------------------
#               Main
# --------------------------------------


root = tk.Tk()
root.title("Tableau de données")
root.title("Tableau de données")

colonnes = ["Adresse de sous-réseau", "Adresse de broadcast", "Première IP", "Dernière IP"]
donnees = [
    [""],
    
]

donnees.append(["Adresse de sous-réseau", "Adresse de broadcast", "Première IP", "Dernière IP"])
tree = ttk.Treeview(root, columns=colonnes, show='headings')

# Définir les en-têtes
for col in colonnes:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor='center')

# Ajouter les lignes
for ligne in donnees:
    tree.insert('', 'end', values=ligne)

tree.pack(expand=True, fill='both')
root.mainloop()

# Vérification de la validité de l'adresse IP
if(not is_ip_valide(adresse_ip_string)):
    print("Adresse IP non valide")
    #exit()
adresse_ip = IPv4Address(adresse_ip_string)

# Détermination de la classe de l'adresse IP
if classfull: 
    if(adresse_ip in classeA):
        print("Classe A")
        masque = "255.0.0.0"
    elif(adresse_ip in classeB):
        print("Classe B")
        masque = "255.255.0.0"   
    elif(adresse_ip in classeC):
        print("Classe C")
        masque = "255.255.255.0"
    elif(adresse_ip in classeD):
        print("Classe D")
        masque = None
    else:
        print("Adresse IP non classée")
        exit()

# Si le masque est None, on ne peut pas découper le réseau (car par exemple en classe D)
if masque is None:
    print("Découpage impossible")
    exit()

# Force l'adresse donnée à se transformer en adresse réseau (dernier(s) octet(s) à 0) au lieu de causer une erreur
network = IPv4Network((adresse_ip, masque), strict=False)

# log2 exemple : log2(32) = 5 car 2^5 = 32
# ceil arrondi à l'entier supérieur donc si log2 = 4.1 -> 5
# puis 2^5 donnera l'exposant nécessaire pour le nombre d'hôtes par sous-réseau
# + 2 pour l'adresse de réseau et de diffusion
nb_machines = 2 ** ceil(log2((nb_machines + 2)))

print("Adresse réseau :", network.network_address)
print("Masque :", network.netmask)
print("Adresse de diffusion :", network.broadcast_address)
print("Nombre d'hôtes :", network.num_addresses - 2) 
print("Plage d'adresses disponible :", list(network.hosts())[0], "à", list(network.hosts())[-1])
print("Nombre de machines possible par sous-réseau :", floor(network.num_addresses/nb_sr))
print("Nombre de machines par sous-réseau", nb_machines)
print("Pas :", pas_calculation(nb_machines)[0], "sur le ", pas_calculation(nb_machines)[1], "ème octet")

# Vérification que le nombre de machines par sous-réseau est possible
if(nb_machines > floor((network.num_addresses) / nb_sr)):
    print("Trop de machines par sous-réseau")
    exit()

increment = 0

# Boucle d'affichage des sous-réseaux
for i in range(nb_sr):
    print("Sous-réseau", i+1)

    # S'il s'agit du premier sous-réseau, l'adresse de sous-réseau est l'adresse réseau (list(network.hosts()) ne prends que les adresses utilisables)
    if(i == 0):
        print("Adresse de sous-réseau :", network.network_address)
    else:
        print("Adresse de sous-réseau :", list(network.hosts())[i + increment - 1])

    # S'il s'agit du dernier sous-réseau, l'adresse de broadcast est l'adresse de broadcast du réseau (list(network.hosts()) ne prends que les adresses utilisables)
    if((i + increment + nb_machines - 2)  == network.num_addresses - 2):
        print("Adresse de broadcast :", network.broadcast_address)
    else:
        print("Adresse de broadcast :", list(network.hosts())[(i + increment + nb_machines - 2)])

    print("Première IP :", list(network.hosts())[i + increment])
    print("Dernière IP :", list(network.hosts())[(i + increment + nb_machines - 3)])

    increment += nb_machines - 1
    print()



#question à poser : En classfull, jusqu'a quelle classe faut-il aller pour déterminer le masque par défaut ? (A, B, C, ...) : Classe D
#question à poser : La découpe se fait-elle en classless ou classfull ? : les 2.
#question à poser : Faut-il refuser à l'utilisateur les adresses réservées ? : Oui
#question à poser : La première adresse IP lors de la découpe en SR doit-elle commencer par ?.?.?.0 : Oui
#question à poser : Faut-il mettre le pas ainsi que le nombre de machine par SR pour chaque SR ? : Non, on peut le mettre une fois au dessus de la découpe