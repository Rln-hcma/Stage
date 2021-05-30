from sqlobject import *


class Word(SQLObject):
    word = StringCol(alternateID=True)
    urls = SQLRelatedJoin('Url', 	
        intermediateTable='occurence',
        createRelatedTable=False)
    
class Url(SQLObject):
    url = StringCol(alternateID=True)
    words = SQLRelatedJoin('Word',	
        intermediateTable='occurence',
        createRelatedTable=False)
  

class Occurence(SQLObject):
    class sqlmeta:
        table = "occurence"
    target_word = ForeignKey('Word', notNull=True, cascade=True)
    target_url = ForeignKey('Url', notNull=True, cascade=True)
    nb_occurence = IntCol()
    unique = index.DatabaseIndex(target_word, target_url, unique=True)

class User(SQLObject):
    username = StringCol(alternateID=True)
    password = SQLRelatedJoin('Password',
        intermediateTable='user_password',
        createRelatedTable=False)
    
class Password(SQLObject):
    password = StringCol(alternateID=True)
    user = SQLRelatedJoin('User',
    intermediateTable='user_password',
        createRelatedTable=False)

class UserPassword(SQLObject):
    class sqlmeta:
        table = "user_password"
    target_user = ForeignKey('User', notNull=True, cascade=True)
    target_password = ForeignKey('Password', notNull=True, cascade=True)
    unique = index.DatabaseIndex(target_user, target_password, unique=True) 

def init():
    Word.createTable()
    Url.createTable()
    Occurence.createTable()
    User.createTable()
    Password.createTable()
    UserPassword.createTable()

