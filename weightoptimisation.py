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
import constants as const

# We try to find the optimal linear combination of these parameters.
# Edit this list to configure the parameters to use.
# Make sure that these parameters have been defined by parameters.readFile() first.
parametersToOptimise = ['Close', 'RatioClose', 'AvgClose', 'DiffCloseSign', 'RunningRatio']

# Test multiple algorithms
# The average score of the algorithms is used as the objective function.
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

# Test only sts (overwrites the previous algosToTest if not commented out)
algosToTest = {
    'sts': similarity.tsdist('stsDistance'),
}


# This is the main function to call in weightoptimisation.py.
# Call this to run weight optimisation.
def optimise():
    testCases = testcollection.readTests()
    #grouping.redefineGroupingConditions(dataselect.conditionBreakHigh)
    #grouping.redefineGroupingConditions(dataselect.conditionDoubleTopsFiltered)

    ### Objective Function.
    ### An input for pyswarm.pso. Returns a float utility score from testing with a set of weights.
    def testWithWeights(weights):
        arrLen = len(parametersToOptimise)
        weightDict = {}
        for i in range(0,arrLen):
            weightDict[parametersToOptimise[i]] = weights[i]
        result = testAlgorithmsForAverageScore(testCases, weightDict)
        print(str(result) + ' <- ' + str(weights)) # print as we go.
        return (result - 1)*100
   
    ### Uncomment this to test the running time of weight optimisation.
    # testWeightOptimisationRunningTime(testWithWeights)

    ub = [1]*5 # Upper bound = 1
    lb = [0]*5 # Lower bound = 0
    xopt, fopt = pyswarm.pso(testWithWeights, lb, ub, maxiter=20)
    
    # If we reach this point, it means the weight optimisation process is complete.
    print('Final Weights:')
    print(xopt)
    print('Score = ' + str(fopt))


# weightDict is a dictionary (parameterName => weight)
def testAlgorithmsForAverageScore(testCases, weightDict):
    allResults = []
    weightDataFun = weightedData(weightDict)

    for companyName in testCases.keys():
        #print('Testing ' + companyName)
        data, headers = para.readFile(display.nameToFile(companyName))
        for key in algosToTest.keys():
            #print('    algo ' + key)
            algo = algosToTest[key]
            for target in testCases[companyName]:
                result = testAlgoWeighted(algo, target, weightDataFun, data)
                if result != None:
                    allResults.append(result)

    averageResult = testalgos.computeAverageResult(allResults)
    return averageResult[2]                     # Maximise the amount of return alone.
    #return averageResult[0]*averageResult[1]   # Maximise the product of LpScore and Rankscore


# Returns a function that computes the linear combination of the weights and values from weightDict.
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


# Tests an algorithm using a weighted set of data, and returns a result object.
def testAlgoWeighted(algo, target, weightDataFun, data):
    dates = data['Date']
    groupsWeighted = grouping.groupUp(data, weightDataFun(data))
    groupsClose = grouping.groupUp(data, data['Close'])

    targetNext = target+const.ma
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
    usingOnlyAverageData = True

    totalRank = 0
    lpScore = 0
    nResults = 10

    for v in results[0:nResults]:
        rank = testalgos.getRank(results2, v[0]+const.ma)
        totalRank += rank
        lpScore += similarity.computeWith(groupsClose[v[0]+const.ma], groupsClose[targetNext], [similarity.byFirst], similarity.lpNorms(2))
    
    dataLists = testalgos.getDataLists(groupsClose, results[0:nResults], const.ma)
    if usingOnlyAverageData:
            dataLists = tradingmeasure.averageData(dataLists)

    money = tradingmeasure.computeWithFunOn(dataLists, groupsClose[targetNext][2], tradePolicy)
    #totalRank *= 100        # normalize totalRank for equal weightage.
    #totalRank /= len(results2) # normalize totalRank for equal weightage.

    return (lpScore/nResults, totalRank/nResults, money)


# A test function to see how fast the weight optimisation function runs.
# I used this when I was trying to optimise the performance of the weight optimisation process.
def testWeightOptimisationRunningTime(testWithWeights):
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
    return
