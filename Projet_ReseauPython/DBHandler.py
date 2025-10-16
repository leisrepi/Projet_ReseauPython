import sqlite3 as sq


def create_db():
    # Connexion DB
    conn = sq.connect('DecoupeUtilisateurDB.db')
    cursor = conn.cursor()

    # Activation clés étrangères
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Création des tables
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS Utilisateur (
        Pseudo TEXT NOT NULL PRIMARY KEY,
        MotDePasse TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS DecoupeReseau (
        idDR TEXT NOT NULL,
        Pseudo TEXT NOT NULL,
        AdresseIP TEXT NOT NULL,
        Masque TEXT NOT NULL,
        IsClassfull BOOLEAN NOT NULL DEFAULT 0,
        PRIMARY KEY (idDR, Pseudo),
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
            REFERENCES DecoupeReseau(idDR, Pseudo)
            ON DELETE CASCADE ON UPDATE CASCADE
    );
    ''')

    conn.commit()
    cursor.close()
    conn.close()

    print("DB OK")

def is_user_on_db(pseudo, motdepasse):
    conn = sq.connect('DecoupeUtilisateurDB.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
        SELECT * FROM Utilisateur 
        WHERE Pseudo = ? AND MotDePasse = ?
    """, (pseudo, motdepasse))

    user = cursor.fetchone()
    conn.close()

    return user is not None
    
def get_user_subnetting(pseudo, id_subnetting):
    conn = sq.connect('DecoupeUtilisateurDB.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
        SELECT * FROM DecoupeReseau 
        WHERE Pseudo = ? AND idDR = ?
    """, (pseudo, id_subnetting))

def insert_user():
    conn = sq.connect('DecoupeUtilisateurDB.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("insert into Utilisateur(pseudo, MotDePasse) values (?, ?)", ('Babar', 'Elephant01'))
    conn.commit()
    conn.close()
    print('Utilisateur crée !')

def delete_user(user):
    conn = sq.connect('DecoupeUtilisateurDB.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("DELETE FROM Utilisateur WHERE Pseudo = ?", (user,))
    conn.commit()
    conn.close()
    print('Utilisateur supprimer !')

