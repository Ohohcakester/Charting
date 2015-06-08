# library imports
from datetime import date
import matplotlib.pyplot as plt
# linking imports
import similarity
import dataselect
import testcollection
import parameters as para
import grouping
import display
import testalgos
import weightoptimisation

# parameters.readFile will write to two variables:
data = {}
headers = []

def main():
    choice = 1

    options = {
        0:runTests,
        1:runDataSelect,
        2:runVisualise,
        3:weightoptimisation.optimise,
        4:findDoubleTops,
        5:viewGraph,
    }
    options[choice]()



def runTests():
    testCases = testcollection.readTests()
    testalgos.compareAlgorithmsWithData(testCases)
    #compareAlgorithms('table.csv')


def getRandomSublist(arr, size):
    import random
    arr = list(arr)
    random.shuffle(arr)
    return arr[:size]


def runDataSelect():
    dataFiles = listDataFiles()
    dataFiles = getRandomSublist(dataFiles, 20)

    for f in dataFiles:
        dataselect.run(f)
    #dataselect.run('data/ABERDEEN_ASIA_PACIFIC_INCOME_FD.csv')


def findDoubleTops():
    dataFiles = listDataFiles()
    for f in dataFiles:
        data, headers = para.readFile(f)
        intervals = dataselect.findDoubleTops(data)
        if (len(intervals) > 0):
            print(display.getNameOnly(f))
            print(intervals)

def viewGraph():
    fileName = 'data/F_5_NETWORKS_INC.csv'
    start, end = 1139, 1204

    data, headers = para.readFile(fileName)
    dates = data['Date']
    dhigh = data['High']
    dlow = data['Low']
    dclose = data['Close']
    dopen = data['Open']

    plt.plot(dhigh[start:end])
    plt.plot(dlow[start:end])
    plt.plot(dclose[start:end])
    plt.plot(dopen[start:end])
    plt.show()


def runVisualise():
    fileName = 'data/MENTOR_GRAPHICS_CORP.csv'
    #fileName = 'table.csv'
    targetGroup = 142

    global data, headers
    data, headers = para.readFile(fileName)
    dates = data['Date']
    close = data['Close']
    groups = grouping.groupUp(data['Day'], dates, close)

    target = targetGroup
    targetNext = target+4
    results = testalgos.compareAllGroupsBefore(groups, target)
    results2 = testalgos.compareAllGroupsBefore(groups, targetNext)
    #results2 = compareAllGroupsTo(groups, targetNext)
    
    results.reverse()
    results.sort(key=lambda x : x[2])
    results2.sort(key=lambda x : x[2])

    print('Target ' + str(target))
    display.plotgroup(data, groups[target])
    plt.show()

    for v in results[0:10]:
        print(v)

    totalRank = 0
    ranks = []
    for v in results[0:10]:
        rank = testalgos.getRank(results2, v[0]+4)
        totalRank += rank
        ranks.append(rank)
    print('Total Rank = ' + str(totalRank))
    print(ranks)

    display.plotAverageHighLow(groups, results[0:10], groups[targetNext][2])
    return

    for v in results[0:10]:
        print()
        print('Chosen group:')
        print('Number ' + str(v[0]) + ', SimilarityScore = ' + str(v[2]))
        print('Matching Group:')
        print('Number ' + str(v[0]+4) + ', Rank = ' + str(testalgos.getRank(results2, v[0]+4)))
        print('Plotting Target Next Group (blue)')
        display.plotnormalizedWith(data, groups[targetNext], [similarity.byFirst])
        print('Plotting Predicted Next Group (green)')
        display.plotnormalizedWith(data, groups[v[0]+4], [similarity.byFirst])
        plt.show()
            

def listDataFiles():
    import os

    def extension(s):
        return s[-4:] == '.csv'
    def addDir(s):
        return 'data/' + s

    files = map(addDir, filter(extension, os.listdir('data')))
    return files




if __name__ == '__main__':
    main()