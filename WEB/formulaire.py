from flask import Flask, request, render_template
import pickle, os, pytest, re, formulaire
from sqlobject import * 
from model import init, Word, Url, Occurence

def get_config():
    app.config.from_envvar('DING_CONFIG')

def consult(url=None):  
    if url==True:
        return [elem.url for elem in Url.select()]
        
    else:
        return [elem.word for elem in Word.select()]

def check_exist_word(word):
    try:
        return Word.byWord(word)
    except SQLObjectNotFound:
        return False

def check_exist_url(url):
    try:
        return Url.byUrl(url)
    except SQLObjectNotFound:
        return False
        
def associate_url(word):
    search_word = check_exist_word(word)
    if search_word:
        peeps = Occurence.selectBy(target_word=search_word)
        request_sql = list(peeps)
        return [(elem.target_url).url for elem in request_sql]
    else:
        return None
        
        
        
        
        
 
def insert_url(target_url):
    try:
        Url(url=target_url)
    except dberrors.DuplicateEntryError:
        pass 
        
def insert_word(target_word):
    try:
        Word(word=target_word)
    except dberrors.DuplicateEntryError:
        pass
             
def delete_url(target_url):
    search_url = check_exist_url(target_url)
    if search_url:
        Url.delete(search_url)

def delete_word(target_word):
    search_word = check_exist_word(target_word)
    if search_word:
        Word.delete(search_word.id)

def contains(word, url):

    insert_url(url)
    insert_word(word)
    
    search_word = check_exist_word(word)   
    search_url = check_exist_url(url)

    
    if search_word:
        if search_url: 
            search_word.addUrl(search_url)

def url_associate(word,all_url=None):
    urls = []
    search_word = Word.byWord(word)
    url_db = search_word.urls
    return [elem.url for elem in search_word.urls]  
        

def resset_occ_nmbr(url, word, nmbr):
    url_sql = check_exist_url(url)
    word_sql = check_exist_word(word)
    if url_sql and word_sql:
        peeps = Occurence.selectBy(target_word=word_sql,target_url= url_sql)
        request_sql = list(peeps)
        if request_sql:
            Occurence(target_word= word_sql, target_url= url_sql, nb_occurence=nmbr)
            return nmbr
    else:
        return None 
      
app = Flask(__name__)


@app.route('/')
def index():
    
    return render_template('index.html')
    

@app.route('/search', methods=["POST"])
def search():
    urls_sort = []
    search = request.form['search']

    search_word = check_exist_word(search)
    if search_word:
        peeps = Occurence.selectBy(target_word=search_word)
        request_sql = list(peeps)
        urls_sort = [(elem.target_url).url for elem in request_sql]
     
    return render_template('resultat.html', search=search, urls_sort=urls_sort)
    
