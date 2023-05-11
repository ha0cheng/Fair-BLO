from utils import *


def Mechanism_Core_WF_CGS_CR(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare):
    global Constraint_memory
    Constraint_memory = []
    Active_winners = Winners.win_bids
    winner_num = len(Active_winners)
    Delta = 0
    Utility = dict(zip(Active_winners,[0]*winner_num))

    Query_time = 0
    while Active_winners:
        # update the constraint memory and the next initial Delta
        # Constraint_memory,Init_Delta = Constraint_update(Active_winners, Delta, max(bid_prices))

        # find the minimum incremental utility
        Delta, Fix_winners, maxmin_Query_time = maxmin_search(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare, Active_winners, Utility,Delta,max(bid_prices))

        # update the utility and next active winner set
        for i in Active_winners:
            Utility[i] += Delta

        Active_winners = diff(Active_winners,Fix_winners)
        Query_time += maxmin_Query_time

    return list(Utility.values()), Query_time







def maxmin_search(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare, Active_winners, Utility,last_Delta, maxPrice):

    ## remove the winner bids in Incremental_winners
    global Constraint_memory
    Query_time = 0
    Delta = maxPrice
    fix_winners = []
    R_list = []

    for fix_bidders, delta in Constraint_memory:
        common_bidders = intersection(fix_bidders, Active_winners)
        if common_bidders:
            cur = (delta - last_Delta) * len(fix_bidders) / len(common_bidders)
            if  Delta > cur:
                Delta = cur
                fix_winners = common_bidders
            R_list.append((common_bidders,cur))
    Constraint_memory = R_list.copy()




    while True:
        Cur_utility = Utility.copy()
        for i in Active_winners:
            Cur_utility[i] += Delta

        truncate_bids(bid_information, bid_prices, bid_items, dummy_bids, Cur_utility)
        Block_welfare, Block_coalition = Winner_determination(bid_information, bid_prices, bid_items)
        Query_time += 1
        recover_bids(bid_prices, Winners.all_bids, Winners.all_prices)

        if Welfare - sum(list(Cur_utility.values())) >= Block_welfare - Err:
            break
        else:
            transformed_block_coalition = transform_bids(bid_information, bid_items, Winners, Block_coalition)
            fix_winners = diff(Active_winners, transformed_block_coalition)
            Delta -= (Block_welfare - (Welfare - sum(list(Cur_utility.values())))) / len(fix_winners)
            Constraint_memory.append((fix_winners, Delta))

            if len(fix_winners) == 1:
                break

    return Delta, fix_winners, Query_time



def Constraint_update(Constraint_memory,active_bidders,cur_Delta,maxPrice):
    Init_Delta = ([],maxPrice)
    R_list = []
    for fix_bidders, Delta in Constraint_memory:
        common_bidders = intersection(fix_bidders, active_bidders)
        if common_bidders:
            cur = (Delta - cur_Delta) * len(fix_bidders) / len(common_bidders)
            if Init_Delta[1] > cur:
                Init_Delta = (common_bidders, cur)
            R_list.append((common_bidders,cur))

    return R_list, Init_Delta
