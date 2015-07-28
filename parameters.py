from datetime import date
import util

# Set to true if you want to cache data files so that when you open the same
# company a second time, it does not have to load the file again.
# This is to speed up certain processes (e.g. weightoptimisation)
caching = False

# Don't modify these
data = {}
headers = []
cachedFiles = {}

# Call this function to read the file into python.
# returns a pair (data, headers).
# data is a dictionary, headers is the keys of the dictionary in a fixed order.
def readFile(fileName):
    global data, headers, cachedFiles
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
        
    """ Configure Parameters - START """
    #reverseAll()   # uncomment this if the data is in reverse order.
    convertformat('Date', mapdateSlash) # used for dates in the format YYYY/MM/DD
    #convertformat('Date', mapdate)     # used for dates in the format YYYY-MM-DD
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
    """ Configure Parameters - END """

    # This safety check will throw an error if the days are in reversed order.
    days = data['Day']
    if len(days) >= 2 and days[1] < days[0]:
        raise ValueError('ERROR! Days are in reverse order!')

    if caching == True:
        cachedFiles[fileName] = data, headers

    return data, headers


# Reverse all of the lists in data.
def reverseAll():
    global data, headers
    for key in headers:
        data[key].reverse()

# Used by readFile. Parses the first line as headers.
def parseHeaders(s):
    return s.split(',')
    
# Used by readFile. Parses the other lines as individual rows.
def parseRow(s):
    return s.rstrip().split(',')

# Not in use. For debugging purposes. Prints the read data in range (a,b)
def printrange(a, b):
    global data, headers
    for key in headers:
        print(key)
        print(data[key][a:b])

# Uses the function fun to convert a data type from one format to another.
# e.g. convertformat('Close', float) converts all entries in data['Close'] from string to float.
def convertformat(headerName, fun):
    global data
    data[headerName] = list(map(fun,data[headerName]))

# Similar to convert format, but creates a new header instead.
# e.g. createformat('Day', 'Date', mapDateToDay) creates a new entry data['Day'],
#      where data['Day'][i] stores mapDateToDay(data['Date'][i]) for all i.
def createformat(headerName, source, fun):
    global data, headers
    data[headerName] = list(map(fun,data[source]))
    headers.append(headerName)


# Fixed Parameter functions always act on the same data types in data.
# This creates a new entry in data using the function fun(data, size)
def applyFixedParameter(headerName, fun):
    global data
    size = 0
    for k in data.keys():
        size = len(data[k])
        if size != 0:
            break
    data[headerName] = fun(data, size)


# Variable Parameter functions act on the specified data types in data.
# This creates a new entry in data using the function:
# fun([data[inputs[0]], data[inputs[1]], ..., data[inputs[k]]], size)
# e.g. applyVarParameter('AvgClose', 'Close', averageLast(10)) computes the running
#      average of the last 10 elements of data['Close'], and saves it as data['AvgClose']
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

# converts a string date 1980-12-30 to a date object.
def mapdate(d):
    args = d.split('-')
    return date(int(args[0]),int(args[1]),int(args[2]))

# converts a string date 1980/12/30 to a date object.
def mapdateSlash(d):
    args = d.split('/')
    return date(int(args[0]),int(args[1]),int(args[2]))

# converts a date object to an integer day using a fixed reference point 1980/12/12.
def mapDateToDay(d):
    base = date(1980,12,12)
    return (d-base).days

""" REGION: DIRECT MAP FUNCTIONS - END """


""" REGION: FIXED PARAMETER MAP FUNCTIONS - START """
# functions of the form fun(data, size) : dataList

""" REGION: FIXED PARAMETER MAP FUNCTIONS - END """

""" REGION: VARIABLE PARAMETER MAP FUNCTIONS - START """
# functions of the form fun(dataTypes, size) : dataList
# where dataTypes is a list like ['Close', 'Open', 'High']

# Applies the sign function to the output of a map function.
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

# E.g. for runningAverageDifference(10, 30),
# this computes averageLast(10) - averageLast(30)
def runningAverageDifference(n1, n2):
    avg1 = averageLast(n1)
    avg2 = averageLast(n2)

    def fun(inputs, size):
        li1 = avg1(inputs, size)
        li2 = avg2(inputs, size)
        return [a-b for a,b in zip(li1,li2)]

    return fun

# E.g. for runningAverageRatio(10, 30),
# this computes averageLast(10) / averageLast(30)
def runningAverageRatio(n1, n2):
    avg1 = averageLast(n1)
    avg2 = averageLast(n2)

    def fun(inputs, size):
        li1 = avg1(inputs, size)
        li2 = avg2(inputs, size)
        return [a/b for a,b in zip(li1,li2)]

    return fun

# Computes the n-running average of a dataList.
# e.g. in the list [9,8,7,6,5,4,3,2,1], the 5-running average at index 6 is mean([7,6,5,4,3])
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

# returns the averageLast of an input dataList.
# this one is designed o be called from other scripts. More convenient to use than averageLast.
def averageLastList(dataList, n):
    return averageLast(n)([dataList], len(dataList)) 

""" REGION: UTILITY - END """
