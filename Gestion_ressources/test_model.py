from modify_model_ressource import create_ressource, check_loan_time_of_ressource, check_the_type_ressource_of_ressource, check_count_retries_of_ressource, check_state_chg_of_ressource, check_state_of_ressource, consult_ressources, change_state_of_ressource, delete_ressource, consult_type_ressources, check_exist_type_of_ressource, check_exist_ressource, consult_ressources_connect_of_type_ressource, create_type_ressource, delete_type_ressource, change_type_of_ressource, check_contact1_of_ressource, check_contact2_of_ressource
from sqlobject import *
import os, pytest, random, tempfile
from model import init, TypeRessource, Ressource
from datetime import datetime, timedelta
from utility import create_information_ressource, random_string


@pytest.fixture
def config_test():
    # temp_db = tempfile.NamedTemporaryFile(delete=False)
    temp_config = tempfile.NamedTemporaryFile()

    config = {
        'ROOT_DIR': '/truc/machin/bidule',
        'DB_FILE': 'sqlite:/:memory:',
        'TIMEOUT': '86400',
        'NBR_RETRIES' : '3',
        'HOOK-CONTACT' : 'testhook_func.fonction_contact',
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
    dic_ressources contient pour chaque type de ressource une liste des ressources qui lui sont lié
    {'type1': [{'Contact1': 'student.ovvumu@ucl.be', ... , 'loan_time': 2, 'ID': 1}, {'Contact1': 'student.prajup@ucl.be', ... , 'loan_time': 2, 'ID': 2}],
     'type2': [{'Contact1': 'student.eszkak@ucl.be', ... , 'loan_time': 2, 'ID': 3}, 
    """
    list_of_type_ressources = ["type1","type2"]
    dic_ressources = {}

    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    init()
    

    for elem in list_of_type_ressources:
        list_ressources = []
        Type = TypeRessource(Name=elem, hook_create='fonction', hook_supress='fonction')
        for i in range(2):
            ressource = create_information_ressource ()
            r = Ressource(typeRessource=Type, Contact1=ressource["Contact1"], Contact2=ressource["Contact2"], State=ressource["State"], State_chg=ressource["State_chg"] , loan_time=ressource["loan_time"])
            ressource["ID"] = r.id
            list_ressources.append(ressource)
        dic_ressources[elem] = list_ressources

    

    yield list_of_type_ressources, dic_ressources



def test_check_exist_type_of_ressource_false(db_test):
    """
    check_exist_type_of_ressource(str)
    Vérifie si le type de ressource existe
        Return l'object "TypeRessource" si existe - Return False si n'existe pas 
    """
    type_of_ressource = random_string(word=True)
    rep = check_exist_type_of_ressource(type_of_ressource)
    assert not rep

def test_check_exist_type_of_ressource_true(db_test):
    """
    check_exist_type_of_ressource(str)
    Vérifie si le type de ressource existe
        Return l'object "TypeRessource" si existe - Return False si n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    rep = check_exist_type_of_ressource(type_of_ressource)
    assert rep    
  
def test_check_exist_ressource_true(db_test):
    """
    check_exist_ressource(int)
    Vérifie si la ressource existe
        Return l'object "Ressource" si existe - Return False si n'existe pas 
    """
    list_of_ressource = consult_ressources()
    ID = random.choice(list_of_ressource)
    rep = check_exist_ressource(ID)
    assert rep 

def test_check_exist_ressource_false(db_test):
    """
    check_exist_ressource(int)
    Vérifie si la ressource existe
        Return l'object "Ressource" si existe - Return False si n'existe pas  
    """
    ID = random.randint(100, 1000)
    rep = check_exist_ressource(ID)
    assert not rep      
    
def test_create_ressource_true(db_test):
    """
    Vérifie si la création de ressource et l'attriubtion à un type de ressource a bien été effectué
    Si le type de ressource encodé pour la création n'existe pas alors Return False
        Return l'object "Ressource" si réussi 
    create_information_ressource ()
        génère des données aléatoires stocké sous forme de dictionnaire
    """
    ressource = create_information_ressource ()   
    type_of_ressource = random.choice(db_test[0])
    ressource["typeRessource"] = type_of_ressource
      
    nb_ressources_before = len(consult_ressources())
    rep = create_ressource(ressource)
    assert rep
    nb_ressources_after = len(consult_ressources())
    assert not nb_ressources_before == nb_ressources_after
    
    assert rep in consult_ressources_connect_of_type_ressource(type_of_ressource)
    
def test_create_ressource_false(db_test):
    """
    Vérifie si la création de ressource et l'attriubtion à un type de ressource a bien été effectué
    Si le type de ressource encodé pour la création n'existe pas alors Return False
        Return l'object "Ressource" si réussi  
    create_information_ressource ()
        génère des données aléatoires stocké sous forme de dictionnaire
    """
    ressource = create_information_ressource ()   
    type_of_ressource = random_string(word=True)
    ressource["typeRessource"] = type_of_ressource
      
    nb_ressources_before = len(consult_ressources())
    rep = create_ressource(ressource)
    assert not rep
    nb_ressources_after = len(consult_ressources())
    assert nb_ressources_before == nb_ressources_after

def test_create_type_ressource_exist(db_test):
    """
    create_type_ressource(str)
    Return False si le type de ressource existait déjà - Return l'object "TypeRessource" créé si existe pas
    """
    type_ressource = random.choice(db_test[0])
    rep = create_type_ressource(type_ressource)
    assert not rep 

def test_create_type_ressource_doesnt_exist(db_test):
    """
    create_type_ressource(str)
    Return False si le type de ressource existait déjà - Return l'object "TypeRessource" créé si existe pas 
    """
    type_ressource = random_string(word=True)
    rep = create_type_ressource(type_ressource)
    assert rep  
    
def test_consult_ressources_connect_of_type_ressource_true(db_test):
    """
    consult_ressources_connect_of_type_ressource(str)
    Vérifie si les ressources liées au type de ressource sont correctes
       Return False si type de ressource n'existe pas 
       Return l'object "Ressource" qui lui sont liés 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    list_of_id = []
    for elem in list_of_ressources:
         list_of_id.append(elem['ID'])
    
    
    rep = consult_ressources_connect_of_type_ressource(type_of_ressource) 
    assert rep
    for elem in reversed(rep):
        a = list_of_id.pop()
        assert elem.id == a


def test_consult_ressources_connect_of_type_ressource_false(db_test):
    """
    consult_ressources_connect_of_type_ressource(str)
    Vérifie si les ressources liées au type de ressource sont correctes
       Return False si type de ressource n'existe pas 
       Return l'object Ressource qui lui sont liés 
    """
    type_of_ressource = random_string(word=True)
    
    rep = consult_ressources_connect_of_type_ressource(type_of_ressource) 
    assert not rep

def test_change_type_of_the_ressource_true(db_test):
    """
    change_type_of_ressource(int,str)
    Vérifie si le type de la ressource a bien été modifié
    Le type de ressource et la ressource doivent exister  
        Return l'object "Ressource" si la ressource a été moidifiée
        Retrun False si pas 
    """
    type_of_ressource = db_test[0][1]
    other_type_of_ressource = db_test[0][0]
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep_before = len(consult_ressources_connect_of_type_ressource(type_of_ressource))
    rep_ID_before = check_the_type_ressource_of_ressource(ID)
    rep = change_type_of_ressource(ID,other_type_of_ressource)
    assert rep
    
    rep_ID_after = check_the_type_ressource_of_ressource(ID)
    rep_after = len(consult_ressources_connect_of_type_ressource(type_of_ressource))
    assert not rep_after == rep_before
    assert not rep_ID_after == rep_ID_before
    
def test_change_type_of_the_ressource_bad_type(db_test):
    """
    change_type_of_ressource(int,str)
    Vérifie si le type de la ressource a bien été modifié
    Le type de ressource et la ressource doivent exister  
        Return l'object "Ressource" si la ressource a été moidifiée
        Retrun False si pas 
    """
    type_of_ressource = db_test[0][1]
    fake_type_of_ressource = random_string(word=True)
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']

    
    rep_before = len(consult_ressources_connect_of_type_ressource(type_of_ressource))
    rep_ID_before = check_the_type_ressource_of_ressource(ID)
    rep = change_type_of_ressource(ID,fake_type_of_ressource)
    assert not rep
    
    rep_ID_after = check_the_type_ressource_of_ressource(ID)
    rep_after = len(consult_ressources_connect_of_type_ressource(type_of_ressource))
    assert rep_after == rep_before
    assert rep_ID_after == rep_ID_before
    
def test_change_type_of_the_ressource_bad_ressource(db_test):
    """
    change_type_of_ressource(int,str)
    Vérifie si le type de la ressource a bien été modifié
    Le type de ressource et la ressource doivent exister  
        Return l'object "Ressource" si la ressource a été moidifiée
        Retrun False si pas 
    """
    type_of_ressource = db_test[0][1]
    other_type_of_ressource = db_test[0][0]
    dic_ressources = db_test[1]
    list_of_id = dic_ressources[type_of_ressource]
    ID = random.randint(100, 1000)
    
    rep_before = len(consult_ressources_connect_of_type_ressource(type_of_ressource))
    rep = change_type_of_ressource(ID,other_type_of_ressource)
    assert not rep
    
    rep_after = len(consult_ressources_connect_of_type_ressource(type_of_ressource))
    assert rep_after == rep_before


def test_delete_type_ressource_exist(db_test):
    """
    delete_type_ressource(str)
    Vérifie si le type de ressource a été supprimé 
        Return True - Return False 
    """
    type_of_ressource = random.choice(db_test[0])
    list_of_type_ressource_before = len(consult_type_ressources())
    
    rep = delete_type_ressource(type_of_ressource)
    list_of_type_ressource_after = len(consult_type_ressources())
    assert rep
    assert not list_of_type_ressource_after == list_of_type_ressource_before

def test_delete_type_ressource_doesnt_exist(db_test):
    """
    delete_type_ressource(str)
    Vérifie si le type de ressource a été supprimé 
        Return True - Return False 
    """
    type_of_ressource = random_string(word=True)
    list_of_type_ressource_before = len(consult_type_ressources())
    
    rep = delete_type_ressource(type_of_ressource)
    list_of_type_ressource_after = len(consult_type_ressources())
    assert not rep
    assert list_of_type_ressource_after == list_of_type_ressource_before
    
    
def test_delete_ressource_exist(db_test):
    """
    delete_ressource(int)
    Vérifie si la ressource a été supprimé 
        Return True - Return False 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    list_of_ressource_before = len(consult_ressources())
   
    rep = delete_ressource(ID)
    list_of_ressource_after = len(consult_ressources())
    assert rep
    assert not list_of_ressource_before == list_of_ressource_after
    
def test_delete_ressource_doesnt_exist(db_test):
    """
    delete_ressource(int)
    Vérifie si la ressource a été supprimé 
        Return True - Return False  
    """
    ID = random.randint(100, 1000)
    list_of_ressource_before = len(consult_ressources())
   
    rep = delete_ressource(ID)
    list_of_ressource_after = len(consult_ressources())
    assert not rep
    assert list_of_ressource_before == list_of_ressource_after
    
    
def test_check_the_type_ressource_of_ressource_ressource_doesnt_exist(db_test):
    """
    check_the_type_ressource_of_ressource(int)
    Return le type de ressouce de la ressource sous format str - return false si la ressource n'existe pas 
    """
    ID = random.randint(100, 1000)
    rep = check_the_type_ressource_of_ressource(ID)
    assert not rep

def test_check_the_type_ressource_of_ressource_ressource_exist(db_test):
    """
    check_the_type_ressource_of_ressource(int)
    Return le type de ressouce de la ressource sous format str - return false si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep = check_the_type_ressource_of_ressource(ID)
    assert rep

def test_check_contact1(db_test):
    """
    check_contact1_of_ressource(int)
    Return le contact n°1 lié à la ressource sous format str - return false si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep = check_contact1_of_ressource(ID)
    assert rep
    assert dic_ressource['Contact1'] == rep
    
def test_check_contact2(db_test):
    """
    check_contact2_of_ressource(int)
    Return le contact n°2 lié à la ressource sous format str - return false si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep = check_contact2_of_ressource(ID)
    assert rep
    assert dic_ressource['Contact2'] == rep

def test_check_state_of_ressource_exist(db_test):
    """
    check_state_of_ressource(int)
    Return l'état de la ressource sous format int - return false si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep = check_state_of_ressource(ID)
    assert rep
    assert dic_ressource['State'] == rep

def test_check_state_of_ressource_doesnt_exist(db_test):
    """
    check_state_of_ressource(int)
    Return l'état de la ressource sous format int - return false si la ressource n'existe pas 
    """
    ID = random.randint(100, 1000)   
    rep = check_state_of_ressource(ID)
    assert not rep
    
def test_check_count_retries_exist(db_test):
    """
    check_count_retries_of_ressource(int)
    Return le nbre de tentative réalisée lié à la ressource sous format int - return false si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep = check_count_retries_of_ressource(ID)
    assert dic_ressource['count_retries'] == rep

def test_check_count_retries_doesnt_exist(db_test):
    """
    check_count_retries_of_ressource(int)
    Return le nbre de tentative réalisée lié à la ressource sous format int - return false si la ressource n'existe pas 
    """
    ID = random.randint(100, 1000)   
    rep = check_count_retries_of_ressource(ID)
    assert not rep
    
def test_check_loan_time(db_test):
    """
    check_loan_time_of_ressource(int)
    Return le temps de location lié à la ressource sous format int - return false si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep = check_loan_time_of_ressource(ID)
    assert rep   
    assert dic_ressource['loan_time'] == rep
    
def test_check_chgmen_etat(db_test):
    """
    check_state_chg_of_ressource(int)
    Return l'état lié à la ressource sous format int - return false si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep = check_state_chg_of_ressource(ID)
    assert rep     
    assert dic_ressource['State_chg'] == rep

def test_change_state_of_ressource(db_test):
    """
    change_state_of_ressource(ID=int,nbr=int)
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    nbr = random.randint(5,10)
    
    rep_before = check_state_of_ressource(ID)
    rep = change_state_of_ressource(ID, nbr)
    assert rep == nbr
    
    rep_after = check_state_of_ressource(ID)
    
    assert not rep_after == rep_before
    
    
