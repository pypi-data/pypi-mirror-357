import numpy as np
from mils_de.geometry.params import _is_parameter_key, get_sensors_idx

def paired_constraints(a1, R1, Z1, a2, R2, Z2, eps=0.0005, suffix=''):
    '''
    Return a dictionary with the value of the constraints on pairs of sensors
    '''
    paired_constr = {
        f"radial_gap{suffix}":        radial_gap(a1, R1, a2, R2) - eps,
        f"vertical_gap{suffix}":      vertical_gap(a1, Z1, a2, Z2) - eps,
        f"angle_gap{suffix}":         a2 - a1 - eps,
        f"avoid_reflections{suffix}": avoid_reflections(a1, a2, R1, R2, Z1, Z2) - eps,
    }
    return paired_constr

def constraints(a0=0, R0=0, Z0=0, eps=0.0005, **kwargs):
    '''
    Return a dictionary containing the values of the sensor constraints (less than
    `eps` is valid) for all triple a, R, Z found in `kwargs`. Sensors are paired
    following the order of their indices.
    '''
    constraints_dict = {}
    for idx in sorted(get_sensors_idx(kwargs)):
        # get the sensor parameters
        try:
            a = kwargs.pop(f"a{idx:d}")
            R = kwargs.pop(f"R{idx:d}")
            Z = kwargs.pop(f"Z{idx:d}")
        except Exception as e:
            print(f"Wrong parameters for sensor {idx}")
            print(f"one of a{idx:d} R{idx:d} Z{idx:d} not in {kwargs}")
            raise e

        if not constraints_dict:
            # If first sensor
            constraints_dict = {
                f"min_dist_{idx}": -R**2 - 2*R*1.0402 - Z**2 - Z*0.4291 - eps,
                f"shift_limiter_{idx}": shift_limiter(R, Z) - eps
            }
        else:
            # consider paired constraints with previous sensor
            constraints_dict.update(
                {f"shift_limiter_{idx}": shift_limiter(R, Z) - eps} |
                paired_constraints(pv_a, pv_R, pv_Z, a, R, Z, eps=eps,
                                   suffix=f"_{pv_idx:d}{idx:d}")
            )
        pv_a, pv_R, pv_Z, pv_idx = a, R, Z, idx
    return constraints_dict

def optuna_constrain_fn(trial):
    # TODO: Why reverse order?
    return list(constraints(**trial.params).values())[::-1]

def shift_limiter(R, Z):
    """
     all receivers are shifted from the closest to the limiter position by maximum 0.1 m
    """
    return (R + 1.0402)**2 + (Z + 0.21455)**2 - (1.0621 + 0.1)**2

def gamma_1(a, b):
    """
    Radial gap between recievers: 0.016 is the half of the length of the antenna
    edge and 0.005 is the minimum distance between antennas’ closest edges.
    """
    return 0.016*np.cos(-a*np.pi/180) + 0.016*np.cos(-b*np.pi/180) + 0.005*np.cos((-a-b)/2*np.pi/180)

def gamma_2(a, b):
    """
    Vertical gap between recievers: 0.016 is the half of the length of the antenna
    edge and 0.005 is the minimum distance between antennas’ closest edges.
    """
    return 0.016*np.sin(-a*np.pi/180) + 0.016*np.sin(-b*np.pi/180) + 0.005*np.sin((-a-b)/2*np.pi/180)

def radial_gap(a1, R1, a2, R2):
    """
    Radial gap between recievers
    """
    return -R2 + R1 + gamma_1(a1, a2)

def vertical_gap(a1, Z1, a2, Z2):
    """
    Vertical gap between recievers
    """
    return Z2 - Z1 + gamma_2(a1, a2)

def avoid_reflections(a1, a2, R1, R2, Z1, Z2, eps=1e-8):
    """
    Avoid strong reflections between receivers
    """
    return np.abs(np.arctan((Z1-Z2)/(R2-R1+eps))*180/np.pi + (a1+a2)/2) - 15

def eval_constraints(x, eps=1e-5):
    '''
    Evaluate the constraints on a pandas series
    TODO: Remove this. Outdated procedure:
    ```
    df_const = pd.DataFrame(geom_df.apply(eval_constraints, axis=1, result_type='expand'))
    ```
    the above has been replaced by its vectorised version:
    ```
    df_const = pd.DataFrame(constraints(**geom_df))
    ```
    '''
    _d = x.to_dict()
    if x.index.nlevels == 1:
        d = {key: _d.get(key) for key in _d.keys() if _is_parameter_key(key)}
    elif x.index.nlevels == 2:
        # Flat parameters keys
        flat_tuple = lambda key_tuple: "".join([str(k) for k in key_tuple])
        d = {flat_tuple(k): v for k, v in _d.items() if k[0] in ['a', 'R', 'Z']}
    else:
        raise
    constr = constraints(**d)
    return constr | {'valid': np.all(np.array(list(constr.values()))<=eps)}