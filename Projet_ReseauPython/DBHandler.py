import sqlite3 as sq
import AuthHandler as ath
import AppException 
#TODO : Gerer la recuperation pseudo grace a la session dans les méthode.

#Ouverture de la db
conn = sq.connect('DecoupeUtilisateurDB.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

#TODO supprimer la fonction lors du merge
def delete_subnetting(session, subnetting_id):
    print(subnetting_id ,"supprimé")
    
#TODO supprimer la fonction lors du merge
def get_all_subnettings_of_user(session):
    return [["Découpe1", "Jean", "192.168.0.1", "255.255.255.0"], ["Découpe2", "Jean", "192.168.0.2", "255.255.255.0"], ["Découpe3", "Jean", "192.168.0.3", "255.255.255.0"]]

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
        IdDR TEXT NOT NULL,
        NbMachine INTEGER NOT NULL DEFAULT 0,
        NumSR INTEGER NOT NULL,
        Pseudo TEXT NOT NULL,
        PRIMARY KEY (NumSR, IdDR, Pseudo),
        FOREIGN KEY (IdDR, Pseudo)
            REFERENCES DecoupeReseau(IdDR, Pseudo)
            ON DELETE CASCADE ON UPDATE CASCADE
    );
    ''')

    conn.commit()
    #print("DB créer")

def is_user_on_db(pseudo, motdepasse):
    """ Sert à vérifier si un utilisateur est déjà dans la base de donnée.
    
        Args:
            pseudo (String) : Pseudo de l'utilisateur.
            motdepasse (String) : Mot de passe lié a l'utilisateur.
        
        Returns:
            out: Renvoie True si l'utilisateur existe ou False si il n'éxiste pas.
    """
    
    if(pseudo is None or motdepasse is None):
        print("Aucun pseudo ou mot de passe insérer.")
        return False
    
    #récuperation du mdp hashé
    cursor.execute(""" SELECT MotDePasse FROM Utilisateur WHERE Pseudo = ? """, (pseudo,))
    try:
        hashedMDP = cursor.fetchone() #--> renvoie un tuple donc hashedMDP[0] est le Bytes que l'on doit envoyer
        if hashedMDP[0] == '':
            hashedMDP[0] = "None"
    except:
        hashedMDP = []
        hashedMDP.append(ath.DUMMY_HASH)
        
    #vérification du mdp et renvoie d'acceptation ou de refus
    try:
        answer = ath.is_password_correct(motdepasse, hashedMDP[0])
    except:
        #print("L'utilisateur n'existe pas dans la db.")
        return False
    
    #print("L'utilisateur existe dans la db.")
    return answer
    
def get_user_subnetting(session,  id_subnetting):
    """ Sert à obtenir la découpe réseau spécifié de l'utilisateur.
    
        Args:
            pseudo (String) : Pseudo de l'utilisateur.
            id_subnetting (String) : Nom de la découpe du réseau.
        
        Returns:
            out: Renvoie la découpe réseau de l'utilisateur.
        Raises:
            AppException.NotAuthentifyException : si la session est échue.
    """
    if(ath.verify_session(session) is not True):
        raise AppException.NotAuthentifyException
    #Vérification de l'utilisateur et recherche de sa découpe dans la db
    cursor.execute(""" SELECT * FROM DecoupeReseau WHERE Pseudo = ? AND IdDR = ? """, (session.user_name, id_subnetting))
    return cursor.fetchall()

def get_user_specified_subnet(session, id_subnetting, numSR):
    """ Sert à obtenir le sous-réseaux spécifié de l'utilisateur.
    
        Args:
            pseudo (String) : Pseudo de l'utilisateur.
            id_subnetting (String) : Nom de la découpe du réseau.
            numSR (int) : Numéro du sous-réseaux.

        Returns:
            out: Renvoie le sous-réseaux de la découpe spécifié.

        Raises:
            AppException.NotAuthentifyException : si la session est échue.
    """
    if(ath.verify_session(session) is not True):
        raise AppException.NotAuthentifyException
    cursor.execute(""" SELECT * FROM SousReseau WHERE Pseudo = ? AND IdDR = ? AND NumSR = ?""", (session.user_name, id_subnetting, numSR))
    return cursor.fetchall()

def get_all_subnettings_of_user(session):
    """ Sert à obtenir tous les découpe-réseaux d'un utilisateur.
    
        Args:
            session (String) : Session de l'utilisateur actif
        
        Returns:
            out: Renvoie les découpe-réseaux de l'utilisateur. Revoie None si aucune découpe-réseaux n'est trouvé.
        
        Raises:
            sqlite3.IntegrityError : si la decoupe existe déjà.
            AppException.NotAuthentifyException : si la session est échue. 
    """
    if(ath.verify_session(session) is not True):
        raise AppException.NotAuthentifyException

    cursor.execute(""" SELECT * FROM DecoupeReseau WHERE Pseudo = ? """, (session.user_name,))
    data = cursor.fetchall()

    if(len(data) == 0):
        return None
    else:
        return data
    
def get_all_subnets_of_a_subnetting(session, subnetting_id):
    """ Sert à obtenir tous les sous-réseaux d'une découpe.
    
        Args:
            session (String) : Session de l'utilisateur actif
            subnetting_id (String) : Nom de la découpe-réseau.
        
        Returns:
            out: Renvoie les sous-réseaux de la decoupe spécifié de l'utilisateur. Revoie None si aucun sous-réseaux n'est trouvé.
        
        Raises:
            sqlite3.IntegrityError : si le sous-réseau n'existe pas.
            AppException.NotAuthentifyException : si la session est échue. 
    """

    if(ath.verify_session(session) is not True):
        raise AppException.NotAuthentifyException
    
    cursor.execute(""" SELECT * FROM SousReseau WHERE Pseudo = ? and IdDR = ?""", (session.user_name,subnetting_id,))
    data = cursor.fetchall()

    if(len(data) == 0):
        return None
    else:
        return data

def insert_user( pseudo, mdp):
    """ Sert à ajouter un utilisateur à la base de donnée.
    
        Args:
            pseudo (String) : Pseudo de l'utilisateur.
            mdp (String) : Mot de passe lié a l'utilisateur.
        
        Returns:
            out: Aucun retour (Void method)

        Raises:
            sqlite3.IntegrityError : si l'utilisateur existe déjà.
            AppException.UserAlreadyInDBException : si l'utilisateur existe déjà.
    """
    if(is_user_on_db(pseudo, mdp) is not False):
        #print("Refusé ! l'utilisateur existe deja.")
        return AppException.UserAlreadyInDBException

    mdp = ath.password_encrypt(mdp)
    cursor.execute("insert into Utilisateur(pseudo, MotDePasse) values (?, ?)", (pseudo, mdp))
    conn.commit()   
    #print('Utilisateur crée !')

def insert_decoupe(session, nomDecoupe, AdresseReseaux, masqueReseaux):
    """ Sert à ajouter une découpe à l'utilisateur spécifié.
    
        Args:
            session : Session d'authentification.
            nomDecoupe (String): Nom de la découpe à créer.
            pseudo (String) : Pseudo de l'utilisateur.
            id_subnetting (String) : Nom de la découpe du réseau.
            AdresseReseaux (String) : Adresse IP du réseau.
            masqueReseaux (String) : Masque du réseau.

        Returns:
            out: False si un ou plusieurs champ(s) est/sont manquant(s). Si la méthode ne renvoie rien c'est qu'aucune erreur n'a été commise.
        
        Raises:
            sqlite3.IntegrityError : si la decoupe existe déjà.
            AppException.NotAuthentifyException : si la session est échue.
    """
    if(ath.verify_session(session) is not True):
        raise AppException.NotAuthentifyException
    if(nomDecoupe is None or session.user_name is None or AdresseReseaux is None or masqueReseaux is None):
        #print("Un des champs est manquant !")
        return False
    
    cursor.execute("Insert into DecoupeReseau(IdDR, Pseudo, AdresseIP, Masque) values(?, ?, ?, ?)",(nomDecoupe,session.user_name, AdresseReseaux,masqueReseaux,))
    conn.commit()
    #print("insertion de la decoupe effectue")

def insert_sous_reseau(session, numSR, nbMachine, nomDecoupe):
    """ Sert à ajouter une découpe à l'utilisateur spécifié.
    
        Args:
            session : Session d'authentification.
            numSR (String): Numéro du sous réseau à créer.
            nbMachine (Int) : Nombre de machine shouaité par l'utilisateur.
            nomDecoupe (String) : Nom de la découpe ou insérer le sous-réseau.
            pseudo (String) : Pseudo de l'utilisateur.
            
        Returns:
            out: False si un ou plusieurs champ(s) est/sont manquant(s). La méthode ne renvoie rien si aucune erreur n'a été commise.
        
        Raises:
            sqlite3.IntegrityError : si le sous-réseaux existe déjà.
            AppException.NotAuthentifyException : si la session est échue.
    """
    if(ath.verify_session(session) is not True):
        raise AppException.NotAuthentifyException
    if(numSR is None or nbMachine is None or nomDecoupe is None or session.user_name is None):
        print("Un des champs est manquant !")
        return False
    cursor.execute("Insert into SousReseau(NumSR, NbMachine, IdDR, Pseudo) values(?, ?, ?, ?)",(numSR, nbMachine, nomDecoupe, session.user_name,))
    conn.commit()
    #print("Sous-réseaux creer")

def delete_user(user):
    cursor.execute("DELETE FROM Utilisateur WHERE Pseudo = ?", (user,))
    conn.commit()
    print('Utilisateur supprimer !')

def delete_subnetting( session, subNettingId):
    """ Sert à ajouter une découpe à l'utilisateur spécifié.
    
        Args:
            session : Session d'authentification.
            
            
        Returns:
            out: False si un ou plusieurs champ(s) est/sont manquant(s). La méthode ne renvoie rien si aucune erreur n'a été commise.
        
        Raises:
            sqlite3.IntegrityError : si la découpe-réseau n'existe pas.
            AppException.NotAuthentifyException : si la session est échue.
    """
    if(ath.verify_session(session) is not True):
        raise AppException.NotAuthentifyException
    cursor.execute("DELETE FROM DecoupeReseau where Pseudo = ? and IdDR = ?",( session.user_name, subNettingId,))
    conn.commit()
    #print("Découpe réseau effacer")

def close_cursor():
    conn.close()
    cursor.close()
    print("Le curseur est fermé")

def open_cursor():
    conn = sq.connect('DecoupeUtilisateurDB.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")