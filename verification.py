import parameters as para
import similarity
import dataselect
import tradingmeasure
import util
import verificationconfig
import chartprinter

config = verificationconfig.configure()

groupSize = config.groupSize
similarityMeasure = config.similarityMeasure
tradePolicy = config.tradePolicy
tradingPreprocess = config.tradingPreprocess
resultsFile = config.resultsFile

outputCharts = True


""" TEST FRAMEWORK - START """

def getKnownFun(todayIndex):
    def fun(dataList):
        return dataList[:todayIndex]
    return fun

def getFutureFun(todayIndex, answerLength):
    def fun(dataList):
        return dataList[todayIndex:todayIndex+answerLength]
    return fun

def verify(fileName, todayIndex):
    global groupSize, config
    if outputCharts == True:
        chart = chartprinter.new(fileName, todayIndex, config.algo, groupSize) 
    else:
        chart = None

    data, headers = para.readFile(fileName)

    if todayIndex - groupSize < 0: return None
    if todayIndex + groupSize > len(data['Close']): return None

    getKnownData = getKnownFun(todayIndex)
    getFutureData = getFutureFun(todayIndex, groupSize)

    knownData = {}
    futureData = {}
    for key in data:
        knownData[key] = getKnownData(data[key])
        futureData[key] = getFutureData(data[key])

    strategy = decideStrategy(knownData, groupSize, chart)
    if strategy == None: return (1, False) #dontTrade

    result = applyStrategy(strategy, futureData)
    return (result, True)

""" TEST FRAMEWORK - END """

def groupByLast(data, dataList):
    curr = 0
    lastmonth = -1
    groups = []
    days = data['Day']
    dates = data['Date']

    firstGroupDay = days[-1]
    def inRangeFunction(firstGroupDay, tolerance):
        upperLimit = firstGroupDay + 3
        lowerLimit = firstGroupDay - 3
        if upperLimit > 31:
            diff = upperLimit - 31
            upperLimit -= diff
            lowerLimit -= diff
        elif lowerLimit < 0:
            diff = 0 - lowerLimit
            upperLimit += diff
            lowerLimit += diff
        def fun(day):
            return lowerLimit <= day and day <= upperLimit
        return fun

        """
        if upperLimit > 31 or lowerLimit < 0:
            if upperLimit > 31: upperLimit -= 31
            if lowerLimit < 0: lowerLimit += 31
            def fun(day):
                return day <= upperLimit or day >= lowerLimit
            return fun
        else:
            def fun(day):
                return lowerLimit <= day and day <= upperLimit
            return fun"""

    isInRange = inRangeFunction(firstGroupDay, 3)


    for i in range(len(days)-1, -1, -1):
        date = dates[i]
        if date.month == lastmonth: continue
        if not isInRange(date.day): continue

        lastmonth = date.month
        start = i - 74 # i - 75 + 1
        end = i + 1

        if start < 0: continue
        groups.append((start, end, dataList[start:end], len(groups), []))

    groups.reverse()
    return groups


# i: query index, j: target (reference) index
# returns a tuple (index, similarityScore)
def getSimilarity(groups, i, j):
    sim = similarity.compute(groups[i], groups[j])
    return (i,sim)

# returns a list of tuples (index, similarityScore)
def compareAllGroupsBefore(groups, groupSize, targetIndex):
    latestEndDate = groups[targetIndex][1] - groupSize
    candidateIndexes = filter(lambda i : groups[i][1] <= latestEndDate, range(0, targetIndex)) 
    return list(map(lambda i : getSimilarity(groups, i, targetIndex), candidateIndexes))


def getDataLists(fullData, groups, results, groupSize):
    def get(result):
        startIndex = groups[result[0]][1]
        return fullData[startIndex:startIndex+groupSize]
    return list(map(get, results))

# 1: buy, -1: sell, 0: do nothing
def createStrategyFromPolicy(sourceData):
    global tradePolicy, tradingPreprocess
    if tradingPreprocess != None:
        sourceData = tradingPreprocess(sourceData)
    buySellPoints = tradePolicy(sourceData)

    buy = []
    sell = []

    for i in range(0,len(buySellPoints)):
        if i%2 == 0:
            buy.append(buySellPoints[i])
        else:
            sell.append(buySellPoints[i])

    def strategy(i, futureData):
        if i in buy: return 1
        if i in sell: return -1
        return 0
    return strategy

