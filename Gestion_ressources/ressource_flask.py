from flask import Flask, request, render_template, session, redirect, url_for
from user_mdp import get_config, consult_username, check_exist_user, login, check_key, check_role_of_user
from modify_model_ressource import change_state_of_ressource, check_exist_ressource, consult_type_ressources, check_exist_type_of_ressource
from projet_ressource import hook_create
from model import init, TypeRessource, Ressource, UserPassword
from datetime import datetime

def get_config():
    app.config.from_envvar('CONFIG')

def consult_ressources_state_0():
    """
    Fonction liée directement à flask 
    Renvoie sous forme de tableau les ressources en état 0 
    """
    tab = []
    for elem in Ressource.select():
        if elem.State == 0:
            tab2 = [elem.id,elem.typeRessource.Name, elem.Contact1, elem.Contact2, elem.username]
            tab.append(tab2)
    return tab 

def check_empty_form():
    if not request.form.get('type_ressource'):
        return False
    if not request.form.get('contact1'):
        return False
    if not request.form.get('contact2'):
        return False
    return True    
 
def create_ressource_state_0():
    """
    Fonction liée directement à flask 
    Création d'une ressource dans l'état 0 à partir du formulaire remplit par l'utilisateur 
    """
    type_object = check_exist_type_of_ressource(request.form['type_ressource'])
    if type_object:
        return Ressource(typeRessource=type_object, Contact1=request.form['contact1'], Contact2=request.form['contact2'], State=0, State_chg=None , loan_time=None, username=session['name'])  
    else:
        return False 

def change_to_state_1(ID):
    """
    change_to_state_1(int)
    Fonction servant à l'application flask 
    Modifie la ressource pour l'intégrer dans la state machine 
    """
    ressource_object = check_exist_ressource(ID)
    if ressource_object:    
        ressource_object.State = 1
        ressource_object.State_chg = datetime.now()
        ressource_object.loan_time = 777600
        return ressource_object.State
    else:
        return False 


app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xc1 \xe7dm\x0fn\x14\xa5Aj\xe6\xb0d\xc1\xa7'

    
@app.route('/reservation', methods=["GET","POST"])
def reservation():
    """
    La page contient un formulaire de réservation composé :
      - d'un type de ressource
      - d'un contact n°1
      - d'un contact n°2
    lorsque le formulaire envoyé est valide, create_ressource_state_0() crée la ressource à partir du formulaire et
    ajoute le nom de l'utilisateur stocké dans la session
    """
    if session['user'] == 'user' or session['user'] == 'admin':
        type_ressources = consult_type_ressources()
        if request.method == 'POST':
            rep = check_empty_form()
            if rep:
                type_ressource = request.form['type_ressource']
                rep = check_exist_type_of_ressource(type_ressource)
                if rep == False:  
                    info = (f"Le type de ressource sélectionné nommé {type_ressource} est inexistant")
                    return render_template('ressource_reserv.html', type_ressources=type_ressources, info=info)
                else:
                    create_ressource_state_0()
                    info = (f"formulaire envoyé")
                    return render_template('ressource_reserv.html', type_ressources=type_ressources, info=info)
            else:
                info = (f"Le formulaire doit être entièrement rempli")
                return render_template('ressource_reserv.html', type_ressources=type_ressources, info=info)  
        else:
            return render_template('ressource_reserv.html', type_ressources=type_ressources)        
    else:
        return redirect(url_for('welcome'))
    
@app.route('/board', methods=["GET","POST"])
def board():
    """
    La page Board n'est disponible que pour les comptes admins 
    La page Board est composée :
        - De toutes les ressources à l'état 0 suivit d'une checkbox (case à cocher)
        - D'un bouton name=autoriser, la valeur renvoyé lorsque le bouton name=autoriser est pressé est : 'Autoriser'
        - D'un bouton name=supprimer, la valeur renvoyé lorsque le bouton name=supprimer est pressé est : 'Supprimer'
    Si 'Autoriser' la ressource est créée 
    Si 'Supprimer' on attribue State=5 à la ressource
    """
    if session['user'] == 'admin':
        if request.method == 'POST':
            target_ressources = request.form.getlist('mychekbox')
            if not request.form.get('supprimer'):
                request_admin = request.form.get('autoriser') 
            else:
                request_admin = request.form.get('supprimer')
            if request_admin == 'Autoriser':
                for ID in target_ressources:
                    change_state_of_ressource(ID,1)
                    hook_create(ID)
                info = (f"Les ressources {target_ressources} ont été approuvées")
            elif request_admin == 'Supprimer':
                for ID in target_ressources:
                    change_state_of_ressource(ID,5)
                info = (f"Les ressources {target_ressources} ont été désapprouvées")
            db_state_0 = consult_ressources_state_0()
            return render_template('board.html', db=db_state_0, info=info)
        else:
            db_state_0 = consult_ressources_state_0()
            return render_template('board.html', db=db_state_0)
    else:
        return redirect(url_for('welcome'))

@app.route('/', methods=["GET","POST"])
def welcome():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        rep = login(username, password)
        if rep:
            role = check_role_of_user(username)
            session['user'] = role
            session['name'] = username
            if role == 'admin':
                return redirect(url_for('board'))
            elif role == 'user':
                return redirect(url_for('reservation'))
        else:
            info = (f"Utilisateur ou mot de passe incorrecte")
            return render_template('index.html', info=info)
    else:
        return render_template('index.html')
