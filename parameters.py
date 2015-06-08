from datetime import date

data = {}
headers = []

# read file and save into analyse's global variables.
def readFile(fileName):
    global data, headers
    data = {}

    f = open(fileName)
    s = f.readline().rstrip()
    headers = parseHeaders(s)
    n = len(headers)
    
    cols = []
    for i in range(0,n):
        cols.append([])
    
    for s in f:
        row = parseRow(s.rstrip())
        for i in range(0,n):
            cols[i].append(row[i])
            
    for i in range(0,n):
        data[headers[i]] = cols[i]
    f.close()
        
    #reverseAll()
    convertformat('Date', mapdateSlash)
    #convertformat('Date', mapdate)
    createformat('Day', 'Date', mapDateToDay)
    convertformat('Open', float)
    convertformat('High', float)
    convertformat('Low', float)
    convertformat('Close', float)
    convertformat('Volume', int)
    #convertformat('Adj Close', float)
    #applyVarParameter('AvgClose', 'Close', averageLast(10))

    return data, headers


def reverseAll():
    global data, headers
    for key in headers:
        data[key].reverse()

def parseHeaders(s):
    return s.split(',')
    
def parseRow(s):
    return s.split(',')

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
