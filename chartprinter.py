import util
import verificationconfig

#path = 'ChartOutput_' + verificationconfig.datasetname
path = 'ChartOutput'

class ChartPrinter:
    def __init__(self, fileName, today, algo, predictSize):
        self.algo = algo
        self.predictSize = predictSize
        self.company = util.getNameOnly(fileName)
        self.today = today

    def generateFileName(self):
        global path
        li = [self.company,self.today,self.algo,self.predictSize]
        li = map(str, li)
        return path + '/' + '_'.join(li) + '.row'

    def formatRow(self, predicted):
        cols = list(map(str, [self.company,self.today,self.algo,self.predictSize]))
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