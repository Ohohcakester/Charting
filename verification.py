import parameters as para
import similarity
import dataselect
import tradingmeasure
import util
import verificationconfig
import chartprinter

dataSource = 'data_' + verificationconfig.datasetname

config = verificationconfig.configure()

groupSize = config.groupSize
predictSize = config.predictsize
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

def getDefaultEarnings(futureData):
    close = futureData['Close']
    return close[-1]/close[0]

def verify(fileName, todayIndex):
    global groupSize, predictSize, config
    if outputCharts == True:
        chart = chartprinter.new(fileName, todayIndex, config.algo, groupSize) 
    else:
        chart = None

    data, headers = para.readFile(fileName)

    if todayIndex - groupSize < 0: return None
    if todayIndex + predictSize > len(data['Close']): return None

    getKnownData = getKnownFun(todayIndex)
    getFutureData = getFutureFun(todayIndex, predictSize)

    knownData = {}
    futureData = {}
    for key in data:
        knownData[key] = getKnownData(data[key])
        futureData[key] = getFutureData(data[key])

    defaultEarnings = getDefaultEarnings(futureData)

    strategy = decideStrategy(knownData, groupSize, predictSize, chart)
    if strategy == None: return (1, False, defaultEarnings) #dontTrade

    result = applyStrategy(strategy, futureData)
    return (result, True, defaultEarnings)

""" TEST FRAMEWORK - END """

def groupByLast(data, dataList, groupSize):
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
        start = i - groupSize + 1
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


def getDataLists(fullData, groups, results, predictSize):
    def get(result):
        startIndex = groups[result[0]][1]
        return fullData[startIndex:startIndex+predictSize]
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


def decideStrategy(knownData, groupSize, predictSize, chart = None):
    global tradePolicy, tradingPreprocess, similarityMeasure

    dates = knownData['Date']
    fullData = knownData['Close']
    groups = groupByLast(knownData, fullData, groupSize)

    if (len(groups) < 20): return dontTrade()

    target = len(groups) - 1
    #printGroups(groups)
    # TODO: What are the group indexes for? Reversing them seems to throw it all over the place...

    matches = dataselect.findMatches(knownData, groups)
    printGroups(matches)
    #printGroup(groups[target])
    if groups[target] not in matches:
        return dontTrade()

    similarity.normalizeFuns = [similarity.byMean]
    similarity.measureFun = similarityMeasure

    results = compareAllGroupsBefore(groups, groupSize, target)
    
    results.reverse()
    results.sort(key=lambda x : x[1])

    nResults = 10
    dataLists = getDataLists(fullData, groups, results[0:nResults], predictSize)
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
    global predictSize

    data, headers = para.readFile(fileName)
    length = len(data['Close']) - predictSize
    cases = filter(lambda v : random.random() < 0.05, range(0,length))

    results = []
    for i in cases:
        result = verify(fileName, i)
        if result != None:
            results.append(result)
    return results


def main():
    print('Start Test')
    global dataSource
    if dataSource == None:
        files = util.listDataFiles()
    else:
        files = util.listDataFiles(dataSource)

    results = []
    for file in files:
        print('> Test ' + file)
        results += randomTestOnFile(file)


    first = lambda r : r[0]
    second = lambda r : r[1]
    third = lambda r : r[2]

    tradedPeriodsMoney = list(map(first, filter(second, results)))
    allPeriodsMoney = list(map(first, results))
    controlMoney = list(map(third, results))

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
        controlMean = 'N/A'
        controlSD = 'N/A'
    else:
        allMean = statistics.mean(allPeriodsMoney)
        allSD = statistics.stdev(allPeriodsMoney)
        controlMean = statistics.mean(controlMoney)
        controlSD = statistics.stdev(controlMoney)

    sb = []
    sb.append('Traded: ' + str(tradedCount) + ' / ' + str(allCount))
    sb.append('Traded Periods Money: ' + str(tradedMean) + ' +/- ' + str(tradedSD))
    sb.append('All Periods Money: ' + str(allMean) + ' +/- ' + str(allSD))
    sb.append('Control Money (All Periods): ' + str(controlMean) + ' +/- ' + str(controlSD))
    s = '\n'.join(sb)

    print(s)
    global resultsFile
    f = open(resultsFile, 'w+')
    f.write(s)
    f.close()
    

def predict():
    global groupSize, predictSize, config
    fileName = 'chinasp.csv'
    todayIndex = 6230

    chart = chartprinter.new(fileName, todayIndex, config.algo, predictSize) 
    
    data, headers = para.readFile(fileName)
    getKnownData = getKnownFun(todayIndex)
    
    knownData = {}
    for key in data:
        knownData[key] = getKnownData(data[key])
    
    strategy = decideStrategy(knownData, groupsize, predictSize, chart)
    if strategy == None: print("don't trade")



if __name__ == '__main__':
    predict()
    #main()