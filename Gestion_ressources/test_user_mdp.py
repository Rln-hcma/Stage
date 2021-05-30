from sqlobject import *
import os, pytest, random, string, tempfile, binascii, hashlib, re
from user_mdp import get_config, consult_username, check_exist_user, login, check_key, check_role_of_user
from model import init, UserPassword
from utility import random_string

@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def config_test():
    # temp_db = tempfile.NamedTemporaryFile(delete=False)
    temp_config = tempfile.NamedTemporaryFile(delete=False)

    config = {
        'ROOT_DIR': '/truc/machin/bidule',
        'DB_FILE': 'sqlite:/:memory:',
        'IP_ADDR': '127.0.0.1',
        'PORT': '8080'
    }

    for key, value in config.items():
        temp_config.file.write((f'{key} = "{value}"\n').encode("UTF-8"))
    temp_config.file.seek(0)

    os.environ['DING_CONFIG'] = temp_config.name

    yield config

    sqlhub.processConnection.close()


@pytest.fixture
def db_test(config_test):
    """
    dic_user_information : 
     - user_information["username"]
     - user_information["storage"]
     - user_information["role"] = admin ou user 
    """
    dic_user_information = {}
    list_of_type_role = ["admin","user"]
    
    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    init()
    
    for elem in list_of_type_role:
        list_role = []
        for i in range(3):
            user_information = {}
            user_information["username"] = random_string(word=True)
            user_information["mdp_en_clair"] = random_string(word=True)
             
            salt = os.urandom(32)
            salt_str = binascii.hexlify(salt).decode()
            key = hashlib.pbkdf2_hmac('sha256', user_information["mdp_en_clair"].encode('utf-8'), salt, 100000)
            key_str = binascii.hexlify(key).decode()
            storage = salt_str + key_str
            user_information["storage"] = storage
            
            if elem == "admin":
                UserPassword(username=user_information["username"], storage=user_information["storage"], role="admin")
                user_information["role"] = "admin"
            elif elem == "user":
                UserPassword(username=user_information["username"], storage=user_information["storage"], role="user")
                user_information["role"] = "user"
            list_role.append(user_information)
        dic_user_information[elem] = list_role

    yield list_of_type_role, dic_user_information


def test_good_login(db_test):
    """
    Vérifie si l'utilisateur est à la bonne combinaison username/password
        Return False si mauvaise combinaison - Return True si bonne combinaison
    """
    list_of_type_role = random.choice(db_test[0])
    dic_user_information = db_test[1]
    user_information = random.choice(dic_user_information[list_of_type_role])

    rep = login(user_information["username"], user_information["mdp_en_clair"])
    assert rep

def test_wrong_login(db_test):
    """
    Vérifie si l'utilisateur est à la bonne combinaison username/password
        Return False si mauvaise combinaison - Return True si bonne combinaison
    """
    list_of_type_role = random.choice(db_test[0])
    dic_user_information = db_test[1]
    user_information = random.choice(dic_user_information[list_of_type_role])
    false_password = random_string(word=True)

    rep = login(user_information["username"], false_password)
    assert not rep

def test_check_key(db_test):
    """
    Vérifie si le hash est le même, prend en paramètre l'objet SQL UserPassword prend plutot username et prend le mot de passe en clair 
        Return False si mauvaise combinaison - Return la clé si vrai
    check_exist_user(username)
       Return False si l'utilisateur n'existe pas - Return l'objet utilisateur si il existe
    32 est la taille du sel
    """
    list_of_type_role = random.choice(db_test[0])
    dic_user_information = db_test[1]
    user_information = random.choice(dic_user_information[list_of_type_role])

    storage = binascii.unhexlify(user_information["storage"])
    salt_from_storage = storage[:32]

    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        user_information["mdp_en_clair"].encode('utf-8'),
        salt_from_storage,
        100000
    )

    key = check_key(user_information["username"], user_information["mdp_en_clair"])
    assert key == new_key

def test_check_key_wrong_salt(db_test):
    """
    Vérifie si le hash est le même
        Return False si mauvaise combinaison - Return seulement la clé si vrai
    check_exist_user(username)
       Return False si l'utilisateur n'existe pas - Return l'objet utilisateur si il existe
    32 est la taille du sel
    """
    list_of_type_role = random.choice(db_test[0])
    dic_user_information = db_test[1]
    user_information = random.choice(dic_user_information[list_of_type_role])
    
    storage = binascii.unhexlify(user_information["storage"])
    salt_from_storage = storage[:32]

    false_password = random_string(word=True)

    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        false_password.encode('utf-8'),
        salt_from_storage,
        100000
    )

    key = check_key(user_information["username"], false_password)
    assert not key == new_key

def test_check_exist_user_True(db_test):
    """
      Renvoie l'objet utilisateur si existe - Si pas return False
    """
    list_of_user = consult_username()
    username = random.choice(list(list_of_user))

    rep = check_exist_user(username)
    objet = str((type(rep)))

    assert objet == "<class 'model.UserPassword'>"


def test_check_exist_user_False(db_test):
    """
    Renvoie false si l'utilisateur n'existe pas
    """
    username = random_string(word=True)

    rep = check_exist_user(username)
    assert not rep

def test_check_role_of_user_amdin(db_test):
    """
    list_of_type_role = db_test[0][0]
    dic_user_information : 
     - user_information["username"]
     - user_information["storage"]
     - user_information["role"] = admin 
    """
    list_of_type_role = db_test[0][0]
    dic_user_information = db_test[1]
    user_information = random.choice(dic_user_information[list_of_type_role])
    role = user_information["role"]
    
    rep = check_role_of_user(user_information["username"])
    
    assert rep == role 

def test_check_role_of_user_user(db_test):
    """
    list_of_type_role = db_test[0][1]
    dic_user_information : 
     - user_information["username"]
     - user_information["storage"]
     - user_information["role"] = user 
    """
    list_of_type_role = db_test[0][1]
    dic_user_information = db_test[1]
    user_information = random.choice(dic_user_information[list_of_type_role])
    role = user_information["role"]
    
    rep = check_role_of_user(user_information["username"])
    
    assert rep == role  
