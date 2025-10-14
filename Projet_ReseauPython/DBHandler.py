import sqlite3 as sq



def createDB():

    conn = sq.connect('DecoupeUtilisateurDB.db')
    cursor = conn.cursor()

    cursor.execute
    ('''
    CREATE TABLE IF NOT EXISTS Utilisateur (
    Pseudo varchar(40) not null,
    MotDePasse varchar(60) not null,
    primary key(Pseudo)
    )engine=innodb;

    CREATE TABLE IF NOT EXISTS DecoupeReseau(
    idDR smallint not null,
    Pseudo varchar(40) not null,
    AdresseIP varchar(20) not null,
    Masque varchar(20) not null,
    IsClassfull boolean not null default false,
    primary key(idDR),
    key(Pseudo)
    )engine=innodb;

    CREATE TABLE IF NOT EXISTS SousReseau (
    NumSR smallint not null,
    NbMachine smallint not null default 0,
    IdDR smallint not null,
    primary key(NumSR)
    )engine=innodb;
    ''')

    conn.commit() #Sauvegarde la création des données
    cursor.close()
    conn.close()

    return