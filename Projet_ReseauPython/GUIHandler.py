import tkinter as tk




import tkinter as tk
from tkinter import messagebox

# Constantes de taille de police
H1_FONT = ("Arial", 24, "bold")
H2_FONT = ("Arial", 20, "bold")
H3_FONT = ("Arial", 16, "bold")
P_FONT = ("Arial", 16)
P2_FONT = ("Arial", 14)
P3_FONT = ("Arial", 12)

global _root
_root = None  # Variable globale pour la fenêtre principale

def init_GUI():
    show_login_window()

def show_login_window():
    root = tk.Tk()
    root.title("Connexion")
    root.geometry("500x300")
    root.resizable(False, False)


    label_font = H3_FONT
    entry_font = P_FONT
    button_font = H3_FONT


    tk.Label(root, text="Email:", font=label_font).pack(pady=(20, 0))
    email_entry = tk.Entry(root, width=30, font=entry_font)
    email_entry.pack(pady=5)

    tk.Label(root, text="Mot de passe:", font=label_font).pack(pady=(10, 0))
    password_entry = tk.Entry(root, show="*", width=30, font=entry_font)
    password_entry.pack(pady=5)

    def on_login():
        email = email_entry.get()
        password = password_entry.get()
        # Ici, vous pouvez ajouter la logique de connexion
        messagebox.showinfo("Info", f"Email: {email}\nMot de passe: {password}")
        #TODO : verifier si les identifiants sont corrects avant d'ouvrir la fenetre principale
        #TODO : ouvrir la fenetre en lui fournissant l'id de l'utilisateur
        root.destroy()
        show_main_window()

    tk.Button(root, text="Se connecter", command=on_login, font=button_font).pack(pady=20)

    root.mainloop()

def confirmation_popup(message ):
    return messagebox.askyesno("Confirmation", message)
    

def close_main_window():
    global _root
    #si _root existe on le supprime
    if _root:
        if confirmation_popup("Voulez-vous vraiment quitter ?"):
            _root.destroy()
            _root = None
    else:
        # Si _root n'existe pas, on affiche un message en gui
        messagebox.showwarning("Avertissement", "La fenêtre principale n'existe pas.")


