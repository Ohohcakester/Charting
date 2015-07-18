import parameters as para
import util
import random

defaultPredictSize = 75
probability = 0.05

def computeResults(datalist, predictSize = None):
    if predictSize == None:
        global defaultPredictSize
        predictSize = defaultPredictSiz

    global probability
    results = []
    for i in range(0,len(datalist)-predictSize):
        if random.random() < probability:
            results.append(datalist[i+predictSize]/datalist[i])
    return results

def verify(fileName, predictSize):
    data, headers = para.readFile(fileName)
    return computeResults(data['Close'], predictSize)

def main():
    dataFiles = util.listDataFiles()
    results = []
    for dataFile in dataFiles:
        print('Reading ' + dataFile)
        data, headers = para.readFile(dataFile)
        datalist = data['Close']
        results += computeResults(datalist)
    import statistics
    print('Results: ' + str(len(results)))
    print(statistics.mean(results))
    print(statistics.stdev(results))


if __name__ == '__main__':
    main()