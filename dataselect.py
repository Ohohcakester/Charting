import display
import parameters as para
import grouping
#Format of group:
# (startindex, endindex, data, index) #bitmap deprecated

def run(fileName):
    data, headers = para.readFile(fileName)
    dates = data['Date']
    if (len(dates) == 0):
        #print('Empty File')
        return
    close = data['Close']
    groups = grouping.groupUp(data['Day'], dates, close)

    matches = findMatches(close, groups)
    #print('Found ' + str(len(matches)) + ' matches')
    if (len(matches) <= 0): return #print only when there is at least one match.
    print(display.getNameOnly(fileName))
    for group in matches:
        display.printgroupattrs(group, dates)


def findMatches(fulldata, groups):
    global criteriaType, criteriaFun
    return criteriaType(fulldata, groups, criteriaFun)

def findMatchesWith(fulldata, groups, criteriaType, criteriaFun):
    return criteriaType(fulldata, groups, criteriaFun)


def byIndividual(fulldata, groups, criteria):
    def fun(group):
        return criteria(fulldata, group[0], group[1])
    return filter(fun, groups)

# Assumes groups are sorted in chronological order (increasing)
def byPoints(fulldata, groups, criteria):
    markedPoints = criteria(fulldata)
    selectedGroups = []
    for point in markedPoints:
        group = findFirstGroupContainingPoint(groups, point)
        if group != None: # rare case. point is outside of all groups.
            selectedGroups.append(group)
    return selectedGroups


""" REGION: INDIVIDUAL CRITERION - START """



def containsPoints(markedPoints):
    def fun(fulldata, startIndex, endIndex):
        for point in markedPoints:
            if startIndex <= point and point < endIndex:
                return True
        return False
    return fun

""" REGION: INDIVIDUAL CRITERION - START """




""" REGION: POINTS CRITERION - START """

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



""" REGION: UTILITY - START """

def findFirstGroupContainingPoint(groups, point):
    for group in groups: # group[0] = startIndex, group[1] = endIndex
        if group[0] <= point and point < group[1]:
            return group
    return None



def yearsToDays(years):
    return years*250 #250 working days in a year.


# Given an array(list) arr, and a window of size wSize,
# |------[-------]--------|
#         '-max-'
# For window positions from 0 to len(data) - wSize,
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
    for i in range(1,len(arr)-wSize):
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


def getEndPoints(intervals):
    return list(map(lambda v : v[1], intervals))


def peakIdentifierFun(dataList, peakGap):
    def isPeak(i):
        return i >= peakGap and i + peakGap < len(high) and \
            high[i] >= high[windowHighs[i-peakGap]]
    return isPeak


def findDoubleTops(fileName, plotGraphs = False):
    import matplotlib.pyplot as plt
    data, headers = para.readFile(fileName)
    dates = data['Date']
    high = data['High']
    low = data['Low']
    close = data['Close']

    start = 0
    end = len(high)
    #start = 1200
    
    peakGap = 5
    trenchValueTolerance = 0.85
    toleranceDown = 0.95
    toleranceUp = 1.05

    if start+(peakGap*2) >= end: return []

    graphBaseValue = min(high[start:end])
    graphPeakValue = max(high[start:end])

    windowHighs = generateMaxIndexList(high, peakGap*2)

    intervals = []

    def isPeak(i):
        return i >= peakGap and i + peakGap < len(high) and \
            high[i] >= high[windowHighs[i-peakGap]]
            #high[i] >= high[windowHighs[i-peakGap]] and \
            #high[i] >= high[windowHighs[i+1]]

    #def isPeakInt(i):
    #    if isPeak(i):
    #        return graphPeakValue
    #    return graphBaseValue

    def addInterval(a, b):
        for interval in intervals:
            if abs(interval[0] - a) <= 2 and abs(interval[1] - b) <= 2:
                return
        intervals.append((a,b))


    def addRecord(i,j, v):
        record = [graphBaseValue]*(end-start)
        for k in range(i,j+1):
            record[k-start] = v#high[i]
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

            #addRecord(curr,next, high[curr])

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

            addRecord(curr,next, high[curr])
            addRecord(curr,next, high[next])
            addRecord(leftTail,rightTail-1, trenchValue)
            addInterval(leftTail,rightTail)

    #peaks = list(map(isPeakInt, range(start,end)))
    #plt.plot(peaks)
    plt.plot(high[start:end])
    plt.show()
    return intervals


""" REGION: UTILITY - END """

criteriaType = byPoints
criteriaFun = breakHigh(yearsToDays(1), yearsToDays(5))


def main():
    findDoubleTops('data/AKAMAI_TECHNOLOGIES_INC.csv', True)



if __name__ == '__main__':
    main()