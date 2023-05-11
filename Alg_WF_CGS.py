from utils import *


def Mechanism_Core_WF_CGS(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare):


    Active_winners = Winners.win_bids
    winner_num = len(Active_winners)
    MAX_price = max(bid_prices)

    Utility = dict(zip(Active_winners,[0]*winner_num))

    Query_time = 0
    while Active_winners:

        # find the minimum incremental utility
        Delta, Block_coalition, maxmin_Query_time = maxmin_search(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare, Active_winners, MAX_price, Utility)
        # update the winner set that is incremental
        for i in Active_winners:
            Utility[i] += Delta
        Active_winners = intersection(Active_winners,Block_coalition)
        Query_time += maxmin_Query_time



    return list(Utility.values()),Query_time

##
def maxmin_search(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare, Active_winners, MAX_price, Utility):
    '''
    Find the minimum increment for the bidder set
    :param S:
    :param MAXutility:
    :param dummy_winners:
    :param MaxSW:
    :param bid_price:
    :param bid_items:
    :param bid_information:
    :param dummy_bid:
    :return:
    '''

    ## remove the winner bids in Incremental_winners
    Query_time = 0
    Delta = MAX_price


    while True:

        Cur_utility = Utility.copy()
        for i in Active_winners:
            Cur_utility[i] += Delta

        truncate_bids(bid_information, bid_prices, bid_items, dummy_bids, Cur_utility)

        Block_welfare, Block_coalition = Winner_determination(bid_information, bid_prices, bid_items)
        Query_time +=1
        recover_bids(bid_prices, Winners.all_bids, Winners.all_prices)
        transformed_block_coalition = transform_bids(bid_information, bid_items, Winners, Block_coalition)
        if Welfare - sum(list(Cur_utility.values())) >= Block_welfare - Err:
            break
        else:
            fix_winner_num = len(diff(Active_winners, transformed_block_coalition))
            Delta -= (Block_welfare - (Welfare - sum(list(Cur_utility.values())))) /fix_winner_num
            Final_block_coalition = transformed_block_coalition


            if fix_winner_num == 1:
                break

   
    return Delta, Final_block_coalition,Query_time
