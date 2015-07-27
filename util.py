""" Lightweight utility functions only with no imports! """
""" Importing util.py should not take a long time like similarity.py """


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



def listDataFiles(directory = 'data_'):
    import os

    def extension(s):
        return s[-4:] == '.csv'
    def addDir(s):
        return directory + '/' + s

    files = map(addDir, filter(extension, os.listdir(directory)))
    return files