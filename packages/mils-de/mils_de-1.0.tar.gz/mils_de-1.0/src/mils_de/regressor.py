from sklearn.base import RegressorMixin
from sklearn.neighbors._base import KNeighborsMixin, NeighborsBase, RadiusNeighborsMixin
from mils_de.utils import _to_object_array
from mils_de.weights import _custom_get_weights
import warnings

import numpy as np

class RKNearestNeighbors(KNeighborsMixin, RadiusNeighborsMixin, RegressorMixin, NeighborsBase):
    """
    Adapts from:
     - sklearn.neighbors NearestNeighbors 
     - sklearn.neighbors._regression RadiusNeighborsRegressor, KNeighborsRegressor
     - weights can be float -> weights = inverseDistance(weights)
    """
    def __init__(
        self,
        n_neighbors=5,
        radius=1.0,
        *,
        weights="uniform",
        algorithm="auto",
        leaf_size=30,
        p=2,
        metric="minkowski",
        metric_params=None,
        n_jobs=None,
    ):
        super().__init__(
            n_neighbors=n_neighbors,
            radius=radius,
            algorithm=algorithm,
            leaf_size=leaf_size,
            p=p,
            metric=metric,
            metric_params=metric_params,
            n_jobs=n_jobs,
        )

        self.weights = weights

    def rkneighbors(self, X=None):
        _knn = self.kneighbors(X, return_distance=True)
        _rnn = self.radius_neighbors(X, return_distance=True)
        _knn_list = [[(i,d) for i,d in zip(ind, dist)] for dist, ind in zip(_knn[0], _knn[1])]
        _rnn_list = [[(i,d) for i,d in zip(ind, dist)] for dist, ind in zip(_rnn[0], _rnn[1])]
        _rk_list = [list(set(_k) | set(_r)) for _k,_r in zip(_knn_list, _rnn_list)]
        _idxs = _to_object_array([np.array([x[0] for x in neigh]) for neigh in _rk_list])
        _dist = _to_object_array([np.array([x[1] for x in neigh]) for neigh in _rk_list])
        return _dist, _idxs

    def _predict_weights_neighbors(self, X):
        """
        As RadiusNeighborsRegressor.predict but returns:
        - y
        - weights
        - neigh_ind
        """
        neigh_dist, neigh_ind = self.rkneighbors(X)

        weights = _custom_get_weights(neigh_dist, self.weights)

        _y = self._y
        if _y.ndim == 1:
            _y = _y.reshape((-1, 1))

        if weights is None:
            y_pred = np.array(
                [np.mean(_y[ind, :], axis=0) for (i, ind) in enumerate(neigh_ind)]
            )

        else:
            y_pred = np.array(
                [
                    (
                        np.average(_y[ind, :], axis=0, weights=weights[i])
                    )
                    for (i, ind) in enumerate(neigh_ind)
                ]
            )

        if np.any(np.isnan(y_pred)):
            empty_warning_msg = (
                "One or more samples have no neighbors "
                "within specified radius; predicting NaN."
            )
            warnings.warn(empty_warning_msg)

        if self._y.ndim == 1:
            y_pred = y_pred.ravel()

        return y_pred, weights, neigh_ind

    def predict(self, X):
        """Predict the target for the provided data.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_queries, n_features), \
                or (n_queries, n_indexed) if metric == 'precomputed'
            Test samples.

        Returns
        -------
        y : ndarray of shape (n_queries,) or (n_queries, n_outputs), \
                dtype=double
            Target values.
        """
        y_pred, _, _ = self._predict_weights_neighbors(X)
        return y_pred

    def fit(self, X, y):
        return self._fit(X, y)