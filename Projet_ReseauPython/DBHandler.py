import sqlite3 as sq
import AuthHandler


#Ouverture de la db
conn = sq.connect('DecoupeUtilisateurDB.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

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
    #récuperation du mdp hashé
    cursor.execute(""" SELECT MotDePasse FROM Utilisateur WHERE Pseudo = ? """, (pseudo,))
    hashedMDP = cursor.fetchone() #--> renvoie un tuple donc hashedMDP[0] est le Bytes que l'on doit envoyer
    #vérification du mdp et renvoie d'acceptation ou de refus
    return AuthHandler.is_password_correct(motdepasse, hashedMDP[0]) 
    
def get_user_subnetting(pseudo, id_subnetting):
    #Vérification de l'utilisateur et recherche de sa découpe dans la db
    cursor.execute(""" SELECT * FROM DecoupeReseau WHERE Pseudo = ? AND IdDR = ? """, (pseudo, id_subnetting))
    return cursor.fetchall()

def get_user_specified_subnet(pseudo, id_subnetting, numSR):
    cursor.execute(""" SELECT * FROM SousReseau WHERE Pseudo = ? AND IdDR = ? AND NumSR = ?""", (pseudo, id_subnetting, numSR))
    return cursor.fetchall()

def insert_user(pseudo, mdp):
    mdp = AuthHandler.password_encrypt(mdp)
    cursor.execute("insert into Utilisateur(pseudo, MotDePasse) values (?, ?)", (pseudo, mdp))
    conn.commit()   
    print('Utilisateur crée !')

def insert_decoupe():
    cursor.execute("Insert into DecoupeReseau(IdDR, Pseudo, AdresseIP, Masque) values(?, ?, ?, ?)",("Animaux","Baptiste", "caca","cucu",))
    conn.commit()
    print("insertion decoupe OK")

def insert_sous_reseau():
    cursor.execute("Insert into SousReseau(NumSR, NbMachine, IdDR, Pseudo) values(?, ?, ?, ?)",("1","4","Animaux","Baptiste",))

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