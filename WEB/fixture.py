import pickle, os, pytest
from shutil import copyfile
from formulaire import app

dic = { "https://example.com" : ("12365", { "corbeau" : 6, "renard" : 7}), "https://fontaine.com" : ("12654", { "corbeau" : 6, "renard" : 7}), "https://renard.com" : ("65235", { "corbeau" : 6, "renard" : 7})}

@pytest.fixture
def client():
    return app.test_client()
    
@pytest.fixture
def db():
    if os.path.isfile('db.pick'):
 
        copyfile('db.pick','db.pick.bkp')
        os.remove('db.pick')
        
        with open('db.pick', 'wb') as f:
            pickle.dump(dic, f)
        
        yield 
        copyfile('db.pick.bkp','db.pick')
        os.remove('db.pick.bkp')
    
    else: 
        with open('db.pick', 'wb') as f:
            pickle.dump(dic, f)
    
        yield
        os.remove('db.pick')
