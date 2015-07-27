import matplotlib.pyplot as plt
import similarity
import analyse
import util
import constants as const

def plotgroup(data, group):
    start, end = group[0], group[1]
    days = data['Day'][start:end]
    base = days[0]
    days = list(map(lambda d : d - base, days))

    dates = data['Date']
    print('Plotting ' + str(dates[start]) + ' to ' + str(dates[end]))
    plt.plot(days, group[2])
    #plt.show()

def plotnormalized(data, group):
    start, end = group[0], group[1]

    dates = data['Date']
    print('Plotting ' + str(dates[start]) + ' to ' + str(dates[end]))
    plt.plot(similarity.normalize(group[2]))
    #plt.show()

def plotnormalizedWith(data, group, normalizeFuns):
    start, end = group[0], group[1]
  
    dates = data['Date']
    print('Plotting ' + str(dates[start]) + ' to ' + str(dates[end]))
    plt.plot(similarity.normalizeWith(group[2], normalizeFuns))
    #plt.show()


def nameToFile(s, datasetname = ''):
    return 'data_' + datasetname + '/' + s + '.csv'

def bitmapToStr(bitmap):
    return ''.join(map(str,bitmap))

def printgroup(group, dates):
    start = group[0]
    end = group[1]
    print('Start: ' + str(start) + '-' + str(end) + ' from ' +
        str(dates[start]) + ' to ' + str(dates[end]))
    if len(group >= 3): print(bitmapToStr(group[3]))
    print(group[2])

def printgroupattrs(group, dates):
    start = group[0]
    end = group[1]
    index = group[3]
    print(str(index) + ': ' + str(start) + '-' + str(end) + ' from ' +
        str(dates[start]) + ' to ' + str(dates[end]))


def plotAverageHighLow(groups, results, compareTo):
    import statistics
    lists = list(map(lambda v : groups[v[0]+const.ma][2][:], results))
    for i in range(0,len(lists)):
        lists[i] = similarity.byFirst(lists[i])

    datapoints = util.transposeLists(lists)

    meanGraph = list(map(statistics.mean, datapoints))
    stdGraph = list(map(statistics.stdev, datapoints))

    first = meanGraph[0]
    scale = lambda v : v / first
    meanGraph = list(map(scale, meanGraph))
    stdGraph = list(map(scale, stdGraph))

    upper = list([a+b for a,b in zip(meanGraph, stdGraph)])
    lower = list([a-b for a,b in zip(meanGraph, stdGraph)])

    compareTo = similarity.byFirst(compareTo)
    plt.plot(compareTo)
    plt.plot(meanGraph)
    plt.plot(upper)
    plt.plot(lower)
    plt.show()