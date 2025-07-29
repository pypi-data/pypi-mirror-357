import numpy as np
import optuna


base_distributions = {
    "a": optuna.distributions.FloatDistribution(-60,0),
    "R": optuna.distributions.FloatDistribution(-0.0116,0.1218),
    "Z": optuna.distributions.FloatDistribution(-.2,.05),
}

def get_params_distributions(num_sensors=3):
    # emitter
    _d = {
        "a0": optuna.distributions.FloatDistribution(0,0),
        "R0": optuna.distributions.FloatDistribution(0,0),
        "Z0": optuna.distributions.FloatDistribution(0,0),
    }
    # Recievers
    for i in range(1, num_sensors+1):
        for p in ['a', 'R', 'Z']:
            _d[p+f"{i:d}"] = base_distributions[p]
    return _d
