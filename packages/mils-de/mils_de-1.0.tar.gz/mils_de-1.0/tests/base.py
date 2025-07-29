import numpy as np
import unittest

class TestRegressorBase(unittest.TestCase):
    def _rkneighbors_test(self, regressor, sample, true_d, true_i):
        _dist, _idx = regressor.rkneighbors(sample)
        _sort = np.argsort(_idx[0])
        _idx = np.array(_idx[0])[_sort]
        _dist = np.array(_dist[0])[_sort]

        self.assertTrue(np.allclose(_dist, true_d),
            f"rkneighbors - Wrong distances! test sample: {sample}" + \
            f"\nGot {_dist} instead of {true_d}")

        self.assertTrue(np.allclose(_idx, true_i),
            f"rkneighbors - Wrong indices! test sample: {sample}" + \
            f"\nGot {_idx} instead of {true_i}")

    def _predict_test(self, regressor, X_test, y_true):
        y_pred = regressor.predict(X_test)
        self.assertTrue(np.allclose(y_pred, y_true),
            f"predict - Wrong prediction!" + \
            f"\nGot {y_pred} instead of {y_true}")