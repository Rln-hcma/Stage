from sqlobject import *
from model import TypeRessource, Ressource
from datetime import datetime


def consult_ressources():
    return [elem.id for elem in Ressource.select()]
    
def consult_type_ressources():
    return [elem.Name for elem in TypeRessource.select()]

def check_exist_type_of_ressource(type_ressource):
    try:
        return TypeRessource.byName(type_ressource)
    except SQLObjectNotFound:
        return False

def check_exist_ressource(ID):
    try:
        return Ressource.get(ID)
    except SQLObjectNotFound:
        return False

def check_contact1_of_ressource(ID):
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        return ressource_object.Contact1
    else:
        return False 

def check_contact2_of_ressource(ID):
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        return ressource_object.Contact2
    else:
        return False

def check_state_of_ressource(ID):
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        return ressource_object.State
    else:
        return False
        
def check_state_chg_of_ressource(ID):
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        return ressource_object.State_chg
    else:
        return False

def check_count_retries_of_ressource(ID):
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        return ressource_object.count_retries
    else:
        return False   

def check_the_type_ressource_of_ressource(ID):
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        return ressource_object.typeRessource.Name
    else:
        return False

def check_exist_ressource(ID):
    try:
        return Ressource.get(ID)
    except SQLObjectNotFound:
        return False

def consult_ressources_connect_of_type_ressource(type_ressource):
    object_type_ressource = check_exist_type_of_ressource(type_ressource)
    if object_type_ressource:
        return object_type_ressource.ressources
    else:
        return False 

def check_exist_type_of_ressource(type_ressource):
    try:
        return TypeRessource.byName(type_ressource)
    except SQLObjectNotFound:
        return False

def check_the_type_ressource_of_ressource(ID):
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        return ressource_object.typeRessource.Name
    else:
        return False

def check_loan_time_of_ressource(ID):
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        return ressource_object.loan_time
    else:
        return False 

def create_ressource(ressource):
    """
    Création d'une ressource et attriubtion à un type de ressource 
    La fonction prend en paramètre un dictionnaire contenant les inforamtions suivantes :
    ressource["Contact1"], ressource["Contact2"], ressource["State"], ressource["count_retries"] 
    ressource["loan_time"], ressource["State_chg"], ressource["typeRessource"]
    Si le type de ressource encodé pour la création n'existe pas alors Return False
        Return l'object "Ressource" si réussi 
    """
    type_object = check_exist_type_of_ressource(ressource["typeRessource"])
    if type_object:
        return Ressource(typeRessource=type_object, Contact1=ressource["Contact1"], Contact2=ressource["Contact2"], State= 1, State_chg=datetime.now() , loan_time=ressource["loan_time"])      
    else:
        return False

def create_type_ressource(type_ressource):
   """
   create_type_ressource(str)
   Return False si le type de ressource existait déjà - Return l'object "TypeRessource" créé si existe pas
   """
   if check_exist_type_of_ressource(type_ressource):
       return False
   else:
       return TypeRessource(Name=type_ressource, hook_create='fonction', hook_supress='fonction')

def delete_type_ressource(type_ressource):
    """
    delete_type_ressource(str)
    Supprime le type de ressource 
        Return True - Return False 
    """
    type_ressource_object = check_exist_type_of_ressource(type_ressource)
    if type_ressource_object:
        TypeRessource.delete(type_ressource_object.id)
        return True
    else:
        return False
        
def delete_ressource(ID):
    """
    delete_ressource(int)
    Supprime la ressource
        Return True - Return False 
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        Ressource.delete(ID)
        return True
    else:
        return False

def change_type_of_ressource(ID,type_ressource):
    """
    change_type_of_ressource(ID=int,type_ressource=str)
    Le type de ressource et la ressource doivent exister  
        Return l'object "Ressource" si la ressource a été moidifiée
        Retrun False si pas 
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:
        type_ressource_object = check_exist_type_of_ressource(type_ressource)
        if type_ressource_object:
            ressource_object.typeRessource = type_ressource_object 
            return ressource_object
        else:
            return False
    else:
        return False   
 
def change_state_of_ressource(ID,nbr):
    """
    change_state_of_ressource(ID=int,nbr=int)
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:    
        ressource_object.State = nbr  
        return ressource_object.State
    else:
        return False      