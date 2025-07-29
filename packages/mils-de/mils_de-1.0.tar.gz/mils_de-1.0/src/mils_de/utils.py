import numpy as np

large_confidence_interval = lambda x: range(x-4,x+5,2)
small_confidence_interval = lambda x: range(x-2,x+3,1)

argmin_ioi  = lambda x: np.argmin(x, axis=1)
centred_ioi = lambda x: 2 * np.ones((x.shape[0],) + x.shape[2:], dtype=int)


def ioi_default(_red, default=lambda x: x.shape[1]//2 - 1):
    """
    In case of multiple minima takes the default index.
    _red: array-like.
    default_index: lambda with integer output.
    """
    _argmin = np.argmin(_red, axis=1)
    _min = np.min(_red, axis=1)
    mask = np.count_nonzero(_red-_min.reshape(-1,1) == 0 , axis=1)>1
    _argmin[mask] = default(_red)
    return _argmin.reshape(_red.shape[0],)


def call_profile(params, log_scale=True):
    '''
    Takes the profile parameters and returns a callable
    '''
    if len(params) == 3:
        n_lim, a_in, a_out = params
        if log_scale:
            return lambda x: np.where(x<0,
                                      np.log10(n_lim) + a_in * x/100,
                                      np.log10(n_lim) + a_out * x/100)
        else:
            return lambda x: np.where(x<0,
                                      n_lim * 10 ** (a_in * x/100),
                                      n_lim * 10 ** (a_out * x/100))
    else:
        raise NotImplementedError


def eval_params(params, loc=np.arange(-5,5.5,.5), log_scale=True):
    """
    Evaluate a profile defined by params on the values in loc
    """
    return call_profile(params, log_scale)(loc)


def _to_object_array(sequence):
    """Convert sequence to a 1-D NumPy array of object dtype.

    numpy.array constructor has a similar use but it's output
    is ambiguous. It can be 1-D NumPy array of object dtype if
    the input is a ragged array, but if the input is a list of
    equal length arrays, then the output is a 2D numpy.array.
    _to_object_array solves this ambiguity by guarantying that
    the output is a 1-D NumPy array of objects for any input.

    Code from scikit-learn.utils

    Parameters
    ----------
    sequence : array-like of shape (n_elements,)
        The sequence to be converted.

    Returns
    -------
    out : ndarray of shape (n_elements,), dtype=object
        The converted sequence into a 1-D NumPy array of object dtype.

    """
    out = np.empty(len(sequence), dtype=object)
    out[:] = sequence
    return out

def convert_score2error(score):
    """ Convert the score to realtive error.
    """
    z = np.pow(10, score)
    return 100 * np.abs(z - 1/z) / 2

def convert_error2score(error):
    """ Inverse function of convert_score2error for negative scores.
    """
    return np.log10(np.sqrt(error**2 + 10**4) - error ) - 2