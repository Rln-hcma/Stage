import timeit

def flat_cart_prod(inputlist):
    cartesian_result = [[]]
    for a_list in inputlist:
        temp = []
        for a_elem in cartesian_result:
            for b_elem in a_list:
                temp.append(a_elem + [b_elem])
        cartesian_result = temp
    return cartesian_result


