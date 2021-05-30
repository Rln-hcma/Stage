def filter_positive(num_list):
    """
        Filtre les nombres positif
        >>> filter_positive([1,3,5,-7,2,-5])
        [1,3,5,2]
    """
    positif=[]
    for i in num_list:
        if i >0:
            positif.append(i)
    return positif
            
