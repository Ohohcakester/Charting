import rpy2.tests
import unittest

# the verbosity level can be increased if needed
tr = unittest.TextTestRunner(verbosity = 2)
suite = rpy2.tests.suite()
tr.run(suite)