from sklearn.neighbors._base import _get_weights
import numpy as np

def scaled_akaike(neigh_dist, alpha=0):
    if type(alpha) == int or type(alpha) == float:
        return [np.exp(-.5*np.square(x.astype(float)) + alpha) for x in neigh_dist]
    elif alpha == 'nn':
        alpha = [np.min(d) for d in neigh_dist]
        return [np.exp(-.5*np.square(x.astype(float)) + .5*(alpha[i])**2) for i, x in enumerate(neigh_dist)]
    else:
        raise TypeError

class scaledAkaike():
    def __init__(self, alpha='nn'):
        self.alpha=alpha

    def __call__(self, neigh_dist):
        return scaled_akaike(neigh_dist, self.alpha)

    def __str__(self):
        return f"scaled akaike {self.alpha}"

class inverseDistance():
    def __init__(self, p=2):
        self.p=p

    def __call__(self, neigh_dist):
        # TODO: Check performances. alpha=2, or pow+reciprocal...
        # TODO: why not value error? setting an array element with a sequence.
        if self.p == 2:
            pow = np.square(neigh_dist)
        else:
            pow = np.power(neigh_dist, self.p)
        return np.reciprocal(pow)

    def __str__(self):
        return f"1/d^{self.p}"

class exponentialDecrease():
    def __init__(self, p=1):
        self.p=p

    def __call__(self, neigh_dist):
        if self.p == 1:
            return  [np.exp(-x) for x in neigh_dist]
        else:
            return [np.exp(-np.power(x, self.p, dtype=np.float64)) for x in neigh_dist]

    def __str__(self):
        return f"exp(-d^{self.p})"

def _custom_get_weights(dist, weights):
    """
    Add int or float option to scikitlearn.neighbors._base._get_weights
    """
    if isinstance(weights, (float, int)):
        weights = inverseDistance(weights)
    return _get_weights(dist, weights)
