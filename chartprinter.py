import util
path = 'ChartOutput'

class ChartPrinter:
    def __init__(self, fileName, today, algo, groupSize):
        self.algo = algo
        self.groupSize = groupSize
        self.company = util.getNameOnly(fileName)
        self.today = today

    def generateFileName(self):
        global path
        li = [self.company,self.today,self.algo,self.groupSize]
        li = map(str, li)
        return path + '/' + '_'.join(li) + '.row'

    def formatRow(self, predicted):
        cols = list(map(str, [self.company,self.today,self.algo,self.groupSize]))
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