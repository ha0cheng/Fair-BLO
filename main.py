from inspect import trace
from utils import *
import time
import argparse
import csv
import os
import numpy as np
import traceback
from tqdm import tqdm
from Alg_VCG import Mechanism_VCG
from Alg_MRC import Mechanism_Core_MRC
from Alg_MRC_VCG import Mechanism_Core_Quad_VCG
from Alg_MRC_Zero import Mechanism_Core_Quad_Zero
from Alg_FastCore import Mechanism_Core_FastCore
from Alg_WF_CGS import Mechanism_Core_WF_CGS
from Alg_WF_CGS_CR import Mechanism_Core_WF_CGS_CR


func_dict = {'VCG':Mechanism_VCG,
             "MRC": Mechanism_Core_MRC,
             "MRC-VCG":Mechanism_Core_Quad_VCG,
             'MRC-Zero':Mechanism_Core_Quad_Zero,
             "FastCore": Mechanism_Core_FastCore,
             "WF-CGS":Mechanism_Core_WF_CGS,
             "WF-CGS-CR":Mechanism_Core_WF_CGS_CR,            
             }

class Mechanism:
    def __init__(self):
        self.utility = []
        self.total_utility = []
        self.revenue = []
        self.run_time = []
        self.query_time = []
        self.std = []
        self.max_min_diff = []
        self.zero_num = []


def run(Mechanisms_dict,index):
    for m in Mechanisms_dict:
        print(m)
        if m == 'FastCore':
            t1 = time.time()
            utility, query_time = func_dict[m](bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare,args.Epsilon)
            t2 = time.time()
        else:
            t1 = time.time()
            utility, query_time = func_dict[m](bid_information, bid_prices, bid_items, dummy_bids, Winners, Welfare)
            t2 = time.time()
        total_utility = sum(utility)
        revenue = Welfare - total_utility
        Mechanisms_dict[m].utility.append(utility)
        Mechanisms_dict[m].total_utility.append(total_utility)
        Mechanisms_dict[m].revenue.append(revenue)
        Mechanisms_dict[m].run_time.append(t2-t1)
        Mechanisms_dict[m].query_time.append(query_time)
        Mechanisms_dict[m].std.append(np.std(utility))
        Mechanisms_dict[m].max_min_diff.append(max(utility)-min(utility))
        Mechanisms_dict[m].zero_num.append(sum([1 for i in utility if i<Err]))

        if index == 0:
            st = 'w'
        else:
            st = 'a'
        if m== 'FastCore':
            p = open(path + '{}_{}.csv'.format(m,args.Epsilon), st, newline='')
        else:
            p = open(path+'{}.csv'.format(m),st,newline='')
        writer_p = csv.writer(p)
        if index==0:
            writer_p.writerow(['instance','total_utility','revenue','query_time','run_time','std','max_min_diff','utility'])
        
        writer_p.writerow([index,Mechanisms_dict[m].total_utility[-1],Mechanisms_dict[m].revenue[-1],
                            Mechanisms_dict[m].query_time[-1],Mechanisms_dict[m].run_time[-1],
                            Mechanisms_dict[m].std[-1],Mechanisms_dict[m].max_min_diff[-1]]+Mechanisms_dict[m].utility[-1]
                            )
        p.close()





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hyperparams')
    parser.add_argument('--mechanism', type=str, default='all',
                        help='mechanism: VCG|MRC|MRC-VCG|MRC-Zero|FastCore|WF-CGS|WF-CGS-CR')
    parser.add_argument('--distribution', type=str, default='all',
                        help='distribution type: all|arbitrary|L4|matching|paths|regions|scheduling')
    parser.add_argument('--goods', type=int, default=64,
                        help='number of goods')
    parser.add_argument('--bids', type=int, default=1000,
                        help='number of bids')
    parser.add_argument('--Epsilon', type=float, default=1e-6,
                        help='Epsilon for Water filling algorithm')
    parser.add_argument('--num', type=int, default=50,
                        help='number of instances')

    args = parser.parse_args()
    print(args)
    
    if args.distribution == 'all':
        D_list = ['arbitrary', 'L4', 'matching', 'paths', 'regions', 'scheduling']
    else:
        D_list = [args.distribution]
    for distribution in D_list:
        print(distribution)
        filename = "Data\{}\g{}_b{}\\".format(distribution,args.goods,args.bids)

        Mechanisms_dict = dict()
        if args.mechanism == 'all':
            for m in ['VCG','MRC','MRC-VCG','MRC-Zero','WF-CGS','WF-CGS-CR']:
                Mechanisms_dict[m] = Mechanism()
        else:
            Mechanisms_dict[args.mechanism] = Mechanism()


        path = 'Result/{}/g{}_b{}/'.format(distribution,args.goods,args.bids)
        if not os.path.exists(path):
            os.makedirs(path)

        
        i=0
        num = args.num
        while i<num:
            print('instance:',i)
            file = filename + str(i) + '.txt'
            bid_information, bid_prices, bid_items, dummy_bids = read_bidfile(file)
            Welfare, my_winners = Winner_determination(bid_information, bid_prices, bid_items)
            Winners = Winner(bid_information, bid_prices, bid_items, dummy_bids, my_winners)
            try:
                run(Mechanisms_dict,i)



            except Exception as e:
                print('instance',i,'errer')
                traceback.print_exc()

            i+=1






