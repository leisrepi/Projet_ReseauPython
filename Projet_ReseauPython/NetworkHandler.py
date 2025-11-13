# --------------------------------------
#             Imports
# --------------------------------------

from ipaddress import IPv4Address, IPv4Network, AddressValueError, NetmaskValueError
from AppException import InvalidMaskException, MaskNotInRangeException, SNMaskErrorException
from AddressHandler import is_ip_valid, create_ip_address
import re

# --------------------------------------
#             Fonctions
# --------------------------------------

#Retourne l'Ip du réseau et son adresse broadcast et le sous réseaux si possible
def get_network_information_from_ip_address_and_mask(IpAddress, SNMask):

    """ Retourne les infos du réseaux.

        Args:
            IpAddress (String) : adresse ip en format string
            SNMask (String) : masque lier à l'adresse ip en format string
            
        Returns:
            Adresse du réseaux et son broadcast. Adresse sous-réseaux et son broadcast.
            Si le sous réseaux est impossible il renverra 'None' pour le sous réseaux et son broadcast.

        Raises:
            SNMaskErrorException: si le masque n'est pas correcte."""
    
    IpClient = create_ip_address(IpAddress)
    netMask = define_mask_by_ip_class(IpClient)
    IpNetwork = create_network(IpAddress, netMask, strict=False)

    #vérification de l'appartenance du masque dde sous réseaux par rapport a celui du réseaux (vérification que celui-ci n'est pas plus grand)
    if(str(IpNetwork.netmask) < SNMask):
        raise SNMaskErrorException 
    #TODO: gérer l'erreur dans le cas ou le sous réseaux est plus grand que le réseaux lui meme

    if(IpNetwork.netmask == SNMask): #Vérification de la possibilité de sous-réseaux
        return IpNetwork.network_address, IpNetwork.broadcast_address, None, None
    
    for SNIp in IpNetwork.hosts(): #boucle de recherche du sous réseaux dans lequel se trouve l'adresse Ip du client
        SNIpAddress = SNIp
    
    SNBroadcast = IPv4Network(str(SNIpAddress)+"/"+SNMask, strict=False).broadcast_address
    return IpNetwork.network_address, IpNetwork.broadcast_address, SNIpAddress, SNBroadcast

# Vérification de la validité du masque.
def validate_mask_format(mask, *, classful: bool = None):
    """Vérifie le format d'un masque (classful ou classless ou indifférent)

    Args:
        mask (string): chaîne de caractères du masque
        classful (bool, optional): Indique si le masque doit être vérifié en classful (True), classless (False) ou indifférent (None). Par défaut à None.

    Raises:
        InvalidMaskException : Si le masque est invalide
        MaskNotInRangeException : Si le masque n'est pas dans les bornes autorisées (/8 à /29 = 255.0.0.0 à 255.255.255.248)
    """
    mask = mask.strip()
    # Vérification du format du masque (peut importe si classful ou classless)
    if(classful is None):
        if(mask[0] != "/"):
            mask = "/" + mask
        try:
            network = IPv4Network(("0.0.0.0"+mask), strict=False) 
            if(not network.num_addresses in range(8, 16777217)): # entre /8 et /29
                raise MaskNotInRangeException("Masque ne se trouve pas entre /8 et /29")
        except NetmaskValueError:
            raise InvalidMaskException("Masque invalide")  
        
    # Vérification du classful    
    elif(classful):
    
        # Vérification du format du masque (par regex)
        if(not re.search(r"^((255|254|252|248|240|224|192|128|0)\.){3}(255|254|252|248|240|224|192|128|0)$", mask)):
            raise InvalidMaskException("Masque invalide")
        
        # Vérification des bornes du masque (entre le /8 et le /29)
        if(mask < "255.0.0.0" or mask > "255.255.255.248"):
            raise MaskNotInRangeException("Masque ne se trouve pas entre 255.0.0.0 et 255.255.255.248")
        
        # Vérification des octets du masque (par exemple refuser 255.0.128.0)
        mask_parts = [int(part) for part in mask.split(".")]
        for i in range(4):
            # S'il s'agit du premier octet, on vérifie s'il est différent de 255 (car 255.0.0.0 est le masque minimal), 
            # sinon on initialise la variable previous_byte
            if(i == 0):
                if(mask_parts[i] != 255):
                    raise InvalidMaskException("Masque invalide")
                else:
                    previous_byte = mask_parts[i]
                    continue
            
            # Pour les octets suivants, on vérifie si l'octet précédent n'est pas égal à 255, 
            # que l'octet actuel soit égal à 0 (car 255.x.0.x n'est pas valide)
            if(previous_byte != 255 and mask_parts[i] != 0):
                raise InvalidMaskException("Masque invalide")
            
            previous_byte = mask_parts[i]

    # Vérification du classless
    else:   
        if(mask[0] != "/"):
            raise InvalidMaskException("Masque invalide")
        try:
            prefix_length = int(mask[1:])
            if(prefix_length < 0 or prefix_length > 32):
                raise InvalidMaskException("Masque invalide")
            if(prefix_length < 8 or prefix_length > 29):
                raise MaskNotInRangeException("Masque ne se trouve pas entre /8 et /29")
        except ValueError:
            raise InvalidMaskException("Masque invalide")

