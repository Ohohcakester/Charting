#Lightweight functions only with no imports!

# ma: months ahead
ma = 4

def getRandomSublist(arr, size):
    import random
    arr = list(arr)
    random.shuffle(arr)
    return arr[:size]


# Assumption: all lists in lists have the same length. (i.e. a proper rectangular matrix)
def transposeLists(lists):
    return list(map(list, zip(*lists)))

def mean(dataList):
    return sum(dataList) / len(dataList)