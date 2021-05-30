import pickle, os, pytest, re, formulaire, random, string
from shutil import copyfile
import tempfile 

from formulaire import app, get_config, insert_url, delete_url, consult, delete_word, insert_word, contains, url_associate, resset_occ_nmbr, associate_url, consult_username, username_insert, passwd_insert, consult_passwd, account_is_create, create_account, delte_account
from model import init, Word, Url, Occurence, User, Password, UserPassword
from sqlobject import *
from random import randrange


@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def config_test():
    #temp_db = tempfile.NamedTemporaryFile(delete=False)
    temp_config = tempfile.NamedTemporaryFile(delete=False)

    config ={
        'ROOT_DIR': '/truc/machin/bidule',
        'DB_FILE' : 'sqlite:/:memory:',
        'IP_ADDR' : '127.0.0.1',
        'PORT' : '8080'
    }

    for key, value in config.items():
        temp_config.file.write((f'{key} = "{value}"\n').encode("UTF-8"))
    temp_config.file.seek(0)
    
    os.environ['DING_CONFIG'] = temp_config.name
    
    yield config

    sqlhub.processConnection.close()
    
@pytest.fixture
def db_test(config_test):
    dic_user_passw = {   'renardo': 'password1234',
    
                         'user54': 'le111098'}    
  
    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    init()
    
    for key, value in dic_user_passw.items():
        user = User(username=key)
        passwd = Password(password=value)
        UserPassword(target_user=user, target_password=passwd)
            
    yield 
    
def test_config(config_test):
    get_config()
    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    for key, value in config_test.items():
        assert config_test[key] == app.config[key]
        
def test_create_account_user_alreday_exist(db_test):
    """
       Vérifie si la fonction create_account réussi à ajouter un compte dans la DB 
       Renvoie True si créé
       Renvoie False si pas créé
       account_is_create(username,passwd) renvoie true si le compte à déjà été crée auparavant
    """
    #check username
    list_of_user = consult_username()
    username = random.choice(list(list_of_user))
    assert username in list_of_user, "Username doesn't exists in DB"
   
    #check passwd
    passwd = random_string(word=True)
    passwd_insert(passwd)
   
    response = account_is_create(username,passwd)
    assert response == False
    
    rep = create_account(username,passwd)
    assert rep == False
    
    response = account_is_create(username,passwd)
    assert response == False

def test_create_account_user_doesnt_exist(db_test):
    """
       Vérifie si la fonction create_account réussi à ajouter un compte dans la DB 
       Renvoie True si créé
       Renvoie False si pas créé
       Consult_username() renvoie une liste comportant l'entièreté des username de la DB 
       account_is_create(username,passwd) renvoie true si le compte à déjà été crée auparavant
    """
    username = random_string(word=True)
    passwd = random_string(word=True)
    
    #check username
    list_of_user = consult_username()
    assert not username in list_of_user, "Username already exists in DB"
    rep = username_insert(username)
    list_of_user = consult_username()
    assert rep in list_of_user, "The username has not been registered"
    
    #check passwd
    passwd_insert(passwd)
    
    #faire l'association
    response = account_is_create(username,passwd)
    assert response == False
    
    rep = create_account(username,passwd)
    assert rep == True
    
    response = account_is_create(username,passwd)
    assert response == True

def test_delete_account(db_test):
    """
       Vérifie si la fonction delete_account réussi à supprimer le compte dans la DB 
       account_is_create(username,passwd) renvoie true si le compte existe
    """
    list_of_user = consult_username()
    username = random.choice(list(list_of_user)) 
    
    list_of_psswd = consult_passwd()
    passwd = random.choice(list(list_of_psswd))
    
    rep = account_is_create(username,passwd)
    assert rep == True
    
    rep = delte_account(username,passwd)
    assert rep == True

    response = account_is_create(username,passwd)
    assert response == False

def test_insert_username_user_already_exist(db_test):
   """
      Si l'utilisateur est déjà existant la fonction doit renvoyer None
   """
   list_of_user = consult_username()
   username = random.choice(list(list_of_user))
   
   rep = username_insert(username)
   assert rep == None

def test_insert_username_user(db_test):
   """
      Si l'tilisateur n'existe pas la fonction le crée et renvoie l'utilisateur
   """
   username = random_string(word=True)
   list_of_user = consult_username()
   
   rep = username_insert(username)
   assert rep == username
   
   list_of_user = consult_username()
   assert rep in list_of_user

def test_passwd_insert_passw_doesnt_exist(db_test):
    """
       le mot de passe est un AlternateID
       Si la mot de passe n'éxiste pas la fonction le crée et renvoie l'ojet 
       la fonction doit renvoyer l'objet en toute circonstance 
    """
    passwd = random_string(word=True)
    list_of_psswd = consult_passwd()
   
    rep = passwd_insert(passwd)
    assert rep == passwd
   
    list_of_psswd = consult_passwd()
    assert rep in list_of_psswd

def test_passwd_insert_passwd_exist(db_test):
    """
       le mot de passe est un AlternateID
       Si la mot de passe éxiste, la fonction renvoie l'ojet 
       la fonction doit renvoyer l'objet en toute circonstance 
    """
    list_of_psswd = consult_passwd()
    passwd = random.choice(list(list_of_psswd))
   
    rep = passwd_insert(passwd)
    assert rep == passwd
   
    list_of_psswd = consult_passwd()
    assert rep in list_of_psswd

def test_account_is_create_true(db_test):
    """
      Renvoie True si le compte existe 
    """
    username = 'renardo'
    list_of_user = consult_username()
    assert username in list_of_user
    passwd = 'password1234'
    list_of_psswd = consult_passwd()
    assert passwd in list_of_psswd
    
    rep = account_is_create(username,passwd)
    assert rep == True
    
def test_account_is_create_false(db_test):
    """
      Renvoie False si le compte n'existe pas 
    """
    list_of_user = consult_username()
    username = random_string(word=True)
    assert not username in list_of_user
    passwd = 'password1234'
    list_of_psswd = consult_passwd()
    assert passwd in list_of_psswd
    
    rep = account_is_create(username,passwd)
    assert rep == False


