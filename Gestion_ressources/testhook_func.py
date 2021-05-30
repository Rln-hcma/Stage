from utility import create_information_ressource, random_string

validation = ""

def check_validation_func():
    return validation

def fonction_contact(contact):
    global validation
    validation = random_string(word=True)
    return contact

def fonction_supp(ID):
    global validation
    validation = random_string(word=True)
    return ID

def fonction_create(ID):
    global validation
    validation = random_string(word=True)
    return ID
