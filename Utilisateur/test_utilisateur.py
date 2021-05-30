from sqlobject import *
import os, pytest, random, string, tempfile, binascii, hashlib,  re
from utilisateur import app, get_config, consult_username, create_account, delete_account, check_exist_user, login, \
    check_key, create_hash, check_length_password, change_password, delete_password, consult_storage, consult_account
from model import init, UserPassword



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
        'PORT': '8080',
        'LENGTH_CHARACTER': '4',
        'SECRET_KEY' : 'c120e7646d0f6e14a5416ae6b064c1a7'
    }

    for key, value in config.items():
        temp_config.file.write((f'{key} = "{value}"\n').encode("UTF-8"))
    temp_config.file.seek(0)

    os.environ['DING_CONFIG'] = temp_config.name

    yield config

    sqlhub.processConnection.close()


@pytest.fixture
def db_test(config_test):
    dic_user_passw = {}

    dic_user_storage = {}

    for i in range(0, 5):
        dic_user_passw[random_string(word=True)] = random_string(word=True)

    for username, password in dic_user_passw.items():
        salt = os.urandom(32)
        salt_str = binascii.hexlify(salt).decode()
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        key_str = binascii.hexlify(key).decode()
        storage = salt_str + key_str
        dic_user_storage[username] = storage

    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    init()

    for key, value in dic_user_storage.items():
        UserPassword(username=key, storage=value)

    yield dic_user_storage, dic_user_passw


def test_config(config_test):
    get_config()
    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    for key, value in config_test.items():
        assert config_test[key] == app.config[key]


def test_create_account_user_alreday_exist(db_test):
    """
    Vérifie si la fonction create_account() réussi à ajouter un compte dans la DB
        Return la clé + le hash sous format string si le compte a été créé - si non Return False
    check_exist_user(username)
       Return False si l'utilisateur n'existe pas - Return l'objet utilisateur si il existe
    """
    list_of_user = consult_username()
    username = random.choice(list(list_of_user))
    password = random_string(word=True)

    rep = check_length_password(password)
    assert rep,'Password is too weak'

    user = check_exist_user(username)
    assert user

    rep = create_account(username, password)
    assert rep == None


def test_create_account_user_doesnt_exist(db_test):
    """
    Vérifie si la fonction create_account() réussi à ajouter un compte dans la DB
        Return le nom de compte si réussi 
        Return False si le mdp est trop faible
        Return None si l'utilisateur existe déjà
    check_exist_user(username)
       Return False si l'utilisateur n'existe pas - Return l'objet utilisateur si il existe
    """
    username = random_string(word=True)
    salt = os.urandom(32)
    password = random_string(word=True)

    rep = check_length_password(password)
    assert rep,'Password is too weak'

    user = check_exist_user(username)
    assert not user, "Username already exists in DB"

    new_username = create_account(username, password, fix_salt_for_test=salt)
    assert new_username

    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    
    storage_str = create_hash(password,salt)
    storage = binascii.unhexlify(storage_str)
    key_from_storage = storage[32:]
    assert key == key_from_storage
    
    user = check_exist_user(new_username)
    assert user
    

def test_create_account_user_exist_weak_passwd(db_test):
    """
    Vérifie si la fonction create_account() réussi à ajouter un compte dans la DB
        Return le nom de compte si réussi 
        Return False si le mdp est trop faible
        Return None si l'utilisateur existe déjà
    check_exist_user(username)
       Return False si l'utilisateur n'existe pas - Return l'objet utilisateur si il existe
    """
    username = random_string(word=True)
    salt = os.urandom(32)
    length_character = int(app.config['LENGTH_CHARACTER'])
    password = ''.join(random.choice(string.ascii_lowercase) for i in range(length_character - 1))

    rep = check_length_password(password)
    assert not rep,'Password is not too weak'

    user = check_exist_user(username)
    assert not user, "Username already exists in DB"

    new_username = create_account(username, password, fix_salt_for_test=salt)
    assert not new_username

    user = check_exist_user(username)
    assert not user

