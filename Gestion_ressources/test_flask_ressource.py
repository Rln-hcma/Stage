from sqlobject import *
import os, pytest, random, tempfile, pytest, re, binascii, hashlib
from ressource_flask import app, create_ressource_state_0, consult_ressources_state_0, change_to_state_1, get_config
from modify_model_ressource import check_state_of_ressource, check_count_retries_of_ressource, consult_ressources, consult_ressources_connect_of_type_ressource, consult_type_ressources, change_state_of_ressource
from model import init, TypeRessource, Ressource, UserPassword
from utility import create_information_ressource, random_string
import html
import flask

@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def config_test():
    # temp_db = tempfile.NamedTemporaryFile(delete=False)
    temp_config = tempfile.NamedTemporaryFile()

    config = {
        'ROOT_DIR': '/truc/machin/bidule',
        'DB_FILE': 'sqlite:/:memory:',
    }

    for key, value in config.items():
        temp_config.file.write((f'{key} = "{value}"\n').encode("UTF-8"))
    temp_config.file.seek(0)

    os.environ['CONFIG'] = temp_config.name

    yield config

    sqlhub.processConnection.close()   

@pytest.fixture
def db_test(config_test):
    """
    dic_ressources contient des dictionnaires :
     - ressource["Contact1"]
     - ressource["Contact2"]
     - ressource["State"]
     - ressource["State_chg"]
     - ressource["loan_time"]
     - ressource["ID"]
     
    dic_ressources contient pour chaque type de ressource une liste des ressources qui lui sont lié
    {'type1': [{'Contact1': 'student.ovvumu@ucl.be', ... , 'loan_time': 2, 'ID': 1}, {'Contact1': 'student.prajup@ucl.be', ... , 'loan_time': 2, 'ID': 2}],
     'type2': [{'Contact1': 'student.eszkak@ucl.be', ... , 'loan_time': 2, 'ID': 3}, 
     'Type3' Contient que des stat 0
    """
    list_of_type_ressources = ["type1","type2","type3"]
    dic_ressources = {}
 
    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    init()
   
    for elem in list_of_type_ressources:
        list_ressources = []
        Type = TypeRessource(Name=elem, hook_create='testhook_func.fonction_create', hook_supress='testhook_func.fonction_supp')
        for i in range(3):
            ressource = create_information_ressource ()
            if elem =="type3":
                r = Ressource(typeRessource=Type, Contact1=ressource["Contact1"], Contact2=ressource["Contact2"], State=0, State_chg=ressource["State_chg"] ,count_retries= i, loan_time=ressource["loan_time"], username=random_string(word=True))
            else:
                r = Ressource(typeRessource=Type, Contact1=ressource["Contact1"], Contact2=ressource["Contact2"], State=ressource["State"], State_chg=ressource["State_chg"] , loan_time=ressource["loan_time"], username=random_string(word=True))
            ressource["ID"] = r.id
            ressource["State"] = r.State
            list_ressources.append(ressource)
        dic_ressources[elem] = list_ressources

    yield list_of_type_ressources, dic_ressources

