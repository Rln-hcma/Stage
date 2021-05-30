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


def filter_bounds(num_list, low_bound=None, up_bound=None):
    """
        Filtre les nombres entre entre une valeur maximal et minimal si spécifié
        >>> filter_bounds([1,3,5,-7,2,-5])
        [1,3,5,-7,2,-5]
        >>> filter_bounds([1,3,5,-7,2,-5], low_bound = -5)
        [1,3,5,2,-5]
        >>> filter_bounds([1,3,5,-7,2,-5], up_bound = 2)
        [1,-7,2,-5]
        >>> filter_bounds([1,3,2], low_bound = -2, up_bound = 3)
        
    """
    a_list=[]
    if low_bound is None and up_bound is None:
        return num_list
    elif low_bound is None and up_bound is not None:
        for i in num_list:
            if i <= up_bound:
                a_list.append(i)
        return a_list
    elif low_bound is not None and up_bound is None:
        for i in num_list:
            if i >= low_bound:
                a_list.append(i)
        return a_list
    else:
        for i in num_list:
            if i <= up_bound and i >= low_bound:
                a_list.append(i)
        return a_list
    	

    


def filter_bound2(num_list, low_bound=None, up_bound=None):
    """
        Filtre les nombres entre entre une valeur maximal et minimal si spécifié, puis est
        filtrée par la fonction fun
        >>> filter_bound2([11,-7,-6,40,7],low_bound = -2, up_bound = 12)
        [7]
    """
    
    numlist_filtre = filter_bounds(num_list, low_bound, up_bound)
    
    return filter_fun(numlist_filtre,fun)
