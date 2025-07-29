from mils_de.weights import _custom_get_weights
from mils_de.regressor import RKNearestNeighbors

import numpy as np
import pandas as pd

class densityEstimator(RKNearestNeighbors):
    def __init__(
        self,
        n_neighbors=5,
        radius=1.0,
        *,
        algorithm="auto",
        leaf_size=30,
        p=2,
        metric="minkowski",
        metric_params=None,
        n_jobs=None,
        R=319,
        weights=None,
        reduction=lambda x,y,z: np.std(y, axis=0),
        num_sensors = 1,
        ioi=lambda x: np.argmin(x, axis=1),
        confidence_interval = lambda x: range(x-2,x+3),
    ):
        """"
        If num_sensors > 1, R can be an array
        """
        self.R = R
        self.reduction = reduction
        self.ioi = ioi

        self.num_sensors = int(num_sensors)
        assert self.num_sensors > 0

        super().__init__(
            n_neighbors=n_neighbors,
            radius=radius,
            algorithm=algorithm,
            leaf_size=leaf_size,
            p=p,
            metric=metric,
            metric_params=metric_params,
            n_jobs=n_jobs,
            weights = weights,
        )

        self.confidence_interval = confidence_interval

    def _df2features(self, df):
        """
        Gets the R rescaled features from a dataframe

        # TODO: Checks on R here? If in __init__ GS FAILS
        """

        if not hasattr(self.R, "__len__"):
            self.R = [1] * self.num_sensors + [self.R] * self.num_sensors

        if len(self.R) == (2 * self.num_sensors - 1):
            self.R = [1] + list(self.R)

        assert len(self.R) == (2 * self.num_sensors)

        if self.num_sensors == 1:
            _X = pd.concat([df.phi, df.P], axis = 1)
        else:
            _X = df.loc[:,np.in1d(df.columns.get_level_values(0) , ('P','phi'))] 

        return _X * self.R

    def weight_function(self, dist):
        # TODO: Is this useful?
        return _custom_get_weights(dist, self.weights)

    def get_rkneighbors(self, df):
        X = self._df2features(df)
        _dist, _idxs = self.rkneighbors(X)
        _df_idx = [self._train_idx[_i] for _i in _idxs]
        return _dist, _df_idx

    def neighbors_profiles_stats(self, df, reduction=None):
        X = self._df2features(df)
        y, w, neigh_ind = self._predict_weights_neighbors(X)
        return self._neighbors_profiles_stats(y, w, neigh_ind, reduction)

    def _neighbors_profiles_stats(self, y_pred, weights, neigh_ind, reduction=None):

        if reduction is None:
            reduction = self.reduction

        if not hasattr(weights, '__len__'):
            weights = [weights] * len(y_pred)

        _red = np.empty_like(y_pred)
        for i, ind in enumerate(neigh_ind):
            _red[i] = reduction(y_pred[i], self._y[ind, :], weights[i])
        return _red

    def index_of_interest(self, df, reduction=None):
        """
        Returns the index where the domain of interest is cntered.
        This is the point minimising the `reduction` of the
        neighbours' profiles (e.g. minimum of the variance).
        """
        X = self._df2features(df)
        y, w, neigh_ind = self._predict_weights_neighbors(X)
        _red = self._neighbors_profiles_stats(y, w, neigh_ind, reduction)
        return self._index_of_interest(_red)

    def _index_of_interest(self, _red):
        return self.ioi(_red)

    def predict(self, df, reduction=None):
        X = self._df2features(df)
        y, w, neigh_ind = super()._predict_weights_neighbors(X)
        # NAN outside of confidence interval
        # 1) Compute the Index of interest (e.g. min nn variance)
        _red = self._neighbors_profiles_stats(y, w, neigh_ind, reduction)
        _idx = self._index_of_interest(_red)
        # 2) Mask by np.nan outside the confidence interval
        for i, _ioi in enumerate(_idx):
            # compute the confidence interval mask
            idxs_int = self.confidence_interval(_ioi)
            mask_int = np.isin(np.arange(y.shape[1]), idxs_int)
            # Apply np.nan outside
            y[i, ~mask_int] = np.nan
        return y

    def fit(self, df, y):
        X = self._df2features(df)
        self._train_idx = df.index
        return super().fit(X, y)
