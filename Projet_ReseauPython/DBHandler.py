import sqlite3 as sq
import AuthHandler
import AppException as appex

#Ouverture de la db
conn = sq.connect('DecoupeUtilisateurDB.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

#TODO : Vérifier le principe de session et autorisé les changement seulment quand la session est valide  

def create_db():
    
    # Création des tables requises si non-existantes
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS Utilisateur (
        Pseudo TEXT NOT NULL PRIMARY KEY,
        MotDePasse TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS DecoupeReseau (
        IdDR TEXT NOT NULL,
        Pseudo TEXT NOT NULL,
        AdresseIP TEXT NOT NULL,
        Masque TEXT NOT NULL,
        PRIMARY KEY (IdDR, Pseudo),
        FOREIGN KEY (Pseudo) REFERENCES Utilisateur(Pseudo)
            ON DELETE CASCADE ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS SousReseau (
        NumSR INTEGER NOT NULL,
        NbMachine INTEGER NOT NULL DEFAULT 0,
        IdDR TEXT NOT NULL,
        Pseudo TEXT NOT NULL,
        PRIMARY KEY (NumSR, IdDR, Pseudo),
        FOREIGN KEY (IdDR, Pseudo)
            REFERENCES DecoupeReseau(IdDR, Pseudo)
            ON DELETE CASCADE ON UPDATE CASCADE
    );
    ''')

    conn.commit()
    print("DB créer")

def is_user_on_db(pseudo, motdepasse):
    if(pseudo is None or motdepasse is None):
        print("Aucun pseudo ou mot de passe insérer.")
        return False
    #récuperation du mdp hashé
    cursor.execute(""" SELECT MotDePasse FROM Utilisateur WHERE Pseudo = ? """, (pseudo,))
    hashedMDP = cursor.fetchone() #--> renvoie un tuple donc hashedMDP[0] est le Bytes que l'on doit envoyer
    #vérification du mdp et renvoie d'acceptation ou de refus
    try:
        answer = AuthHandler.is_password_correct(motdepasse, hashedMDP[0])
    except:
        print("L'utilisateur n'existe pas dans la db.")
        return False
    
    print("L'utilisateur existe dans la db.")
    return answer
    
def get_user_subnetting(pseudo, id_subnetting):
    """ Sert à obtenir la découpe réseau spécifié de l'utilisateur.
    
        Args:
            pseudo (String) : Pseudo de l'utilisateur.
            id_subnetting (String) : Nom de la découpe du réseau.
        
        Returns:
            Renvoie la découpe réseau de l'utilisateur.
    """
    #Vérification de l'utilisateur et recherche de sa découpe dans la db
    cursor.execute(""" SELECT * FROM DecoupeReseau WHERE Pseudo = ? AND IdDR = ? """, (pseudo, id_subnetting))
    return cursor.fetchall()

def get_user_specified_subnet(pseudo, id_subnetting, numSR):
    """ Sert à obtenir le sous-réseaux spécifié de l'utilisateur.
    
        Args:
            pseudo (String) : Pseudo de l'utilisateur.
            id_subnetting (String) : Nom de la découpe du réseau.
            numSR (int) : Numéro du sous-réseaux.
        
        Returns:
            Renvoie le sous-réseaux de la découpe spécifié.
    """
    cursor.execute(""" SELECT * FROM SousReseau WHERE Pseudo = ? AND IdDR = ? AND NumSR = ?""", (pseudo, id_subnetting, numSR))
    return cursor.fetchall()

def insert_user(pseudo, mdp):
    if(is_user_on_db(pseudo, mdp) is not False):
        print("Refusé ! l'utilisateur existe deja .")
        return appex.UserAlreadyInDBException

    mdp = AuthHandler.password_encrypt(mdp)
    cursor.execute("insert into Utilisateur(pseudo, MotDePasse) values (?, ?)", (pseudo, mdp))
    conn.commit()   
    print('Utilisateur crée !')

def insert_decoupe(nomDecoupe, pseudo, AdresseReseaux, masqueReseaux):
    if(nomDecoupe is None or pseudo is None or AdresseReseaux is None or masqueReseaux is None):
        print("Un des champs est manquant !")
        return False
    
    cursor.execute("Insert into DecoupeReseau(IdDR, Pseudo, AdresseIP, Masque) values(?, ?, ?, ?)",(nomDecoupe,pseudo, AdresseReseaux,masqueReseaux,))
    conn.commit()
    print("insertion de la decoupe effectue")

def insert_sous_reseau(numSR, nbMachine, nomDecoupe, pseudo):
    if(numSR is None or nbMachine is None or nomDecoupe is None or pseudo is None):
        print("Un des champs est manquant !")
        return False
    cursor.execute("Insert into SousReseau(NumSR, NbMachine, IdDR, Pseudo) values(?, ?, ?, ?)",(numSR, nbMachine, nomDecoupe, pseudo,))
    conn.commit()
    print("Sous-réseaux creer")

def delete_user(user):
    cursor.execute("DELETE FROM Utilisateur WHERE Pseudo = ?", (user,))
    conn.commit()
    print('Utilisateur supprimer !')

def close_cursor():
    conn.close()
    cursor.close()
    print("Le curseur est fermé")

def open_cursor():
    conn = sq.connect('DecoupeUtilisateurDB.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")