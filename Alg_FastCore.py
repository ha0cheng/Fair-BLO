from utils import *

def Mechanism_Core_FastCore(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare,Epsilon):

    Active_winners = Winners.win_bids
    winner_num = len(Active_winners)
    MAX_price = max(bid_prices)
    MIN_price = min(bid_prices)

    Utility = dict(zip(Active_winners,[0]*winner_num))

    Query_time = 0
    while Active_winners:

        Upper_utility, Lower_utility,Core_Query_time = Core_search(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare,
                                                   Active_winners, MAX_price,MIN_price, Utility,Epsilon)
        Query_time += Core_Query_time
        Utility = Lower_utility.copy()

        truncate_bids(bid_information, bid_prices, bid_items, dummy_bids, Upper_utility)
        Block_Welfare, Block_coalition = Winner_determination(bid_information, bid_prices, bid_items)
        Query_time += 1
        Block_coalition = transform_bids(bid_information, bid_items, Winners, Block_coalition)
        recover_bids(bid_prices, Winners.all_bids, Winners.all_prices)
        Active_winners = intersection(Active_winners, Block_coalition)



    return list(Utility.values()), Query_time
##
def Core_search(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare, Active_winners, MAX_price,MIN_price, Utility,Epsilon):
    Query_time = 0
    Delta_l = 0
    Delta_h = MAX_price-MIN_price
    while Delta_h - Delta_l > Epsilon*(MAX_price-MIN_price)/len(Active_winners):
        Cur_utility = Utility.copy()
        Delta = (Delta_l + Delta_h)/2
        for i in Active_winners:
            Cur_utility[i] += Delta
        Cur_utility0 = Welfare - sum(list(Cur_utility.values()))

        truncate_bids(bid_information, bid_prices, bid_items, dummy_bids, Cur_utility)
        Block_welfare, Block_coalition = Winner_determination(bid_information, bid_prices, bid_items)
        Query_time +=1

        recover_bids(bid_prices, Winners.all_bids, Winners.all_prices)

        if Cur_utility0 >= Block_welfare-Err:
            Delta_l = Delta
        else:
            Delta_h = Delta


    Upper_utility = Utility.copy()
    Lower_utility = Utility.copy()
    for i in Active_winners:
        Upper_utility[i] += Delta_h
        Lower_utility[i] += Delta_l
    return Upper_utility, Lower_utility, Query_time




