from modify_model_ressource import create_ressource, delete_type_ressource, delete_ressource, create_type_ressource, change_type_of_ressource, check_contact1_of_ressource, check_contact2_of_ressource, consult_ressources_connect_of_type_ressource, check_exist_type_of_ressource, check_count_retries_of_ressource, check_state_chg_of_ressource, check_state_of_ressource, check_exist_ressource, consult_ressources, consult_type_ressources
from model import TypeRessource, Ressource
from sqlobject import *
from datetime import datetime
from importlib import import_module
import os, re

dic_config = {}

def get_config():
    global dic_config
    i=0 
    with open (os.environ["CONFIG"], 'r')as f:
        config = f.read()
        key_dic = re.findall("(.*) =",config)
        value_dic = re.findall(" = [\"](.*?)[\"]", config)
    
    for elem in key_dic:
        dic_config[elem]=value_dic[i]
        i = i +1
    return dic_config

   
def add_count_retries(ID): 
    """
    add_count_retries(int)
    Incrémentation(+1)
    Return le nbre de tentative réalisée pour ressource sous format int - return false si la ressource n'existe pas 
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:    
        retries = ressource_object.count_retries
        ressource_object.count_retries = retries +1  
        return retries +1
    else:
        return False 
        
def up_state(ID):
    """
    up_state(int)
    Incrémentation(+1)
    Return l'etat sous format int - return false si la ressource n'existe pas 
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:    
        state = ressource_object.State
        ressource_object.State = state +1  
        return ressource_object.State
    else:
        return False 
        
def modify_state_chg_etat_to_now(ID):
    """
    modify_state_chg_etat_to_now(id)
    Changement de date à maintenant
    Return True ou Return False 
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:    
        ressource_object.State_chg = datetime.now()
        return True
    else:
        return False 

def check_time_spent(ID):
    """
    test_check_time_spent(int)
    Vérifie si la ressourcé à dépassée la limite de time out
    Return True si le temps est dépassé - return false si le temps n'est pas dépassé 
    Return None si la ressource n'existe pas 
    """
    state_chg =check_state_chg_of_ressource(ID)
    if state_chg:
        time_out = int(dic_config['TIMEOUT'])
        
        time = (datetime.now() - state_chg).total_seconds()
        if time >= time_out:
            return True
        else:
            return False
    else:
        return None 
        
def check_time_spent_loan_time(ID):
    """
    test_check_time_spent_loan_time(int)
    Vérifie si la ressourcé à dépassée la limite de temps
    Return True si le temps est dépassé - return false si le temps n'est pas dépassé 
    Return None si la ressource n'existe pas 
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        loan_time = ressource_object.loan_time
        state_chg = ressource_object.State_chg
        test_time = int(dic_config['TIMEOUT'])
        nb_retries = (int(dic_config['NBR_RETRIES']))*2
        w = loan_time - nb_retries*test_time
        time = (datetime.now() - state_chg).total_seconds()
        if time >= w:
            return True
        else:
            return False
    else:
        return None
      
def check_nb_count_retries_limit(ID,state3=None):
    """
    check_nb_count_retries_limit(ID) pour l'état 2 
    check_nb_count_retries_limit(ID,state=True) pour l'état 3 
    Vérifie si la ressourcé à dépassée la limite d'essai 
    Return True si le nombre d'essai est dépassé - return false si le nombre n'est pas dépassé 
    Return None si la ressource n'existe pas 
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        limit_nb_retries = int(dic_config['NBR_RETRIES'])
        count_retries = check_count_retries_of_ressource(ID)
        if state3:
            if count_retries >= limit_nb_retries*2:
               return True
            else: 
               return False    
        else:
            if count_retries >= limit_nb_retries:
                return True
            else: 
               return False
    else:
        return None

def hook_contact(ID, state2=None, state3=None):
    """
    Prend la fonction hook_contact à partir de la config et prend le contact n°1 ou n°2 en fonction de l'état choisi state2 ou state3
    HOOK-CONTACT doit suivre le procédé suivant : MODULE.FONCTION
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        f, m = dic_config['HOOK-CONTACT'].rsplit('.', 1)
        mod = import_module(f)
        hook_contact = getattr(mod, m)
        if state2:
            contact = ressource_object. Contact1
        else : 
            contact = ressource_object.Contact2
        hook_contact(contact)
        return True
    else:
        return False


def hook_sup(ID):
    """
    Prend la fonction hook_supress à partir du type de la ressource
    hook-supress doit suivre le procédé suivant : MODULE.FONCTION
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        module_func = ressource_object.typeRessource.hook_supress
        f, m = module_func.rsplit('.', 1)
        mod = import_module(f)
        hook_suppress = getattr(mod, m)
        hook_suppress(ID)
        return True
    else:
        return False

def hook_create(ID):
    """
    Prend la fonction hook_create à partir du type de la ressource
    hook-create doit suivre le procédé suivant : MODULE.FONCTION
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        module_func = ressource_object.typeRessource.hook_create
        f, m = module_func.rsplit('.', 1)
        mod = import_module(f)
        hook_create = getattr(mod, m)
        hook_create(ID)
        return True
    else:
        return False

def ressource_state_machine(ID):
    ressource_object = check_exist_ressource(ID)
    if ressource_object:  
        state = check_state_of_ressource(ID)
        if state == 1:
            time = check_time_spent_loan_time(ID)
            if time:
                up_state(ID)
                modify_state_chg_etat_to_now(ID)
        elif state == 4:
            hook_sup(ID)
        else:
            time = check_time_spent(ID)
            if time:
                state = check_state_of_ressource(ID)
                if state == 2:
                    count = check_nb_count_retries_limit(ID)
                    if count:
                        up_state(ID)
                    else:  
                        hook_contact(ID,state2=True)
                    add_count_retries(ID)
                if state == 3:
                    count = check_nb_count_retries_limit(ID,state3=True)
                    if count:
                        up_state(ID)
                    else: 
                        hook_contact(ID,state3=True)
                    add_count_retries(ID)
                modify_state_chg_etat_to_now(ID)
    else:
        return None
        
