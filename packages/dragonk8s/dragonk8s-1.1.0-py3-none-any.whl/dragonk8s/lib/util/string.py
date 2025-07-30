

def list_equal(l: list, l2: list) -> bool:
    if len(l) != len(l2):
        return False
    for i in l:
        if i not in l2:
            return False
    for i in l2:
        if i not in l:
            return False

    return True