def test_delete_account_user_exist(db_test):
    """
    Vérifie si la fonction delete_account réussi à supprimer le compte dans la DB
    L'utilisateur doit être identifié pour pouvoir supprimer le compte
    	Return True si le compte à été supprimé - si non Return False
    check_exist_user(username)
       Return False si l'utilisateur n'existe pas - Return l'objet utilisateur si il existe
    """
    dic_password = db_test[1]
    username, password = random.choice(list(dic_password.items()))

    user = check_exist_user(username)
    assert user

    rep = delete_account(username)
    assert rep

    user = check_exist_user(username)
    assert not user


def test_delete_account_user_doesnt_exist(db_test):
    """
    Vérifie si la fonction delete_account réussi à supprimer le compte dans la DB
    L'utilisateur doit être identifié pour pouvoir supprimer le compte
    	Return True si le compte à été supprimé - si non Return False
    check_exist_user(username)
       Return False si l'utilisateur n'existe pas - Return l'objet utilisateur si il existe
    """
    username = random_string(word=True)

    user = check_exist_user(username)
    assert not user

    rep = delete_account(username)
    assert not rep


def test_change_password_user_exist(db_test):
    """
    Vérifie si la fonction change_password arrive à changer de mot de passe
        Return False si utilisateur n'existe pas - Return clef + sel si vrai
    Consult_account(username)
        Return une liste contenant l'utilisateur et son storage
    check_key(usrername, password)
        Return False si mauvaise combinaison - Return seulement la clef si vrai
    """
    dic_hash = db_test[0]
    dic_password = db_test[1]

    username, storage_hash = random.choice(list(dic_hash.items()))
    password = dic_password[username]
    new_password = random_string(word=True)
    account_before = consult_account(username)
    
    rep = change_password(username, new_password)
    assert not rep == storage_hash

    user = check_exist_user(username)
    assert user

    key = check_key(user, new_password)

    account_after = consult_account(username)
    assert not account_before == account_after
    
    storage = binascii.unhexlify(account_after[1])
    key_from_storage = storage[32:]
    assert key_from_storage == key
    
def test_change_password_user_doesnt_exist(db_test):
    """
    Vérifie si la fonction change_password arrive à changer de mot de passe
        Return False si utilisateur n'existe pas - Return clef + sel si vrai
    login(username, password)
        Return False si mauvaise combinaison - Return True si bonne combinaison
    check_key(usrername, password)
        Return False si mauvaise combinaison - Return seulement la clef si vrai
    """

    username = random_string(word=True)
    new_password = random_string(word=True)
    
    rep = change_password(username, new_password)
    assert not rep 


def test_delete_password_user_exist(db_test):
    """ 
    Vérifie si la fonctione supprime le mot de passe de l'utilisateur cible, remplace le mot de passe par None
        Return False si l'utilisateur n'existe pas - Return username et storage si vrai 
    Consult_account(username)
        Return une liste contenant l'utilisateur et son storage
    """
    dic_hash = db_test[0]
    dic_password = db_test[1]

    username, storage_hash = random.choice(list(dic_hash.items()))
    password = dic_password[username]
    new_password = None
    account_before = consult_account(username)
    
    rep = delete_password(username)
    assert not rep == storage_hash
    
    account_after = consult_account(username)
    assert not account_before == account_after
    assert account_after[1] == None

def test_delete_password_user_doesnt_exist(db_test):
    """ 
    Vérifie si la fonctione supprime le mot de passe de l'utilisateur cible, remplace le mot de passe par None
        Return False si l'utilisateur n'existe pas - Return username et storage si vrai 
    """
    username = random_string(word=True)
    new_password = None
    
    rep = delete_password(username)
    assert not rep
    

def test_good_login(db_test):
    """
    Vérifie si l'utilisateur est à la bonne combinaison username/password
        Return False si mauvaise combinaison - Return True si bonne combinaison

    """
    dic_password = db_test[1]
    username, password = random.choice(list(dic_password.items()))

    rep = login(username, password)
    assert rep


def test_wrong_login(db_test):
    """
    Vérifie si l'utilisateur est à la bonne combinaison username/password
        Return False si mauvaise combinaison - Return True si bonne combinaison

    """
    dic_password = db_test[1]
    username = random.choice(list(dic_password.keys()))
    password = random_string(word=True)

    rep = login(username, password)
    assert not rep

