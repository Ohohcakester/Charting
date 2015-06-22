import testalgos
import testcollection
import parameters as para
import display
import similarity
import grouping
import tradingmeasure
import pyswarm
import dataselect
import util

keys = ['Close', 'RatioClose', 'AvgClose', 'DiffCloseSign', 'RunningRatio']

algosToTest = {
    'sts': similarity.tsdist('stsDistance'),
    'inf.norm': similarity.tsdist('inf.normDistance'),
    'cort': similarity.tsdist('cortDistance'),
    'lcss_05': similarity.tsdist('lcssDistance', 0.05),
    'minkowski_25': similarity.lpNorms(2.5), #otherwise known as lp-norms
    'minkowski_30': similarity.lpNorms(3),
    'lbKeogh_3': similarity.tsdist('lb.keoghDistance', 3),
    'dtw': similarity.tsdist('dtwDistance'),
    'euclidean': similarity.tsdist('euclideanDistance'),
    'fourier': similarity.tsdist('fourierDistance'),
    'dissim': similarity.tsdist('dissimDistance'),
}

algosToTest = {
    'sts': similarity.tsdist('stsDistance'),
}

data = {}
headers = []

def optimise():
    testCases = testcollection.readTests()
    #grouping.redefineGroupingConditions(dataselect.conditionBreakHigh)
    #grouping.redefineGroupingConditions(dataselect.conditionDoubleTopsFiltered)

    def testWithWeights(weights):
        global keys
        arrLen = len(keys)
        weightDict = {}
        for i in range(0,arrLen):
            weightDict[keys[i]] = weights[i]
        result = testAlgorithmsForAverageScore(testCases, weightDict)
        print(str(result) + ' <- ' + str(weights))
        return (result - 1)*100
   
    """ 
    import time
    print ('start:')
    s = time.time()
    testWithWeights([1,1,1,1,0])
    testWithWeights([1,1,1,0,0.5])
    testWithWeights([1,1,0,0,0.5])
    testWithWeights([1,0,1,0,0.5])
    testWithWeights([1,0,1,1,0.5])
    e = time.time()
    print('end')
    print(e - s)
    return"""
    ub = [1]*5
    lb = [0]*5
    xopt, fopt = pyswarm.pso(testWithWeights, lb, ub, maxiter=20)
    
    print('Weights:')
    print(xopt)
    print('Score = ' + str(fopt))





def testAlgorithmsForAverageScore(testCases, weightDict):
    global algosToTest, data, headers
    allResults = []
    weightDataFun = weightedData(weightDict)

    for companyName in testCases.keys():
        #print('Testing ' + companyName)
        data, headers = para.readFile(display.nameToFile(companyName))
        for key in algosToTest.keys():
            #print('    algo ' + key)
            algo = algosToTest[key]
            for target in testCases[companyName]:
                result = testAlgoWeighted(algo, target, weightDataFun)
                if result != None:
                    allResults.append(result)

    averageResult = testalgos.computeAverageResult(allResults)
    return averageResult[2]
    return averageResult[0]*averageResult[1]


def weightedData(weightDict):
    def fun(data):
        length = len(data['Close']) #length of any key in dict.

        def weightedSum(i):
            value = 0
            for key in weightDict.keys():
                value += data[key][i]*weightDict[key]
            return value
        return list(map(weightedSum, range(0,length)))
    return fun


def testAlgoWeighted(algo, target, weightDataFun):
    global data
    dates = data['Date']
    groupsWeighted = grouping.groupUp(data, weightDataFun(data))
    groupsClose = grouping.groupUp(data, data['Close'])

    targetNext = target+util.ma
    if targetNext >= len(groupsWeighted):
        return None
    similarity.normalizeFuns = [similarity.byMean]
    similarity.measureFun = algo
    results = testalgos.compareAllGroupsBefore(groupsWeighted, target)
    results2 = testalgos.compareAllGroupsBefore(groupsClose, targetNext)
    
    results.reverse()
    results.sort(key=lambda x : x[2])
    results2.sort(key=lambda x : x[2])

    tradePolicy = tradingmeasure.sellOrKeep
    tradingPreprocess = tradingmeasure.averageData

    totalRank = 0
    lpScore = 0
    nResults = 10

    for v in results[0:nResults]:
        rank = testalgos.getRank(results2, v[0]+util.ma)
        totalRank += rank
        lpScore += similarity.computeWith(groupsClose[v[0]+util.ma], groupsClose[targetNext], [similarity.byFirst], similarity.lpNorms(2))
    
    dataLists = testalgos.getDataLists(groupsClose, results[0:nResults], util.ma)
    money = tradingmeasure.computeWithFunOn(dataLists, groupsClose[targetNext][2], tradePolicy, tradingPreprocess)
    #totalRank *= 100        # normalize totalRank for equal weightage.
    #totalRank /= len(results2) # normalize totalRank for equal weightage.

    return (lpScore/nResults, totalRank/nResults, money)
