=====
Machines à états et cycles de vie
=====

Notre application est conçue pour gérer le cycle de vie des ressources informatiques fournies aux utilisateurs. Une ressource est créée pour une certaine période de temps, avant sa fin de période de location nous esseyons de contacter la personne de contacte. Afin d'effectuer cette opération, toutes les x temps notre application analysera l'état de chaque ressource. 

Une ressource peut avoir 5 états différents 
    - state 0 : ressource en attente de validation afin d'entrer ou pas dans la machine à états 
    - state 5 : demande de la ressource désaprouvée, stockée dans l'état 5
    - state 1 à 4 : directement lié à la machine à états (voir state_machine_ressource.png)
    
Pour changer d'état une ressource doit respecter 3 conditions :
    1. Être pourvu d'un état ;
    2. Le temps imparti doit être dépassé ; 
    3. Le nombre de tentatives doit être dépassé ; 


Le temps imparti doit être dépassé. Soit Time >= Timeout 
    - Time exprime le temps passé dans un état (exprimé en seconde). Ce temps est calculé de la manière suivante :
      Time = date actuelle - State_chg
    - Timeout exprime la durée accordée avant de réitérer l'opération (exprimé en seconde)

Chaque itération dans une boucle implique le recalcule de State_chg. 

SQL
-----
La base donnée SQL est composée de 3 tables :

1. TypeRessource 
    - Name =  StringCol(alternateID=True) 
    - hook_create = StringCol()
    - hook_supress = StringCol()
    - ressources = MultipleJoin('Ressource')
    
2. Ressource
    - typeRessource = ForeignKey('TypeRessource')
    - Contact1 = StringCol()
    - Contact2 = StringCol()
    - State = IntCol()
    - Chgment_etat = TimestampCol()
    - count_retries = IntCol(default=0)
    - loan_time = IntCol()  => temps de location de la ressources
    - *username = StringCol(default=None)

3. UserPassword


*username. La réservation d'une ressource ce fait par le biais d'une page web, username fait référence au nom du compte permettant de s'authentifier

Une relation Many-to-one est établie entre les 2 tables.
L'attribut "typeRessource" de l'entité "Ressource", crée la relation avec l'entité "TypeRessource"
En d'autres termes, une ressource est liée à un seul type de ressource et un type de ressource peut avoir plusieurs ressources.

hook_create et hook_supress doivent contenir sous forme de string MODULE.FONCTION (le module et la fonction qui leur sont propre)

=====
Gestion des utilisateurs (username/mot de passe)
=====

SQL
-----
La base donnée SQL est composée de 3 tables :

1. TypeRessource 
    
2. Ressource

3. UserPassword
    - username = StringCol(alternateID=True)
    - storage = StringCol()
    - role = StringCol()


storage contient le sel + le hash 

Utilisation de PBKDF2 comme fonction de dérivation de clé
-----
PBKDF2 fournit PBKDF2_HMAC comme fonction pseudo-aléatoire, calculé en utilisant une fonction de hachage cryptographique en combinaison avec une clé secrète.
PBKDF2_HMAC est fourni avec Python, en Python 3.4 ou supérieur.
https://docs.python.org/3/library/hashlib.html#hashlib.pbkdf2_hmac

PBKDF2_HMAC prendra 4 paramètres:

1. hash_name: algorithme de hachage pour HMAC 
2. password: le mot de passe étant transformé en clé (c.-à-d. convertit en bytes)
3. salt: un sel généré aléatoirement 
4. iterations: nombre d'itérations dans le calcul 

1. La famille SHA-2 comprend six fonctions de hachage, SHA-256 est la version la plus utilisée. SHA-256 renvoie un code de 64 caractères sous la forme d'un nombre hexadécimal. Cette version sera utilisée comme algorithme de hachage pour HMAC.

2. Le mot de passe doit être convertit en bytes. Il est donc nécessaire de le convertir par le biais de "encode('utf-8')"

3. Chaque mot de passe relatif à un utilisateur doit avoir son propre sel. En effet, celui-ci une fois combiné au mot de passe permet de couvrir une plus grande plage et de limiter les attaques sur plusieurs mots de passe en simultané. Le sel doit être assez longs pour que le sel de chaque utilisateur soit unique. 32 bits est conseillé 

4. Plus le nombre d'iterations est élevé, plus le nombre de calculs augmente(100000 dans notre cas).


Binascii
-----
Il est nécessaire pour pouvoir stocker le résultat sous forme de string d'importer le module binascii.
https://docs.python.org/3/library/binascii.html

binascii.unhexlify(data) renvoie la représentation hexadécimale des données binaire.
binascii.hexlify(data) renvoie les données binaires représentées par la chaîne hexadécimale hexstr.
binascii.hexlify(data).decode() renvoie une chaîne de string

La méthode unhexlify() pemettera de stocker le hash sous forme de string dans la DB.
La méthode binascii.unhexlify(data) pemettera une fois le hash extrait de la DB de le remettre sous sa forme originale 


=====
fichier
=====
La Machine à états et cycles de vie est décomposée en 5 fichiers python :

- modify_model_ressource.py : composé des fonctions liées au model de la base de donnée des tables ( TypeRessource et Ressource) // test_model.py
- projet_ressource.py : composé des fonctions liées directement à la machine à états  // test_state_machine_utility.py, test_state_machine(1_4,2,3).py
- ressource_flask.py : composé des fonctions liées a flask // test_flask_ressource.py
- user_mdp : composé des fonctions liées au mot de passe, la création de hash // test_user_mdp.py
- model.py : définit le fonctionnement de la db (trois tables : TypeRessource, Ressource, UserPassword)