@pytest.fixture
def db_test_mdp(config_test):
    """
     dic_user_information contient des dictionnaires : 
     - user_information["username"]
     - user_information["storage"]
     - user_information["role"] = user 
     
     dic_user_information contient :
     {'admin': [{'username': 'yvdmvb', 'mdp_en_clair': 'tqfxpu', 'storage': '...185b4..'}, {'username': 'jugztyjis', 'mdp_en_clair': 'zkkome', 'storage': '...6oi4m....'}, {'username': 'ahvjmczzua', 'mdp_en_clair': 'xhnzyhl', 'storage': '...46qd...'}], 
     'user': [{'username': 'rtiucyrofh', 'mdp_en_clair': 'lprlmv', 'storage': '...9q84...'},
         
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
            elif elem == "user":
                UserPassword(username=user_information["username"], storage=user_information["storage"], role="user")
                
            list_role.append(user_information)
        dic_user_information[elem] = list_role

    yield list_of_type_role, dic_user_information

def test_config(config_test):
    get_config()
    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    for key, value in config_test.items():
        assert config_test[key] == app.config[key]
    
def test_first_look_reservation(db_test, client):
    """
    Vérifie si les types de ressources listés sur la page sont bien ceux présent dans la DB 
    """
    list_of_ressource = db_test[0]
    url_post = '/reservation'
    
    with client: 
        with client.session_transaction() as sess:
            sess['user'] = 'user'
        rv = client.get(url_post)

    target_ressources = re.findall("<ul>(.*?) </ul>", rv.data.decode("utf-8"))
    assert target_ressources == list_of_ressource


def test_create_ressource_state_0(db_test, client):   
    type_of_ressource = random.choice(db_test[0])
    url_post = '/reservation'
    field_username = 'username'
    field_type_of_ressource = 'type_ressource'
    field_contact1 = 'contact1'
    field_contact2 = 'contact2'
    
    username = random_string(word=True)
    type_of_ressource = random.choice(db_test[0])
    contact1 = random_string(email2=True)
    contact2 = random_string(email=True)
    
    nb_ressources_before = len(consult_ressources())   
    nb_ressources_before_connect = len(consult_ressources_connect_of_type_ressource(type_of_ressource))

    with client: 
        with client.session_transaction() as sess:
            sess['user'] = 'user'
            sess['name'] = random_string(word=True)
        rv = client.post(url_post,
                     data={field_username: username, field_type_of_ressource: type_of_ressource, field_contact1: contact1, field_contact2: contact2})
    
    assert "formulaire envoyé" in rv.data.decode("utf-8")
      

    nb_ressources_after = len(consult_ressources())
    assert nb_ressources_before < nb_ressources_after
    
    nb_ressources_after_connect = len(consult_ressources_connect_of_type_ressource(type_of_ressource))
    assert nb_ressources_before_connect < nb_ressources_after_connect

def test_reservation_false_type_of_ressource(db_test, client):
    """
    Vérifie si un mauvais type de ressource est envoyé
        Si oui renvoie une erreur en mentionnant le type de ressource en question
    """
    url_post = '/reservation'
    field_username = 'username'
    field_type_of_ressource = 'type_ressource'
    field_contact1 = 'contact1'
    field_contact2 = 'contact2'
    
    username = random_string(word=True)
    type_of_ressource = random_string(word=True)
    contact1 = random_string(email2=True)
    contact2 = random_string(email=True)
    
    with client: 
        with client.session_transaction() as sess:
            sess['user'] = 'user'      
        rv = client.post(url_post,
                     data={field_username: username, field_type_of_ressource: type_of_ressource, field_contact1: contact1, field_contact2: contact2})
    
    target_search = re.findall("Le type de ressource sélectionné nommé (.*?) est inexistant", rv.data.decode("utf-8"))
    assert target_search[0] == type_of_ressource

def test_reservation_form_empty_contact1(db_test, client):
    """
    Vérifie si le formulaire a été entièrement complété
        Si non renvoie une erreur en mentionnant en informant que l'utilisateur n'a pas tout rempli
    """
    url_post = '/reservation'
    field_username = 'username'
    field_type_of_ressource = 'type_ressource'
    field_contact1 = None
    field_contact2 = 'contact2'
    
    username = random_string(word=True)
    type_of_ressource = random.choice(db_test[0])
    contact1 = random_string(email2=True)
    contact2 = random_string(email=True)

    with client: 
        with client.session_transaction() as sess:
            sess['user'] = 'user'       
        rv = client.post(url_post,
                     data={field_username: username, field_type_of_ressource: type_of_ressource, field_contact1: contact1, field_contact2: contact2})
                 
    assert "Le formulaire doit être entièrement rempli" in rv.data.decode("utf-8")

def test_reservation_form_empty_contact2(db_test, client):
    """
    Vérifie si le formulaire a été entièrement complété
        Si non renvoie une erreur en mentionnant en informant que l'utilisateur n'a pas tout rempli
    """
    url_post = '/reservation'
    field_username = 'username'
    field_type_of_ressource = 'type_ressource'
    field_contact1 = 'contact1'
    field_contact2 = None
    
    username = random_string(word=True)
    type_of_ressource = random.choice(db_test[0])
    contact1 = random_string(email2=True)
    contact2 = random_string(email=True)
    
    with client: 
        with client.session_transaction() as sess:
            sess['user'] = 'user'     
        rv = client.post(url_post,
                     data={field_username: username, field_type_of_ressource: type_of_ressource, field_contact1: contact1, field_contact2: contact2})
                 
    assert "Le formulaire doit être entièrement rempli" in rv.data.decode("utf-8")

def test_reservation_form_empty_type_ressource(db_test, client):
    """
    Vérifie si le formulaire a été entièrement complété
        Si non renvoie une erreur en mentionnant en informant que l'utilisateur n'a pas tout rempli
    """
    url_post = '/reservation'
    field_username = 'username'
    field_type_of_ressource = None
    field_contact1 = 'contact1'
    field_contact2 = 'contact2'
    
    username = random_string(word=True)
    type_of_ressource = random.choice(db_test[0])
    contact1 = random_string(email2=True)
    contact2 = random_string(email=True)
    
    with client: 
        with client.session_transaction() as sess:
            sess['user'] = 'user'      
        rv = client.post(url_post,
                     data={field_username: username, field_type_of_ressource: type_of_ressource, field_contact1: contact1, field_contact2: contact2})
                 
    assert "Le formulaire doit être entièrement rempli" in rv.data.decode("utf-8")

def test_first_look_board(db_test, client):
    """
    Vérifie si les types de ressources listés sur la page sont bien ceux présent dans la DB 
    Pour ce faire à l'aide des expressions régulières nous capturons dans la variable 'target_ressources', les ID présent sur la page 
    """
    ID_ressource_state_0 = []
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type3"]
    for elem in list_of_ressources:
        ID_ressource_state_0.append(elem['ID'])

    url_post = '/board'
    
    with client: 
        with client.session_transaction() as sess:
            sess['user'] = 'admin'  
        rv = client.get(url_post)

    target_ressources = re.findall("ID: (.*?),", rv.data.decode("utf-8"))
    target_ressources = list( map(int, target_ressources) )
  
    assert target_ressources == ID_ressource_state_0

    
def test_board_check_box_autoriser(db_test, client):
    """
    Box fait référence aux valeurs cochées disponible sur la page
    filed_request_admin fait référence au bouton name=autoriser
    request_admin fait référence à la valeur renvoyé lorsque le bouton name=autoriser est pressé
    """
    ID_ressource_state_0 = []
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type3"]
    for elem in list_of_ressources:
        ID_ressource_state_0.append(elem['ID'])

    url_post = '/board'
  
    with client: 
        with client.session_transaction() as sess:
            sess['user'] = 'admin'  
        rv = client.get(url_post)

    target_ressources_before = re.findall("ID: (.*?),", rv.data.decode("utf-8"))
    target_ressources_before = list( map(int, target_ressources_before) )
  
    assert target_ressources_before == ID_ressource_state_0
    
    ID_ressource_state_0 = []
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type3"]
    for elem in list_of_ressources:
        ID_ressource_state_0.append(elem['ID'])
    
    url_post = '/board'
    field_box = 'mychekbox'
    filed_request_admin = 'autoriser'
    
    box = random.sample(ID_ressource_state_0, 2)
    request_admin = 'Autoriser'
    
    with client: 
        with client.session_transaction() as sess:
            sess['user'] = 'admin'       
        rv = client.post(url_post,
                     data={field_box: box, filed_request_admin: request_admin})

                 
    target_ressources_supp = re.findall("Les ressources (.*?) ont été approuvées", rv.data.decode("utf-8"))
    assert target_ressources_supp
    target_ressources_supp = html.unescape(target_ressources_supp[0])
    target_ressources_supp = re.findall("'(.*?)'", target_ressources_supp)
    target_ressources_supp = list( map(int, target_ressources_supp) )
    assert target_ressources_supp ==  box
    

    target_ressources_after = re.findall("ID: (.*?),", rv.data.decode("utf-8"))
    target_ressources_after = list( map(int, target_ressources_after) )
    assert not target_ressources_before == target_ressources_after

    for elem in box:
        assert not elem in target_ressources_after
    
    for elem in box:
        assert elem in target_ressources_before
        
def test_board_check_box_supprimer(db_test, client):
    """
    Box fait référence aux valeurs cochées disponible sur la page
    filed_request_admin fait référence au bouton name=supprimer
    request_admin fait référence à la valeur renvoyé lorsque le bouton name=supprimer est pressé
    à l'aide des expressions régulières nous capturons dans la variable 'target_ressources', les ID présent sur la page
    """
    ID_ressource_state_0 = []
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type3"]
    for elem in list_of_ressources:
        ID_ressource_state_0.append(elem['ID'])

    url_post = '/board'

    with client: 
        with client.session_transaction() as sess:
            sess['user'] = 'admin'     
        rv = client.get(url_post)

    target_ressources_before = re.findall("ID: (.*?),", rv.data.decode("utf-8"))
    target_ressources_before = list( map(int, target_ressources_before) )
  
    assert target_ressources_before == ID_ressource_state_0
    
    ID_ressource_state_0 = []
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type3"]
    for elem in list_of_ressources:
        ID_ressource_state_0.append(elem['ID'])
    
    url_post = '/board'
    field_box = 'mychekbox'
    filed_request_admin = 'supprimer'
    
    box = random.sample(ID_ressource_state_0, 2)
    request_admin = 'Supprimer'

    with client: 
        with client.session_transaction() as sess:
            sess['user'] = 'admin'           
        rv = client.post(url_post,
                     data={field_box: box, filed_request_admin: request_admin})
                 
    target_ressources_supp = re.findall("Les ressources (.*?) ont été désapprouvées", rv.data.decode("utf-8"))
    assert target_ressources_supp
    target_ressources_supp = html.unescape(target_ressources_supp[0])
    target_ressources_supp = re.findall("'(.*?)'", target_ressources_supp)
    target_ressources_supp = list( map(int, target_ressources_supp) )
    assert target_ressources_supp ==  box
    

    target_ressources_after = re.findall("ID: (.*?),", rv.data.decode("utf-8"))
    target_ressources_after = list( map(int, target_ressources_after) )
    assert not target_ressources_before == target_ressources_after

    for elem in box:
        assert not elem in target_ressources_after
    
    for elem in box:
        assert elem in target_ressources_before
    
def test_change_state_of_ressource_to_state_5(db_test, client):
    """
    up_state(int)
    Vérifie si le changement à bien eu lieu
    Return l'etat sous format int - return false si la ressource n'existe pas
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep_before = check_state_of_ressource(ID)
    rep = change_state_of_ressource(ID,5)
    assert rep == 5
    
    rep_after = check_state_of_ressource(ID)
    
    assert not rep_before == 5
    assert rep_after == 5
    
