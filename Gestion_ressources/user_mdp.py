from sqlobject import *
from model import UserPassword
import os, random, string, binascii, hashlib


def get_config():
    app.config.from_envvar('DING_CONFIG')
    # sqlhub.processConnection = connectionForURI(app.config['DB_FILE'])

def consult_username():
    return [elem.username for elem in UserPassword.select()]

def consult_storage():
    return [elem.storage for elem in UserPassword.select()]
    
def consult_account(username):
    rep = check_exist_user(username)
    if rep:
        return [rep.username,rep.storage]
    else:
        return False
        
def check_exist_user(user):
    try:
        return UserPassword.byUsername(user)
    except SQLObjectNotFound:
        return False


def create_account(username, passwd, fix_salt_for_test=None):
    if check_length_password(passwd):
        rep = check_exist_user(username)
        if rep == False:
            if fix_salt_for_test:
                storage = create_hash(passwd, fix_salt_for_test)
            else:
                storage = create_hash(passwd)
            UserPassword(username=username, storage=storage)
            return username
        else:
            return None
    else:
        return False


def delete_account(username):
    rep = check_exist_user(username)
    if rep:
        UserPassword.delete(rep.id)
        return True
    else:
        return False

def change_password(username, passwd):
    rep = check_exist_user(username)
    if rep:
        storage = create_hash(passwd)
        rep.storage = storage
        return storage
    else:
        return False

def delete_password(username):
    rep = check_exist_user(username)
    if rep:
        storage = None
        rep.storage = storage
        return storage
    else:
        return False

def login(username, passwd):
    rep = check_exist_user(username)
    if rep:
        if check_key(username, passwd):
            return True
        else:
            return False
    else:
        return False

def check_role_of_user(username):
    rep = check_exist_user(username)
    if rep:
        return rep.role
    else: 
        return False

def check_key(username, passwd):
    """
    check_key(username=str, passwd=str)
        Return False si mauvaise combinaison - Return la clé si vrai
    check_exist_user(username)
       Return False si l'utilisateur n'existe pas - Return l'objet utilisateur si il existe
       
    La clef = itération 100000x(hash du mot de passe + sel)
    La clef est sotckée dans la DB dans la table UserPassword à l'attribut storage.
    storage est composé :
       - d'un sel qui occupe les 32 premiers caractères 
       - de la clef qui occupe les 32 derniers caractères 
    """    
    rep = check_exist_user(username)
    if rep:
        storage_str = rep.storage
        storage = binascii.unhexlify(storage_str)
        salt_from_storage = storage[:32]
        key_from_storage = storage[32:]

        password_to_check = passwd

        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password_to_check.encode('utf-8'),
            salt_from_storage,
            100000
        )
        if new_key == key_from_storage:
            return new_key
        else:
            return False
    else:
        return False

def create_hash(passwd, fix_salt_for_test=None):
    """
    create_hash(passwd=str)
    Génère par le biais de os.urandom un sel
    La clef = itération 100000x(hash du mot de passe + sel)
    binascii.unhexlify(data) renvoie la représentation hexadécimale des données binaire.
    binascii.hexlify(data) renvoie les données binaires représentées par la chaîne hexadécimale hexstr. 
    binascii.hexlify(data).decode() renvoie une chaîne de string
    """
    if fix_salt_for_test:
        salt = fix_salt_for_test
    else:
        salt = os.urandom(32)
    salt_str = binascii.hexlify(salt).decode()
    key = hashlib.pbkdf2_hmac('sha256', passwd.encode('utf-8'), salt, 100000)
    key_str = binascii.hexlify(key).decode()
    return salt_str + key_str
  
