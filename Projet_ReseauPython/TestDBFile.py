import DBHandler as db
import AuthHandler as ath
if (__name__ == "__main__"):

    db.create_db()
    db.insert_user("test","test")
    session = ath.create_session("test", "test")
    print(db.get_all_subnettings_of_user(session))
    db.insert_decoupe(session, "Bonjour", "192.168.0.0","255.255.255.0")
    db.insert_decoupe(session, "Aurevoir", "192.168.0.0","255.255.255.0")
    print(db.get_all_subnettings_of_user(session))
    db.insert_sous_reseau(session, 0, "10", "Bonjour")
    db.insert_sous_reseau(session, "1", 4, "Bonjour")
    print(db.get_all_subnets_of_a_subnetting(session,"Bonjour"))