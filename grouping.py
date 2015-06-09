
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




# each group is a tuple (startindex, endindex, data, index)
# minDay is the day to start searching from.
def groupUp(days, dates, datalist, minDay = 0):
    curr = 0
    lastmonth = -1
    groups = []
    for i in range(minDay,len(days)):
        if dates[i].month != lastmonth and dates[i].day < 7:
            lastmonth = dates[i].month
            #first monday of month
            #firstmonday = days[i] + ((7 - getweekday(days[i])) % 7)

            #start, end, bitmap = nextfewweeks(i, firstmonday, days, dates, 13)
            start, end = nextndays(i, days, 75)
            if start != None:
                #group = (start, end, datalist[start:end], bitmap)
                group = (start, end, datalist[start:end], len(groups))
                groups.append(group)
    return groups
