import parameters as para
#Format of group:
# (startindex, endindex, data, index) #bitmap deprecated

""" REGION: CONFIGURATION - START """
# Change the default configuration here. (choice of criteria from those available below in criteriaOptions)
defaultChoice = 2

# The different critera that can be used for dataselect are defined here.
def configureCriteriaOptions():
    def configure(criteriaFun, criteriaType, singleTS): return (criteriaFun, criteriaType, singleTS)
    global criteriaOptions

    # criteriaFun: The function used to filter out groups that match a criteria
    # criteriaType: The type of function used. Either "byPoints" or "byIndividual"
    # singleTS: True if the function operates on data['Close'] only. False if it operates on everything in data.

    criteriaOptions = {
        # criteria 0: break five-years-high
        0: configure (
            criteriaFun = breakHigh(yearsToDays(1), yearsToDays(5)),
            criteriaType = byPoints,
            singleTS = True,
            ),

        # criteria 1: Double Tops
        1: configure (
            criteriaFun = compose(getEndPoints, findDoubleTops),
            criteriaType = byPoints,
            singleTS = False,
            ),

        # criteria 2: Double Tops Filtered
        2: configure (
            criteriaFun = compose(getEndPoints, findDoubleTopsFiltered),
            criteriaType = byPoints,
            singleTS = False,
            ),

        # criteria 3: Random select
        3: configure (
            criteriaFun = randomMatch(0.003),
            criteriaType = byIndividual,
            singleTS = True,
            ),
    }

""" REGION: CONFIGURATION - END """


""" REGION: MAIN CONTROLS - START """

# This function is the main function to call in dataselect.py
# choice is numeric (which configuration to use)
def findMatches(data, groups, choice = None):
    if choice == None: choice = defaultChoice

    criteriaFun, criteriaType, singleTS = criteriaOptions[choice]

    if singleTS: data = data['Close']

    return criteriaType(data, groups, criteriaFun)


# An alternative function to call in dataselect.py.
# Allows you to specify the criteriaType and criteriaFun manually instead of 
# using one of the existing configurations.
def findMatchesWith(data, groups, criteriaType, criteriaFun):
    return criteriaType(data, groups, criteriaFun)


# One of the criteria types.
# Used for individual criteria.
def byIndividual(fulldata, groups, criteria):
    def fun(group):
        return criteria(fulldata, group[0], group[1])
    return list(filter(fun, groups))


# One of the criteria types.
# Used for points criteria.
# Assumes groups are sorted in chronological order (increasing)
def byPoints(fulldata, groups, criteria):
    markedPoints = criteria(fulldata)
    selectedGroups = []
    for point in markedPoints:
        group = findFirstGroupContainingPoint(groups, point)
        if group != None: # rare case. point is outside of all groups.
            selectedGroups.append(group)
    return selectedGroups

""" REGION: MAIN CONTROLS - END """


""" REGION: INDIVIDUAL CRITERION - START """
# Format of an individual criteria (byIndividual) function:
# function(fulldata, startIndex, endIndex)
# where startIndex, endIndex refers to the start, end points of the group.
# Returns: True if the group is to be selected, False if the group is to be omitted.

def randomMatch(probability):
    import random
    def criteria(fulldata, startIndex, endIndex):
        return random.random() < probability
    return criteria


def containsPoints(markedPoints):
    def fun(fulldata, startIndex, endIndex):
        for point in markedPoints:
            if startIndex <= point and point < endIndex:
                return True
        return False
    return fun

""" REGION: INDIVIDUAL CRITERION - END """




""" REGION: POINTS CRITERION - START """
# Format of a points criteria (byPoints) function:
# function(fulldata)
# Returns: A set of points (by index) in the data which match the criteria.
# Later on, we use these points to select groups by identifying the first group that contains each point.

def randomPoints(frac):
    import random
    def criteria(fulldata):
        return list(filter(lambda v : random.random() < frac, range(0,len(fulldata))))
    return criteria


def breakHigh(minDays, maxDays):
    def criteria(fulldata):
        if len(fulldata) < maxDays:
            return []

        markedPoints = []
        maxIndexList = generateMaxIndexList(fulldata, maxDays)
        preMaxIndexList = generateMaxIndexList(fulldata, maxDays-1)
        maxMinusMin = maxDays-minDays
        for i in range(0,len(maxIndexList)):
            point = i+maxDays-1
            if maxIndexList[i] == point and preMaxIndexList[i] < i+maxMinusMin:
                markedPoints.append(point)
        return markedPoints
        
    return criteria

