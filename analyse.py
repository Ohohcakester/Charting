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
import util

# parameters.readFile will write to two variables:
data = {}
headers = []

def main():
    choice = 0

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
    #grouping.redefineGroupingConditions(dataselect.conditionBreakHigh, dataselect.conditionDoubleTops, dataselect.conditionDoubleTopsFiltered)
    #grouping.redefineGroupingConditions(dataselect.conditionBreakHigh)
    #grouping.redefineGroupingConditions(dataselect.conditionDoubleTopsFiltered)
    #grouping.changeToShiftedMonthsGroups()

    testCases = testcollection.readTests()
    testalgos.compareAlgorithmsWithData(testCases)
    #compareAlgorithms('table.csv')


""" REGION: DATA SELECT - START """
def runDataSelect():
    dataFiles = util.listDataFiles()
    #dataFiles = util.getRandomSublist(dataFiles, 20)

    for f in dataFiles:
        runDataSelectOn(f)
    #dataselect.run('data/ABERDEEN_ASIA_PACIFIC_INCOME_FD.csv')


def runDataSelectOn(fileName):
    data, headers = para.readFile(fileName)
    dates = data['Date']
    if (len(dates) == 0):
        #print('Empty File')
        return
    groups = grouping.groupUp(data, data['Close'])

    matches = dataselect.findMatches(data, groups)
    #print('Found ' + str(len(matches)) + 'matches')
    if (len(matches) <= 0): return #print only when there is at least one match.
    print(util.getNameOnly(fileName))
    for group in matches:
        display.printgroupattrs(group, dates)

""" REGION: DATA SELECT - END """


def findDoubleTops():
    dataFiles = util.listDataFiles()
    for f in dataFiles:
        data, headers = para.readFile(f)
        intervals = dataselect.findDoubleTops(data)
        if (len(intervals) > 0):
            print(util.getNameOnly(f))
            print(intervals)

def viewGraph():
    fileName = 'data/F_5_NETWORKS_INC.csv'
    start, end = 200,1000

    data, headers = para.readFile(fileName)
    dates = data['Date']
    #lines = ['High', 'Low', 'Close', 'Open']
    lines = ['Running', 'DiffClose', 'DiffCloseSign']

    for line in lines:
        #plt.plot(data[line][start:end])
        plt.plot(similarity.byMean(data[line][start:end]))

    plt.show()


def runVisualise():
    fileName = 'data/AMERICAN_MANAGEMENT_SYSTEMS_INC.csv'
    #fileName = 'table.csv'
    targetGroup = 89

    global data, headers
    data, headers = para.readFile(fileName)
    dates = data['Date']
    close = data['Close']
    groups = grouping.groupUp(data, data['Close'])

    target = targetGroup
    targetNext = target+util.ma
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
        rank = testalgos.getRank(results2, v[0]+util.ma)
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
        print('Number ' + str(v[0]+util.ma) + ', Rank = ' + str(testalgos.getRank(results2, v[0]+util.ma)))
        print('Plotting Target Next Group (blue)')
        display.plotnormalizedWith(data, groups[targetNext], [similarity.byFirst])
        print('Plotting Predicted Next Group (green)')
        display.plotnormalizedWith(data, groups[v[0]+util.ma], [similarity.byFirst])
        plt.show()
            


if __name__ == '__main__':
    main()