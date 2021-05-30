from sqlobject import *


class TypeRessource(SQLObject):
    Name = StringCol(alternateID=True)
    hook_create = StringCol()
    hook_supress = StringCol()
    ressources = MultipleJoin('Ressource')

class Ressource(SQLObject):
    typeRessource = ForeignKey('TypeRessource')
    Contact1 = StringCol()
    Contact2 = StringCol()
    State = IntCol(default=1)
    State_chg = TimestampCol()
    count_retries = IntCol(default=0)
    loan_time = IntCol()
    username = StringCol(default=None)

class UserPassword(SQLObject):
    username = StringCol(alternateID=True)
    storage = StringCol()
    role = StringCol()

def init():
    Ressource.createTable()
    TypeRessource.createTable()
    UserPassword.createTable()
