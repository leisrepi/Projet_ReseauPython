from ipaddress import IPv4Address, IPv4Network

#ceci est ce que j'ai ajouter ;)

#Adresse IP valide ou pas
def validation_ip(ip_string):
    try:
        IPv4Address(ip_string)
        return True
    except ValueError:
        return False

#Création d'une adresse IP en chaine de caractères -> None si adresse non valide   
def ip_adress_string(ip_string):
    try:
        return IPv4Address(ip_string)
    except ValueError:
        return None

#Définition du masque en fonction de la classe de l'adresse IP
def definition_masque(ip_adress):
    #Attribution des ip aux différentes classes (reprend la première adresse et le masque)
    class_a = IPv4Network(("0.0.0.0", "128.0.0.0"))
    class_b = IPv4Network(("128.0.0.0", "192.0.0.0"))
    class_c = IPv4Network(("192.0.0.0", "224.0.0.0"))

    #Attribution du masque en fonction des classes
    if ip_adress in class_a:
        return "255.0.0.0"
    elif ip_adress in class_b:
        return "255.255.0.0"
    elif ip_adress in class_c:
        return "255.255.255.0"
    else:
        return None

#Vérifier si une IP appartient bien au réseau
def appartient_au_reseau(ip_str, reseau_str, masque_str):
    try:
        ip=IPv4Address(ip_str)
        reseau = IPv4Network(f"{reseau_str}/{masque_str}", strict=False)
        return ip in reseau
    except ValueError:
        return False

#Donner les ip machines (début et fin) d'un réseau
def bornes(reseau_str, masque_str):
    try:
        reseau = IPv4Network(f"{reseau_str}/{masque_str}", strict=False)
        if reseau.num_addresses <= 2:
            return(None, None)
        debut = IPv4Address(int(reseau.network_address)+1)
        fin = IPv4Address(int(reseau.broadcast_address)-1)
        return (debut,fin)
    except ValueError:
        return(None, None)
    
#Programme principal
print("Vérification d'appartenance IP à un réseau IPv4\n")

#Ecriture de l'adresse IP par l'utilisateur
ip = input("Entrez une adresse IP : ")
while not validation_ip(ip):
    ip = input("Cette adresse n'est pas valide\nEntrez en une à nouveau : ")
#Réseau
ip_object = ip_adress_string(ip)
masque = definition_masque(ip_object)
if masque is None:
    print("Impossible de déterminer la classe de cette IP")

print(f"\nMasque de réseau : {masque}")
#Entrée du réseau et pas du sous-réseau
reseau  = input("Entrez le réseau (ex : 192.168.3.0) : ")
while not validation_ip(reseau):
    reseau = input("Adresse invalide\nVeuillez réessayez : ")
#Sous-réseau
entree_reseau = input("Entrez le sous-réseau (ex : 192.168.3.0/26) : ")

#Valeurs finales qui seront utilisées par tes fonctions inchangées
reseau_normalise = None
masque_a_utiliser = None

try:
    if "/" in entree_reseau:
        #CIDR
        net = IPv4Network(entree_reseau, strict=False)
        reseau_normalise = str(net.network_address)
        masque_a_utiliser = str(net.netmask)
        print(f"\nSous-réseau détecté : {net.with_netmask} (réseau {reseau_normalise} et masque {masque_a_utiliser})")
    else:
        #Adresse réseau seule
        while not validation_ip(entree_reseau):
            entree_reseau = input("Cette adresse n'est pas valide\nEntrez en une à nouveau : ")
        #Masque manuel (décimal ou CIDR)
        saisie_masque = input("Masque (décimal (255.255.255.0) ou CIDR(/26)) : ")

        if saisie_masque:
            if saisie_masque.startswith("/"):
                #L'utilisateur entre un préfixe (/26 par exemple)
                try:
                    p = int(saisie_masque[1:])
                    net_tmp = IPv4Network(f"0.0.0.0/{p}")
                    masque_a_utiliser = str(net_tmp.netmask)
                except Exception:
                    raise ValueError("CIDR invalide") #raise : sert à lever manuellement une execption pour signaler une erreur ou une condition anormale
            else:
                #masque décimal
                try:
                    net_tmp = IPv4Network(f"0.0.0.0/{saisie_masque}")
                    masque_a_utiliser = str(net_tmp.netmask) #normalisé
                except Exception:
                    raise ValueError("Masque décimal invalide")
        else:
            #Masque de classe basé sur l'adresse réseau et pas l'adresse IP saisie
            reseau_ip_object = ip_adress_string(entree_reseau)
            masque_class = definition_masque(reseau_ip_object)
            if masque_class is None:
                raise ValueError("Impossible de déduire un masque de classe (adresse réseau en classe D ou E)")
            masque_a_utiliser = masque_class
        reseau_normalise = entree_reseau
except ValueError as e:
    print(f"{e}")
    print("Fin du programme")

#Vérification d'appartenance + bornes
appartient = appartient_au_reseau(ip, reseau_normalise, masque_a_utiliser)
appartient_reseau = appartient_au_reseau(ip, reseau, masque)
#S'il appartient au réseau il sera noté d'un True si non false
print(f"\nEst-ce que l'IP {ip} appartient au sous-réseau {reseau_normalise} dont le masque est {masque_a_utiliser} ? {appartient}")
if appartient == True:
    debut, fin = bornes(reseau_normalise, masque_a_utiliser)
    if debut and fin:
        print(f"Premiere adresse IP machine : {debut}")
        print(f"Dernière adresse IP machine : {fin}")
    else:
        print("Ce (sous-)réseau ne possède pas d'adresse IP machine (préfixe /31 ou /32)")
    
print(f"\nEst-ce que l'IP {ip} appartient au réseau {reseau} dont le masque est {masque} ? {appartient}")

if appartient_reseau == True:
    debut_reseau, fin_reseau = bornes(reseau, masque)
    if debut_reseau and fin_reseau:
        print(f"Premiere adresse IP machine : {debut_reseau}")
        print(f"Dernière adresse IP machine : {fin_reseau}")
    else:
        print("Ce réseau ne possède pas d'adresse IP machine")
    print("Fin du programme")
else:
    print("Fin du programme")