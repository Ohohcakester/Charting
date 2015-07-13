path = 'output/'

def rename(headers, fromName, toName):
    for i in range(0,len(headers)):
        if headers[i] == fromName:
            headers[i] = toName
            
def addIndex(indexes, headers, fromName, toName):
    for i in range(0,len(headers)):
        if headers[i] == fromName:
            headers[i] = toName
            indexes.append(i)
            return

def createAndOpen(name):
    global path
    name = '_'.join(name.split())
    return open(path+name+'.csv', 'w+')
            
def splitFile(fileName):
    f = open(fileName)
    headers = f.readline().rstrip().split(',')
    usedIndexes = []
    addIndex(usedIndexes, headers, 'date', 'Date')
    addIndex(usedIndexes, headers, 'BIDLO', 'Low')
    addIndex(usedIndexes, headers, 'ASKHI', 'High')
    #addIndex(usedIndexes, headers, 'BID', 'Bid')
    #addIndex(usedIndexes, headers, 'ASK', 'Ask')
    addIndex(usedIndexes, headers, 'PRC', 'Close')
    addIndex(usedIndexes, headers, 'OPENPRC', 'Open')
    addIndex(usedIndexes, headers, 'VOL', 'Volume')
    splitByIndex = 3
    #usedIndexes = [1,5,6,7,8,10,11,13]
    
    currentName = None
    currentFile = None
    for line in f:
        args = line.rstrip().split(',')
        if currentName != args[splitByIndex]:
            if currentFile != None:
                currentFile.close()
            currentName = args[splitByIndex]
            currentFile = createAndOpen(currentName)
            s = []
            for i in usedIndexes:
                s.append(headers[i])
            currentFile.write(','.join(s) + '\n')
        s = []
        for i in usedIndexes:
            if len(args[i]) > 0:
                s.append(args[i])
            else:
                s = None
                break
        if s != None:
            currentFile.write(','.join(s) + '\n')
            
    currentFile.close()
        
        
        
splitFile('alldata.csv')