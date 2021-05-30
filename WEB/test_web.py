import pickle, os, pytest, re, formulaire, random, string
from shutil import copyfile
import tempfile 

from formulaire import app, get_config, insert_url, delete_url, consult, delete_word, insert_word, contains, url_associate, resset_occ_nmbr, associate_url
from model import init, Word, Url, Occurence
from sqlobject import *
from random import randrange


@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def config_test():
    #temp_db = tempfile.NamedTemporaryFile(delete=False)
    temp_config = tempfile.NamedTemporaryFile(delete=False)

    config ={
        'ROOT_DIR': '/truc/machin/bidule',
        'DB_FILE' : 'sqlite:/:memory:',
        'IP_ADDR' : '127.0.0.1',
        'PORT' : '8080'
    }

    for key, value in config.items():
        temp_config.file.write((f'{key} = "{value}"\n').encode("UTF-8"))
    temp_config.file.seek(0)
    
    os.environ['DING_CONFIG'] = temp_config.name
    
    yield config

    sqlhub.processConnection.close()
    
@pytest.fixture
def db_test(config_test):
    dic = {   'cachalot': {   'http://mer-sans-eau.com': (None, '15256'),
                    'https://mer-salée.com': (2, '15686')},
    'corbeau': {   'https://example.com': (6, '15256'),
                   'https://montagne.com': (5, '47255'),
                   'https://renard.com': (2, '15686')},
    'renard': {'https://colibris.com': (5, '47255')}}
  
    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    init()
    
    for key, value in dic.items():
        word = Word(word=key)
        for k,v in value.items():
            url = Url(url=k)
            Occurence(target_word= word, target_url= url, nb_occurence=v[0])
            
    yield dic
    
def test_config(config_test):
    get_config()
    sqlhub.processConnection = connectionForURI(config_test['DB_FILE'])
    for key, value in config_test.items():
        assert config_test[key] == app.config[key]
        

def test_set_occ_nmbr_urlNotExist(db_test):
    """
       set_occ_nmbr fixe le nombre d'une association existante
       (fixe le nombre d'occurence du mot <word> dans l'url <url> à <nmbr>)
       occurence_associate(url,word) renvoie le nombe de fois que le mot apparait dans l'url
    """
    url = random_string(url=True)
    list_word = consult()
    word = random.choice(list(list_word)) 
    nmbr = random.randint(0,9)
    
    list_url = consult(url=True)
    assert url not in list_url
    
    response = resset_occ_nmbr(url, word, nmbr)
    assert response == None 
    
def test_set_occ_nmbr_wordNotExist(db_test):
    """
       set_occ_nmbr fixe le nombre d'une association existante
       (fixe le nombre d'occurence du mot <word> dans l'url <url> à <nmbr>)
    """   
    word = random_string(word=True)
    list_url = consult(url=True)
    url = random.choice(list(list_url)) 
    nmbr = random.randint(0,9)
    
    list_word = consult()
    assert word not in list_word
    
    response = resset_occ_nmbr(url, word, nmbr)
    assert response == None 
    
def test_set_occ_nmbr_url_notAssociate(db_test):
    """
       set_occ_nmbr fixe le nombre d'une association existante
       (fixe le nombre d'occurence du mot <word> dans l'url <url> à <nmbr>)
       occurence_associate(url,word) renvoie le nombe de fois que le mot apparait dans l'url
       url_associate(word) renvoie les urls associées aux mots
    """  
    url = 'https://mer-salée.com'
    word = 'renard'
    nmbr = random.randint(0,9)
    list_url_associate = associate_url(word)
    assert not url in list_url_associate
    
    response = resset_occ_nmbr(url, word, nmbr)
    assert response == None 
    
    
def _set_occ_nmbr_url(db_test):
    """
       set_occ_nmbr fixe le nombre d'une association existante
       (fixe le nombre d'occurence du mot <word> dans l'url <url> à <nmbr>)
       url_associate(word) renvoie les urls associées aux mots  
       occurence_associate(url,word) renvoie le nombe de fois que le mot apparait dans l'url
    """  
    url = 'http://mer-sans-eau.com'
    word = 'cachalot'
    nmbr = 7
    insert_url(target_url)
    
    list_url_associate = associate_url(word)
    assert url in list_url_associate
  
    response = resset_occ_nmbr(url, word, nmbr)
    assert response == nmbr
    assert occurence_associate(url,word) == nmbr
   
    
  
