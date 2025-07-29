import unittest
from tests import TestEstimator, TestRegressor

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRegressor))
    suite.addTest(unittest.makeSuite(TestEstimator))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbose=3)
    runner.run(suite())