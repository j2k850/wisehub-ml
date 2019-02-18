#!/bin/env/python2
from basic_fns import *
import configuration
import numpy as np

def tag_tx_ids(tx):
    """
    TRANSACTION TAGGING
    tag the tx_ids in recurrent and non recurrent

    Parameters:
    ____________
        tx: transaction dataframe

    Returns:
    ___________
        a dictionary of tx_ids with
            if there are more than 2 obs:  their classifactions
            else: NA
    """

    tags  = {}
    unique_tx_id = set(tx.tx_id)
    for _id in unique_tx_id:
        size_recurrent, time_recurrent = False, False
        data_series = tx.loc[tx.tx_id == _id, ['date', 'tx_size']]
        if data_series.shape[0] < 3:
            tags[_id] = 'NA'
            continue

        size_mean = data_series.tx_size.mean()
        size_std = data_series.tx_size.std()

        time_gaps =  pd.Series(list(data_series.date.iloc[1:])) - pd.Series(list(data_series.date.iloc[:-1]))
        time_gaps  = time_gaps.astype('timedelta64[D]')
        time_gaps_mean = time_gaps.mean()
        time_gaps_std = time_gaps.std()

        if size_std < configuration.size_recurrent_threshold:
            size_recurrent = True

        if time_gaps_std < configuration.time_recurrent_threshold:
            time_recurrent = True

        tags[_id] = {
            'size_mean' : size_mean,
            'size_variance' : size_std,
            'time_mean' : time_gaps_mean,
            'time_std' : time_gaps_std,
            'recurrent': {
                'size': size_recurrent,
                'time': time_recurrent,
                'absolute': size_recurrent and time_recurrent,
                'not_recurrent': not size_recurrent and not time_recurrent
            }
        }

    return tags


def predict_overdraft_likelihood(tx):
    """
    OVERDRAFT PREDICTION
    returns the likelihood of the customer overdrawing from the bank account

    Parameters:
    ___________
        tx

    Returns:
    __________
        likelihood number between 0 and 1
    """
    remaining_balance_post_withdrawal = tx[tx.tx_size < 0].balance - tx[tx.tx_size < 0].withdrawals
    max_withdrawal = -1 * min(tx[tx.tx_size < 0].tx_size)
    return 1 - 1.0 * (sum(remaining_balance_post_withdrawal >= \
                    configuration.overdraft_safety_factor *  max_withdrawal)/tx[tx.tx_size < 0].shape[0])

def recommend_autosavings_budget(tx):
    """
    AUTOSAVINGS RECOMMENDATION
    returns a number suggesting the amount that should be put in savings account without affecting overdraft likelihood

    Parameters:
    ___________
        tx

    Returns:
    __________
        number
    """
    remaining_balance_post_withdrawal = tx[tx.tx_size < 0].balance - tx[tx.tx_size < 0].withdrawals
    max_withdrawal = -1 * min(tx[tx.tx_size < 0].tx_size)

    return min(remaining_balance_post_withdrawal - configuration.overdraft_safety_factor *  max_withdrawal)

def net_cash_flow(tx):
    """
    CASHFLOW Predictor
    returns a df of monthly netcash flows

    Parameters:
    ___________
        tx

    Returns:
    __________
       df
    """
    data_list =[]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    tx['month'] = tx['date'].apply(lambda x:x.strftime('%b'))

    for m in months:
        total_income = tx[tx.month == m].deposits.sum()
        total_expenses = tx[tx.month == m].withdrawals.sum()
        net_cash_flow = total_income - total_expenses
        data = {}
        data['month'] = m
        data['total_income'] = total_income
        data['total_expenses'] = total_expenses
        data['net_cash_flow'] = net_cash_flow
        data_list.append(data)

    cash_flows = pd.DataFrame(data_list)
    net_cash_flows = cash_flows.filter(items=['month', 'net_cash_flow'])

    coefficients, residuals, _, _, _ = np.polyfit(range(len(net_cash_flows.index)),net_cash_flows.net_cash_flow,1,full=True)

    mse = residuals[0]/(len(net_cash_flows.index))
    nrmse = np.sqrt(mse)/(net_cash_flows.net_cash_flow.max().max() - net_cash_flows.net_cash_flow.min().min())

    return coefficients, nrmse
