"""
    Module premettant d'afficher la suite des nombres de fibonacci
"""

def fibonacci(n):
    """
    >>>fibonacci(10)
    [1, 1, 2, 3, 5, 8]
    """
    result = []
    a, b = 0, 1
    while b < n:
        result.append(b)
        a, b =b , a+b
    return result
    
