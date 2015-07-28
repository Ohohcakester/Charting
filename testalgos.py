import similarity
import display
import grouping
import tradingmeasure
import parameters as para
import util
import constants as const

#testOutputFilename = 'testresults.txt'
testOutputFilename = 'testresults_test.txt'
#testOutputFilename = 'results_confidenceSellOrKeep_fyh_nocond_byFirst.txt'

# test all algos
algosToTest = {
    'acf': similarity.tsdist('acfDistance'),
    'ar.lpc.ceps': similarity.tsdist('ar.lpc.cepsDistance'),
    #'ar.mah': similarity.tsdist('ar.mahDistance'), #Need to retrieve p-value
    'ar.pic': similarity.tsdist('ar.picDistance'),
    'ccor': similarity.tsdist('ccorDistance'),
    #'cdm': similarity.tsdist('cdmDistance'), # (USE) SLOW / INTERNAL ERROR 5 IN MEMCOMPRESS...?
    'cid': similarity.tsdist('cidDistance'),
    'cor': similarity.tsdist('corDistance'),
    'cort': similarity.tsdist('cortDistance'),
    'dissimapprox': similarity.tsdist('dissimapproxDistance'),
    'dissim': similarity.tsdist('dissimDistance'),
    'dtw': similarity.tsdist('dtwDistance'),
    'edr_005': similarity.tsdist('edrDistance', 0.05),
    'edr_01': similarity.tsdist('edrDistance', 0.1),
    'edr_025': similarity.tsdist('edrDistance', 0.25),
    'edr_05': similarity.tsdist('edrDistance', 0.5),
    'erp_01': similarity.tsdist('erpDistance', 0.1),
    'erp_05': similarity.tsdist('erpDistance', 0.5),
    'erp_10': similarity.tsdist('erpDistance', 1),
    'euclidean': similarity.tsdist('euclideanDistance'),
    'fourier': similarity.tsdist('fourierDistance'),
    #'frechet': similarity.tsdist('frechetDistance'), # (USE?) prints a lot of nonsense
    'inf.norm': similarity.tsdist('inf.normDistance'),
    'int.per': similarity.tsdist('int.perDistance'),
    'lbKeogh_3': similarity.tsdist('lb.keoghDistance', 3),
    'lcss_05': similarity.tsdist('lcssDistance', 0.05),
    'lcss_15': similarity.tsdist('lcssDistance', 0.15),
    'lcss_30': similarity.tsdist('lcssDistance', 0.3),
    'lcss_50': similarity.tsdist('lcssDistance', 0.5),
    'lp': similarity.tsdist('lpDistance'),
    'manhattan': similarity.tsdist('manhattanDistance'),
    'mindist.sax_1': similarity.tsdist('mindist.saxDistance',1),
    'mindist.sax_2': similarity.tsdist('mindist.saxDistance',2),
    'mindist.sax_4': similarity.tsdist('mindist.saxDistance',4),
    'mindist.sax_8': similarity.tsdist('mindist.saxDistance',8),
    'mindist.sax_16': similarity.tsdist('mindist.saxDistance',16),
    'minkowski_25': similarity.lpNorms(2.5), #otherwise known as lp-norms
    'minkowski_30': similarity.lpNorms(3),
    'minkowski_05': similarity.lpNorms(0.5),
    #'ncd': similarity.tsdist('ncdDistance'),  # Unknown internal error
    'pacf': similarity.tsdist('pacfDistance'),
    'pdc': similarity.tsdist('pdcDistance'),
    'per': similarity.tsdist('perDistance'),
    #'pred': similarity.tsdist('predDistance'),
    #'spec.glk': similarity.tsdist('spec.glkDistance'), # {USE} SLOW. Also, I'm getting strange L-BFGS-B errors.
    #'spec.isd': similarity.tsdist('spec.isdDistance'), # {USE) SLOW. Also, I'm getting strange L-BFGS-B errors.
    'spec.llr': similarity.tsdist('spec.llrDistance'),
    'sts': similarity.tsdist('stsDistance'),
    'tquest': similarity.tsdist('tquestDistance', tau=0.5), #seems to do nothing...?
    'wav': similarity.tsdist('wavDistance'),
}

# test only a limited set
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

# test an even more limited set
algosToTest = {
    'sts': similarity.tsdist('stsDistance'),
    'mindist.sax_1': similarity.tsdist('mindist.saxDistance',1),
    'dtw': similarity.tsdist('dtwDistance'),
}

