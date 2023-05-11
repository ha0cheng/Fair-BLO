from utils import *


def Mechanism_VCG(bid_information,bid_prices, bid_items, dummy_bids, Winners, Welfare):
    VCG_utility = []
    Query_time = 0
    for i in Winners.win_bids:
        temp = {}
        if bid_items[i][-1] >= bid_information['goods']:
            for j in dummy_bids[bid_items[i][-1]]:
                temp[j] = bid_prices[j]
                bid_prices[j] =-1
        else:
            temp[i] = bid_prices[i]
            bid_prices[i] = -1

        new_wefare, new_winners = Winner_determination(bid_information, bid_prices, bid_items)
        Query_time +=1

        for j in temp.keys():
            bid_prices[j] = temp[j]

        VCG_utility.append(Welfare - new_wefare)

    return VCG_utility, Query_time