# Vérification de la validité du masque.
def validate_mask_format(mask, *, classful: bool = None):
    """Vérifie le format d'un masque (classful ou classless ou indifférent)

    Args:
        mask (string): chaîne de caractères du masque
        classful (bool, optional): Indique si le masque doit être vérifié en classful (True), classless (False) ou indifférent (None). Par défaut à None.

    Raises:
        InvalidMaskException : Si le masque est invalide
        MaskNotInRangeException : Si le masque n'est pas dans les bornes autorisées (/8 à /29 = 255.0.0.0 à 255.255.255.248)
    """

    # Vérification du format du masque (peut importe si classful ou classless)
    if(classful is None):
        if(mask[0] != "/"):
            mask = "/" + mask
        try:
            network = IPv4Network(("0.0.0.0"+mask), strict=False) 
            if(not network.num_addresses in range(8, 16777217)): # entre /8 et /29
                raise MaskNotInRangeException("Masque ne se trouve pas entre /8 et /29")
        except NetmaskValueError:
            raise InvalidMaskException("Masque invalide")  
        
    # Vérification du classful    
    elif(classful):
    
        # Vérification du format du masque (par regex)
        if(not re.search(r"^((255|254|252|248|240|224|192|128|0)\.){3}(255|254|252|248|240|224|192|128|0)$", mask)):
            raise InvalidMaskException("Masque invalide")
        
        # Vérification des bornes du masque (entre le /8 et le /29)
        if(mask < "255.0.0.0" or mask > "255.255.255.248"):
            raise MaskNotInRangeException("Masque ne se trouve pas entre 255.0.0.0 et 255.255.255.248")
        
        # Vérification des octets du masque (par exemple refuser 255.0.128.0)
        mask_parts = [int(part) for part in mask.split(".")]
        for i in range(4):
            # S'il s'agit du premier octet, on vérifie s'il est différent de 255 (car 255.0.0.0 est le masque minimal), 
            # sinon on initialise la variable previous_byte
            if(i == 0):
                if(mask_parts[i] != 255):
                    raise InvalidMaskException("Masque invalide")
                else:
                    previous_byte = mask_parts[i]
                    continue
            
            # Pour les octets suivants, on vérifie si l'octet précédent n'est pas égal à 255, 
            # que l'octet actuel soit égal à 0 (car 255.x.0.x n'est pas valide)
            if(previous_byte != 255 and mask_parts[i] != 0):
                raise InvalidMaskException("Masque invalide")
            
            previous_byte = mask_parts[i]

    # Vérification du classless
    else:   
        if(mask[0] != "/"):
            raise InvalidMaskException("Masque invalide")
        try:
            prefix_length = int(mask[1:])
            if(prefix_length < 0 or prefix_length > 32):
                raise InvalidMaskException("Masque invalide")
            if(prefix_length < 8 or prefix_length > 29):
                raise MaskNotInRangeException("Masque ne se trouve pas entre /8 et /29")
        except ValueError:
            raise InvalidMaskException("Masque invalide")


# Vérification de la validité du masque.
def is_mask_valid(mask):
    """Vérifie si un masque est valide

    Args:
        mask (string): chaîne de caractères du masque
    
    Returns:
        return (boolean): Renvoie true si le masque est valide, false sinon

    Raises:
        InvalidMaskException : Si le masque est invalide
    """
    if (mask == "" or mask is None):
        return False
    if(mask[0] != "/"):
        mask = "/" + mask
    if(mask[1] == "0"):
        return False
    try:
        IPv4Network(("0.0.0.0"+mask), strict=False)   
        return True
    except NetmaskValueError:
        return False
    
