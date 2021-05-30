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
    	