def test_check_key(db_test):
    """
    Vérifie si le hash est le même, prend en paramètre l'objet SQL UserPassword
        Return False si mauvaise combinaison - Return la clé si vrai
    check_exist_user(username)
       Return False si l'utilisateur n'existe pas - Return l'objet utilisateur si il existe
    32 est la taille du sel
    """
    dic_hash = db_test[0]
    dic_password = db_test[1]

    username, storage_hash = random.choice(list(dic_hash.items()))
    password = dic_password[username]

    user_object = check_exist_user(username)
    assert user_object
    
    storage = binascii.unhexlify(storage_hash)
    salt_from_storage = storage[:32]

    password_to_check = password

    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        password_to_check.encode('utf-8'),
        salt_from_storage,
        100000
    )

    key = check_key(user_object, password)
    assert key == new_key

def test_check_key_wrong_salt(db_test):
    """
    Vérifie si le hash est le même
        Return False si mauvaise combinaison - Return seulement la clé si vrai
    check_exist_user(username)
       Return False si l'utilisateur n'existe pas - Return l'objet utilisateur si il existe
    32 est la taille du sel
    """
    dic_hash = db_test[0]
    dic_password = db_test[1]

    username, storage_hash = random.choice(list(dic_hash.items()))
    password = dic_password[username]

    user_object = check_exist_user(username)
    assert user_object

    storage = binascii.unhexlify(storage_hash)
    salt_from_storage = storage[:32]

    password_to_check = password

    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        password_to_check.encode('utf-8'),
        salt_from_storage,
        100000
    )

    key = check_key(user_object, password)
    assert key == new_key


def test_create_hash_good_salt(db_test):
    """
    Renvoie sous forme de string la clé et le sel
    Le sel est crée à partir de la fonction os.urandom(32), celle_ci créant une taille de 32 octets
    """
    password = random_string(word=True)
    salt = os.urandom(32)

    storage_str = create_hash(password, fix_salt_for_test=salt)
    assert storage_str

    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    key_str = binascii.hexlify(key).decode()
    salt_str = binascii.hexlify(salt).decode()
    storage = salt_str + key_str
    
    assert storage_str == storage
    
def test_create_hash_wrong_salt(db_test):
    """
    Renvoie sous forme de string la clé et le sel
    Le sel est crée à partir de la fonction os.urandom(32), celle_ci créant une taille de 32 octets
    """
    password = random_string(word=True)
    salt = os.urandom(32)

    storage_str = create_hash(password)
    assert storage_str

    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    key_str = binascii.hexlify(key).decode()
    salt_str = binascii.hexlify(salt).decode()
    storage = salt_str + key_str
    
    assert not storage_str == storage

def test_check_length_password_good(client, db_test,):
    """
    Vérifie si le mot de passe est de bonne longueur
        Return True si bonne longueur - Return False si non
    """
    length_character = int(app.config['LENGTH_CHARACTER'])
    password = ''.join(random.choice(string.ascii_lowercase) for i in range(length_character))
    rep = check_length_password(password)
    assert rep

def test_check_length_password_wrong(client, db_test):
    """
    Vérifie si le mot de passe est de bonne longueur
        Return True si bonne longueur - Return False si non
    """
    length_character = int(app.config['LENGTH_CHARACTER'])
    password = ''.join(random.choice(string.ascii_lowercase) for i in range(length_character - 1))
    rep = check_length_password(password)
    assert not rep