def test_change_state_of_ressource_to_state_5_doesnt_exist(db_test, client):
    """
    up_state(int)
    Vérifie si le changement à bien eu lieu
    Return l'etat sous format int - return false si la ressource n'existe ppas  
    """
    ID = random.randint(100, 1000)
    
    rep_before = rep = check_state_of_ressource(ID)
    rep = change_state_of_ressource(ID,5)
    assert not rep
    rep_after = check_state_of_ressource(ID)
  
    assert not rep_after and not rep_before

def test_change_to_state_1(db_test, client):
    """
    Fonction servant à l'application flask 
    Modifie la ressource pour l'intégrer dans la state machine 
    """  
    ID_ressource_state_0 = []  
    nb_ressources_state_0_before = len(consult_ressources_state_0())
    db_state_0 = consult_ressources_state_0()
    for elem in db_state_0:
        ID_ressource_state_0.append(elem[0])
    ressources_state_0_random = random.sample(ID_ressource_state_0, 2)
    
    for ID in ressources_state_0_random:
            change_to_state_1(ID)

    nb_ressources_state_0_after = len(consult_ressources_state_0())
    assert not nb_ressources_state_0_before == nb_ressources_state_0_after

def test_consult_ressources_state_0(db_test, client):
    """
    Affiche les les ressources possédant l'état 0 
    """
    ID_ressource_state_0 = []
    ID_ressource_state_0_consult = []
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type3"]
    for elem in list_of_ressources:
        ID_ressource_state_0.append(elem['ID'])
    
    db_state_0 = consult_ressources_state_0()
    for elem in db_state_0:
        ID_ressource_state_0_consult.append(elem[0])

    assert ID_ressource_state_0_consult == ID_ressource_state_0

