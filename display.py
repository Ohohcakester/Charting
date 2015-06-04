import matplotlib.pyplot as plt
import similarity
import analyse

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



def getNameOnly(s):
    firstSlash = s.find('/')
    if firstSlash != -1:
        s = s[firstSlash+1:]
    lastDot = s.rfind('.')
    if lastDot != -1:
        s = s[:lastDot]
    return s

def nameToFile(s):
    return 'data/' + s + '.csv'

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
    lists = list(map(lambda v : groups[v[0]+4][2][:], results))
    for i in range(0,len(lists)):
        first = lists[i][0]
        for j in range(0,len(lists[i])):
            lists[i][j] /= first

    datapoints = []
    for i in range(0,len(lists[0])):
        datapoints.append([])
    for i in range(0,len(lists)):
        for j in range(0,len(lists[i])):
            datapoints[j].append(lists[i][j])
    meanGraph = list(map(statistics.mean, datapoints))
    stdGraph = list(map(statistics.stdev, datapoints))
    upper = []
    lower = []
    for i in range(0,len(meanGraph)):
        upper.append(meanGraph[i]+stdGraph[i])
        lower.append(meanGraph[i]-stdGraph[i])

    compareTo = similarity.byFirst(compareTo)
    plt.plot(compareTo)
    plt.plot(meanGraph)
    plt.plot(upper)
    plt.plot(lower)
    plt.show()