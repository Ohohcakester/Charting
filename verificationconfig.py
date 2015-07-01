import similarity
import tradingmeasure

class TradingConfig:

    def __init__(self):
        #configure options here
        self.groupSize = 75
        self.algo = 'mindist.sax_1'
        self.strategy = 'sellOrKeep'
        

        #runConfig...
        global tradeStrategy, algosToTest
        self.similarityMeasure = algosToTest[self.algo]
        self.tradePolicy, self.tradingPreprocess = tradeStrategy[self.strategy]

        fileTokens = [self.groupSize, self.algo, self.strategy]
        self.resultsFile = 'verification_' + '_'.join(map(str,fileTokens)) + '.txt'




tradeStrategy = {
    'dontSell' : (tradingmeasure.dontSell, tradingmeasure.averageData),
    'sellOrKeep' : (tradingmeasure.sellOrKeep, tradingmeasure.averageData),
    'riskAverseSellOrKeep' : (tradingmeasure.riskAverseSellOrKeep, tradingmeasure.averageData),
    'confidenceSellOrKeep' : (tradingmeasure.confidenceFilter(0.2, tradingmeasure.sellOrKeep), None),
    'largestReturn' : (tradingmeasure.largestReturn, tradingmeasure.averageData),
}


algosToTest = {
    'acf': similarity.tsdist('acfDistance'),
    'ar.lpc.ceps': similarity.tsdist('ar.lpc.cepsDistance'),
    #'ar.mah': similarity.tsdist('ar.mahDistance'), #Need to retrieve p-value
    'ar.pic': similarity.tsdist('ar.picDistance'),
    'ccor': similarity.tsdist('ccorDistance'),
    #'cdm': similarity.tsdist('cdmDistance'), # (USE) SLOW / INTERNAL ERROR 5 IN MEMCOMPRESS...?
    'cid': similarity.tsdist('cidDistance'),
    'cor': similarity.tsdist('corDistance'),
    'cort': similarity.tsdist('cortDistance'),
    'dissimapprox': similarity.tsdist('dissimapproxDistance'),
    'dissim': similarity.tsdist('dissimDistance'),
    'dtw': similarity.tsdist('dtwDistance'),
    'edr_005': similarity.tsdist('edrDistance', 0.05),
    'edr_01': similarity.tsdist('edrDistance', 0.1),
    'edr_025': similarity.tsdist('edrDistance', 0.25),
    'edr_05': similarity.tsdist('edrDistance', 0.5),
    'erp_01': similarity.tsdist('erpDistance', 0.1),
    'erp_05': similarity.tsdist('erpDistance', 0.5),
    'erp_10': similarity.tsdist('erpDistance', 1),
    'euclidean': similarity.tsdist('euclideanDistance'),
    'fourier': similarity.tsdist('fourierDistance'),
    #'frechet': similarity.tsdist('frechetDistance'), # (USE?) prints a lot of nonsense
    'inf.norm': similarity.tsdist('inf.normDistance'),
    'int.per': similarity.tsdist('int.perDistance'),
    'lbKeogh_3': similarity.tsdist('lb.keoghDistance', 3),
    'lcss_05': similarity.tsdist('lcssDistance', 0.05),
    'lcss_15': similarity.tsdist('lcssDistance', 0.15),
    'lcss_30': similarity.tsdist('lcssDistance', 0.3),
    'lcss_50': similarity.tsdist('lcssDistance', 0.5),
    'lp': similarity.tsdist('lpDistance'),
    'manhattan': similarity.tsdist('manhattanDistance'),
    'mindist.sax_1': similarity.tsdist('mindist.saxDistance',1),
    'mindist.sax_2': similarity.tsdist('mindist.saxDistance',2),
    'mindist.sax_4': similarity.tsdist('mindist.saxDistance',4),
    'mindist.sax_8': similarity.tsdist('mindist.saxDistance',8),
    'mindist.sax_16': similarity.tsdist('mindist.saxDistance',16),
    'minkowski_25': similarity.lpNorms(2.5), #otherwise known as lp-norms
    'minkowski_30': similarity.lpNorms(3),
    'minkowski_05': similarity.lpNorms(0.5),
    #'ncd': similarity.tsdist('ncdDistance'),  # Unknown internal error
    'pacf': similarity.tsdist('pacfDistance'),
    'pdc': similarity.tsdist('pdcDistance'),
    'per': similarity.tsdist('perDistance'),
    #'pred': similarity.tsdist('predDistance'),
    #'spec.glk': similarity.tsdist('spec.glkDistance'), # {USE} SLOW. Also, I'm getting strange L-BFGS-B errors.
    #'spec.isd': similarity.tsdist('spec.isdDistance'), # {USE) SLOW. Also, I'm getting strange L-BFGS-B errors.
    'spec.llr': similarity.tsdist('spec.llrDistance'),
    'sts': similarity.tsdist('stsDistance'),
    'tquest': similarity.tsdist('tquestDistance', tau=0.5), #seems to do nothing...?
    'wav': similarity.tsdist('wavDistance'),
}


def configure():
    return TradingConfig()