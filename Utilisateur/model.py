from sqlobject import *

class UserPassword(SQLObject):
    username = StringCol(alternateID=True)
    storage = StringCol()

def init():
    UserPassword.createTable()