def test_insert_url(db_test):
    """
       Vérifie si la donction insert_url réussi à ajouter une url dans la DB 
       Consult(url=True) renvoie une liste comportant l'entièreté des urls de la DB 
    """
    target_url = random_string(url=True)
    list_url = consult(url=True)
    
    
    assert not target_url in list_url, "Url already exists"
    insert_url(target_url)
    list_url = consult(url=True)
    assert target_url in list_url, "The url has not been registered"
    
def delete_url(db_test):
    """
       Vérifie si la fonction delete_url réussi à supprimer un mot dans la DB 
       Consult(url=True) renvoie une liste comportant l'entièreté des urls de la DB
    """
    list_url = consult(url=True)
    target_url = random.choice(list(list_url)) 
    
    assert target_url in list_url, "The url doesn't exist"
    delete_url(target_url)
    list_url = consult(url=True)
    assert not target_url in list_url, "The url has not been deleted"

def test_insert_word(db_test):
    """
       Vérifie si la fonction insert_word réussi à ajouter une mot dans la DB 
       Consult() renvoie une liste comportant l'entièreté des mots de la DB
    """
    target_word = random_string(word=True)
    
    list_word = consult()
    
    assert not target_word in list_word, "Word already exists"
    insert_word(target_word)
    list_word = consult()
    assert target_word in list_word, "The word has not been registered"
    
def delete_word(db_test):
    """
       Vérifie si la fonction delete_word réussi à supprimer un mot dans la DB 
       Consult() renvoie une liste comportant l'entièreté des mots de la DB
    """
    list_word = consult()
    target_word = random.choice(list(list_word))
    
    
    assert target_word in list_word, "The word doesn't exist"
    delete_word(target_word)
    list_word = consult()
    assert not target_word in list_word, "The word has not been deleted"

 
def test_index(client):
    """Checks if the app returns HTML page with a form to search"""
    
    rv = client.get('/')
    assert b'<form action="http://127.0.0.1:5000/search" method="post">'  in rv.data
    #print((rv.data).decode("utf-8"))
    
    
def random_string(url=None,word=None):
    if url:
        random_string = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
        return (f'https://{random_string}.com')
    if word:
        return ''.join(random.choice(string.ascii_lowercase) for i in range(6))
    
    
def universal_search(client, true_urls, url_post, search, field_search):
    
    rv = client.post(url_post, 
                     data={field_search:search})
    
    data_decode = (rv.data).decode("utf-8")
    
    #catch le mot dans HTML
    target_search = re.findall("Recherche: (.*?)[<]", data_decode)

    #catch url dans HTML
    target_urls = re.findall("<li>(.*?)</li>", data_decode)
    
    #if empty    
    assert target_search[0]
    assert target_search[0] == search
    
    true_urls.sort()
    target_urls.sort()
    
    #verification de la liste
    for elem in reversed(true_urls): 
        a = target_urls.pop()
        assert elem == a
        
    assert not target_urls 
 
    
def test_search_all_url(client, db_test):    
    """test"""
    
    true_urls = ['https://example.com', 'https://renard.com','https://montagne.com']
    url_post = '/search'
    search = 'corbeau'
    field_search = 'search'
    
    universal_search(client, true_urls, url_post, search, field_search)

def test_search_1_url(client, db_test):    
    """test"""
    
    true_urls = ['https://colibris.com']
    url_post = '/search'
    search = 'renard'
    field_search = 'search'
    
    universal_search(client, true_urls, url_post, search, field_search)
    
def test_search_no_url(client, db_test):    
    """test"""
   
    true_urls = []
    url_post = '/search'
    search = 'sanglier'
    field_search = 'search'
   
    universal_search(client, true_urls, url_post, search, field_search)  
    
