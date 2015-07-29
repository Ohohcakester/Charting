import similarity
import util

""" REGION: MAIN API - START """

# Compute the amount of return when policyFun is applied to targetData.
# sourceData : The data (prices) used to decide the strategy (generally, the predicted data)
# targetData : The actual data (prices) (unknown)
# policyFun : The trading policy to be used.
def computeWithFunOn(sourceData, targetData, policyFun):
    buySellPoints = policyFun(sourceData)
    return computeWithPoints(targetData, buySellPoints)

# Compute the amount of return by the trading policy policyFun when the future data is fully known.
# i.e. computeWithFunOn, but where sourceData = targetData.
def computeReturnForFullyKnownData(data, policyFun):
    return computeWithFunOn(data, data, policyFun)

# policyFun must be a function that returns a strategy(index, futureData)
def computeWithStrategy(sourceData, targetData, policyFun):
    strategy = policyFun(sourceData)
    return computeWithPointsUsingStrategy(targetData, strategy)

""" REGION: MAIN API - END """


# buySellPoints is a list/tuple that alternates between a buy and a sell..
def computeWithPoints(futureData, buySellPoints):
    futureData = similarity.byFirst(futureData)
    money = 1
    stock = 0
    holdingStocks = False
    for i in range(0,len(buySellPoints)):
        if holdingStocks:
            #sell
            money += stock*futureData[buySellPoints[i]]
            stock = 0
            holdingStocks = False
        else:
            #buy
            stock = money / futureData[buySellPoints[i]]
            money = 0
            holdingStocks = True

    # Sell remaining stock at end of period.
    if holdingStocks:
        money += stock*futureData[len(futureData)-1]

    return money


# UNTESTED
# strategy(index, futureData). 1 means buy, -1 means sell, 0 means do nothing.
def computeWithPointsUsingStrategy(futureData, strategy):
    futureData = similarity.byFirst(futureData)
    money = 1
    stock = 0
    holdingStocks = False
    for i in range(0,len(futureData)):
        action = strategy(i, futureData[:i+1])
        if action == 0:
            continue
        elif action == -1:
            if not holdingStocks: return
            #sell
            money += stock*futureData[buySellPoints[i]]
            stock = 0
            holdingStocks = False
        else: # action == 1
            if holdingStocks: return
            #buy
            stock = money / futureData[buySellPoints[i]]
            money = 0
            holdingStocks = True

    # Sell remaining stock at end of period.
    if holdingStocks:
        money += stock*futureData[len(futureData)-1]

    return money


""" REGION: UTILITY - START """

# Note: higher value is lower confidence
# Values are usually between 0 and 1. However it is occasionally more than 1.
def computeConfidence(meanList, sdList):
    return util.mean([sd/val for val,sd in zip(meanList,sdList)])
    

def computeMeanAndSD(dataLists):
    import statistics
    dataLists = list(map(similarity.byFirst, dataLists))
    datapoints = util.transposeLists(dataLists)

    meanList = list(map(statistics.mean, datapoints))
    sdList = list(map(statistics.stdev, datapoints))
    return meanList, sdList

def averageData(dataLists):
    import statistics
    dataLists = list(map(similarity.byFirst, dataLists))
    datapoints = util.transposeLists(dataLists)

    return list(map(statistics.mean, datapoints))

""" REGION: UTILITY - END """


""" REGION: TRADING POLICIES : STRAETGY - START """
# Strategy(index, futureData)
# The input futureData is only the future data up till the day being analysed i. (i.e. futureData[0:i+1])
# 1 means buy, -1 means sell, 0 means do nothing.

def buyingThreshold(fraction):
    def fun(data):
        meanList, sdList = computeMeanAndSD(data)
        last = len(data)-1
        if data[last] < data[0]:
            return None

        class Strategy:
            def __init__(self, limit):
                self.bought = False
                self.limit = limit
                self.data = data
            def decide(self, i, futureData):
                if self.bought:
                    return 0
                if futureData[i] < limit:
                    self.bought = True
                    return 1

        limit = min(data)
        limit = 1 - fraction*(1-limit)
        strat = Strategy(limit)
        return strategy.decide




""" REGION: TRADING POLICIES : STRAETGY - END """



""" REGION: TRADING POLICIES : GENERAL - START """
# these algorithms are run using a set of dataLists for sourceData.

# bails and does nothing when it is not confident in its answer.
def confidenceFilter(threshold, policy):
    def fun(data):
        meanList, sdList = computeMeanAndSD(data)
        confidence = computeConfidence(meanList, sdList)
        if confidence > threshold: return (0,0)
        else: return policy(meanList)
    return fun
    

""" REGION: TRADING POLICIES : GENERAL - END """


""" REGION: TRADING POLICIES : USING AVERAGEDATA ONLY - START """
# these algorithms are run using a single dataList for sourceData.
# If you have a set of dataLists instead, preprocess them with the averageData function first
# to compute a single dataList as the average of the multiple dataLists.

def maxValueSell(data):
    sellPoint = max(enumerate(data), key=lambda t:t[1])[0]
    return (0,sellPoint)

def tenPercentSell(data):
    sellPoint = len(data)-1
    for i in range(0,len(data)-1):
        ratio = data[i+1]/data[i]
        if ratio <= 0.9:
            sellPoint = i
        if ratio >= 1.1:
            sellPoint = i+1
    return (0,sellPoint)

# used as a control. does not use the data at all.
def dontSell(data):
    return (0,len(data)-1)


def sellOrKeep(data):
    last = len(data)-1
    if data[last] < data[0]:
        return (0,0)
    else:
        return (0,last)

# only keep when the graph rises by a significant amount.
def riskAverseSellOrKeep(data):
    last = len(data)-1
    if data[last] >= 1.1*data[0]:
        return (0,last)
    else:
        return (0,0)

# tries to lose as much money as possible
def reversedSellOrKeep(data):
    last = len(data)-1
    if data[last] < data[0]:
        return (0,last)
    else:
        return (0,0)


# tries to lose as much money as possible
# only sells when the graph falls by a significant amount.
def reversedRiskAverseSellOrKeep(data):
    last = len(data)-1
    if data[last] < 0.9*data[0]:
        return (0,last)
    else:
        return (0,0)


def largestReturn(data):
    data = similarity.byFirst(data)
    runningMin = data[0]
    minIndex = 0
    maxReturn = -1
    buyPoint = -1
    sellPoint = -1
    for i in range(0,len(data)):
        v = data[i]
        if (v < runningMin):
            runningMin = v
            minIndex = i
        if (v - runningMin  > maxReturn):
            maxReturn = v - runningMin
            buyPoint = minIndex
            sellPoint = i

    return(buyPoint, sellPoint)


""" REGION: TRADING POLICIES : USING AVERAGEDATA ONLY - END """



if __name__ == '__main__':
    import random
    test = []
    for i in range(0,20):
        test.append(50+random.randrange(100))

    print(test)
    print('Length = ' + str(len(test)))
    lr = largestReturn(test)
    print(lr)
    print(str(test[lr[1]]) + ' ' + str(test[lr[0]]))
    print(test[lr[1]]-test[lr[0]])
    print(computeWithPoints(test, lr))
    print(computeReturnForFullyKnownData(test, largestReturn))
