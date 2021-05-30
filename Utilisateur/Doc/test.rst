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


Base de donnée 
-----

La base de donnée est composée d'une entité nommée UserPassword. Celle-ci est elle même composée de 2 attributs.

- ``username = StringCol(alternateID=True)``
- ``storage = StringCol()``

storage contient la clé et le sel sous format string
