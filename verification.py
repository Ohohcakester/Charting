# Existing Modules
import parameters as para
import similarity
import dataselect
import tradingmeasure
import util

# Verification-releated modules
import verificationconfig
import chartprinter
import randomverify


def initialise(**kwargs):
    global config, dataSource, groupSize, predictSize, similarityMeasure
    global tradePolicy, tradingPreprocess, resultsFile, outputCharts

    if len(kwargs) == 0:
        config = verificationconfig.configure()
    else:
        config = verificationconfig.configureManual(**kwargs)

    dataSource = 'data_' + config.datasetname
    chartprinter.initialise(config.datasetname)

    groupSize = config.groupSize
    predictSize = config.predictSize
    similarityMeasure = config.similarityMeasure
    tradePolicy = config.tradePolicy
    tradingPreprocess = config.tradingPreprocess
    resultsFile = config.resultsFile

    outputCharts = True


""" TEST FRAMEWORK - START """

def getKnownFun(tomorrowIndex):
    def fun(dataList):
        return dataList[:tomorrowIndex]
    return fun

def getFutureFun(tomorrowIndex, length):
    def fun(dataList):
        return dataList[tomorrowIndex:tomorrowIndex+length]
    return fun

def getDefaultEarnings(futureData):
    close = futureData['Close']
    return close[-1]/close[0]

def verify(fileName, todayIndex):
    tomorrowIndex = todayIndex + 1

    global groupSize, predictSize, config
    if outputCharts == True:
        chart = chartprinter.new(fileName, tomorrowIndex, config.algo, groupSize, predictSize) 
    else:
        chart = None

    data, headers = para.readFile(fileName)

    if tomorrowIndex - groupSize < 0: return None
    if tomorrowIndex + predictSize > len(data['Close']): return None

    getKnownData = getKnownFun(tomorrowIndex)
    getFutureData = getFutureFun(tomorrowIndex, predictSize)

    knownData = {}
    futureData = {}
    for key in data:
        knownData[key] = getKnownData(data[key])
        futureData[key] = getFutureData(data[key])

    defaultEarnings = getDefaultEarnings(futureData)

    strategy = decideStrategy(knownData, groupSize, predictSize, chart)
    if strategy == None: return (1, False, defaultEarnings) #dontTrade

    result, traded = applyStrategy(strategy, futureData)
    return (result, traded, defaultEarnings)

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
    #print(buySellPoints)

    buy = []
    sell = []

    for i in range(0,len(buySellPoints)):
        if i%2 == 0:
            buy.append(buySellPoints[i])
        else:
            sell.append(buySellPoints[i])

    def strategy(i, futureData):
        if i in buy:
            if i in sell: return 0
            return 1
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


def getDataselectPoints(knownData):
    return dataselect.getEndPoints(dataselect.findDoubleTopsFiltered(knownData))

def decideStrategy(knownData, groupSize, predictSize, chart = None):
    global tradePolicy, tradingPreprocess, similarityMeasure
    
    dates = knownData['Date']
    fullData = knownData['Close']
    points = getDataselectPoints(knownData)

    if len(fullData)-1 not in points:
        return dontTrade()

    groups = groupByLast(knownData, fullData, groupSize)

    if (len(groups) < 20): return dontTrade()

    target = len(groups) - 1

    """
    matches = dataselect.findMatches(knownData, groups, 2)
    printGroups(matches)
    #printGroup(groups[target])
    if groups[target] not in matches:
        return dontTrade()
    """

    similarity.normalizeFuns = [similarity.byMean]
    similarity.measureFun = similarityMeasure

    results = compareAllGroupsBefore(groups, groupSize, target)
    
    results.reverse()
    results.sort(key=lambda x : x[1])

    nResults = 10
    #print(','.join(map(lambda x : str(x[0]), results[0:nResults])))
    dataLists = getDataLists(fullData, groups, results[0:nResults], predictSize)
    strategy = createStrategyFromPolicy(dataLists)

    if chart != None:
        avgData = tradingmeasure.averageData(dataLists)
        chart.writeChart(avgData)

    return strategy

# returns a tuple (money, traded).
# money is how much money is left at the end, and traded is true iff some trading was done that month.
def applyStrategy(strategy, futureData):
    prices = futureData['Close']
    money = 1
    stock = 0

    #print(list(map(lambda x : strategy(x,prices), range(0,len(prices)))))

    traded = False
    for i in range(0,len(prices)):
        action = strategy(i, prices[:i+1])
        if action == 1:
            #buy:
            stock += money / prices[i]
            money = 0
            traded = True
        elif action == -1:
            #sell
            money += stock * prices[i]
            stock = 0
            traded = True

    # Sell remaining stock at end of period.
    money += stock*prices[-1]
    stock = 0

    return money, traded

