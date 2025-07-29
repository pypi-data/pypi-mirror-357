import re

param_pattern = r'^[aRZ][0-9]+$'

def get_param_names(num_sensors=3, sender=True):
    '''
    Return a ordered list of the parameters for a geometry
    with `num_sensors` receivers.
    '''
    start_id = 0 if sender else 1
    ids = [str(i) for i in range(start_id, num_sensors+1)]
    _param_names = []
    for p in ['a', 'R', 'Z']:
        _param_names += [p + id for id in ids]
    return _param_names

def get_params_sensor(i):
    '''
    return the name of the parameters for sensor `i`
    '''
    return [f"a{i:d}",f"R{i:d}",f"Z{i:d}"]

def _is_parameter_key(key):
    '''
    Check if `key` is a parameter key.
    '''
    return bool(re.match(param_pattern, key))

def get_sensors_idx(dictionary):
    '''
    Return a list of the sensor indices found within the keys of
    `dictionary`. If no sensor parameter is found return empty list
    '''
    # Find key with lowest sensor index, if any
    rex = re.compile(r'[a-zA-Z](\d+)$')
    sensors = []
    for key in dictionary:
        # Check if the key matches the pattern
        match = rex.match(key)
        # If the key matches the pattern, update the list
        if match:
            sensor_idx  = int(match.group(1))
            if sensor_idx not in sensors: sensors.append(sensor_idx)
    return sensors