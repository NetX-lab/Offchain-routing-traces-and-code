import networkx as nx
import numpy as np
from scipy import stats

from datetime import datetime
import csv
import random

import sys
sys.path.append('./routing')

import shortest_path
import waterfilling
import flash
import speedymurmurs
import max_flow

import ripple_proc
import lightning_proc


# GENERAL TERMINOLOGY
#
# "trace"
#     dataset to get transactions and network topology from: 'ripple' or 'lightning'
# "trans"
#     set of transactions sampled from the dataset
# "nflows"
#     how many transactions to sample from the dataset and route through the network
#     (this number needs to be sufficiently high, otherwise the network is not in
#     "steady state" but instead the performance is still affected by the initialization
#     of the balances on the payment channels)
#     (in arxiv:1902.05260v2: "Number of transactions", Fig. 7)
# "nruns"
#     how many times to run the overall experiment and average over
#     (in arxiv:1902.05260v2 this is by default 5)
# "percentage"
#     what fraction of the transfers should be considered mice payments
#     (in arxiv:1902.05260v2: "Percentage of Mice Payments (%)", Fig. 10)
# "scale_factor"
#     the payment channels' capacities are scaled by this factor
#     with respect to their original value in the dataset
#     (in arxiv:1902.05260v2: "Capacity Scale Factor", Fig. 6)
# "num_max_cache"
#     how many routes should be cached for simplified routing of mice payments
#     (in arxiv:1902.05260v2: "Number of Paths Per Receiver", Fig. 11)


VALID_TRACES = ['ripple', 'lightning']
VALID_SCHEMES = ['sp', 'speedymurmurs', 'waterfilling', 'flash']



# this function determines the transaction value such that "percentage" fraction of the
# transactions "trans" (which have to come from trace "trace") have smaller or equal value
# (i.e., the threshold for mice vs. elephant payments)

def get_threshold(trace, trans, percentage):
	assert(trace in VALID_TRACES)

	if trace == 'ripple':
		sorted_trans = sorted(trans, key=lambda x: x[2])
		threshold = sorted_trans[int(1.0*percentage/100*(len(sorted_trans)-1))]
		return threshold[2]

	elif trace == 'lightning':
		sorted_trans = sorted(trans)
		threshold = sorted_trans[int(1.0*percentage/100*(len(sorted_trans)-1))]
		return threshold


# initializes the network topology and transactions from the dataset

def get_topology_and_transactions(trace):
	assert(trace in VALID_TRACES)

	G_ori = nx.DiGraph()
	trans = []

	if trace == 'ripple':
		G_ori, trans = ripple_proc.setup()
	elif trace == 'lightning':
		G_ori, trans = lightning_proc.setup()

	return (G_ori, trans)


# generates payments from the dataset

def generate_payments(trace, seed, nflows, trans, G):
	assert(trace in VALID_TRACES)

	payments = []

	if trace == 'ripple':
		payments = ripple_proc.generate_payments(seed, nflows, trans, G)
	elif trace == 'lightning':
		payments = lightning_proc.generate_payments(seed, nflows, trans, G)

	return payments


# takes a given topology with capacities ("G_ori") and scales
# the capacity of each edge by factor "scale_factor"

def scale_topo_cap(G_ori, scale_factor):
	G = nx.DiGraph()

	for e in G_ori.edges():
		G.add_edge(e[0], e[1], capacity = G_ori[e[0]][e[1]]['capacity']*scale_factor, cost = G_ori[e[0]][e[1]]['cost'])

		if (e[1], e[0]) not in G_ori.edges():
			G.add_edge(e[1], e[0], capacity = G_ori[e[0]][e[1]]['capacity']*scale_factor, cost = G_ori[e[0]][e[1]]['cost'])
		else:
			G.add_edge(e[1], e[0], capacity = G_ori[e[1]][e[0]]['capacity']*scale_factor, cost = G_ori[e[1]][e[0]]['cost'])

	return G




# MICRO BENCHMARKS

# generates the data ('<trace>-threshold.txt') for Figure 10 of arxiv:1902.05260v2
# input: all transactions, number of flows to send, number of runs, scale factor for topology capacity