def create_page1(parent):
    frame = tk.Frame(parent)
    def add_placeholder(entry, placeholder):
        entry.insert(0, placeholder)
        entry.config(fg='grey')
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, 'end')
                entry.config(fg='black')
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg='grey')
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

    # Conteneur principal horizontal
    main_row = tk.Frame(frame)
    main_row.pack(fill="both", expand=True)

    # Partie gauche (déjà existante)
    left_col = tk.Frame(main_row)
    left_col.pack(side="left", padx=20, pady=10, fill="y")

    # Ligne 1
    row1 = tk.Frame(left_col)
    row1.pack(pady=10)
    ipv4_entry = tk.Entry(row1, font=H2_FONT, bd=2, relief="solid", width=20, justify='center')
    ipv4_entry.pack(side="left", padx=10)
    add_placeholder(ipv4_entry, "IPV4")
    mask_entry = tk.Entry(row1, font=P3_FONT, bd=2, relief="solid", width=28, justify='center')
    mask_entry.pack(side="left", padx=10)
    add_placeholder(mask_entry, "Masque 255.255.255.255\nou /26")

    # Ligne 2
    row2 = tk.Frame(left_col)
    row2.pack(pady=10)
    reseau_entry = tk.Entry(row2, font=H3_FONT, bd=2, relief="solid", width=20, justify='center')
    reseau_entry.pack(side="left", padx=10)
    add_placeholder(reseau_entry, "Réseau")
    broadcast1_entry = tk.Entry(row2, font=H3_FONT, bd=2, relief="solid", width=28, justify='center')
    broadcast1_entry.pack(side="left", padx=10)
    add_placeholder(broadcast1_entry, "Broadcast")

    # Ligne 3
    row3 = tk.Frame(left_col)
    row3.pack(pady=10)
    sous_reseau_entry = tk.Entry(row3, font=H3_FONT, bd=2, relief="solid", width=20, justify='center')
    sous_reseau_entry.pack(side="left", padx=10)
    add_placeholder(sous_reseau_entry, "sous-Réseau")
    broadcast2_entry = tk.Entry(row3, font=H3_FONT, bd=2, relief="solid", width=28, justify='center')
    broadcast2_entry.pack(side="left", padx=10)
    add_placeholder(broadcast2_entry, "Broadcast")

    # Séparateur vertical
    sep = tk.Frame(main_row, width=2, bg="black", height=200)
    sep.pack(side="left", fill="y", padx=10, pady=10)

    # Partie droite (nouvelle)
    right_col = tk.Frame(main_row)
    right_col.pack(side="left", padx=20, pady=10, fill="y")

    # Ligne 1 droite : adresse ip, adresse réseau
    row1r = tk.Frame(right_col)
    row1r.pack(pady=10)
    ip_addr_entry = tk.Entry(row1r, font=H3_FONT, bd=2, relief="solid", width=28, justify='center')
    ip_addr_entry.pack(side="left", padx=10)
    add_placeholder(ip_addr_entry, "Adresse IP")
    net_addr_entry = tk.Entry(row1r, font=H3_FONT, bd=2, relief="solid", width=28, justify='center')
    net_addr_entry.pack(side="left", padx=10)
    add_placeholder(net_addr_entry, "Adresse Réseau")

    # Ligne 2 droite : 1ere adresse, 2eme adresse
    row2r = tk.Frame(right_col)
    row2r.pack(pady=10)
    first_addr_entry = tk.Entry(row2r, font=H3_FONT, bd=2, relief="solid", width=28, justify='center')
    first_addr_entry.pack(side="left", padx=10)
    add_placeholder(first_addr_entry, "1ère adresse")
    second_addr_entry = tk.Entry(row2r, font=H3_FONT, bd=2, relief="solid", width=28, justify='center')
    second_addr_entry.pack(side="left", padx=10)
    add_placeholder(second_addr_entry, "2ème adresse")

    # Rectangle vert sous les champs de la partie droite
    green_rect = tk.Label(right_col, text="", bg="#00FF00", width=62, height=4, bd=2, relief="solid")
    green_rect.pack(pady=30)

    return frame
    frame = tk.Frame(parent)



def create_page2(parent):
    frame = tk.Frame(parent)
    label = tk.Label(frame, text="Page 2", font=H1_FONT)
    label.pack(pady=40)
    label2 = tk.Label(frame, text="Voici une autre ligne de texte pour la page 2.", font=P_FONT)
    label2.pack(pady=10)
    return frame

def create_page3(parent):
    frame = tk.Frame(parent)
    label = tk.Label(frame, text="Page 3", font=H1_FONT)
    label.pack(pady=40)
    label2 = tk.Label(frame, text="Voici une autre ligne de texte pour la page 3.", font=P_FONT)
    label2.pack(pady=10)
    return frame

def show_main_window():
    global _root
    _root = tk.Tk()
    _root.title("Application Principale")
    _root.geometry("1600x800")
    _root.resizable(False, False)

    _root.protocol("WM_DELETE_WINDOW", close_main_window)

    # Système de pages avec frames empilées
    container = tk.Frame(_root)
    container.pack(expand=True, fill="both")

    pages = {}
    pages[1] = create_page1(container)
    pages[2] = create_page2(container)
    pages[3] = create_page3(container)
    for i in range(1, 4):
        pages[i].place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_page(page_num):
        pages[page_num].tkraise()

    # Barre de navigation
    nav_frame = tk.Frame(_root)
    nav_frame.pack(side="bottom", fill="x")
    tk.Button(nav_frame, text="Page 1", font=H3_FONT, command=lambda: show_page(1)).pack(side="left", expand=True, fill="x")
    tk.Button(nav_frame, text="Page 2", font=H3_FONT, command=lambda: show_page(2)).pack(side="left", expand=True, fill="x")
    tk.Button(nav_frame, text="Page 3", font=H3_FONT, command=lambda: show_page(3)).pack(side="left", expand=True, fill="x")

    show_page(1)
    _root.mainloop()
