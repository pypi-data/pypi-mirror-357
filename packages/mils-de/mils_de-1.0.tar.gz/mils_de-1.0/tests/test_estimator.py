from tests import TestRegressorBase
from mils_de import densityEstimator
import numpy as np
import pandas as pd
import unittest

class TestEstimator(TestRegressorBase):

    @classmethod
    def setUpClass(cls):
        cls.setUpSyntheticData()
        cls.setUpRealData()

    @classmethod
    def setUpSyntheticData(cls):
        X = [[0.,0.],[0.,1.],[1.,0.],[1.,1.],[.8,.9]]
        X_test = [[.1,.1],[.6,.6]]
        y = np.sum(X, axis=1).reshape((-1,1))

        synt_df = pd.DataFrame(X, columns=['phi','P'])

        cls.synt_est = densityEstimator(n_neighbors=3, radius=.75, R=1, weights='uniform')
        cls.synt_est.fit(synt_df, y)
        cls.synt_test = pd.DataFrame(X_test, columns=['phi','P'])


    @classmethod
    def setUpRealData(cls):
        import os
        import mils_de.data
        from mils_de.weights import scaledAkaike
        from sklearn.model_selection import train_test_split

        # LOAD DATA
        col_names = mils_de.data.columns_names(num_sensors=1)
        df = pd.read_csv(os.path.join("data","MILS_10.csv"),
                         header=None,
                         names=col_names)
        # Correct for systematic errors of MILS 1.0
        df.phi += 1
        df.P *= 0.99
        df.P = np.log10(df.P)
        # Define radial domain and grid
        domain = np.arange(-5,5.5,.5)
        true_idx = mils_de.data.columns_true(domain)

        # Compute profiles values on grid
        df = mils_de.data.eval_ne_profiles(df, domain=domain)
        # Train/Test  split
        df_train, df_test = train_test_split(df, test_size=.1, random_state=42)
        # Define class attributes: trained estimator, X_test, y_true
        cls.real_est = densityEstimator(n_neighbors=5, radius=2, R=319,
                               weights=scaledAkaike())
        cls.real_est.fit(df=df_train, y=df_train[true_idx])
        cls.real_test = df_test[['phi','P']]
        cls.real_true = df_test[true_idx].to_numpy()

    def _get_rkneighbors_test(self, estimator, sample, true_d, true_i):
        nn_dist, nn_id = estimator.get_rkneighbors(sample)
        _sort = np.argsort(nn_id[0])
        nn_id = np.array(nn_id[0])[_sort]
        nn_dist = np.array(nn_dist[0])[_sort]

        self.assertTrue(np.allclose(nn_dist, true_d),
            f"get_rkneighbors - Wrong distances! test sample: {sample}" + \
            f"\nGot {nn_dist} instead of {true_d}")

        self.assertTrue(np.allclose(nn_id, true_i),
            f"get_rkneighbors - Wrong indices! test sample: {sample}" + \
            f"\nGot {nn_id} instead of {true_i}")

    def _rmse_test(self, y_true, y_pred, true_rmse, msg=''):
        from mils_de.metrics import reduced_masked_RMSE

        rmse = reduced_masked_RMSE(y_true, y_pred)
        self.assertTrue(np.allclose(rmse, true_rmse),
                        f"Wrong RMSE on prediction!" + msg +\
                        f"\nGot {rmse} instead of {true_rmse}")

    def test_synt_predict(self):
        y_true = [[0.66666667], [1.425]]
        self._predict_test(self.synt_est, self.synt_test, y_true)

    def test_synt_rkneighbors(self):
        sample = self.synt_test.loc[:0]
        true_d, true_i = [0.14142136, 0.90553851, 0.90553851], [0, 1, 2]
        # For Synt case rkneighbors and get_rkneighbors return same indices
        self._rkneighbors_test(self.synt_est, sample, true_d, true_i)
        self._get_rkneighbors_test(self.synt_est, sample, true_d, true_i)

        sample = self.synt_test.loc[1:]
        true_d = [0.72111026, 0.72111026, 0.56568542, 0.36055513]
        true_i = [1, 2, 3, 4]
        self._rkneighbors_test(self.synt_est, sample, true_d, true_i)
        self._get_rkneighbors_test(self.synt_est, sample, true_d, true_i)

    def test_real_data_get_rkneighbors(self):
        sample = self.real_test.loc[[124]]
        
        true_i = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17, 123, 125, 294]
        true_d = [0.47710663, 0.32251137, 0.27564606, 0.94807763, 1.11329354,
                  1.18149523, 1.37869469, 1.43902333, 1.50507891, 0.5649818,
                  0.69570482, 0.77282439, 1.71601859, 1.83128023, 1.95687542,
                  0.65157436, 0.73948013, 0.69442192]
        self._get_rkneighbors_test(self.real_est, sample, true_d, true_i)

    def test_real_data_rmse(self):
        y_pred = self.real_est.predict(self.real_test)
        true_rmse = 0.06288727916942549
        self._rmse_test(self.real_true, y_pred, true_rmse)

if __name__=='__main__':
    unittest.main()