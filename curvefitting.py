import parameters as para
import similarity
import grouping
import numpy
from scipy.interpolate import interp1d

def main():
    bestPolyFit()



def testCubicFit():
    import matplotlib.pyplot as plt
    data, headers = para.readFile('data/3_D_SYSTEMS_CORP_DEL.csv')
    dates = data['Date']
    close = data['Close']
    start = 390
    end = 450

    dataList = para.averageLast(5)([close], len(close))
    #dataList = close

    linf = linearInterpolate(dataList[start:end])
    cubf = cubicSpline(dataList[start:end])

    x = list(map(lambda x : x/10, range(0,9*(end-start))))
    linear = list(map(linf, x))
    cubic = list(map(cubf, x))
 
    coeffs = fitPoly(3)(cubic, 0, len(cubic))

    p = polynomialFunction(coeffs)
    estimate = list(map(p,x))

    plt.plot(x, linear)
    plt.plot(x, cubic)
    plt.plot(x, estimate)
    plt.show()

def testPolyFit():
    import matplotlib.pyplot as plt
    data, headers = para.readFile('data/A_C_I_WORLDWIDE_INC.csv')
    dates = data['Date']
    close = data['Close']
    #groups = grouping.groupUp(data['Day'], dates, close)
    start = 80
    end = 200

    #dataList = para.averageLast(5)([close], len(close))
    dataList = close

    #group = groups[23]
    #coeffs = fitPoly(3)(dataList, group[0], group[1])
    
    plt.plot(dataList[start:end])
    coeffs = fitPoly(4)(dataList, start, end)

    p = polynomialFunction(coeffs)
    estimate = list(map(p, range(0,end-start)))
    plt.plot(estimate)
    plt.show()

def bestPolyFit():
    import matplotlib.pyplot as plt
    data, headers = para.readFile('data/3_D_SYSTEMS_CORP_DEL.csv')
    dates = data['Date']
    close = data['Close']
    #groups = grouping.groupUp(data['Day'], dates, close)
    start = 230
    end = 379

    #dataList = para.averageLast(5)([close], len(close))
    dataList = close

    #group = groups[23]
    #coeffs = fitPoly(3)(dataList, group[0], group[1])
    
    plt.plot(dataList[start:end])
    bestRatio = 0
    bestDegree = -1
    lastValue = -1
    savedPlot = None
    for i in range(2,20):
        coeffs = fitPoly(i)(dataList, start, end)

        p = polynomialFunction(coeffs)
        estimate = list(map(p, range(0,end-start)))

        score = similarity.lpNorms(2)(estimate, dataList[start:end])
        print('Degree ' + str(i) + ' score = ' + str(score))
        #plt.plot(estimate)
        if lastValue == -1:
            lastValue = score
        else:
            ratio = lastValue/score
            lastValue = score
            if ratio > bestRatio:
                savedPlot = estimate
                bestRatio = ratio
                bestDegree = i

    print('Best degree = ' + str(bestDegree) + ' with score = ' + str(bestRatio))
    plt.plot(savedPlot)
    plt.show()


""" REGION: UTILITY - START """


def fitPoly(n):
    def fun(fulldata, startIndex, endIndex):
        length = endIndex-startIndex
        fit = numpy.polyfit(list(range(0,length)), fulldata[startIndex:endIndex], n)
        return list(fit)
    return fun


def polynomialFunction(coefficients):
    def fun(x):
        result = 0
        for a in coefficients:
            result *= x
            result += a
        return result
    return fun


def cubicSpline(arr):
    return interp1d(range(0,len(arr)),arr, kind='cubic')

def linearInterpolate(arr):
    return interp1d(range(0,len(arr)),arr)


""" REGION: UTILITY - END """


if __name__ == '__main__':
    main()