def test_wrong_login_flask(client, db_test_mdp):
    """
    Vérifie si l'utilisateur est à la bonne combinaison username/password
        Return un cookie de session si Vrai
    """

    url_post = '/'
    field_name = 'name'
    field_password = 'password'
    name = 'corbeau'
    password = '1234'

    rv = client.post(url_post,
                     data={field_name: name, field_password: password})

    assert not 'Set-Cookie' in rv.headers    
    assert "Utilisateur ou mot de passe incorrecte" in  rv.data.decode("utf-8")
    
def test_wrong_mdp_flask(client, db_test_mdp):
    """
    Vérifie si l'utilisateur est à la bonne combinaison username/password
        Return un cookie de session si Vrai
    """
    list_of_type_role = random.choice(db_test_mdp[0])
    dic_user_information = db_test_mdp[1]
    user_information = random.choice(dic_user_information[list_of_type_role])

    url_post = '/'
    field_name = 'name'
    field_password = 'password'
    name = user_information["username"]
    password = random_string(word=True)

    rv = client.post(url_post,
                     data={field_name: name, field_password: password})

    assert not 'Set-Cookie' in rv.headers    
    assert "Utilisateur ou mot de passe incorrecte" in  rv.data.decode("utf-8")

def test_good_mdp_flask_admin(client, db_test_mdp):
    """
    Vérifie si l'utilisateur est à la bonne combinaison username/password
        Return un cookie de session si Vrai
        
    list_of_type_role = db_test[0][0]
    dic_user_information : 
     - user_information["username"]
     - user_information["storage"]
     - user_information["role"] = admin
    """
    list_of_type_role = db_test_mdp[0][0]
    dic_user_information = db_test_mdp[1]
    user_information = random.choice(dic_user_information[list_of_type_role])

    url_post = '/'
    field_name = 'name'
    field_password = 'password'
    name = user_information["username"]
    password = user_information["mdp_en_clair"]

    with client: 
        rv = client.post(url_post, data={field_name: name, field_password: password})
        assert flask.session['user'] == 'admin'
    

def test_good_mdp_flask_user(client, db_test_mdp):
    """
    Vérifie si l'utilisateur est à la bonne combinaison username/password
        Return un cookie de session si Vrai
        
    list_of_type_role = db_test[0][1]
    dic_user_information : 
     - user_information["username"]
     - user_information["storage"]
     - user_information["role"] = user     
    """
    list_of_type_role = db_test_mdp[0][1]
    dic_user_information = db_test_mdp[1]
    user_information = random.choice(dic_user_information[list_of_type_role])

    url_post = '/'
    field_name = 'name'
    field_password = 'password'
    name = user_information["username"]
    password = user_information["mdp_en_clair"]

    with client: 
        rv = client.post(url_post, data={field_name: name, field_password: password})
        assert flask.session['user'] == 'user'
    
