import sqlite3 as sq
import AuthHandler as ath

class DBService():

    containerService = None

    def __new__(cls):
        raise RuntimeError("Singleton : Utiliser le get pour instancier si non-existant")

    def __init__(self):
        pass

    @classmethod
    def get_instance(classe):
        if(classe.containerService is None):
            classe.containerService = super().__new__(classe)
            classe.containerService.__init__()
        return classe.containerService
    
    #Ouverture de la db
    conn = sq.connect('DecoupeUtilisateurDB.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    def create_db():
        
        # Création des tables requises si non-existantes
        DBService.cursor.executescript('''
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

        DBService.conn.commit()
        print("DB créer")

    def is_user_on_db(pseudo, motdepasse):
        #récuperation du mdp hashé
        DBService.cursor.execute(""" SELECT MotDePasse FROM Utilisateur WHERE Pseudo = ? """, (pseudo,))
        hashedMDP = DBService.cursor.fetchone() #--> renvoie un tuple donc hashedMDP[0] est le Bytes que l'on doit envoyer
        #vérification du mdp et renvoie d'acceptation ou de refus
        return ath.password_verification(motdepasse, hashedMDP[0]) 
        
    def get_user_subnetting(pseudo, id_subnetting):
        #Vérification de l'utilisateur et recherche de sa découpe dans la db
        DBService.cursor.execute(""" SELECT * FROM DecoupeReseau WHERE Pseudo = ? AND IdDR = ? """, (pseudo, id_subnetting))
        return DBService.cursor.fetchall()

    def get_user_secified_subnet(pseudo, id_subnetting, numSR):
        DBService.cursor.execute(""" SELECT * FROM SousReseau WHERE Pseudo = ? AND IdDR = ? AND NumSR = ?""", (pseudo, id_subnetting, numSR))
        return DBService.cursor.fetchall()

    def insert_user(pseudo, mdp):
        mdp = ath.password_encrypt(mdp)
        DBService.cursor.execute("insert into Utilisateur(pseudo, MotDePasse) values (?, ?)", (pseudo, mdp))
        DBService.conn.commit()
        print('Utilisateur crée !')

    def insert_decoupe():
        DBService.cursor.execute("Insert into DecoupeReseau(IdDR, Pseudo, AdresseIP, Masque) values(?, ?, ?, ?)",("Animaux","Baptiste", "caca","cucu",))
        DBService.conn.commit()
        print("insertion decoupe OK")

    def insert_sous_reseau():
        DBService.cursor.execute("Insert into SousReseau(NumSR, NbMachine, IdDR, Pseudo) values(?, ?, ?, ?)",("1","4","Animaux","Baptiste",))


    def delete_user(user):
        DBService.cursor.execute("DELETE FROM Utilisateur WHERE Pseudo = ?", (user,))
        DBService.conn.commit()
        print('Utilisateur supprimer !')

    def close_cursor():
        DBService.conn.close()
        DBService.cursor.close()
        print("Le curseur est fermé")

    def open_cursor():
        DBService.conn = sq.connect('DecoupeUtilisateurDB.db')
        DBService.cursor = DBService.conn.cursor()
        DBService.cursor.execute("PRAGMA foreign_keys = ON;")