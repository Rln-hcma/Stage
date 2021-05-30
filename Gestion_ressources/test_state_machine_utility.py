from sqlobject import *
import os, pytest, random, tempfile
from projet_ressource import consult_ressources, check_exist_ressource, add_count_retries, up_state, modify_state_chg_etat_to_now, check_time_spent, check_nb_count_retries_limit, check_time_spent_loan_time, hook_contact, hook_sup, hook_create
from modify_model_ressource import check_state_of_ressource, check_count_retries_of_ressource, check_state_chg_of_ressource
from model import init, TypeRessource, Ressource
from testhook_func import check_validation_func
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
        Type = TypeRessource(Name=elem, hook_create='testhook_func.fonction_supp', hook_supress='testhook_func.fonction_supp')
        for i in range(2):
            ressource = create_information_ressource ()
            r = Ressource(typeRessource=Type, Contact1=ressource["Contact1"], Contact2=ressource["Contact2"], State=ressource["State"], State_chg=ressource["State_chg"] , loan_time=ressource["loan_time"])
            ressource["ID"] = r.id
            list_ressources.append(ressource)
        dic_ressources[elem] = list_ressources

    

    yield list_of_type_ressources, dic_ressources


    
def test_add_count_retries_exist(db_test):
    """
    add_count_retries(int)
    Vérifie si l'incrémentation(+1 )a bien eu lieu
    Return le nbre de tentative réalisée pour ressource sous format int - return false si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep_before = check_count_retries_of_ressource(ID)
    rep = add_count_retries(ID)
    assert rep
    
    rep_after = check_count_retries_of_ressource(ID)
    
    assert rep_after > rep_before

def test_add_count_retries_doesnt_exist(db_test):
    """
    add_count_retries(int)
    Vérifie si l'incrémentation(+1 )a bien eu lieu
    Return le nbre de tentative réalisée pour ressource sous format int - return false si la ressource n'existe pas 
    """
    ID = random.randint(100, 1000)
    
    rep_before = check_count_retries_of_ressource(ID)
    rep = add_count_retries(ID)
    assert not rep
    rep_after = check_count_retries_of_ressource(ID)
  
    assert not rep_after and not rep_before

def test_up_state_exist(db_test):
    """
    up_state(int)
    Vérifie si l'incrémentation(+1 )a bien eu lieu
    Return l'etat sous format int - return false si la ressource n'existe pas  
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep_before = check_state_of_ressource(ID)
    rep = up_state(ID)
    assert rep
    
    rep_after = check_state_of_ressource(ID)
    
    assert rep_after > rep_before
    
def test_up_state_doesnt_exist(db_test):
    """
    up_state(int)
    Vérifie si l'incrémentation(+1 )a bien eu lieu
    Return l'etat sous format int - return false si la ressource n'existe pas  
    """
    ID = random.randint(100, 1000)
    
    rep_before = rep = check_state_of_ressource(ID)
    rep = up_state(ID)
    assert not rep
    rep_after = check_state_of_ressource(ID)
  
    assert not rep_after and not rep_before

def test_modify_state_chg_etat_to_now(db_test):
    """
    modify_state_chg_etat_to_now(datetime.datetime)
    Vérifie si le changement de date à bien été effectué 
    Return True ou Return False 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep_before = check_state_chg_of_ressource(ID)
    rep = modify_state_chg_etat_to_now(ID)
    assert rep
    rep_after = check_state_chg_of_ressource(ID)
    
    assert rep_after > rep_before
    
    
def test_check_time_spent_false(db_test):
    """
    test_check_time_spent(ID)
    Vérifie si la ressourcé à dépassée la limite de time out
    Return True si le temps est dépassé - return false si le temps n'est pas dépassé 
    Return None si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep = check_time_spent(ID)
    assert not rep 

def test_check_time_spent_True(db_test):
    """
    test_check_time_spent(ID)
    Vérifie si la ressourcé à dépassée la limite de time out
    Return True si le temps est dépassé - return false si le temps n'est pas dépassé 
    Return None si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    utility_add_two_day(ID)
    
    
    rep = check_time_spent(ID)
    assert rep 

def test_check_nb_count_retries_limit_true(db_test):
    """
    check_nb_count_retries_limit(ID)
    Vérifie si la ressourcé à dépassée la limite d'essai 
    Return True si le nombre d'essai est dépassé - return false si pas 
    Return None si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    utility_add_retries(ID)
    
    rep = check_nb_count_retries_limit(ID)
    assert rep 
 
def test_check_nb_count_retries_limit_false(db_test):
    """
    check_nb_count_retries_limit(ID)
    Vérifie si la ressourcé à dépassée la limite d'essai 
    Return True si le nombre d'essai est dépassé - return false si le nombre n'est pas dépassé 
    Return None si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']

    rep = check_nb_count_retries_limit(ID)
    assert not rep

def test_check_nb_count_retries_limit_true(db_test):
    """
    check_nb_count_retries_limit(ID)
    Vérifie si la ressourcé à dépassée la limite d'essai 
    Return True si le nombre d'essai est dépassé - return false si pas 
    Return None si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    utility_add_retries(ID)
    
    rep = check_nb_count_retries_limit(ID,state3=True)
    assert rep 
 
def test_check_nb_count_retries_limit_false(db_test):
    """
    check_nb_count_retries_limit(ID)
    Vérifie si la ressourcé à dépassée la limite d'essai 
    Return True si le nombre d'essai est dépassé - return false si pas 
    Return None si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep = check_nb_count_retries_limit(ID,state3=True)
    assert not rep 
    
def utility_add_two_day(ID):
    ressource_object = check_exist_ressource(ID)
    if ressource_object:    
        ressource_object.State_chg = datetime.now() - timedelta(hours=90)

def utility_add_retries(ID):
    ressource_object = check_exist_ressource(ID)
    if ressource_object:    
        ressource_object.count_retries = 8

def test_check_time_spent_loan_time_true(db_test): 
    """
    test_check_time_spent_loan_time(ID)
    Vérifie si la ressourcé à dépassée la limite de temps
    Return True si le temps est dépassé - return false si le temps n'est pas dépassé 
    Return None si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    utility_add_two_day(ID)
    
    rep = check_time_spent_loan_time(ID)
    assert rep
    
def test_check_time_spent_loan_time_false(db_test): 
    """
    test_check_time_spent_loan_time(ID)
    Vérifie si la ressourcé à dépassée la limite de temps
    Return True si le temps est dépassé - return false si le temps n'est pas dépassé 
    Return None si la ressource n'existe pas 
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    rep = check_time_spent_loan_time(ID)
    assert not rep

def test_hook_contact(db_test):
    """
    hook_contact(ID,state2=True,state3=None)
    hook_contact(ID,state2=None,state3=True)
    Prend le contact n°1 ou n°2 en fonction de l'état choisi state2 ou state3
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    global_before = check_validation_func()
    rep = hook_contact(ID,state2=True)
    assert rep
    global_after = check_validation_func()

    assert not global_after == global_before

def test_hook_sup(db_test):
    """
    hook_sup(ID)
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    global_before = check_validation_func()
    rep = hook_sup(ID)
    global_after = check_validation_func()

    assert not global_after == global_before
  
 
def test_hook_create(db_test):
    """
    hook_create(ID)
    """
    type_of_ressource = random.choice(db_test[0])
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources[type_of_ressource]
    dic_ressource = random.choice(list_of_ressources)
    ID = dic_ressource['ID']
    
    global_before = check_validation_func()
    rep = hook_create(ID)
    global_after = check_validation_func()
    
    assert not global_after == global_before    
