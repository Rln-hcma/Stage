def filter_positive(num_list):
    """
        Filtre les nombres positif
        >>> filter_positive([1,3,5,-7,2,-5])
        [1,3,5,2]
    """
    positif_list=[]
    for i in num_list:
        if i >0:
            positif_list.append(i)
    return positif_list

def filter_fun(o_list,fun):
    """
        Retourne une liste d'éléments filtré par la fonction fun
        >>> filter_fun([40,25,"ours",7])
        [40,7]
    """
    a_list=[]
    for o in o_list:
        if fun(o):
            a_list.append(o)
    return a_list


def fun(anything):
    true_list=[40,"poisson",7,15,8]
    return (anything in true_list)


def filter_positive2(num_list):
    """
        Retourne une liste d'éléments positifs puis est filtrée par la fonction fun
        >>> filter_positive2([11,-7,-6,40])
        [40]
    """
   
    positive_numlist = filter_positive(num_list)
            
    return filter_fun(positive_numlist,fun)
    