# Création d'un réseau à partir d'une adresse IP et d'un masque (renvoie None si le masque n'est pas valide)
def create_network(address, mask):
    """Crée un réseau à partir d'une adresse IP et d'un masque

        Args:
            address (string) : chaîne de caractères de l'adresse IP
            mask (string) : chaîne de caractères du masque

        Returns:
            return (IPv4Network) : Renvoie une instance de IPv4Network

        Raises:
            InvalidMaskException : si le masque n'est pas valide
            AddressValueError : si l'adresse IP n'est pas valide
    """ 
    if(not is_mask_valid(mask)):
        raise InvalidMaskException("Masque non valide ou vide")
    if(mask[0] != "/"):
        mask = "/" + mask
    try:   
        return IPv4Network((address.strip() + mask.strip()), strict=False)
    except AddressValueError:
        raise AddressValueError("Adresse IP non valide")
    except NetmaskValueError:
        raise InvalidMaskException("Masque non valide")

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

#Vérifie si l'adresse IP entré fait bien parti du réseau entré
def check_ip_network(page2):
    ip = page2.ip_var.get().strip()
    reseau_input = page2.reseau_var.get().strip()
    masque_input = page2.masque_var.get().strip()

    #Validation de l'IP
    if not is_ip_valid(ip):
        print(reseau_input)
        page2._set_status("Adresse IP invalide", ok=False)
        page2._set_details("")
        raise AddressValueError("Adresse IP invalide")
    
    #Détermination reseau_normalise et masque_a_utiliser
    reseau_normalise = None
    masque_a_utiliser = None
    masque_class = None # Evite une erreur local si on veut l'utiliser dans ce scope

    if not reseau_input:
        page2._set_status("Réseau/sous-réseau manquant", ok=False)
        page2._set_details("")
        raise AddressValueError("Veuillez saisir un réseau ou sous-réseau")
    
    if "/" in reseau_input:
        #CIDR direct (sous-réseau)
        net = create_network(reseau_input)
        reseau_normalise = str(net.network_address)
        masque_a_utiliser = str(net.netmask)
    else:
        if not is_ip_valid(reseau_input):
            raise AddressValueError("Adresse réseau invalide")
        if masque_input:
            try:
                validate_mask_format(masque_input)
            except InvalidMaskException:
                raise InvalidMaskException("Masque invalide(utilisez '/n' ou '255.255.255.x')")
            except MaskNotInRangeException:
                raise MaskNotInRangeException("Veuillez entrer un masque se trouvant entre /8 et /29 (ou 255.0.0.0 et 255.255.255.248)")
            masque_a_utiliser = masque_input
        else:
            #Masque de classé basé sur l'adresse de réseau
            reseau_ip_obj = create_ip_address(reseau_input)
            try:
                masque_class = define_mask_by_ip_class(reseau_ip_obj)
            except InvalidMaskException:
                raise InvalidMaskException("Impossible de déduire un masque de classe")
            masque_a_utiliser = masque_class
        reseau_normalise = reseau_input
    # except Exception as e :
    #     messagebox.showerror("Erreur", str(e))
    #     self._set_status("Entrée invalides",ok=False)
    #     self._set_details("")
    #     return
		
    #Appartenance + bornes
    appartient = appartient_au_reseau(ip, reseau_normalise, masque_a_utiliser)
    debut, fin = bornes(reseau_normalise, masque_a_utiliser)
    addr_net, addr_bcast = get_network_address_and_broadcast(reseau_normalise, masque_a_utiliser)

    statut = f"{ip} et {addr_net} {masque_a_utiliser} -> {'oui' if appartient else 'non'}"
    page2._set_status(statut, ok=appartient)

    #Les détails
    lignes = []
    print(masque_a_utiliser)
    lignes.append(f"Réseau analysé : {addr_net} {masque_a_utiliser}")
    if addr_net and addr_bcast:
        lignes.append(f"Adresse réseau : {addr_net}")
        lignes.append(f"Adresse broadcast : {addr_bcast}")
    
    if debut and fin:
        lignes.append(f"Première IP hôte : {debut}")
        lignes.append(f"Dernière IP hôte : {fin}")
    else:
        lignes.append("Pas d'adresses hôte (préfixe /31 ou /32)")

    page2._set_details("\n".join(lignes))

    #Vérifier si une IP appartient bien au réseau
def appartient_au_reseau(ip_str, reseau_str, masque_str):
    if(masque_str[0] != "/"):
        masque_str = "/" + masque_str
    try:
        ip=create_ip_address(ip_str)
        reseau = IPv4Network(f"{reseau_str}{masque_str}", strict=False)
        return ip in reseau
    except ValueError:
        return False

