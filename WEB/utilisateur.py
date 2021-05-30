from flask import Flask, request, render_template
import pickle, os, pytest, re, formulaire
from sqlobject import * 
from model import init, Word, Url, Occurence, User, Password, UserPassword

def get_config():
    app.config.from_envvar('DING_CONFIG')
    #sqlhub.processConnection = connectionForURI(app.config['DB_FILE'])


def consult_username():  
    return [elem.username for elem in User.select()]

def consult_passwd():
    return [elem.password for elem in Password.select()]

def account_is_create(username,passwd):
    search_user = check_exist_user(username)
    search_passwd = check_exist_passwd(passwd)
    if search_user and search_passwd:
        peeps = UserPassword.selectBy(target_user=search_user, target_password=search_passwd)
        request_sql = list(peeps)
        if request_sql:
            return True
        else:
            return False
    else:
           return False
           
def check_exist_user(user):
    try:
        return User.byUsername(user) #si exite renvoie l'objet
    except SQLObjectNotFound:   
        return False      #si existe pas renvoie none

def check_exist_passwd(passwd):
    try:
        return Password.byPassword(passwd)
    except SQLObjectNotFound:
        return False

def username_insert(username):
    try:
        user = User(username=username) 
        return user.username
    except dberrors.DuplicateEntryError:
        return None

def passwd_insert(passwd):
    try:
        password = Password.byPassword(passwd)
    except SQLObjectNotFound:
        password = Password(password=passwd)
    return password.password

def create_account(username,passwd):
    rep = username_insert(username)
    if rep == username:
        username = User.byUsername(user)
        #check si le compte n'as pas déjà été créé auparavant
        rep = account_is_create(username,passwd)
        if rep == False:
            new_password = passwd_insert(passwd)
            new_user = User.byUsername(username)
            UserPassword(target_user=new_user, target_password=new_password)
            return True
        else:
            return False
    else:
        return False

def delte_account(username,passwd):
    rep = account_is_create(username,passwd)
    if rep == True:
        user = User.byUsername(username)
        UserPassword.delete(user.id)
        return True
    else:
        return False

