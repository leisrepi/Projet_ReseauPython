import tkinter as tk
from tkinter import ttk, messagebox
from ipaddress import IPv4Address, IPv4Network

#Fonctions inchangées depuis la version 3
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
    
#Aides internes pour l'UI
def normaliser_masque_saisie(saisie_masque: str):
    """
    Accepte '255.255.255.0' ou '/24' et renvoie un masque décimal normalisé '255.255.255.0'.
    Renvoie None si invalide.
    """
    if saisie_masque is None:
        return None
    
    s = str(saisie_masque).strip()
    if not s:
        return None
    
    s = s.replace(" ","")


    try:
        #Cas longueur de préfixe
        if s.startswith("/"):
            s = s[1:]
        if s.isdigit():
            p = int(s)
            if 0 <= p <= 32:
                net_tmp = IPv4Network(f"0.0.0.0/{p}")
                return str(net_tmp.netmask)
            return None
        #Cas masque décimal
        net_tmp = IPv4Network(f"0.0.0.0/{p}")
        return str(net_tmp.netmask)
    except Exception:
        return None
        """
        if not saisie_masque:
            return None
        if saisie_masque.startswith("/"):
            p = int(saisie_masque[1:])
            net_tmp = IPv4Network(f"0.0.0.0/{p}")
            return str(net_tmp.netmask)
        #sinon décimal
        net_tmp = IPv4Network(f"0.0.0.0/{saisie_masque}")
        return str(net_tmp.netmask)
        """
    except Exception:
        return None

def calculer_broadcast_network(reseau_str, masque_str):
    try:
        net = IPv4Network(f"{reseau_str}/{masque_str}",strict=False)
        return str(net.network_address), str(net.broadcast_address)
    except Exception:
        return None, None

#Interface tkinter
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vérification IP (Sous-)Réseau IPv4")
        self.geometry("640x240")
        self.minsize(580,380)

        #Styles
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        pad = {'padx' : 8, 'pady' : 6}

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        #Entrées
        ttk.Label(frame, text="Adresse IP à vérifier :").grid(row=0, column=0, stick="w", **pad)
        self.ip_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.ip_var, width=28).grid(row=0, column=1, sticky="we", **pad)

        ttk.Label(frame, text="Réseau ou sous-réseau :").grid(row=1, column=0, sticky="w", **pad)
        self.reseau_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.reseau_var, width=28).grid(row=1, column=1, sticky="we", **pad)
        ttk.Label(frame, text="ex: 192.168.3.0 ou 192.168.3.0/26").grid(row=1,column=2, sticky="we",**pad)
        
        ttk.Label(frame, text="Masque (optionnel si CIDR) :").grid(row=2, column=0, **pad)
        self.masque_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.masque_var, width=28).grid(row=2, column=1, **pad)
        ttk.Label(frame, text="ex: 255.255.255.192 ou /26").grid(row=2,column=2,sticky="w")

        #Boutons
        btns = ttk.Frame(frame)
        btns.grid(row=3, column=0, columnspan=3, sticky="we",**pad)
        ttk.Button(btns, text="Vérifier", command=self.verifier).pack(side="left", padx=4)
        ttk.Button(btns, text="Effacer", command=self.effacer).pack(side="left",padx=4)

        #Résultats
        sep = ttk.Separator(frame)
        sep.grid(row=4, column=0, columnspan=3, sticky="we", pady=(10,6))

        self.result_appartenance = ttk.Label(frame, text="",font=("TkDefaultFont",11,"bold"))
        self.result_appartenance.grid(row=5, column=0, columnspan=3, sticky="w", **pad)

        self.result_details = tk.Text(frame, height=9, width=72, wrap="word")
        self.result_details.grid(row=6, column=0, columnspan=3, sticky="nsew", **pad)
        self.result_details.configure(state="disabled")

        #Grille responsive
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(6, weight=1)

    def effacer(self):
        self.ip_var.set("")
        self.reseau_var.set("")
        self.masque_var.set("")
        self._set_status("", ok=None)
        self._set_details("")
    
    def _set_status(self, text, ok: bool | None):
        #Couleurs simples selon état
        if ok is True:
            fg = "#0a7d2b"  # vert
        elif ok is False:
            fg = "#b00020" #Rouge
        else:
            fg = ""
        self.result_appartenance.configure(text=text, foreground=fg)

    def _set_details(self, text):
        self.result_details.configure(state="normal")
        self.result_details.delete("1.0","end")
        self.result_details.insert("1.0",text)
        self.result_details.configure(state="disabled")
    
    def verifier(self):
        ip = self.ip_var.get().strip()
        reseau_input = self.reseau_var.get().strip()
        masque_input = self.masque_var.get().strip()

        #Validation de l'IP
        if not validation_ip(ip):
            messagebox.showerror("Erreur", "Adresse IP invalide")
            self._set_status("Adresse IP invalide", ok=False)
            self._set_details("")
            return
        
        #Détermination reseau_normalise et masque_a_utiliser
        reseau_normalise = None
        masque_a_utiliser = None
        masque_class = None # Evite une erreur local si on veut l'utiliser dans ce scope
        try:
            if not reseau_input:
                messagebox.showerror("Erreur", "Veuillez saisir un réseau ou sous-réseau")
                self._set_status("Réseau/sous-réseau manquant", ok=False)
                self._set_details("")
                return
            
            if "/" in reseau_input:
                #CIDR direct (sous-réseau)
                net = IPv4Network(reseau_input, strict=False)
                reseau_normalise = str(net.network_address)
                masque_a_utiliser = str(net.netmask)
            else:
                if not validation_ip(reseau_input):
                    raise ValueError("Adresse réseau invalide")

                if masque_input:
                    masque_norm = normaliser_masque_saisie(masque_input)
                    if masque_norm is None:
                        raise ValueError("Masque invalide(utilisez '/n' ou '255.255.255.x')")
                    masque_a_utiliser = masque_norm
                else:
                    #Masque de classé basé sur l'adresse de réseau
                    reseau_ip_obj = ip_adress_string(reseau_input)
                    masque_class = definition_masque(reseau_ip_obj)
                    if masque_class is None:
                        raise ValueError("Impossible de déduire un masque de classe")
                    masque_a_utiliser = masque_class
                reseau_normalise = reseau_input
        except Exception as e :
            messagebox.showerror("Erreur", str(e))
            self._set_status("Entrée invalides",ok=False)
            self._set_details("")
            return
        
        #Appartenance + bornes
        appartient = appartient_au_reseau(ip, reseau_normalise, masque_a_utiliser)
        debut, fin = bornes(reseau_normalise, masque_a_utiliser)
        addr_net, addr_bcast = calculer_broadcast_network(reseau_normalise, masque_a_utiliser)

        statut = f"{ip} et {reseau_normalise} / {masque_a_utiliser} -> {'oui' if appartient else 'non'}"
        self._set_status(statut, ok=appartient)

        #Les détails
        lignes = []
        lignes.append(f"Réseau analysé : {reseau_normalise} / {masque_a_utiliser}")
        if addr_net and addr_bcast:
            lignes.append(f"Adresse réseau : {addr_net}")
            lignes.append(f"Adresse broadcast : {addr_bcast}")
        
        if debut and fin:
            lignes.append(f"Première IP hôte : {debut}")
            lignes.append(f"Dernière IP hôte : {fin}")
        else:
            lignes.append("Pas d'adresses hôte (préfixe /31 ou /32)")

        self._set_details("\n".join(lignes))
if __name__ == "__main__":
    App().mainloop()