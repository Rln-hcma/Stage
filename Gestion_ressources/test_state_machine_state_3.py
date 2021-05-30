from sqlobject import *
import os, pytest, tempfile
from projet_ressource import ressource_state_machine
from modify_model_ressource import check_state_of_ressource, check_count_retries_of_ressource, check_state_chg_of_ressource
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
    Type 1 contiendra des ressources dont leurs State_chg est inférieur au time_out
    Type 2 contiendra des ressources dont leurs State_chg est supérieur au time_out
    """
    list_of_type_ressources = ["type1","type2"]
    dic_ressources = {}

    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    init()
    

    for elem in list_of_type_ressources:
        list_ressources = []
        Type = TypeRessource(Name=elem, hook_create='fonction', hook_supress='fonction')
        for i in range(4):
            if elem == "type1":
                ressource = create_information_ressource ()
            else:
                ressource = create_information_ressource (add_day=True)
            r = Ressource(typeRessource=Type, Contact1=ressource["Contact1"], Contact2=ressource["Contact2"], State=3, State_chg=ressource["State_chg"] ,count_retries= 4+i, loan_time=ressource["loan_time"])
            ressource["ID"] = r.id
            ressource["count_retries"] = 4+i
            list_ressources.append(ressource)
        dic_ressources[elem] = list_ressources

    yield list_of_type_ressources, dic_ressources

def test_ressource_state_3_count_retries4_no_timeout(db_test):
    """
    {'State': 3, count_retries': 4, State_chg': inférieur au time out}
    devient
    {'State': 3, count_retries': 4, State_chg': ne doit pas avoir été modifié}
    """
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type1"]
    ID = list_of_ressources[0]['ID']

    state_of_ressource_before = check_state_of_ressource(ID)
    count_retries_of_ressource_before = check_count_retries_of_ressource(ID)
    time_before = check_state_chg_of_ressource(ID)
    
    ressource_state_machine(ID)

    state_of_ressource_after = check_state_of_ressource(ID)
    count_retries_of_ressource_after = check_count_retries_of_ressource(ID)
    time_after = check_state_chg_of_ressource(ID)
    
    assert state_of_ressource_before == 3
    assert count_retries_of_ressource_before == 4
    assert state_of_ressource_before == state_of_ressource_after
    assert count_retries_of_ressource_before == count_retries_of_ressource_after
    assert time_before == time_after

def test_ressource_state_3_count_retries4_timeout(db_test):
    """
    {'State': 2, count_retries': 4, State_chg': supérieur au time out}
    devient 
    {'State': 2, count_retries': 5, State_chg': maintenant}
    """
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type2"]
    ID = list_of_ressources[0]['ID']
    state_of_ressource_before = check_state_of_ressource(ID)
    count_retries_of_ressource_before = check_count_retries_of_ressource(ID)
    time_before = check_state_chg_of_ressource(ID)
    
    ressource_state_machine(ID)

    state_of_ressource_after = check_state_of_ressource(ID)
    count_retries_of_ressource_after = check_count_retries_of_ressource(ID)
    time_after = check_state_chg_of_ressource(ID)
    
    assert state_of_ressource_before == 3
    assert count_retries_of_ressource_before == 4
    assert state_of_ressource_before == state_of_ressource_after
    assert count_retries_of_ressource_before < count_retries_of_ressource_after
    assert time_before < time_after
    
def test_ressource_state_3_count_retries5_no_timeout(db_test):
    """
    {'State': 3, count_retries': 5, State_chg': inférieur au time out}
    devient
    {'State': 3, count_retries': 5, State_chg': ne doit pas avoir été modifié}
    """
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type1"]
    ID = list_of_ressources[1]['ID']
    state_of_ressource_before = check_state_of_ressource(ID)
    count_retries_of_ressource_before = check_count_retries_of_ressource(ID)
    time_before = check_state_chg_of_ressource(ID)
    
    ressource_state_machine(ID)

    state_of_ressource_after = check_state_of_ressource(ID)
    count_retries_of_ressource_after = check_count_retries_of_ressource(ID)
    time_after = check_state_chg_of_ressource(ID)

    assert state_of_ressource_before == 3
    assert count_retries_of_ressource_before == 5    
    assert state_of_ressource_before == state_of_ressource_after
    assert count_retries_of_ressource_before == count_retries_of_ressource_after
    assert  time_before == time_after


def test_ressource_state_3_count_retries5_timeout(db_test):
    """
    {'State': 2, count_retries': 5, State_chg': supérieur au time out}
    devient 
    {'State': 2, count_retries': 6, State_chg': maintenant}
    """
    
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type2"]
    ID = list_of_ressources[1]['ID']
    state_of_ressource_before = check_state_of_ressource(ID)
    count_retries_of_ressource_before = check_count_retries_of_ressource(ID)
    time_before = check_state_chg_of_ressource(ID)
    
    ressource_state_machine(ID)

    state_of_ressource_after = check_state_of_ressource(ID)
    count_retries_of_ressource_after = check_count_retries_of_ressource(ID)
    time_after = check_state_chg_of_ressource(ID)
    
    assert state_of_ressource_before == 3
    assert count_retries_of_ressource_before == 5
    assert state_of_ressource_before == state_of_ressource_after
    assert count_retries_of_ressource_before < count_retries_of_ressource_after
    assert time_before < time_after
 

def test_ressource_state_2_count_retries6_no_timeout(db_test):
    """
    {'State': 3, count_retries': 6, State_chg': inférieur au time out}
    devient
    {'State': 3, count_retries': 6, State_chg': ne doit pas avoir été modifié}
    """
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type1"]
    ID = list_of_ressources[2]['ID']
    state_of_ressource_before = check_state_of_ressource(ID)
    count_retries_of_ressource_before = check_count_retries_of_ressource(ID)
    time_before = check_state_chg_of_ressource(ID)
    
    ressource_state_machine(ID)

    state_of_ressource_after = check_state_of_ressource(ID)
    count_retries_of_ressource_after = check_count_retries_of_ressource(ID)
    time_after = check_state_chg_of_ressource(ID)

    assert state_of_ressource_before == 3
    assert count_retries_of_ressource_before == 6   
    assert state_of_ressource_before == state_of_ressource_after
    assert count_retries_of_ressource_before == count_retries_of_ressource_after
    assert  time_before == time_after
    
def test_ressource_state_2_count_retries6_timeout(db_test):
    """
    {'State': 3, count_retries': 6, State_chg': supérieur au time out}
    devient 
    {'State': 4, count_retries': 7, State_chg': maintenant}
    """
    dic_ressources = db_test[1]
    list_of_ressources = dic_ressources["type2"]
    ID = list_of_ressources[2]['ID']
    state_of_ressource_before = check_state_of_ressource(ID)
    count_retries_of_ressource_before = check_count_retries_of_ressource(ID)
    time_before = check_state_chg_of_ressource(ID)
    
    ressource_state_machine(ID)

    state_of_ressource_after = check_state_of_ressource(ID)
    count_retries_of_ressource_after = check_count_retries_of_ressource(ID)
    time_after = check_state_chg_of_ressource(ID)
 
    assert state_of_ressource_before == 3
    assert count_retries_of_ressource_before == 6     
    assert state_of_ressource_before < state_of_ressource_after
    assert count_retries_of_ressource_before < count_retries_of_ressource_after
    assert time_before < time_after
    
