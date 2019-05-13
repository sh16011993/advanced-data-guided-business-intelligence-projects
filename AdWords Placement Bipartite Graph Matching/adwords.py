import pandas as pd
import numpy as np
import sys
import random
import math
#####################################################################################
# Setting seed
random.seed(0)

df = pd.read_csv('queries.txt', sep="\n", header=None)
queries = df[0].values.tolist()
original_queries = queries.copy()
bidder_input = pd.read_csv('bidder_dataset.csv')
query_bidders = dict()
query_bds_budget = dict()
bidder_budget_original = dict()
opt_revenue = 0
for i in range(0, len(bidder_input)):
    key = bidder_input.iloc[i]['Keyword']
    ad = bidder_input.iloc[i]['Advertiser']
    bidval = bidder_input.iloc[i]['Bid Value']
    budget = bidder_input.iloc[i]['Budget']
    # Finding opt_revenue
    if(not math.isnan(budget)):
        opt_revenue += budget
    l = [ad, bidval]
    if key in query_bidders:   
        val = query_bidders[key]
        val.append(l)
        query_bidders.update({key: val})
    else:
        query_bidders.update({key: [l]})
    l1 = [ad, bidval]
    if key in query_bds_budget:
        val = query_bds_budget[key]
        val.append(l1)
        query_bds_budget.update({key: val})
    else:
        query_bds_budget.update({key: [l1]})
    if ad not in bidder_budget_original:   
        bidder_budget_original.update({ad: budget})
for key, value in query_bds_budget.items():
    for lval in value:
        if(math.isnan(lval[1])):
            lval[1] = bidder_budget_original[lval[0]]
for key in query_bds_budget:
    val = query_bds_budget[key]
    val.sort(key = lambda x: x[0]) 
for key in query_bidders:
    val = query_bidders[key]
    val.sort(key = lambda x: x[0]) 
    val.sort(key = lambda x: x[1], reverse = True) 
    query_bidders[key] = val
########################################################################################
def greedyCR():
    # Finding the competitive ratio
    greedy_alg = 0
    for i in range(100):
        np.random.shuffle(queries)
        greedy_alg += greedy(bidder_budget_original.copy())
    avg_greedy_alg = greedy_alg/100
    greedy_cr = avg_greedy_alg/opt_revenue
    return(greedy_cr)

# Code for Greedy
def greedy(bidder_budget):
    # Finding revenue
    greedy_total_revenue = 0
    for query in queries:
        l = query_bidders[query]
        for val in l:
            if((bidder_budget[val[0]]-val[1]) >= 0):
                greedy_total_revenue += val[1]
                bidder_budget[val[0]] -= val[1]
                break
    return(greedy_total_revenue)
##########################################################################################
def balanceCR():
    # Finding the competitive ratio
    balance_alg = 0
    for i in range(100):
        np.random.shuffle(queries)
        balance_alg += balance(bidder_budget_original.copy())
    avg_balance_alg = balance_alg/100
    balance_cr = avg_balance_alg/opt_revenue
    return(balance_cr)

# Code for Balance
def balance(bidder_budget):
    balance_total_revenue = 0
    revenue = 0
    for query in queries:
        l = query_bds_budget[query]
        maxval = 0
        maxadindex = -1
        for val in l:
            if(bidder_budget[val[0]] > maxval):
                maxval = bidder_budget[val[0]]
                maxadindex = val[0]
                revenue = val[1]
        if(maxadindex != -1):
            balance_total_revenue += revenue
            bidder_budget.update({maxadindex: maxval-revenue})
    return(balance_total_revenue)
############################################################################################
def mssvCR():
    # Finding the competitive ratio
    mssv_alg = 0
    for i in range(100):
        np.random.shuffle(queries)
        mssv_alg += mssv(bidder_budget_original.copy())
    avg_mssv_alg = mssv_alg/100
    mssv_cr = avg_mssv_alg/opt_revenue
    return(mssv_cr)

# Code for MSSV
def mssv(bidder_budget):
    mssv_total_revenue = 0
    revenue = 0
    for query in queries:
        l = query_bds_budget[query]
        maxval = 0
        maxadindex = -1
        for val in l:
            x = (bidder_budget_original[val[0]] - bidder_budget[val[0]])/bidder_budget_original[val[0]]
            if((val[1]*(1-np.exp(x-1))) > maxval):
                maxval = val[1]*(1-np.exp(x-1))
                maxadindex = val[0]
                revenue = val[1]
        if(maxadindex != -1):
            mssv_total_revenue += revenue
            bidder_budget.update({maxadindex: bidder_budget[maxadindex]-revenue})
    return(mssv_total_revenue)
##############################################################################################
def main():
	argument = sys.argv[1]
	if(argument == 'greedy'):		
		# Calling Greedy
		print("{:.1f}".format(greedy(bidder_budget_original.copy())))
		print("{:.2f}".format(greedyCR()))
	elif(argument == 'balance'):
		# Calling Balance
		queries = original_queries
		print("{:.1f}".format(balance(bidder_budget_original.copy())))
		print("{:.2f}".format(balanceCR()))
	elif(argument == 'msvv'):
		# Calling MSSV
		queries = original_queries
		print(float(round(mssv(bidder_budget_original.copy()))))
		#print("{:.0f}".format(mssv(bidder_budget_original.copy())))
		print("{:.2f}".format(mssvCR()))
##############################################################################################
if __name__=="__main__":
    main()