#Donner les ip machines (début et fin) d'un réseau
def bornes(reseau_str, masque_str):
    if(masque_str[0] != "/"):
        masque_str = "/" + masque_str
    try:
        reseau = IPv4Network(f"{reseau_str}{masque_str}", strict=False)
        if reseau.num_addresses <= 2:
            return(None, None)
        debut = IPv4Address(int(reseau.network_address)+1)
        fin = IPv4Address(int(reseau.broadcast_address)-1)
        return (debut,fin)
    except ValueError:
        return(None, None)
    
#TODO mettre commentaires :)
#Aides internes pour l'UI
def normaliser_masque_saisie(saisie_masque: str):
    """
    Accepte '255.255.255.0' ou '/24' et renvoie un masque décimal normalisé '255.255.255.0'.
    Renvoie None si invalide.
    """
    if saisie_masque is None:
        raise InvalidMaskException("Masque invalide(utilisez '/n' ou '255.255.255.x')")
    
    s = str(saisie_masque).strip()
    if not s:
        raise InvalidMaskException("Masque invalide(utilisez '/n' ou '255.255.255.x')")

    #Cas longueur de préfixe
    if s.startswith("/"):
        s = s[1:]
    if s.isdigit():
        p = int(s)
    if p <= 7 or p >= 30:
        raise MaskNotInRangeException("Veuillez entrer un masque se trouvant entre /8 et /29 (ou 255.0.0.0 et 255.255.255.248)")

    try:
        net_tmp = IPv4Network(f"0.0.0.0/{p}")
    except NetmaskValueError:
        raise InvalidMaskException("Masque invalide(utilisez '/n' ou '255.255.255.x')")
    #Cas masque décimal
    net_tmp = IPv4Network(f"0.0.0.0/{p}")
    return str(net_tmp.netmask)
    
    
    # if not saisie_masque:
    #     return None
    # if saisie_masque.startswith("/"):
    #     p = int(saisie_masque[1:])
    #     net_tmp = IPv4Network(f"0.0.0.0/{p}")
    #     return str(net_tmp.netmask)
    # #sinon décimal
    # net_tmp = IPv4Network(f"0.0.0.0/{saisie_masque}")
    # return str(net_tmp.netmask)
    

def get_network_address_and_broadcast(reseau_str, masque_str):
    if(masque_str[0] != "/"):
        masque_str = "/" + masque_str
    try:
        net = IPv4Network(f"{reseau_str}{masque_str}",strict=False)
        return str(net.network_address), str(net.broadcast_address)
    except Exception:
        return None, None

# --------------------------------------
#             Tests
# --------------------------------------

# # sans spécification

# print(validate_mask_format("255.0.0.0")) # true
# print(validate_mask_format("/16"))       # true
# try:
#     print(validate_mask_format("254.0.0.0")) # false
# except MaskNotInRangeException as e:
#     print(e)
# try:
#     print(validate_mask_format("255.255.255.252")) # false
# except MaskNotInRangeException as e:
#     print(e)
# try:
#     print(validate_mask_format("/7")) # false
# except MaskNotInRangeException as e:
#     print(e)
# try:
#     print(validate_mask_format("/30"))
# except MaskNotInRangeException as e:
#     print(e)
# try:
#     print(validate_mask_format("255.0.255.0")) # false
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("/33"))       # false
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("255-2102-1")) # false
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("255.0.0.0.0")) # false
# except InvalidMaskException as e:
#     print(e)
# print()

# # classful
# #print(validate_mask_format("/8", False))
# try:
#     print(validate_mask_format("255.0.0.0", classful=True)) # true
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("/16", classful=True))       # false
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("255.0.255.0", classful=True)) # false
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("/33", classful=True))       # false
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("255-2102-1", classful=True)) # false
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("254.0.0.0", classful=True)) # false
# except MaskNotInRangeException as e:
#     print(e)
# try:
#     print(validate_mask_format("255.255.255.252", classful=True)) # false
# except MaskNotInRangeException as e:
#     print(e)
# try:
#     print(validate_mask_format("255.0.0.0.0", classful=True)) # false
# except InvalidMaskException as e:
#     print(e)
# print()

# # classless
# try:
#     print(validate_mask_format("/16", classful=False)) # true
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("255.0.0.0", classful=False)) # false
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("255.0.255.0", classful=False)) # false
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("/33", classful=False))       # false
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("255-2102-1", classful=False)) # false
# except InvalidMaskException as e:
#     print(e)
# try:
#     print(validate_mask_format("/7", classful=False)) # false
# except MaskNotInRangeException as e:
#     print(e)
# try:
#     print(validate_mask_format("/30", classful=False))
# except MaskNotInRangeException as e:
#     print(e)
# print()