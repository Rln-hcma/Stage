"""
    Module asciiart
"""

def carre(l):
    """
       Affiche un carré
       >>> carre(5)
       *****
       *****
       *****
       *****
       *****

    """
    for x in range (l):
        print("*"*l)

def rectangle(l, L):
    """
        Affiche rectangle
        >>> rectangle(5, 2)
        *****
        *****
    """

    for longueur in range(L):
        print("*"*l)


def triangle_iso(h):
"""
        Affiche un triangle iscoèle
        >>> triangle_iso(5)
        *****
        *****
    """
    hauteur = h
    nbr_etoiles = 1
    nbr_espace = hauteur - 1
    for x in range (hauteur):
        print(nbr_espace * " " + nbr_etoiles  * "*")
        
        nbr_etoiles += 2
        nbr_espace -= 1