def dontTrade():
    #def strategy(i, futureData):
    #    return 0
    return None

def groupToStr(group):
    return str(group[0]) + '-' + str(group[1])

def printGroup(group):
    print(groupToStr(group))

def printGroups(groups):
    print('[' + ', '.join(map(groupToStr, groups)) + ']')


def decideStrategy(knownData, groupSize, chart = None):
    global tradePolicy, tradingPreprocess, similarityMeasure

    dates = knownData['Date']
    fullData = knownData['Close']
    groups = groupByLast(knownData, fullData)

    if (len(groups) < 20): return dontTrade()

    target = len(groups) - 1
    #printGroups(groups)
    # TODO: What are the group indexes for? Reversing them seems to throw it all over the place...

    matches = dataselect.findMatches(knownData, groups)
    #printGroups(matches)
    #printGroup(groups[target])
    if groups[target] not in matches:
        return dontTrade()

    similarity.normalizeFuns = [similarity.byMean]
    similarity.measureFun = similarityMeasure

    results = compareAllGroupsBefore(groups, groupSize, target)
    
    results.reverse()
    results.sort(key=lambda x : x[1])

    nResults = 10
    dataLists = getDataLists(fullData, groups, results[0:nResults], groupSize)
    strategy = createStrategyFromPolicy(dataLists)

    if chart != None:
        avgData = tradingmeasure.averageData(dataLists)
        chart.writeChart(avgData)

    return strategy


def applyStrategy(strategy, futureData):
    prices = futureData['Close']
    money = 1
    stock = 0

    for i in range(0,len(prices)):
        action = strategy(i, prices)
        if action == 1:
            #buy:
            stock += money / prices[i]
            money = 0
        elif action == -1:
            #sell
            money += stock * prices[i]
            stock = 0

    # Sell remaining stock at end of period.
    money += stock*prices[-1]
    stock = 0

    return money

def testMain():
    print("Verifying...")
    fileName = 'data/F_5_NETWORKS_INC.csv'
    for i in range(1500,650,-20):
        result = verify(fileName, i)
        print(result)

def randomTestOnFile(fileName):
    import random
    global groupSize

    data, headers = para.readFile(fileName)
    length = len(data['Close']) - groupSize
    cases = filter(lambda v : random.random() < 0.05, range(0,length))

    results = []
    for i in cases:
        result = verify(fileName, i)
        if result != None:
            results.append(result)
    return results


def main():
    print('Start Test')
    files = util.listDataFiles()

    results = []
    for file in files:
        print('> Test ' + file)
        results += randomTestOnFile(file)


    first = lambda r : r[0]
    second = lambda r : r[1]

    tradedPeriodsMoney = list(map(first, filter(second, results)))
    allPeriodsMoney = list(map(first, results))

    print('\nTests Complete\n')

    import statistics
    tradedCount = len(tradedPeriodsMoney)
    allCount = len(allPeriodsMoney)
    if tradedCount == 0:
        tradedMean = 'N/A'
        tradedSD = 'N/A'
    else:
        tradedMean = statistics.mean(tradedPeriodsMoney)
        tradedSD = statistics.stdev(tradedPeriodsMoney)

    if allCount == 0:
        allMean = 'N/A'
        allSD = 'N/A'
    else:
        allMean = statistics.mean(allPeriodsMoney)
        allSD = statistics.stdev(allPeriodsMoney)

    sb = []
    sb.append('Traded: ' + str(tradedCount) + ' / ' + str(allCount))
    sb.append('Traded Periods Money: ' + str(tradedMean) + ' +/- ' + str(tradedSD))
    sb.append('All Periods Money: ' + str(allMean) + ' +/- ' + str(allSD))
    s = '\n'.join(sb)

    print(s)
    global resultsFile
    f = open(resultsFile, 'w+')
    f.write(s)
    f.close()
    
if __name__ == '__main__':
    main()