# test only sts
algosToTest0 = {
    'sts': similarity.tsdist('stsDistance'),
}


def testAlgo(algo, target):
#    global data
#    testAlgoOnData(algo, target, data['Close'])
#
#def testAlgoOnData(algo, target, dataList):
    dates = data['Date']
    groups = grouping.groupUp(data, data['Close'])

    targetNext = target+const.ma
    if targetNext >= len(groups):
        return None
    similarity.normalizeFuns = [similarity.byMean]
    similarity.measureFun = algo
    results = compareAllGroupsBefore(groups, target)
    results2 = compareAllGroupsBefore(groups, targetNext)
    
    results.reverse()
    results.sort(key=lambda x : x[2])
    results2.sort(key=lambda x : x[2])

    #tradePolicy = tradingmeasure.dontSell
    #tradePolicy = tradingmeasure.sellOrKeep
    #tradePolicy = tradingmeasure.riskAverseSellOrKeep
    tradePolicy = tradingmeasure.confidenceFilter(0.2, tradingmeasure.sellOrKeep)
    #tradePolicy = tradingmeasure.largestReturn
    
    #tradingPreprocess = tradingmeasure.averageData
    tradingPreprocess = None

    totalRank = 0
    lpScore = 0
    nResults = 10
    for v in results[0:nResults]:
        rank = getRank(results2, v[0]+const.ma)
        totalRank += rank
        lpScore += similarity.computeWith(groups[v[0]+const.ma], groups[targetNext], [similarity.byFirst], similarity.lpNorms(2))
    
    dataLists = getDataLists(groups, results[0:nResults], const.ma)
    money = tradingmeasure.computeWithFunOn(dataLists, groups[targetNext][2], tradePolicy, tradingPreprocess)
    #print(money)
    totalRank *= 100        # normalize totalRank for equal weightage.
    totalRank /= len(results2) # normalize totalRank for equal weightage.

    return (lpScore/nResults, totalRank/nResults, money)


def compareAlgorithms(fileName):
    global data, headers
    data, headers = para.readFile(fileName)
    if (len(data['Date']) == 0):
        print('Empty File')
        return

    global algosToTest
    for key in algosToTest.keys():
        print('Testing ' + key)
        algo = algosToTest[key]
        result = testAlgo(algo, 404)
        printResult(key, result)


def compareAlgorithmsWithData(testCases):
    global algosToTest, data, headers, testOutputFilename
    allResults = {}
    for key in algosToTest.keys():
        allResults[key] = []

    for companyName in sorted(testCases.keys()):
        print('Testing ' + companyName)
        data, headers = para.readFile(display.nameToFile(companyName))
        for key in sorted(algosToTest.keys()):
            #print('    algo ' + key)
            for target in testCases[companyName]:
                algo = algosToTest[key]
                result = testAlgo(algo, target)
                if result != None:
                    allResults[key].append(result)
                    #printResult(key, result)

    averageResults = {}
    f = open(testOutputFilename, 'w+')
    for key in allResults.keys():
        averageResult = computeAverageResult(allResults[key])
        s = formatResult(key, averageResult)
        f.write(s+'\n')
    f.close()


def formatResult(key, result):
    s = map(str, [key] + list(result))
    return '\t'.join(s)

def printResult(key, result):
    print(formatResult(key, result))


def computeAverageResult(results):
    import statistics
    results = util.transposeLists(results)
    print('Number of results: ' + str(len(results[0])))
    return (statistics.mean(results[0]),
            statistics.mean(results[1]),
            statistics.mean(results[2]),
            statistics.stdev(results[2]))


def getDataLists(groups, results, offset):
    return list(map(lambda v : groups[v[0]+offset][2], results))


def getSimilarity(groups, i, j):
    sim = similarity.compute(groups[i], groups[j])
    return (i,j,sim)
    

def compareAllGroupsTo(groups, targetIndex):
    results = []
    print(dates[groups[targetIndex][0]])
    print(dates[groups[targetIndex][1]])
    for i in range(0,len(groups)):
        if i != targetIndex:
            results.append(getSimilarity(groups,i,targetIndex))
    return results

def compareAllGroupsBefore(groups, targetIndex):
    return list(map(lambda i : getSimilarity(groups, i, targetIndex), range(0,targetIndex)))

# assume results is sorted.
def getRank(results, index):
    for i in range(0,len(results)):
        if results[i][0] == index:
            return i+1
    return -1