def run_flash_thresh(trace, nflows, nruns, scale_factor, percentage_list, num_max_cache):
	assert(trace in VALID_TRACES)


	# initialize topology and transactions from the dataset
	G_ori, trans = get_topology_and_transactions(trace)


	# run Flash simulation ("nruns" times) for every possible "percentage" value and record
	# and average over success ratio, success volume, and number of probing messages
	
	flash_ratio = []	
	flash_volume = []	
	flash_msg = []	
	

	for percentage in percentage_list: 
		G = scale_topo_cap(G_ori, scale_factor)

		threshold = get_threshold(trace, trans, percentage)
		print('threshold', threshold)

		volume_list = []
		ratio_list = []
		msg_list = []

		# simulate multiple runs of payments
		for seed in range(nruns):
			print('Start run simulation. Run', seed)

			payments = generate_payments(trace, seed, nflows, trans, G)

			volume, cost, num_delivered, total_probing_messages, total_max_path_length, hit_ratio, table_size, micro_volume, micro_msg = flash.routing(G.copy(), payments, threshold, num_max_cache)

			# record stats for the current run
			volume_list.append(1.0*volume)
			ratio_list.append(1.0*num_delivered/nflows)
			msg_list.append(1.0*total_probing_messages)


		# average over runs and store averages
		flash_volume.append(sum(volume_list)/nruns)
		flash_ratio.append(sum(ratio_list)/nruns)
		flash_msg.append(sum(msg_list)/nruns)


	# log results to file
	with open(f'{trace}-threshold.txt', 'w') as filehandle:
		filehandle.write(' '.join([ str(e) for e in flash_volume ]) + '\n')
		filehandle.write(' '.join([ str(e) for e in flash_ratio ]) + '\n')
		filehandle.write(' '.join([ str(e) for e in flash_msg ]) + '\n')



# generates the data ('<trace>-cache.txt') for Figure 11 of arxiv:1902.05260v2

def run_flash_cache(trace, nflows, nruns, scale_factor, percentage, cache_list):
	assert(trace in VALID_TRACES)


	# initialize topology and transactions from the dataset
	G_ori, trans = get_topology_and_transactions(trace)


	# run Flash simulation ("nruns" times) for every possible "num_max_cache" value and record
	# and average over success ratio, success volume, and number of probing messages

	flash_micro_volume = []
	flash_micro_msg = []
	flash_ratio = []
	flash_hit = []
	flash_table = []
			
	for num_max_cache in cache_list: 
		G = scale_topo_cap(G_ori, scale_factor)
		threshold = get_threshold(trace, trans, percentage)

		micro_volume_list = []
		micro_msg_list = []
		ratio_list = []
		hit_list = []
		table_list = []

		# payments to send
		for seed in range(nruns):
			print('Start run simulation. Run', seed)

			payments = generate_payments(trace, seed, nflows, trans, G)

		    # todo: lightning trace??? (remark: seems that "flash_micro_msg" remains empty for "lightning"? at least that is the case in "sim/result/rawdata/lightning-cache.txt")

			volume, cost, num_delivered, total_probing_messages, total_max_path_length, hit_ratio, table_size, micro_volume, micro_msg = flash.routing(G.copy(), payments, threshold, num_max_cache)

			# record stats for the current run
			micro_volume_list.append(1.0*micro_volume)
			micro_msg_list.append(micro_msg)
			ratio_list.append(1.0*num_delivered/nflows)
			hit_list.append(hit_ratio)
			table_list.append(table_size)


		# average over runs and store averages
		flash_micro_volume.append(sum(micro_volume_list)/nruns)
		flash_micro_msg.append(sum(micro_msg_list)/nruns)
		flash_ratio.append(sum(ratio_list)/nruns)
		flash_hit.append(sum(hit_list)/nruns)
		flash_table.append(sum(table_list)/nruns)


	# log results to file
	with open(f'{trace}-cache.txt', 'w') as filehandle:
		filehandle.write(' '.join([ str(e) for e in flash_micro_volume ]) + '\n')
		filehandle.write(' '.join([ str(e) for e in flash_ratio ]) + '\n')
		filehandle.write(' '.join([ str(e) for e in flash_hit ]) + '\n')
		filehandle.write(' '.join([ str(e) for e in flash_table ]) + '\n')
		filehandle.write(' '.join([ str(e) for e in flash_micro_msg ]) + '\n')



# MAIN COMPARISON

# run comparison of different routing schemes
# generates the data ('<trace>-<routing scheme>-<nflows>.txt') for Figures 6+7 of arxiv:1902.05260v2

