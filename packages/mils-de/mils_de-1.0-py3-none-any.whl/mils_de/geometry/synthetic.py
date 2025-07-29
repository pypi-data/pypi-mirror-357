"""
Synthetic geometries are obtained by permutation of sensors from simulated geometries.
A permutation is considered valid if it satisfies all the constraints.
"""
import os
import numpy as np
import pandas as pd
import itertools
from mils_de.geometry.constraints import constraints
from mils_de.geometry.params import get_param_names, get_sensors_idx
from mils_de.data import columns_names, _read_dataset_csv

rec_prefix='rec'

def get_rec_names(num_sensors):
    return [f'{rec_prefix}{i:d}' for i in range(1,num_sensors+1)]

def synth_geom_id(paired_ids):
    synth_geom_id = ""
    for g, idx in paired_ids:
        synth_geom_id += f"{g:03d}{idx:02d}"
    return int(synth_geom_id)

def get_rec_pairs(synth_id):
    paired_ids = []
    synth_id = f"{synth_id}"
    while synth_id:
        paired_id = synth_id[-5:]
        paired_ids.insert(0, (int(paired_id[:-2]),int(paired_id[-2:])))
        synth_id = synth_id[:-5]
    return paired_ids

def df_permutations(df, N=2, index_prefix=''):
    '''
    Return a DataFrame with rows permutation of `N` rows of `df`.
    `index_prefix` is prepended to the columns containing the original indices.
    E.g.:
    ```
    df = pd.DataFrame({'Name': ['John', 'Anna', 'Peter'],'Age': [28, 24, 35]})
    df_permutations(df, N=2)
       1  2  Name1  Age1  Name2  Age2
    0  0  1   John    28   Anna    24
    1  0  2   John    28  Peter    35
    2  1  0   Anna    24   John    28
    3  1  2   Anna    24  Peter    35
    4  2  0  Peter    35   John    28
    5  2  1  Peter    35   Anna    24
    '''
    assert N >= 1
    col_names = df.columns
    idx_names = [f"{index_prefix}{d}" for d in range(1, N+1)]
    permutations = list(itertools.permutations(df.index, N))
    new_df = pd.DataFrame(permutations, columns=idx_names)
    # new_df = new_df.merge(df, left_on=idx_names.pop(0), right_index=True, suffixes=('1', '2'))                         
    for i, idx in enumerate(idx_names, start=1):
        new_df = new_df.merge(df, left_on=idx, right_index=True, suffixes=('', f"{i:d}"))
    new_df = new_df.rename(columns=lambda col: col+'1' if col in col_names else col)
    return new_df

def valid_sensors_permutations(df, synth_sensors=2, add_sender=False, synth_index=False, verbose=False):
    '''
    Take a DF with a list of sensors, permute them and keep only the permutations satisfying the constraints.
    NOTE: This is implementation is not efficient! Memory and compute grow as `len(df)^synth_sensors`.
    '''
    assert synth_sensors >= 1
    rec_cols=get_rec_names(synth_sensors)
    synth_df = df_permutations(df, N=synth_sensors, index_prefix=rec_prefix)

    param_cols = get_param_names(synth_sensors, sender=add_sender)
    if add_sender:
        synth_df[['a0','R0','Z0']] = 0

    synth_df = synth_df[rec_cols+param_cols]

    if synth_index:
        synth_df.index = synth_df.apply(lambda x: synth_geom_id(x[rec_cols]), axis=1)
        synth_df = synth_df.drop(columns=rec_cols).sort_index()

    valid_mask = (pd.DataFrame(constraints(**synth_df)) <= 0).all(axis=1)
    if verbose:
        print(f"Valid permutations of {synth_sensors} sensors out of {len(df)}: {np.sum(valid_mask)}/{len(valid_mask)}")
    return synth_df.loc[valid_mask]

def fast_valid_permutations(df, synth_sensors=2, add_sender=False, synth_index=False, verbose=False):
    '''
    Take a DF with a list of sensors, permute them and keep only the permutations satisfying the constraints.
    Check valid permutations from pairs of sensors.
    NOTE: Memory and compute grow slower than `synth_sensors * len(df)^2`.
    '''
    assert synth_sensors >= 1
    valid_pairs = valid_sensors_permutations(df, min(2, synth_sensors), synth_index=False, add_sender=add_sender, verbose=True)
    synth_df = valid_pairs.copy()
    for i in range(2,synth_sensors):
        synth_df = synth_df.merge(valid_pairs, left_on=f"{rec_prefix}{i}", right_on=f"{rec_prefix}1", suffixes=('', f"_R"))
        # rm duplicated columns
        synth_df = synth_df.drop(columns=[col for col in synth_df.columns if ("0_R" in col or "1_R" in col)])
        # rename 
        synth_df.rename(columns=lambda x: x[:-3]+f"{i+1}" if "2_R" in x else x, inplace=True)
        if verbose:
            print(f"Valid permutations of {i} pairs of sensors: {len(synth_df)}")

    rec_cols = get_rec_names(synth_sensors)
    param_cols = get_param_names(synth_sensors, sender=add_sender)
    synth_df = synth_df[rec_cols+param_cols]

    if synth_index:
        synth_df.index = synth_df.apply(lambda x: synth_geom_id(x[rec_cols]), axis=1)
        synth_df = synth_df.drop(columns=rec_cols).sort_index()
    return synth_df

def load_synth_dataframes(geom_id, results_dir, v2=False):
    '''
    Returns the train, val, test dataframes for a synthetic geometry merging
    the tables in `results_dir` from the corresponding simulated geometries.
    '''
    col_names = columns_names(num_sensors=3)
    paired_ids = get_rec_pairs(geom_id)

    # Read densities params
    _tmp_dir = os.path.join(results_dir, str(paired_ids[0][0]))
    train_df = _read_dataset_csv(_tmp_dir,"train", v2, header=None, names=col_names, usecols=[0,1,2])
    val_df   = _read_dataset_csv(_tmp_dir,"val",   v2, header=None, names=col_names, usecols=[0,1,2])
    test_df  = _read_dataset_csv(_tmp_dir,"test",  v2, header=None, names=col_names, usecols=[0,1,2])
    # load and concatenate phi and P for each sensor
    for j, (geom, sens) in enumerate(paired_ids):
        _tmp_dir = os.path.join(results_dir, str(geom))
        _cols  = [2+sens, 5+sens]
        _names = pd.MultiIndex.from_tuples([('phi', j),('P', j)])
        train_se = _read_dataset_csv(_tmp_dir,"train", v2, header=None, names=_names, usecols=_cols)
        val_se   = _read_dataset_csv(_tmp_dir,"val",   v2, header=None, names=_names, usecols=_cols)
        test_se  = _read_dataset_csv(_tmp_dir,"test",  v2, header=None, names=_names, usecols=_cols)
        train_df = pd.concat([train_df, train_se], axis=1)
        val_df   = pd.concat([val_df, val_se], axis=1)
        test_df  = pd.concat([test_df, test_se], axis=1)

    # Sort the columns as usual
    ordered_cols = columns_names(num_sensors=len(paired_ids))
    train_df = train_df[ordered_cols]
    val_df   = val_df[ordered_cols]
    test_df  = test_df[ordered_cols]

    return train_df, val_df, test_df