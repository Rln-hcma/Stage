from sqlobject import *
import os, pytest, random, tempfile
from projet_ressource import get_config, consult_type_ressources
from model import init, TypeRessource, Ressource
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


def test_config(config_test):
    """
    Test d'intégrité de la config  
    """
    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    dic_config = get_config()
     
    for key,value in config_test.items():
        assert value == dic_config[key]

def test_list_of_type_ressources_config(db_test):
    """
    Test d'intégrité de la config  
    """
    types = consult_type_ressources()
    types.sort()
    db_test[0].sort()
    assert types == db_test[0]
    
