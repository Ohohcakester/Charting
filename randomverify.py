import parameters as para
import util
import random

predictSize = 75
probability = 0.05

def computeResults(datalist):
    global predictSize, probability
    results = []
    for i in range(0,len(datalist)-predictSize):
        if random.random() < probability:
            results.append(datalist[i+predictSize]/datalist[i])
    return results


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