from flask import Flask, request, render_template, session, redirect, url_for
from sqlobject import *
from model import UserPassword
import os, random, string, binascii, hashlib


def get_config():
    app.config.from_envvar('DING_CONFIG')
    # sqlhub.processConnection = connectionForURI(app.config['DB_FILE'])


def consult_username():
    return [elem.username for elem in UserPassword.select()]

def consult_storage():
    return [elem.storage for elem in UserPassword.select()]
    
def consult_account(username):
    rep = check_exist_user(username)
    if rep:
        return [rep.username,rep.storage]
    else:
        return False
        
def check_exist_user(user):
    try:
        return UserPassword.byUsername(user)
    except SQLObjectNotFound:
        return False


def create_account(username, passwd, fix_salt_for_test=None):
    if check_length_password(passwd):
        rep = check_exist_user(username)
        if rep == False:
            if fix_salt_for_test:
                storage = create_hash(passwd, fix_salt_for_test)
            else:
                storage = create_hash(passwd)
            UserPassword(username=username, storage=storage)
            return username
        else:
            return None
    else:
        return False


def delete_account(username):
    rep = check_exist_user(username)
    if rep:
        UserPassword.delete(rep.id)
        return True
    else:
        return False

def change_password(username, passwd):
    rep = check_exist_user(username)
    if rep:
        storage = create_hash(passwd)
        rep.storage = storage
        return storage
    else:
        return False

def delete_password(username):
    rep = check_exist_user(username)
    if rep:
        storage = None
        rep.storage = storage
        return storage
    else:
        return False

def login(username, passwd):
    rep = check_exist_user(username)
    if rep:
        if check_key(rep, passwd):
            return True
        else:
            return False
    else:
        return False


def check_key(rep, passwd):
    storage_str = rep.storage
    storage = binascii.unhexlify(storage_str)
    salt_from_storage = storage[:32]
    key_from_storage = storage[32:]

    password_to_check = passwd

    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        password_to_check.encode('utf-8'),
        salt_from_storage,
        100000
    )
    if new_key == key_from_storage:
        return new_key
    else:
        return False


def create_hash(passwd, fix_salt_for_test=None):
    if fix_salt_for_test:
        salt = fix_salt_for_test
    else:
        salt = os.urandom(32)
    salt_str = binascii.hexlify(salt).decode()
    key = hashlib.pbkdf2_hmac('sha256', passwd.encode('utf-8'), salt, 100000)
    key_str = binascii.hexlify(key).decode()
    return salt_str + key_str


def check_length_password(password):
    if int(app.config['LENGTH_CHARACTER']) <= len(password):
        return True
    else:
        return False

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xc1 \xe7dm\x0fn\x14\xa5Aj\xe6\xb0d\xc1\xa7'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check', methods=["POST"])
def check():
    username = request.form['name']
    password = request.form['password']

    rep = login(username, password)
    if rep:
        session['logged_in'] = True
        session['user'] = username
        return redirect(url_for('welcome'))
    else:
        return redirect(url_for('index'))


@app.route('/welcome')
def welcome():
    if 'logged_in' in session:
        return render_template('welcome.html')
    else:
        return redirect(url_for('index'))

@app.route('/board', methods=["GET","POST"])
def board():    
    account = consult_username()
    if request.method == 'POST':
        choice = int(request.form.get('mycheckbox'))
        if choice == 1:
            username = request.form['username']
            password = request.form['password']
            if username and password:
                rep = change_password(username, password)
                if rep == False:
                    info = (f"Utilisateur {username} introuvable")
                    return render_template('board.html',account=account, info=info)
                else:
                    info = (f"Utilisateur {username} a été modifié. Nouveau MDP attribué {password}")
                    return render_template('board.html',account=account, info=info)
            else:
                return render_template('board.html',account=account)
        elif choice == 2:
            username = request.form['username']
            if username:
                rep = delete_password(username)
                if rep == None:
                    info = (f"Mot de passe de {username} a été supprimé")
                    return render_template('board.html',account=account, info=info)
                else:
                    info = (f"Utilisateur {username} introuvable")
                    return render_template('board.html',account=account, info=info)
        elif choice == 3:
            username = request.form['username']
            password = request.form['password']
            if username and password:
                rep = create_account(username, password)
                if rep == False: 
                    info = (f"Mot de passe trop faible")
                    return render_template('board.html',account=account, info=info)
                elif rep:
                    info = (f"Utilisateur {username} a été créé")
                    return render_template('board.html',account=account, info=info)
                else:
                    info = (f"Utilisateur {username} existe déjà")
                    return render_template('board.html',account=account, info=info)
        else: 
            return render_template('board.html',account=account)  
         
    else:
        return render_template('board.html',account=account)
    