def run_general(scheme, trace, nflows, nruns, nlandmarks, scale_list, percentage, num_max_cache):
	assert(trace in VALID_TRACES)
	assert(scheme in VALID_SCHEMES)


	# initialize topology and transactions from the dataset
	G_ori, trans = get_topology_and_transactions(trace)

	# find the right threshold for the requested "percentage"
	threshold = get_threshold(trace, trans, percentage)


	# run simulation ("nruns" times) for every possible "scale_factor" value and record
	# and average over success ratio, success volume, transaction fees,
	# number of probing messages, and cache hit probability (Flash only)

	res_ratio = []
	res_volume = []
	res_cost = []
	res_msg = []
	res_hit = []

	for scale_factor in scale_list:
		G = nx.DiGraph()
		G = scale_topo_cap(G_ori, scale_factor)

		volume_list = []
		ratio_list = []
		cost_list = []
		msg_list = []
		hit_list = []

		# payments to send
		for seed in range(nruns):
			random.seed(seed)
			print('Start run simulation. Run', seed, ' trace ', trace, ' scheme ', scheme)

			payments = generate_payments(trace, seed, nflows, trans, G)

			if scheme == 'sp':
				volume, cost, num_delivered, total_probing_messages, total_max_path_length = shortest_path.routing(G.copy(), payments)
			elif scheme == 'speedymurmurs':
				volume, cost, num_delivered, total_probing_messages, total_max_path_length = speedymurmurs.routing(G.copy(), payments, nlandmarks)
			elif scheme == 'waterfilling':
				volume, cost, num_delivered, total_probing_messages, total_max_path_length = waterfilling.routing(G.copy(), payments)
			elif scheme == 'flash':
				volume, cost, num_delivered, total_probing_messages, total_max_path_length, hit_ratio, table_size, micro_volume, micro_msg  = flash.routing(G.copy(), payments, threshold, num_max_cache)

			# record stats for the current run
			volume_list.append(1.0*volume)
			ratio_list.append(1.0*num_delivered/nflows)
			cost_list.append(cost)
			msg_list.append(1.0*total_probing_messages)
			if scheme == 'flash': 
				hit_list.append(hit_ratio)


		# average over runs and store averages
		res_volume.append(sum(volume_list)/nruns)
		res_ratio.append(sum(ratio_list)/nruns)
		res_cost.append(sum(cost_list)/nruns)
		res_msg.append(sum(msg_list)/nruns)
		if scheme == 'flash': 
			res_hit.append(sum(hit_list)/nruns)

		print(scheme, res_cost)


	# log results to file
	with open(f'{trace}-{scheme}-{nflows}.txt', 'w') as filehandle:
		filehandle.write(' '.join([ str(e) for e in res_volume ]) + '\n')
		filehandle.write(' '.join([ str(e) for e in res_ratio ]) + '\n')
		filehandle.write(' '.join([ str(e) for e in res_msg ]) + '\n')
		if scheme == 'flash':
			filehandle.write(' '.join([ str(e) for e in res_hit ]) + '\n')





# MAIN CODE
# runs experiments as instructed from commandline

def main():
	trace = sys.argv[1] # ripple lightning
	nflows = int(sys.argv[2]) # int 
	exp = sys.argv[3] # threshold cache general 

	nruns = 5 # test


	# #################### run experiment to evaluate flash with different thresholds ####################
	# Figure 10 of arxiv:1902.05260v2

	if exp == 'threshold':
		scale_factor = 10
		percentage_list = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
		num_max_cache = 4
		run_flash_thresh(trace, nflows, nruns, scale_factor, percentage_list, num_max_cache)


	# #################### run experiment to evaluate flash with different number of cached paths ####################
	# Figure 11 of arxiv:1902.05260v2

	if exp == 'cache': 
		scale_factor = 10
		percentage = 90
		# cache_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
		cache_list = [0, 2, 4, 8, 10]
		run_flash_cache(trace, nflows, nruns, scale_factor, percentage, cache_list)


	# #################### run experiments to compare general performance among schemes #################### 
	# Figures 6+7 of arxiv:1902.05260v2

	# run on all schemes
	ALL_SCHEMES = VALID_SCHEMES
	# run only Flash
	# ALL_SCHEMES = ['flash']

	ALL_SCHEMES = ['waterfilling', 'flash']

	if exp == 'general':
		nlandmarks = 3
		percentage = 90
		num_max_cache = 4
		scale_list = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
		for scheme in ALL_SCHEMES:
			run_general(scheme, trace, nflows, nruns, nlandmarks, scale_list, percentage, num_max_cache)



if __name__ == "__main__":
	main()
