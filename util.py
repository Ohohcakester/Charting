#Lightweight functions only with no imports!

# ma: months ahead
ma = 4

def getRandomSublist(arr, size):
    import random
    arr = list(arr)
    random.shuffle(arr)
    return arr[:size]