def test_check_exist_user_True(db_test):
    """
      Renvoie l'objet utilisateur si existe
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


def test_wrong_login_flask(client, db_test):
    """
    Vérifie si l'utilisateur est à la bonne combinaison username/password
        Return Page index si Faux - Return page weclome si vrai
        Return un cookie de session si Vrai
    """

    url_post = '/check'
    field_name = 'name'
    field_password = 'password'
    name = 'corbeau'
    password = '1234'

    rv = client.post(url_post,
                     data={field_name: name, field_password: password})

    assert not 'Set-Cookie' in rv.headers

def test_good_login_flask(client, db_test):
    """
    Vérifie si l'utilisateur est à la bonne combinaison username/password
        Return Page index si Faux - Return page weclome si vrai
        Return un cookie de session si Vrai
    """
    dic_password = db_test[1]
    username, password = random.choice(list(dic_password.items()))

    url_post = '/check'
    field_name = 'name'
    field_password = 'password'
    name = username
    password = password

    rv = client.post(url_post,
                     data={field_name: name, field_password: password})

    cookie = rv.headers['Set-Cookie']

    with client.session_transaction() as sess:
        rep = sess['logged_in']

    assert rep
    assert cookie

def test_flask_consult(client, db_test): #doit afficher les utilisateurs à faire 
    rv = client.get('/board')
    print(rv.data.decode("utf-8"))
    assert not rv
    
def test_change_password_flask_user_exist(client, db_test):
    dic_password = db_test[1]
    username = random.choice(list(dic_password.keys()))
    password = random_string(word=True)
    
    url_post = '/board'
    field_name = 'username'
    field_password = 'password'
    field_box = 'mycheckbox'
    name = username
    password = password
    box = 1

    rv = client.post(url_post,
                     data={field_name: name, field_password: password, field_box: box})
    
    target_search = re.findall("Utilisateur (.*?) a été modifié", rv.data.decode("utf-8"))
    assert target_search[0] == username

def test_change_password_flask_user_doesnt_exist(client,db_test):
    username = random_string(word=True)
    password = random_string(word=True)
    
    url_post = '/board'
    field_name = 'username'
    field_password = 'password'
    field_box = 'mycheckbox'
    name = username
    password = password
    box = 1

    rv = client.post(url_post,
                     data={field_name: name, field_password: password, field_box: box})
    
    target_search = re.findall("Utilisateur (.*?) introuvable", rv.data.decode("utf-8"))
    assert target_search[0] == username

def test_delete_password_flask_user_exist(client, db_test):
    dic_password = db_test[1]
    username = random.choice(list(dic_password.keys()))

    url_post = '/board'
    field_name = 'username'
    field_box = 'mycheckbox'
    name = username
    box = 2 
 
    rv = client.post(url_post,
                     data={field_name: name,field_box: box})
    
    target_search = re.findall("Mot de passe de (.*?) a été supprimé", rv.data.decode("utf-8"))
    assert target_search[0] == username

def test_delete_password_flask_user_doesnt_exist(client, db_test):
    username = random_string(word=True)

    url_post = '/board'
    field_name = 'username'
    field_box = 'mycheckbox'
    name = username
    box = 2 
 
    rv = client.post(url_post,
                     data={field_name: name,field_box: box})
    
    target_search = re.findall("Utilisateur (.*?) introuvable", rv.data.decode("utf-8"))
    assert target_search[0] == username
    
def test_create_account_flask_user_exist(client, db_test):
    dic_password = db_test[1]
    username = random.choice(list(dic_password.keys()))
    password = random_string(word=True)
    
    url_post = '/board'
    field_name = 'username'
    field_password = 'password'
    field_box = 'mycheckbox'
    name = username
    password = password
    box = 3

    rv = client.post(url_post,
                     data={field_name: name, field_password: password, field_box: box})
    
    target_search = re.findall("Utilisateur (.*?) existe déjà", rv.data.decode("utf-8"))
    assert target_search[0] == username
    
def test_create_account_flask_user_psswrd_weak(client, db_test):
    username = random_string(word=True)
    length_character = int(app.config['LENGTH_CHARACTER'])
    password = ''.join(random.choice(string.ascii_lowercase) for i in range(length_character - 1))
    
    url_post = '/board'
    field_name = 'username'
    field_password = 'password'
    field_box = 'mycheckbox'
    name = username
    password = password
    box = 3

    rv = client.post(url_post,
                     data={field_name: name, field_password: password, field_box: box})
    
    target_search = re.findall("Mot de passe trop faible", rv.data.decode("utf-8"))
    assert target_search[0]

def test_create_account_flask_user_doesnt_exist(client, db_test):
    username = random_string(word=True)
    password = random_string(word=True)
    
    url_post = '/board'
    field_name = 'username'
    field_password = 'password'
    field_box = 'mycheckbox'
    name = username
    password = password
    box = 3

    rv = client.post(url_post,
                     data={field_name: name, field_password: password, field_box: box})
    
    target_search = re.findall("Utilisateur (.*?) a été créé", rv.data.decode("utf-8"))
    assert target_search[0] == username
   
def random_string(word=None):
    if word:
        return ''.join(random.choice(string.ascii_lowercase) for i in range(random.randint(6, 10)))

