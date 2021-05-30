def filter_fun(o_list,fun)
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

def fun(anything)
    true_list=[40,"poisson",7,15,8]
    return (anything in true_list)
