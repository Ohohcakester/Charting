import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()
from rpy2.robjects.packages import importr
r = rpy2.robjects.r
ts = importr('TSdist')

def run_ts(data1, data2, measureName, *args, **kwargs):
    measureName = measureName.replace('.', '_')
    measureFun = getattr(ts, measureName)
    d1 = rpy2.robjects.FloatVector(data1)
    d2 = rpy2.robjects.FloatVector(data2)
    result = measureFun(d1, d2, *args, **kwargs)
    return result[0]



#http://dtw.r-forge.r-project.org/
#http://rpy.sourceforge.net/rpy2/doc-2.5/html/robjects_rinstance.html
#https://nipunbatra.wordpress.com/2013/06/09/dynamic-time-warping-using-rpy-and-python/

if __name__ == '__main__':
    pass