#Lightweight functions only with no imports!


def getRandomSublist(arr, size):
    import random
    arr = list(arr)
    random.shuffle(arr)
    return arr[:size]