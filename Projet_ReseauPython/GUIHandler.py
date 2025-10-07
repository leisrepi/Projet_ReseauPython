import tkinter as tk




import tkinter as tk
from tkinter import messagebox

# Constantes de taille de police
H1_FONT = ("Arial", 24, "bold")
H2_FONT = ("Arial", 20, "bold")
H3_FONT = ("Arial", 16, "bold")
P_FONT = ("Arial", 16)
P2_FONT = ("Arial", 14)

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

def show_main_window():
    global _root
    _root = tk.Tk()
    _root.title("Application Principale")
    _root.geometry("800x600")
    _root.resizable(False, False)

    _root.protocol("WM_DELETE_WINDOW", close_main_window)

    tk.Label(_root, text="Bienvenue dans l'application principale!", font=H1_FONT).pack(pady=20)

    # Frame 1 (gros bouton)
    frame1 = tk.Frame(_root, bg="#e0e0e0", bd=2, relief="raised", width=350, height=200)
    frame1.place(x=70, y=150)
    frame1.pack_propagate(False)
    label1 = tk.Label(frame1, text="Bouton 1", font=H2_FONT, bg="#e0e0e0")
    label1.pack(pady=20)
    button1 = tk.Button(frame1, text="Action 1", font=H3_FONT, width=15, height=2)
    button1.pack(pady=10)

    # Frame 2 (gros bouton)
    frame2 = tk.Frame(_root, bg="#d0d0ff", bd=2, relief="raised", width=350, height=200)
    frame2.place(x=400, y=150)
    frame2.pack_propagate(False)
    label2 = tk.Label(frame2, text="Bouton 2", font=H2_FONT, bg="#d0d0ff")
    label2.pack(pady=20)
    button2 = tk.Button(frame2, text="Action 2", font=H3_FONT, width=15, height=2)
    button2.pack(pady=10)

    
    
    _root.mainloop()
