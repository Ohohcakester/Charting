from datetime import date
import util

data = {}
headers = []
cachedFiles = {}
caching = False

# read file and save into analyse's global variables.
def readFile(fileName):
    global data, headers, cachedFiles, caching
    if caching == True:
        if fileName in cachedFiles:
            return cachedFiles[fileName]

    data = {}

    f = open(fileName)
    s = f.readline().rstrip()
    headers = parseHeaders(s)
    n = len(headers)
    
    cols = util.transposeLists(map(parseRow, f))
    f.close()

    for i in range(0,n):
        if len(cols) == 0: data[headers[i]] = []
        else: data[headers[i]] = cols[i]
        
    reverseAll()
    convertformat('Date', mapdateSlash)
    #convertformat('Date', mapdate)
    createformat('Day', 'Date', mapDateToDay)
    convertformat('Open', float)
    convertformat('High', float)
    convertformat('Low', float)
    convertformat('Close', float)
    #convertformat('Volume', int)
    #convertformat('Adj Close', float)

    #applyVarParameter('DiffClose', 'Close', runningAverageDifference(20,40))
    #applyVarParameter('AvgClose', 'Close', averageLast(10))
    #applyVarParameter('Running', 'Close', runningAverageDifference(1,20))
    #applyVarParameter('DiffCloseSign', 'Close', toSign(runningAverageDifference(20, 40)))

    #applyVarParameter('RatioClose', 'Close', runningAverageDifference(20,40))
    #applyVarParameter('RunningRatio', 'Close', runningAverageDifference(1,20))

    if caching == True:
        cachedFiles[fileName] = data, headers

    return data, headers



def reverseAll():
    global data, headers
    for key in headers:
        data[key].reverse()

def parseHeaders(s):
    return s.split(',')
    
def parseRow(s):
    return s.rstrip().split(',')

def printrange(a, b):
    global data, headers
    for key in headers:
        print(key)
        print(data[key][a:b])


def convertformat(headerName, fun):
    global data
    data[headerName] = list(map(fun,data[headerName]))

def createformat(headerName, source, fun):
    global data
    data[headerName] = list(map(fun,data[source]))

# Fixed Parameter functions always act on the same items in data.
def applyFixedParameter(headerName, fun):
    global data
    size = 0
    for k in data.keys():
        size = len(data[k])
        if size != 0:
            break
    data[headerName] = fun(data, size)

# Variable Parameter functions act on the specified items in data.
def applyVarParameter(headerName, inputs, fun):
    global data
    if isinstance(inputs, list):
        variables = []
        for s in inputs:
            variables.append(data[s])
    else: # is a single string
        variables = [data[inputs]]
    size = len(variables[0])

    data[headerName] = fun(variables, size)


""" REGION: DIRECT MAP FUNCTIONS - START """

def mapdate(d):
    args = d.split('-')
    return date(int(args[0]),int(args[1]),int(args[2]))

def mapdateSlash(d):
    args = d.split('/')
    return date(int(args[0]),int(args[1]),int(args[2]))

def mapDateToDay(d):
    base = date(1980,12,12)
    return (d-base).days

""" REGION: DIRECT MAP FUNCTIONS - END """


""" REGION: FIXED PARAMETER MAP FUNCTIONS - START """


""" REGION: FIXED PARAMETER MAP FUNCTIONS - END """

""" REGION: VARIABLE PARAMETER MAP FUNCTIONS - START """

def toSign(mapFun):
    def sgn(x):
        if x > 0:
            return 1
        elif x < 0:
            return -1
        return 0

    def fun(inputs, size):
        return list(map(sgn, mapFun(inputs, size)))

    return fun

def runningAverageDifference(n1, n2):
    avg1 = averageLast(n1)
    avg2 = averageLast(n2)

    def fun(inputs, size):
        li1 = avg1(inputs, size)
        li2 = avg2(inputs, size)
        return [a-b for a,b in zip(li1,li2)]

    return fun

def runningAverageRatio(n1, n2):
    avg1 = averageLast(n1)
    avg2 = averageLast(n2)

    def fun(inputs, size):
        li1 = avg1(inputs, size)
        li2 = avg2(inputs, size)
        return [a/b for a,b in zip(li1,li2)]

    return fun


def averageLast(n):
    def fun(inputs, size):
        assert(len(inputs) == 1)
        li = inputs[0]
        newli = []
        for i in range(0,n):
            newli.append(sum(li[:i])/(i+1))
        for i in range(n,size):
            newli.append(sum(li[i-n:i])/n)
        return newli
    return fun

""" REGION: VARIABLE PARAMETER MAP FUNCTIONS - END """


""" REGION: UTILITY - START """


def averageLastList(dataList, n):
    return averageLast(n)([dataList], len(dataList)) 

""" REGION: UTILITY - END """
