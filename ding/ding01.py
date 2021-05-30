# ding01, first implementation of the DING project
# THIS IS JUST AN EMPTY TEMPLATE
import re

def get_words(filename=None, minlength=3, list_format=None, href_lien= None ):
    """
        Return the words found into <filename> if they have <minlength>
        characters or more
    """
    compteur = {}
    words = []
    special_caract = r"[.\`\-\=\~\!\@\#\$\%\^\&\»\«\*\(\)\_\+\[\]\{\}\;\'\\\:\"\|\<\,\/\>\<\>\?\+ ]"
    
    if filename :  
        with open(filename) as f:
            for line in f:
                line = line.strip().lower() #remove /n
                line = re.split(special_caract,line) 
                words += line 
                
    if list_format:
       for line in list_format:
            line = line.lower() 
            line = re.split(special_caract,line) 
            line =  [k for k in line if k != '']
            words += line 
                
                       
    if words:
        whithout_duplicate = set(words)
        compteur = occurence_words(whithout_duplicate,minlength,words)
    elif href_lien:
        whithout_duplicate = set(href_lien)
        compteur = occurence_words(whithout_duplicate,minlength,href_lien)
    
    return compteur
    
 

def search(d, searchstr, sortit=None, reverse=None):
    """
        Return matching for <searchstr> into dictionnary <d>
    """
    trans = str.maketrans({"é":"e", "è":"e","ê":"e"}) #translate
    
    search_str = searchstr.lower()
    if search_str[0] == "*": 
        search_str = search_str.replace("*","(.)*")
    elif search_str[-1] == "*": 
        search_str = search_str.replace("*","(.)*")
    elif "*" in search_str:  search_str = search_str.replace("*","(.)*") + "$"     

    key_list = [(k,val)  for (k, val) in d.items() if re.match(search_str,k)]
    
    if sortit: 
        key_list.sort(key=lambda k: k[0].translate(trans))
    if reverse: key_list.reverse()
    
    return (key_list)

def occurence_words (whithout_duplicate,minlength,words):
    compteur = {}
    for elem in whithout_duplicate:
            if  len(elem) >= minlength:
                nb_occurence = words.count(elem)
                compteur[elem] = nb_occurence
    return compteur 
