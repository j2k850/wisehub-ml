#!/usr/bin/env python2

import datetime
import os, random
import pandas as pd
from configuration import *

def get_transaction_ids(length, tx_type = 'W'):
    """
    ids are missing from the data. Generates random txids which are then appended to the dataset
    Parameters:
    ___________
        tx_type: withdrawal or deposit

    Returns:
    ___________
        randomly selected tx_id
    """
    if tx_type == 'W':
        return [random.choice(withdrawal_tx_ids) for _ in range(length)]
    return [random.choice(deposit_tx_ids) for _ in range(length)]

def get_transaction_file(base='../fake_data/output/', append_tx_ids = lambda x:x):
    """
    reads the transaction file of each user from fake_data/output/ directory and returns a pandas dataframe

    Paramters:
    ___________
        None

    Returns:
    ___________
        DataFrame of a transaction csv file
    """

    for dirname in os.listdir(base):
        if dirname == '.git':
            continue
        for _,_,filenames in os.walk(base + dirname):
            for fn in filenames:
                print (base + dirname + '/' + fn)
                yield simplify_tx_data(append_tx_ids(pd.read_csv(base + dirname + '/' + fn, decimal=".")))

def append_tx_ids(tnx):
    """
    appends tx_ids to the tx dataframe

    Parameters:
    ____________
        tnx: original dataframe output from fake_data.py

    Returns:
    ____________
        modified dataframe with tx_ids
    """
    tnx['tx_id'] = 0
    tnx.loc[tnx.description == 'Deposit','tx_id'] = get_transaction_ids(tnx[tnx.description == 'Deposit'].shape[0],'D')
    tnx.loc[tnx.description == 'Withdrawal','tx_id'] = get_transaction_ids(tnx[tnx.description == 'Withdrawal'].shape[0],'W')
    return tnx

def simplify_tx_data(tnx):
    """
    simplifies the data by making a separate column in the dataframe which contains the signed number
    this number is the size of transaction

    Paramters:
    ___________
        tnx: dataframe of transaction

    Returns:
    __________
        dataframe with an additional column of signed transaction size
    """
    tnx['tx_size'] = 0
    tnx.loc[tnx.deposits == 0,'tx_size'] = -1*tnx[tnx.deposits == 0].withdrawals
    tnx.loc[tnx.withdrawals == 0,'tx_size'] = tnx[tnx.withdrawals == 0].deposits
    tnx['date'] = pd.to_datetime(tnx['date'])
    return tnx
