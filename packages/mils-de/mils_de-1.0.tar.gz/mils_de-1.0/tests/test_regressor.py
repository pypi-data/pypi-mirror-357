from mils_de import RKNearestNeighbors

from tests import TestRegressorBase
import numpy as np
import unittest

class TestRegressor(TestRegressorBase):

    @classmethod
    def setUpClass(cls):
        X = np.arange(11, dtype=np.float64).reshape((-1,1))**2
        y = np.arange(11, dtype=np.float64)

        cls.regressor = RKNearestNeighbors(n_neighbors=3, radius=6)
        cls.regressor.fit(X, y)
        cls.X_test = np.array([3.5, 80]).reshape((-1,1))

    def test_predict(self):
        y_true = [1.5, 9. ]
        self._predict_test(self.regressor, self.X_test, y_true)

    def test_rkneighbots(self):
        true_d, true_i = [3.5, 2.5, 0.5, 5.5], [0, 1, 2, 3]
        self._rkneighbors_test(self.regressor, self.X_test[:1], true_d, true_i)

        true_d, true_i = [16., 1., 20.], [8, 9, 10]
        self._rkneighbors_test(self.regressor, self.X_test[1:], true_d, true_i)


if __name__=='__main__':
    unittest.main()