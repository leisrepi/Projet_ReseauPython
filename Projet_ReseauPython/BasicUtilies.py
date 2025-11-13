from math import ceil, log2

def to_int(s: str):
    try:
        return int(s)
    except ValueError:
        return None
def to_float(s: str):
    try:
        return float(s)
    except ValueError:
        return None

def round_up_to_power_of_two(n):
    """Arrondit un entier à la puissance de 2 supérieure

        Args:
            n (int) : entier à arrondir

        Returns:
            return (int) : Renvoie l'entier arrondi à la puissance de 2 supérieure
    """
    return 2 ** ceil(log2(n))
    