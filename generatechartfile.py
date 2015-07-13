import parameters as para

datasetname = '454111'

sourceDir = 'ChartOutput_'+datasetname
outputFile = 'combinedChart_'+datasetname+'.txt'

nameLookupFile = 'dataNew/all/'+datasetname+'.csv'
dataFilesDir = 'data_'+datasetname+'/'

nameMap = None

def createNameMap():
    global nameMap, nameLookupFile
    nameMap = {}
    f = open(nameLookupFile)
    headers = f.readline().split(',')
    keyIndex = headers.index('COMNAM')
    valueIndex = headers.index('PERMNO')
    for line in f:
        args = line.split(',')
        key = args[keyIndex].replace(' ','_')
        value = args[valueIndex]
        if key not in nameMap:
            nameMap[key] = value
    f.close()


def translateName(name):
    global nameMap
    if nameMap == None:
        createNameMap()
    return nameMap[name]
    # wow, I have to get this from alldata.csv, and data from para.

def toFileName(name):
    global dataFilesDir
    return dataFilesDir + name + '.csv'

def translateDate(fileName, dayIndex):
    para.caching = True
    data, headers = para.readFile(fileName)
    return data['Date'][int(dayIndex)]


def parseRow(rawRow):
    cols = rawRow.split(',')
    fileName = toFileName(cols[0])

    cols[0] = translateName(cols[0])
    cols[1] = translateDate(fileName, cols[1])

    return ','.join(map(str,cols))

def getHeaders(groupSize):
    headers = ['PERMNO', 'DATE', 'ALGO', 'GROUPSIZE']
    headers += map(lambda n : 'T' + str(n), range(0,groupSize))
    return ','.join(headers)

def generateChartFile():
    global sourceDir, outputFile
    import os
    rowFiles = os.listdir(sourceDir)

    outputF = open(outputFile, 'w+')
    outputF.write(getHeaders(75))
    outputF.write('\n')

    for rowFile in rowFiles:
        f = open(sourceDir + '/' + rowFile)
        rawRow = f.read()
        f.close()

        row = parseRow(rawRow)
        outputF.write(row)
        outputF.write('\n')
    outputF.close()


def main():
    generateChartFile()


if __name__ == '__main__':
    main()