""" REGION: POINTS CRITERION - END """



""" REGION: INTERVAL FILTERS - START """

def getEndPoints(intervals):
    return list(map(lambda v : v[1], intervals))

def increasingAveragesFilter(dataList):
    avg10 = para.averageLastList(dataList, 10)
    avg30 = para.averageLastList(dataList, 30)
    avg60 = para.averageLastList(dataList, 60)
    limit = 60

    def fun(interval): 
        point = interval[0]
        if point < limit: return False
        return avg10[point] > avg30[point] and avg30[point] > avg60[point]

    return lambda intervals : filter(fun, intervals)

""" REGION: INTERVAL FILTERS - END """



""" REGION: UTILITY - START """

# Compose multiple functions into one function
def compose(*funs):
    # reverse the list.
    funs = funs[::-1]
    def composed(x):
        for fun in funs:
            x = fun(x)
        return x
    return composed

# A function used to convert data -> data[dataType]. Useful to compose with other functions.
def using(dataType):
    def fun(data):
        return data[dataType]
    return fun

def findFirstGroupContainingPoint(groups, point):
    for group in groups: # group[0] = startIndex, group[1] = endIndex
        if group[0] <= point and point < group[1]:
            return group
    return None

# An approximate conversion for the number of working days in a year.
def yearsToDays(years):
    return years*250 #250 working days in a year.

# A utility function to efficiently compute the maximum values of a sliding window on an array.
# Given an array/list arr, and a window of size wSize,
# |------[-------]--------|
#         '-max-'
# For all possible window positions, from 0 to len(data) - wSize,
# Return the index of the maximum value of arr[] in that window.
# currently assuming all values of arr are positive. (so that -1 works.)
# O(n) algorithm.
def generateMaxIndexList(arr, wSize):
    resultList = []
    maxIndexList = [-1]*len(arr)
    unprocessedPoint = wSize
    unprocessedMax = -1
    maxIndexList[wSize-1] = wSize-1

    nextMaxPoint = -1
    for i in range(wSize-2, -1, -1):
        if arr[i] >= arr[maxIndexList[i+1]]:
            maxIndexList[i] = i
        else:
            maxIndexList[i] = maxIndexList[i+1]

    resultList.append(maxIndexList[0])
    for i in range(1,len(arr)-wSize+1):
        if i > nextMaxPoint:
            nextMaxPoint = maxIndexList[i]

        unprocessedMax = max(unprocessedMax, arr[i+wSize-1])
        if nextMaxPoint == -1 or arr[nextMaxPoint] < unprocessedMax:
            maxIndexList[i+wSize-1] = i+wSize-1
            for j in range(i+wSize-2, unprocessedPoint-1, -1):
                if arr[j] >= arr[maxIndexList[j+1]]:
                    maxIndexList[j] = j
                else:
                    maxIndexList[j] = maxIndexList[j+1]
            nextMaxPoint = maxIndexList[unprocessedPoint]
            unprocessedPoint = i+wSize
            unprocessedMax = -1

        resultList.append(nextMaxPoint)
    return resultList

# Opposite of generateMaxIndexList above. Also O(n).
def generateMinIndexList(arr, wSize):
    maxValue = max(arr)
    negList = list(map(lambda x : maxValue - x, arr))
    return generateMaxIndexList(negList, wSize)


# Helper function for finding Double Tops
# returns a function that can detects whether an index i is a peak value.
def peakIdentifierFun(dataList, peakGap):
    windowMax = generateMaxIndexList(dataList, peakGap*2)
    def isPeak(i):
        return i >= peakGap and i + peakGap < len(dataList) and \
            dataList[i] >= dataList[windowMax[i-peakGap]]
    return isPeak

# Helper function for finding Double Tops (for drawing the peaks)
# converts a boolean function to a functoin that returns high for True, low for False.
def boolToIntFun(boolFun, low, high):
    def intFun(x):
        if boolFun(x):
            return high
        return low
    return intFun

# Double Tops Filtered: Finds points which are double tops, which satisfy the "increasing averages" condition.
def findDoubleTopsFiltered(data):
    intervals = findDoubleTops(data)
    return increasingAveragesFilter(data['Close'])(intervals)
    

