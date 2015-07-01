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


def getNameOnly(s):
    firstSlash = s.find('/')
    if firstSlash != -1:
        s = s[firstSlash+1:]
    lastDot = s.rfind('.')
    if lastDot != -1:
        s = s[:lastDot]
    return s



def listDataFiles():
    import os

    def extension(s):
        return s[-4:] == '.csv'
    def addDir(s):
        return 'data/' + s

    files = map(addDir, filter(extension, os.listdir('data')))
    return files