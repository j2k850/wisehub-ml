#!/usr/bin/env python2
from basic_fns import *
from fns import *
import json

## Fake data
# tx = get_transaction_file(base='../fake_data/output/', append_tx_ids=append_tx_ids)

def fn(x):
    x['tx_id'] = x['description']
    return x

tx = get_transaction_file(base='../fake_data/output/', append_tx_ids=fn)


# Print results
tnx = tx.next()
print ("\n\nAutosavings recommendation: ", recommend_autosavings_budget(tnx))
print ("\n\nPredicted Overdraft likelihood: ", predict_overdraft_likelihood(tnx))
print ("\n\ntag ids: \n", json.dumps(tag_tx_ids(tnx), indent=4))

coefficients, norm_mse = net_cash_flow(tnx)
print ("\n\nSimple Cash_flow prediction: \n")
print('Slope ' + str(coefficients[0]))
print('Normalized MSE: ' + str(norm_mse))
print('Trend: ' + str(coefficients[0]) + 'x ' + str(coefficients[1]))
