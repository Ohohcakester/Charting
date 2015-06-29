import dataselect

# You have to configure this manually to use getweekday/isweekend/nextfewweeks.
firstsaturday = 1

# 0 is monday, 6 is sunday.
def isweekend(day):
    day = getweekday(day)
    return day == 5 or day == 6

def getweekday(day):
    # 0 is monday, 6 is sunday.
    global firstsaturday
    return (day-firstsaturday-2)%7

# returns startindex, endindex, bitmap
# no longer used in favour of "next n days"
def nextfewweeks(index, firstmonday, days, dates, nweeks):
    #monday to friday of n consecutive weeks
    daylist = []
    for w in range(0,nweeks):
        base = w*7 + firstmonday
        for d in range(0,5):
            daylist.append(base + d)

    bitmap = []
    hits = 0
    curr = index
    while days[curr] < firstmonday:
        curr += 1

    for i in range(0,len(daylist)):
        if curr >= len(days):
            return None, None, None
        if daylist[i] == days[curr]:
            curr += 1
            hits += 1
            bitmap.append(b'\x01')
        else:
            bitmap.append(b'\x00')
    bitmap = b''.join(bitmap)

    #if len(daylist) - hits >= 5:
    #    return None

    endindex = curr
    return index, endindex, bitmap

# returns startindex, endindex
# next n days (data points) starting from index.
def nextndays(index, days, ndays):
    #get the next n data points.
    endindex = index + ndays
    if endindex >= len(days):
        return None, None
    return index, endindex




# each group is a tuple (startindex, endindex, data, index, conditionData)
# minDay is the day to start searching from.
def groupUp(data, dataList, minDay = 0):
    groups = splitIntoGroups(data, dataList, minDay)
    return list(map(lambda group : group + ((),), groups))


def splitIntoGroups(data, dataList, minDay = 0):
    curr = 0
    lastmonth = -1
    groups = []
    days = data['Day']
    dates = data['Date']

    for i in range(minDay,len(days)):
        if dates[i].month != lastmonth and dates[i].day < 7:
            lastmonth = dates[i].month
            #first monday of month
            #firstmonday = days[i] + ((7 - getweekday(days[i])) % 7)

            #start, end, bitmap = nextfewweeks(i, firstmonday, days, dates, 13)
            start, end = nextndays(i, days, 75)
            if start != None:
                #group = (start, end, dataList[start:end], bitmap)
                group = (start, end, dataList[start:end], len(groups))
                groups.append(group)
    return groups

def splitIntoGroupsFree(data, dataList, minDay = 0):
    groups = []
    curr = minDay
    interval = 21
    groupSize = 75
    dataLength = len(dataList)

    while True:
        start = curr
        end = curr+groupSize
        if end >= dataLength: break
        group = (start, end, dataList[start:end], len(groups))
        groups.append(group)
        curr += interval
    return groups


def splitIntoGroupsShifted(data, dataList, minDay = 0):
    curr = 0
    lastmonth = -1
    groups = []
    days = data['Day']
    dates = data['Date']

    for i in range(minDay,len(days)):
        if dates[i].month != lastmonth and dates[i].day >=23:
            lastmonth = dates[i].month

            start, end = nextndays(i, days, 75)
            if start != None:
                #group = (start, end, dataList[start:end], bitmap)
                group = (start, end, dataList[start:end], len(groups))
                groups.append(group)
    return groups


def splitIntoGroupsVariableMonths(data, dataList, minDay = 0):
    curr = 0
    lastmonth = -1
    groups = []
    days = data['Day']
    dates = data['Date']
    firstDay = -1

    for i in range(minDay,len(days)):
        if dates[i].month != lastmonth:
            if firstDay != -1:
                if dates[i].day >= firstDay+7 or dates[i].day < firstDay: continue
            else:
                firstDay = dates[i].day

            lastmonth = dates[i].month

            start, end = nextndays(i, days, 75)
            if start != None:
                #group = (start, end, dataList[start:end], bitmap)
                group = (start, end, dataList[start:end], len(groups))
                groups.append(group)
    return groups


def splitIntoGroupsFreeMonths(data, dataList, minDay = 0):
    curr = 0
    lastmonth = -1
    groups = []
    days = data['Day']
    dates = data['Date']

    for i in range(minDay,len(days)):
        if dates[i].month != lastmonth:
            lastmonth = dates[i].month
            start, end = nextndays(i, days, 75)
            if start != None:
                group = (start, end, dataList[start:end], len(groups))
                groups.append(group)
    return groups



# Each condition must be in a tuple (criteriaType, criteriaFun)
# each group is a tuple (startindex, endindex, data, index, conditionData)
def groupWithConditionData(*conditions):
    def fun(data, dataList, minDay = 0):
        groups = splitIntoGroups(data, dataList, minDay)
        conditionData = []
        for i in range(0,len(groups)): conditionData.append([])

        for condition in conditions:
            matches = dataselect.findMatchesWith(data, groups, condition[0], condition[1])
            for i in range(0,len(groups)):
                conditionData[i].append(groups[i] in matches)
        
        conditionData = list(map(tuple, conditionData))
        def reformGroup(group, cd):
            return group + (cd,)

        return list([reformGroup(group,cd) for group,cd in zip(groups,conditionData)])
    return fun


def redefineGroupingConditions(*conditions):
    global groupUp
    groupUp = groupWithConditionData(*conditions)

def changeToFreeGroups():
    global groupUp
    def groupUp(data, dataList, minDay = 0):
        groups = splitIntoGroupsFree(data, dataList, minDay)
        return list(map(lambda group : group + ((),), groups))

def changeToShiftedMonthsGroups():
    global groupUp
    def groupUp(data, dataList, minDay = 0):
        groups = splitIntoGroupsShifted(data, dataList, minDay)
        return list(map(lambda group : group + ((),), groups))


def changeToFreeMonthsGroups():
    global groupUp
    def groupUp(data, dataList, minDay = 0):
        groups = splitIntoGroupsFreeMonths(data, dataList, minDay)
        return list(map(lambda group : group + ((),), groups))

def changeToVariableMonthsGroups():
    global groupUp
    def groupUp(data, dataList, minDay = 0):
        groups = splitIntoGroupsVariableMonths(data, dataList, minDay)
        return list(map(lambda group : group + ((),), groups))
