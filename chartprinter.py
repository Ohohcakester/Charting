import util
import os

def initialise(datasetname):
    global path
    path = 'ChartOutput_' + datasetname
    #path = 'ChartOutput'
    if not os.path.exists(path):
        os.mkdir(path)

class ChartPrinter:
    def __init__(self, fileName, today, algo, groupSize, predictSize):
        self.algo = algo
        self.groupSize = groupSize
        self.predictSize = predictSize
        self.company = util.getNameOnly(fileName)
        self.today = today

    def generateFileName(self):
        li = [self.company,self.today,self.algo,self.groupSize,self.predictSize]
        li = map(str, li)
        return path + '/' + '_'.join(li) + '.row'

    def formatRow(self, predicted):
        cols = list(map(str, [self.company,self.today,self.algo,self.groupSize,self.predictSize]))
        cols += list(map(str, predicted))
        return ','.join(cols)


    def writeChart(self, predicted):
        fileName = self.generateFileName()
        line = self.formatRow(predicted)
        f = open(fileName, 'w+')
        f.write(line)
        f.close()


def new(*args):
    return ChartPrinter(*args)