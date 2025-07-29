import numpy as np
from sklearn.metrics import mean_squared_error

def masked_RMSE(y_true, y_pred):
    mask = ~np.isnan(y_pred)
    return np.sqrt(mean_squared_error(y_true[mask], y_pred[mask]))

def reduced_masked_RMSE(y_true, y_pred, reduction=np.median):
    return reduction([masked_RMSE(_t, _p) for _t, _p in zip(y_true, y_pred)])

def biased_weighted_sample_variance(y_nn, weights):
    """ Compute the biased weighted sample variance.
    y_nn: array of samples
    weights: array of weights
    """
    weighted_avg = np.average(y_nn, axis=0, weights=weights)
    return np.average((y_nn - weighted_avg)**2, axis=0, weights=weights)

def unbiased_weighted_sample_variance(y_nn, weights):
    """ Correct the biased weighted sample variance 
    (see: https://en.wikipedia.org/wiki/Weighted_arithmetic_mean).
    y_nn: array of samples
    weights: array of weights
    """
    bw_variance = biased_weighted_sample_variance(y_nn, weights)
    return bw_variance / (1 - np.sum(weights**2)/np.sum(weights)**2)
