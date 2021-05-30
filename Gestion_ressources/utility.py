import random, string
from datetime import datetime, timedelta

def create_information_ressource(add_day=None):
    """
    Génère des données aléatoires et renvoi sous forme de dictionnaire 
    """
    ressource = {}
    ressource["Contact1"] = random_string(email=True)
    ressource["Contact2"] = random_string(email2=True)
    ressource["State"] = (random.randint(1, 3))
    ressource["count_retries"] = 0
    ressource["loan_time"] = 777600 #9days
    if add_day :
        ressource["State_chg"] = datetime.now() - timedelta(hours=960)
    else:
        ressource["State_chg"] = datetime.now() - timedelta(hours=4)
        
    return ressource

def create_information_type_ressource():
    """
    Génère des données aléatoires et renvoi sous forme de dictionnaire 
    """
    type_ressource = {}
    type_ressource["hook_create"] = random_string(hook=True)
    type_ressource["hook_supress"] = random_string(hook=True)
    type_ressource["name"] = random_string(word=True)
    return type_ressource

def random_string(word=None, email=None, email2=None, hook=None):
    if word: 
        return ''.join(random.choice(string.ascii_lowercase) for i in range(random.randint(6, 10)))
    if email:
        random_string = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
        return (f'student.{random_string}@ucl.be')
    if email2:
        random_string = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
        return (f'student.{random_string}@hotmail.be')
    if hook:
        random_string = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
        return (f'module.{random_string}')