def testMain():
    print("Verifying...")
    fileName = 'data_/F_5_NETWORKS_INC.csv'
    for i in range(1500,650,-20):
        result = verify(fileName, i)
        print(result)

def randomTestOnFile(fileName):
    import random
    global predictSize

    data, headers = para.readFile(fileName)
    length = len(data['Close']) - predictSize - 1
    cases = filter(lambda v : random.random() < 0.05, range(0,length))

    results = []
    for i in cases:
        result = verify(fileName, i)
        if result != None:
            results.append(result)
    return results

def selectiveTestOnFile(fileName):
    import random
    global predictSize

    data, headers = para.readFile(fileName)
    length = len(data['Close']) - predictSize - 1

    cases = list(filter(lambda v : v < length, getDataselectPoints(data)))
    #cases = filter(lambda v : random.random() < 0.05, range(0,length))
    #print('Cases: ' + str(cases))

    results = []
    for i in cases:
        result = verify(fileName, i)
        if result != None:
            results.append(result)
    return results


def main():
    print('Start Test')
    global dataSource, predictSize
    if dataSource == None:
        files = util.listDataFiles()
    else:
        files = util.listDataFiles(dataSource)

    results = []
    results2 = []
    for file in files:
        #print('> Test ' + file)
        results += selectiveTestOnFile(file)
        results2 += randomverify.verify(file, predictSize)


    first = lambda r : r[0]
    second = lambda r : r[1]
    third = lambda r : r[2]

    tradedPeriodsMoney = list(map(first, filter(second, results)))
    allPeriodsMoney = list(map(first, results))
    tradedControlMoney = list(map(third, results))
    randomControlMoney = results2

    print('\nTests Complete\n')

    import statistics
    tradedCount = len(tradedPeriodsMoney)
    allCount = len(allPeriodsMoney)
    tradedControlCount = len(tradedControlMoney)
    randomControlCount = len(randomControlMoney)

    if tradedCount == 0:
        tradedMean = 'N/A'
        tradedSD = 'N/A'
    else:
        tradedMean = statistics.mean(tradedPeriodsMoney)
        if tradedCount > 1:
            tradedSD = statistics.stdev(tradedPeriodsMoney)
        else:
            tradedSD = 'N/A'

    if allCount == 0:
        allMean = 'N/A'
        allSD = 'N/A'
    else:
        allMean = statistics.mean(allPeriodsMoney)
        if allCount > 1:
            allSD = statistics.stdev(allPeriodsMoney)
        else:
            allSD = 'N/A'

    if tradedControlCount == 0:
        tradedControlMean = 'N/A'
        tradedControlSD = 'N/A'
    else:
        tradedControlMean = statistics.mean(tradedControlMoney)
        if tradedControlCount > 1:
            tradedControlSD = statistics.stdev(tradedControlMoney)
        else:
            tradedControlSD = 'N/A'

    if randomControlCount == 0:
        randomControlMean = 'N/A'
        randomControlSD = 'N/A'
    else:
        randomControlMean = statistics.mean(randomControlMoney)
        if randomControlCount > 1:
            randomControlSD = statistics.stdev(randomControlMoney)
        else:
            randomControlSD = 'N/A'

    sb = []
    global resultsFile
    sb.append(resultsFile)
    sb.append('Traded: ' + str(tradedCount))
    sb.append('Traded Periods Money: ' + str(tradedMean) + ' +/- ' + str(tradedSD))
    sb.append('All: ' +  str(allCount))
    sb.append('All Periods Money: ' + str(allMean) + ' +/- ' + str(allSD))
    sb.append('Traded Control: ' +  str(tradedControlCount))
    sb.append('Traded Control Money (All Periods): ' + str(tradedControlMean) + ' +/- ' + str(tradedControlSD))
    sb.append('')
    sb.append('Random Control Count: ' + str(randomControlCount))
    sb.append('Control Money (Random Periods): ' + str(randomControlMean) + ' +/- ' + str(randomControlSD))
    s = '\n'.join(sb)

    print(s)
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


def testAll():
    groupSizes = [75,150,240]
    predictSizes = [15,30,75]
    algos = ['sts','dtw','mindist.sax_1']
    strategies = ['sellOrKeep']
    datasetnames = ['','334111','211111','454111']

    for groupSize in groupSizes:
        for predictSize in predictSizes:
            for algo in algos:
                for strategy in strategies:
                    for datasetname in datasetnames:
                        initialise(groupSize=groupSize, predictSize=predictSize,algo=algo,strategy=strategy,datasetname=datasetname)
                        main()



if __name__ == '__main__':
    testAll()

    #initialise()
    #main()

    #predict()