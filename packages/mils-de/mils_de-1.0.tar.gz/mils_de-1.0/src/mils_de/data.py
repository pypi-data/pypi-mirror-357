# This module contains common routine for managing 
# and trasforming simulation data in DataFrames
import os
import numpy as np
import pandas as pd

from functools import partial
from mils_de.utils import eval_params

# DATAFRAME CREATION
default_domain = np.arange(-5,5.5,.5)
large_domain   = np.arange(-7,5.5,.5)
small_domain   = np.arange(-2,2.5,1)
smaller_domain = np.arange(-1,1.5,.5)
left_domain    = np.arange(-4,.5,1)
right_domain   = np.arange(0,4.5,1)
center_domain  = np.arange(-4,4.5,2)

ne_params_cols = pd.MultiIndex.from_product([["n_lim", "a_in", "a_out"],[None]],
                                            names=['name', 'sensor'])

def columns_names(num_sensors=3):
    P_phi_cols   = pd.MultiIndex.from_product([['phi', 'P'], np.arange(num_sensors)],
                                              names=['name', 'sensor'])
    return ne_params_cols.union(P_phi_cols, sort=False)

def columns_true(domain=default_domain):
    return pd.MultiIndex.from_tuples([['true', r] for r in domain])

def columns_pred(domain=default_domain):
    return pd.MultiIndex.from_tuples([['pred', r] for r in domain])

def eval_ne_profiles(df, domain=default_domain):
    true_cols = columns_true(domain)
    # Evaluate profiles
    eval_func = partial(eval_params, loc=domain, log_scale=True)
    df[true_cols] = df[ne_params_cols].apply(eval_func, axis=1, result_type='expand')
    return df

def P_log(df):
    """
    Check if power columns in df are posite and apply log.
    """
    P_cols = df.columns.get_level_values(0)=='P'
    mask = (df.loc[:, P_cols]<=0).any(axis=1)
    if np.sum(mask) > 0:
        print(f"Found {np.sum(mask)} simulations out of {len(mask)}"+\
              f"with non positive power values.\nIgnoring them.")
        df = df[~mask]
    df.loc[:,P_cols] = df.loc[:,P_cols].map(np.log10)
    return df

def apply_PBC(df, delta_phi=90):
    '''
    If needed, repeat values in a delta_phi stripe at phi boundaries.
    Skip if (min(phi) - max(phi)) % 360 < delta_phi
    '''
    sensors = df.xs(key='phi', axis=1, level=0).columns
    for s in sensors:
        phi_s = df.loc[:,('phi',s)]
        min_phi = np.min(phi_s)
        max_phi = np.max(phi_s)
        unroll = (max_phi - min_phi)//360 + 1
        # unroll should be always 1
        if (min_phi-max_phi)%360 < delta_phi:
            mask_low = (phi_s < (min_phi + delta_phi))
            mask_upp = (phi_s > (max_phi - delta_phi))
            df_low = df[mask_low].copy()
            df_low.loc[:,('phi',s)] += 360 * unroll
            df_upp = df[mask_upp].copy()
            df_upp.loc[:,('phi',s)] -= 360 * unroll
            df = pd.concat([df, df_upp, df_low],ignore_index=True)
    return df

def _read_dataset_csv(geom_dir, dataset, v2, *args, **kwargs):
    '''
    Read the csv in `geom_dir` for a specific `dataset` ('train', 'test', 'val')
    concatenating with v2 if `v2` is `True`.
    '''
    _df = pd.read_csv(f"{geom_dir}/{dataset}.csv",  *args, **kwargs)
    if v2:
        _df2 = pd.read_csv(f"{geom_dir}/{dataset}_2.csv",  *args, **kwargs)
        _df  = pd.concat([_df, _df2], ignore_index=True)
    return _df


def load_geom_dataframes(geom_id, results_dir, v2=False):
    '''
    Returns the train, val, test dataframes for `geom_id` reading data from
    `results_dir/geom-id`. If path not found returns `None`.
    '''
    col_names = columns_names(num_sensors=3)
    geom_dir = os.path.join(results_dir, str(geom_id))
    # Check if simulated data is available
    if os.path.exists(geom_dir) and os.path.isdir(geom_dir):
        # Read data
        train_df = _read_dataset_csv(geom_dir, "train", v2, header=None, names=col_names)
        val_df   = _read_dataset_csv(geom_dir, "val",   v2, header=None, names=col_names)
        test_df  = _read_dataset_csv(geom_dir, "test",  v2, header=None, names=col_names)
        return train_df, val_df, test_df
    else:
        return None