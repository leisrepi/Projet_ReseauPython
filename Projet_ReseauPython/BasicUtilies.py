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
    