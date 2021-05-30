#!/usr/bin/env python3
# coding: utf-8
import ding01
import re
import urllib.request
from time import time as mtime
import os 
import pickle

dic_url_db = {}
dic_word_db = {}

db_u = 'db_urls.pick'
db_w = 'db_words.pick'

def lock_taker(fonction):
    def wrapper(*args, **kwargs):
        try:
            os.mkdir(".lock")
            retval = fonction(*args, **kwargs)
            os.rmdir(".lock")
           
            return retval
        except OSError:
            return None
   
    return wrapper

def store_universal(db, dic):
    def store_urls_pickle(fonction):
        def wrapper(*arg, **kwargs):
            retval = fonction(*arg, **kwargs)
            with open(db,'wb') as f:
                pickle.dump(dic, f)
            
            return retval
        return wrapper 
    return store_urls_pickle

def get_universal(db,dic):
    def get_urls_pickle(fonction):
        def wrapper(*arg, **kwargs):
            try: 
                with open(db,'rb') as f:
                    dic = pickle.load(f)
                
                return fonction(*arg, **kwargs)
            except FileNotFoundError:
                return {}
 
        return wrapper
    return get_urls_pickle

@lock_taker 
@store_universal(db_u,dic_url_db)
def store_urls(url, url_dict):
    global dic_url_db
    
    if url_dict:
        stamp = mtime()
        dic_url_db[url] = stamp , url_dict
        return stamp
    else: 
        dic_url_db.pop(url,0)
        return 0
 
@lock_taker       
@get_universal(db_u,dic_url_db)
def get_urls(url=None):

    if url is not None: 
        return dic_url_db.get(url,())  
    else: 
        return dic_url_db.keys()  
 
@lock_taker         
@store_universal(db_w,dic_word_db)
def store_data(url, word_dict):
    global dic_word_db
    
    if word_dict:
        stamp = mtime()
        dic_word_db[url] = stamp , word_dict
        return stamp
    
    else: 
        dic_word_db.pop(url,0)
        return 0 

@lock_taker        
@get_universal(db_w,dic_word_db)
def get_data(url=None):
    
    if url is not None: 
        return dic_word_db.get(url,())  
    else: 
        return dic_word_db.keys()  

def search(s, sortit=True, reverse=False):
    """
        Return matching for <searchstr> into dictionnary <d>
    """
    result = {}
    
    trans = str.maketrans({"é":"e", "è":"e","ê":"e"}) #translate
    
    s = s.lower()
    if s[0] == "*": 
        s = s.replace("*","(.)*")
    elif s[-1] == "*": 
        s = s.replace("*","(.)*")
    elif "*" in s:  s = s.replace("*","(.)*") + "$"     

    
    for cle,valeur in dic_word_db.items():#Pour un dictionnaire
        for k,val in valeur[1].items():
            if re.match(s,k):
                result[k]={cle: (val,valeur[0])}
                
    if sortit: 
        result = dict(sorted(result.items(),key=lambda k: k[0].translate(trans)))
    if reverse: result.reverse()
    
    return result

def web_index(url, minl=3):
    links ={}
    words = {}
    try:
        with urllib.request.urlopen(url) as f:
            html= f.read().decode()
    except:
        return links, words

    lien_href = re.findall("href=[\"](.*?)[\"]", html)
    if lien_href:
        links = ding01.get_words(href_lien=lien_href, minlength=minl)
    
     
    clean = re.compile(r'<[^>]*>')
    cleantxt = re.sub(clean, ' ',html)
    cleantxt = cleantxt.split("\n")
        
    words = ding01.get_words(list_format=cleantxt, minlength=minl)
        
    return links,words