def plotDoubleTopsFiltered(data, plotGraphs = False, plotPeaks = False, start = None, end = None):
    if start == None: start = 0
    if end == None: end = len(data['High'])

    intervals = findDoubleTops(data, start=start, end=end)
    intervals = increasingAveragesFilter(data['Close'])(intervals)

    boxlow = 0
    boxhigh = 100

    if plotGraphs:
        import matplotlib.pyplot as plt
        def plotBox(i,j):
            record = [boxlow]*(end-start)
            for k in range(i,j+1):
                record[k-start] = boxhigh
            plt.plot(record)
        for interval in intervals:
            plotBox(interval[0], interval[1])


    findDoubleTops(data, plotGraphs, plotPeaks, start=start, end=end)

# Find Double Tops criteria function. Also can be used to plot the double tops by setting the optional arguments.
# start / end = None means default values.
def findDoubleTops(data, plotGraphs = False, plotPeaks = False, start = None, end = None):
    dates = data['Date']
    high, low, close = data['High'], data['Low'], data['Close']
    if not plotGraphs: plotPeaks = False
    if plotGraphs: import matplotlib.pyplot as plt

    if start == None: start = 0
    if end == None: end = len(high)
    
    peakGap = 5
    trenchValueTolerance = 0.85
    toleranceDown = 0.95
    toleranceUp = 1.05

    if start+(peakGap*2) >= end: return []
    graphBaseValue = min(high[start:end])
    graphPeakValue = max(high[start:end])

    # define functions
    isPeak = peakIdentifierFun(high, peakGap)
    if plotPeaks:
        isPeakInt = boolToIntFun(isPeak, graphBaseValue, graphPeakValue)

    intervals = []

    def addInterval(a, b):
        for interval in intervals:
            if abs(interval[0] - a) <= 2 and abs(interval[1] - b) <= 2:
                return
        intervals.append((a,b))

    if plotGraphs:
        def plotBox(i,j, value):
            record = [graphBaseValue]*(end-start)
            for k in range(i,j+1):
                record[k-start] = value
            plt.plot(record)

    peaks = list(filter(isPeak, range(start,end)))

    for i in range(0,len(peaks)):
        curr = peaks[i]
        currValue = high[curr]
        for j in range(i+1,len(peaks)):
            next = peaks[j]
            nextValue = high[next]
            ratio = nextValue/currValue
            if ratio >= toleranceUp:
                break
            if ratio <= toleranceDown:
                continue

            # toleranceDown < ratio < toleranceUp
            if curr+1 >= next:
                continue
            if min(high[curr+1:next]) >= toleranceDown*min(currValue, nextValue):
                continue

            trenchValue = min(low[curr+1:next])
            peakValue = max(currValue, nextValue)

            leftTail = -1
            rightTail = -1
            # scan right.
            for k in range(next+1,end):
                if high[k] > peakValue:
                    break
                if low[k] < trenchValueTolerance*trenchValue:
                    rightTail = k
                    break
            if rightTail == -1:
                continue

            # scan left.
            for k in range(curr-1,start-1,-1):
                if high[k] > peakValue:
                    break
                if low[k] < trenchValueTolerance*trenchValue:
                    leftTail = k
                    break
            if leftTail == -1:
                continue

            if plotGraphs:
                plotBox(curr,next, high[curr])
                plotBox(curr,next, high[next])
                plotBox(leftTail,rightTail-1, trenchValue)
            addInterval(leftTail,rightTail)

    if plotPeaks:
        peaks = list(map(isPeakInt, range(start,end)))
        plt.plot(peaks)
    if plotGraphs:
        plt.plot(high[start:end])
        plt.show()
    return intervals


""" REGION: UTILITY - END """

""" REGION: INITIALISATION - START """
configureCriteriaOptions()
""" REGION: INITIALISATION - END """

def main():
    #data, headers = para.readFile('data_/AKAMAI_TECHNOLOGIES_INC.csv')
    data, headers = para.readFile('data_334111/FUSION_I_O_INC.csv')

    start = None
    end = None

    plotDoubleTopsFiltered(data, True, False, start=start, end=end)


""" REGION: CONDITION DEFINITIONS - START """
# These are conditions used by grouping.redefineGroupingConditions  (in grouping.py)

conditionBreakHigh = (byPoints,
                    compose(breakHigh(yearsToDays(1), yearsToDays(5)), using('Close'))
                    )

conditionDoubleTops = (byPoints,
                    compose(getEndPoints, findDoubleTops)
                    )

conditionDoubleTopsFiltered = (byPoints,
                    compose(getEndPoints, findDoubleTopsFiltered),
                    )

""" REGION: CONDITION DEFINITIONS - START """


if __name__ == '__main__':
    main()