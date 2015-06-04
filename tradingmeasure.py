import similarity

def computeWithFun(data, policyFun):
    buySellPoints = policyFun(data)
    return computeWithPoints(data, buySellPoints)


def computeWithFunOn(sourceData, targetData, policyFun):
    buySellPoints = policyFun(sourceData)
    return computeWithPoints(targetData, buySellPoints)


# buySellPoints is a list/tuple that alternates between a buy and a sell..
def computeWithPoints(data, buySellPoints):
    data = similarity.byFirst(data)
    money = 1
    stock = 0
    holdingStocks = False
    for i in range(0,len(buySellPoints)):
        if holdingStocks:
            #sell
            money += stock*data[buySellPoints[i]]
            stock = 0
            holdingStocks = False
        else:
            #buy
            stock = money / data[buySellPoints[i]]
            money = 0
            holdingStocks = True

    # Sell remaining stock at end of period.
    if holdingStocks:
        money += stock*data[len(data)-1]

    return money



""" REGION: TRADING POLICIES - START """

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

def dontSell(data):
    return (0,len(data)-1)


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


""" REGION: TRADING POLICIES - END """



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
    print(computeWithFun(test, largestReturn))
