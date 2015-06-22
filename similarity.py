import rbind

#Format of group:
# (startindex, endindex, data, index) #bitmap deprecated.

""" REGION: MAIN FUNCTIONS - START """

def computeConditionScore(group1, group2):
    if len(group1[4]) == 0: return 0

    LARGE_CONSTANT = 10000
    def match(x,y):
        if x == y: return 1
        return 0
    return LARGE_CONSTANT * sum([match(x,y) for x,y in zip(group1[4], group2[4])])

# Computes the similarity score between two groups.
def compute(group1, group2):
    global measureFun
    data1, data2 = group1[2], group2[2] 
    data1, data2 = normalize(data1), normalize(data2)

    return measureFun(data1, data2) + computeConditionScore(group1, group2)

def computeWith(group1, group2, normalizeFuns, measureFun):
    data1, data2 = group1[2], group2[2]
    data1 = normalizeWith(data1, normalizeFuns)
    data2 = normalizeWith(data2, normalizeFuns)

    return measureFun(data1, data2) + computeConditionScore(group1, group2)

# Returns two arrays formed from parsing the bitmaps.
def repairdata(group1, group2):
    global repairFun
    return repairFun(group1, group2)

# Returns two arrays formed from parsing the bitmaps.
def normalize(data):
    global normalizeFuns
    return normalizeWith(data, normalizeFuns)

def normalizeWith(data, normalizeFuns):
    for fun in normalizeFuns:
        data = fun(data)
    return data




""" REGION: MAIN FUNCTIONS - END """


""" REGION: DATA REPAIR FUNCTIONS - START """
# Uses the bitmap and data to generate two equal-length arrays
# that can be used by the similarity measure.
# deprecated. [now we use n consecutive days, means no holes]

def avgRepair_ind(group):
    newdata = []
    bitmap, data = group[3], group[2]
    currIndex = 0
    for i in range(0, len(bitmap)):
        if bitmap[i] == 1:
            newdata.append(data[currIndex])
            currIndex += 1
        else:
            # missing data.
            if currIndex >= len(data):
                newdata.append(data[-1])
            elif currIndex == 0:
                newdata.append(data[0])
            else:
                newdata.append((data[currIndex-1] + data[currIndex]) / 2)
    return newdata


def avgRepair(group1, group2):
    return avgRepair_ind(group1), avgRepair_ind(group2)


""" REGION: DATA REPAIR FUNCTIONS - END """


""" REGION: NORMALIZATION FUNCTIONS - START """


def byMean(data):
    mean = sum(data) / len(data)
    return list(map(lambda v : v / mean, data))

def byFirst(data):
    first = data[0]
    return list(map(lambda v : v / first, data))

def byRatio(data):
    return list(map(lambda i : data[i]/data[i-1], range(1,len(data))))

def avgSmooth(size):
    def fun(data):
        newlist = []
        for i in range(size,len(data)):
            newlist.append(sum(data[i-size:i]))
        return newlist
    return fun

def weightedSmooth(size):
    def fun(data):
        newlist = []
        weights = list(range(1,size+1))
        sumweights = sum(weights)
        for i in range(0,len(data)-size):
            total = 0
            for j in range(0,size):
                total += weights[j] * data[i+j]
            newlist.append(total)
        return newlist
    return fun


""" REGION: NORMALIZATION FUNCTIONS - END """



""" REGION: SIMILARITY MEASURES - START """
# Format of similarity measure: (floatArray,floatArray) -> float
# We can assume both arrays are of the same length

def lpNorms(p):
    def fun(data1, data2):
        diff = map(lambda i : abs(data1[i]-data2[i])**p, range(0,len(data1)))
        return (sum(diff))**(1/p)
    return fun

# Gets a measure from the r TSdist library.
# Example: r('dtwDistance') returns a dtw distance similarity measure.
def tsdist(measureName, *args, **kwargs):
    def fun(data1, data2):
        return rbind.run_ts(data1, data2, measureName, *args, **kwargs)
    return fun



""" REGION: SIMILARITY MEASURES - END """

#repairFun = avgRepair # repair is deprecated
#measureFun = lpNorms(1)
measureFun = tsdist('stsDistance')
normalizeFuns = [byMean]