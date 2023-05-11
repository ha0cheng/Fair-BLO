import cplex
from utils import *
from Alg_VCG import Mechanism_VCG

def Mechanism_Core_Quad_Zero(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare):
    MRC_total_utility, VCG_utility, Prob, Query_time = Compute_Core_MRC(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare)

    recover_bids(bid_prices, Winners.all_bids, Winners.all_prices)

    win_bids = Winners.win_bids
    winner_num = len(win_bids)



    qmat = [1.0 for _ in range(winner_num)]
    my_obj = [("u" + str(win_bids[i]), 0) for i in range(winner_num)]
    row = [["u" + str(win_bids[i]) for i in range(winner_num)],[1.0] * winner_num]

    ## set parameters for QP
    Prob.objective.set_quadratic(qmat)
    Prob.objective.set_linear(my_obj)
    Prob.linear_constraints.add(lin_expr=[row], senses='E', rhs=[MRC_total_utility])
    Prob.set_problem_type(cplex.Cplex.problem_type.MIQP)
    Prob.objective.set_sense(Prob.objective.sense.minimize)

    Prob.parameters.mip.tolerances.mipgap.set(float(0))
    Prob.solve()

    utility = Prob.solution.get_values()
    Utility = dict(zip(win_bids, utility))

    ##  compute the initial most block coalition
    truncate_bids(bid_information, bid_prices, bid_items, dummy_bids, Utility)
    block_Welfare, block_coalition = Winner_determination(bid_information, bid_prices, bid_items)
    Query_time += 1
    block_coalition = transform_bids(bid_information, bid_items, Winners, block_coalition)
    recover_bids(bid_prices, Winners.all_bids, Winners.all_prices)


    while (Welfare - sum(Utility.values()) < block_Welfare -Err):

        ## add a new constraint
        row = [[], []]

        for i in range(winner_num):
            if win_bids[i] in block_coalition:
                block_Welfare += Utility[win_bids[i]]
            else:
                row[0].append("u" + str(win_bids[i]))
                row[1].append(1.0)

        Prob.linear_constraints.add(lin_expr=[row], senses='L', rhs=[Welfare - block_Welfare])
        # Prob.write('test1.lp')
        ## solve the new LP and get a new solution according to the current constraint set
        Prob.solve()

        winner_utility = Prob.solution.get_values()
        Utility = dict(zip(win_bids, winner_utility))

        ## compute the next most block coalition
        truncate_bids(bid_information, bid_prices, bid_items, dummy_bids, Utility)
        block_Welfare, block_coalition = Winner_determination(bid_information, bid_prices, bid_items)
        Query_time +=1
        block_coalition = transform_bids(bid_information, bid_items, Winners, block_coalition)
        recover_bids(bid_prices, Winners.all_bids, Winners.all_prices)

    return list(Utility.values()), Query_time



def Compute_Core_MRC(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare):
    VCG_utility, Query_time = Mechanism_VCG(bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare)


    win_bids = Winners.win_bids
    winner_num = len(win_bids)


    ##  initial parameters
    my_obj = [1.0] * winner_num
    my_ub = VCG_utility
    my_lb = [0.0] * winner_num
    my_ctype = "C" * winner_num
    my_colnames = []
    for i in win_bids:
        my_colnames.append("u" + str(i))

    ##  set initial parameters for LP
    Prob = cplex.Cplex()
    Prob.set_results_stream(None)
    Prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype, names=my_colnames)
    Prob.objective.set_sense(Prob.objective.sense.maximize)
    Prob.parameters.mip.tolerances.mipgap.set(float(0))

    Utility = dict(zip(win_bids, VCG_utility))
    ##  compute the initial most block coalition
    truncate_bids(bid_information, bid_prices, bid_items, dummy_bids, Utility)
    block_Welfare, block_coalition = Winner_determination(bid_information, bid_prices, bid_items)
    Query_time += 1
    block_coalition = transform_bids(bid_information, bid_items, Winners, block_coalition)
    recover_bids(bid_prices, Winners.all_bids, Winners.all_prices)

    ## Main process of  Core Constraint Generation
    while (Welfare - sum(Utility.values()) < block_Welfare - Err):

        ## add a new constraint
        row = [[], []]

        for i in range(winner_num):
            if win_bids[i] in block_coalition:
                block_Welfare += Utility[win_bids[i]]
            else:
                row[0].append("u" + str(win_bids[i]))
                row[1].append(1.0)

        Prob.linear_constraints.add(lin_expr=[row], senses='L', rhs=[Welfare - block_Welfare])
        ## solve the new LP and get a new solution according to the current constraint set
        Prob.solve()
        # Prob.write('test1.lp')
        winner_utility = Prob.solution.get_values()
        Utility = dict(zip(win_bids, winner_utility))

        ## compute the next most block coalition
        truncate_bids(bid_information, bid_prices, bid_items, dummy_bids, Utility)
        block_Welfare, block_coalition = Winner_determination(bid_information, bid_prices, bid_items)
        Query_time +=1
        recover_bids(bid_prices, Winners.all_bids, Winners.all_prices)
        block_coalition = transform_bids(bid_information, bid_items, Winners, block_coalition)


    return sum(Utility.values()), VCG_utility, Prob, Query_time