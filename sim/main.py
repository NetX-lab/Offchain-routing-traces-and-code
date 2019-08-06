import networkx as nx
import numpy as np
from datetime import datetime
import sys
sys.path.append('./routing')
import shortest_path
import waterfilling
import flash
import speedymurmurs
import max_flow
import csv
import random
import ripple_proc
import lightning_proc
from scipy import stats

def get_threshold(trace, trans, percentage):
	if trace == 'ripple':
		sorted_trans = sorted(trans, key=lambda x: x[2])
		threshold = sorted_trans[int(1.0*percentage/100*(len(sorted_trans)-1))]
		return threshold[2]
	else:
		sorted_trans = sorted(trans)
		threshold = sorted_trans[int(1.0*percentage/100*(len(sorted_trans)-1))]
		return threshold

# micro benchmark 
# input: all transactions, number of flows to send, number of runs, scale factor for topology capacity
def run_flash_thresh(trace, nflows, nruns, scale_factor, percentage_list, num_max_cache):
	G_ori = nx.DiGraph()
	trans = []

	if (trace == 'ripple'):
		G_ori, trans = ripple_proc.setup()
	if (trace == 'lightning'):
		G_ori, trans = lightning_proc.setup()

	
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

		# payments to send
		for seed in range(nruns):
			print('Start run simulation. Run', seed)
			payments = []
			if trace == 'ripple': 
				payments = ripple_proc.generate_payments(seed, nflows, trans, G)
			if trace == 'lightning': 
				payments = lightning_proc.generate_payments(seed, nflows, trans, G)

			volume, cost, num_delivered, total_probing_messages, total_max_path_length, hit_ratio, table_size, micro_volume, micro_msg = flash.routing(G.copy(), payments, threshold, num_max_cache)
			volume_list.append(1.0*volume)
			ratio_list.append(1.0*num_delivered/nflows)
			msg_list.append(1.0*total_probing_messages)

		flash_volume.append(sum(volume_list)/nruns)
		flash_ratio.append(sum(ratio_list)/nruns)
		flash_msg.append(sum(msg_list)/nruns)

	with open(trace+'-'+'threshold.txt', 'w') as filehandle: 
		for element in flash_volume:
			filehandle.write('%s ' % element)
		filehandle.write('\n')
		for element in flash_ratio:
			filehandle.write('%s ' % element)
		filehandle.write('\n')
		for element in flash_msg:
			filehandle.write('%s ' % element)

def run_flash_cache(trace, nflows, nruns, scale_factor, percentage, cache_list):
	G_ori = nx.DiGraph()
	trans = []

	if (trace == 'ripple'):
		G_ori, trans = ripple_proc.setup()	
	
	if (trace == 'lightning'):
		G_ori, trans = lightning_proc.setup()

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
			payments = []
			if trace == 'ripple': 
				payments = ripple_proc.generate_payments(seed, nflows, trans, G)
			if trace == 'lightning': 
				payments = lightning_proc.generate_payments(seed, nflows, trans, G)
		    # todo: lightning trace 
			volume, cost, num_delivered, total_probing_messages, total_max_path_length, hit_ratio, table_size, micro_volume, micro_msg = flash.routing(G.copy(), payments, threshold, num_max_cache)


			micro_volume_list.append(1.0*micro_volume)
			micro_msg_list.append(micro_msg)
			ratio_list.append(1.0*num_delivered/nflows)
			hit_list.append(hit_ratio)
			table_list.append(table_size)

		flash_micro_volume.append(sum(micro_volume_list)/nruns)
		flash_micro_msg.append(sum(micro_msg_list)/nruns)
		flash_ratio.append(sum(ratio_list)/nruns)
		flash_hit.append(sum(hit_list)/nruns)
		flash_table.append(sum(table_list)/nruns)

	with open(trace+'-'+'cache.txt', 'w') as filehandle: 
		for element in flash_micro_volume: 
			filehandle.write('%s ' % element)
		filehandle.write('\n')
		for element in flash_ratio: 
			filehandle.write('%s ' % element)
		filehandle.write('\n')
		for element in flash_hit: 
			filehandle.write('%s ' % element)
		filehandle.write('\n')
		for element in flash_table: 
			filehandle.write('%s ' % element)
		for element in flash_micro_msg: 
			filehandle.write('%s ' % element)

def scale_topo_cap(G_ori, scale_factor):
	G = nx.DiGraph()
	for e in G_ori.edges():
		G.add_edge(e[0], e[1], capacity = G_ori[e[0]][e[1]]['capacity']*scale_factor, cost = G_ori[e[0]][e[1]]['cost'])

		if (e[1], e[0]) not in G_ori.edges():
			G.add_edge(e[1], e[0], capacity = G_ori[e[0]][e[1]]['capacity']*scale_factor, cost = G_ori[e[0]][e[1]]['cost'])
		else:
			G.add_edge(e[1], e[0], capacity = G_ori[e[1]][e[0]]['capacity']*scale_factor, cost = G_ori[e[1]][e[0]]['cost'])

	return G

def run_general(scheme, trace, nflows, nruns, nlandmarks, scale_list, percentage, num_max_cache):
	G_ori = nx.DiGraph()
	trans = []

	if (trace == 'ripple'):
		G_ori, trans = ripple_proc.setup()	
	if (trace == 'lightning'):
		G_ori, trans = lightning_proc.setup()

	threshold = get_threshold(trace, trans, percentage)

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

			payments = []
			if trace == 'ripple': 
				payments = ripple_proc.generate_payments(seed, nflows, trans, G)
			if trace == 'lightning': 
				payments = lightning_proc.generate_payments(seed, nflows, trans, G)

			if scheme == 'sp':
				volume, cost, num_delivered, total_probing_messages, total_max_path_length = shortest_path.routing(G.copy(), payments)
			elif scheme == 'speedymurmurs': 
				volume, cost, num_delivered, total_probing_messages, total_max_path_length = speedymurmurs.routing(G.copy(), payments, nlandmarks)
			elif scheme == 'waterfilling':
				volume, cost, num_delivered, total_probing_messages, total_max_path_length = waterfilling.routing(G.copy(), payments)
			elif scheme == 'flash': 
				volume, cost, num_delivered, total_probing_messages, total_max_path_length, hit_ratio, table_size, micro_volume, micro_msg  = flash.routing(G.copy(), payments, threshold, num_max_cache)
			else: 
				print('unknown routing')

			volume_list.append(1.0*volume)
			ratio_list.append(1.0*num_delivered/nflows)
			cost_list.append(cost)
			msg_list.append(1.0*total_probing_messages)
			if scheme == 'flash': 
				hit_list.append(hit_ratio)


		res_volume.append(sum(volume_list)/nruns)
		res_ratio.append(sum(ratio_list)/nruns)
		res_cost.append(sum(cost_list)/nruns)
		res_msg.append(sum(msg_list)/nruns)
		if scheme == 'flash': 
			res_hit.append(sum(hit_list)/nruns)

		print(scheme, res_cost)

	with open(trace+'-'+scheme+'-'+str(nflows)+'.txt', 'w') as filehandle: 
		for element in res_volume: 
			filehandle.write('%s ' % element)
		filehandle.write('\n')
		for element in res_ratio: 
			filehandle.write('%s ' % element)
		filehandle.write('\n')
		for element in res_msg: 
			filehandle.write('%s ' % element)
		if scheme == 'flash':
			filehandle.write('\n')
			for element in res_hit: 
				filehandle.write('%s ' % element)



# general performance 
def main():
	trace = sys.argv[1] # ripple lightning
	nflows = int(sys.argv[2]) # int 
	exp = sys.argv[3] # threshold cache general 

	nruns = 1 # test

	# #################### run experiment to evaluate flash with different thresholds ####################

	if exp == 'threshold':
		scale_factor = 10
		percentage_list = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
		num_max_cache = 4
		run_flash_thresh(trace, nflows, nruns, scale_factor, percentage_list, num_max_cache)

	# #################### run experiment to evaluate flash with different number of cached paths ####################

	if exp == 'cache': 
		scale_factor = 10
		percentage = 90
		# cache_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
		cache_list = [0, 2, 4, 8, 10]
		run_flash_cache(trace, nflows, nruns, scale_factor, percentage, cache_list)

	# #################### run experiments to compare general performance among schemes #################### 

	# parameters for schemes
	# if exp == 'general':
	# 	nlandmarks = 3
	# 	percentage = 90
	# 	num_max_cache = 4
	# 	scale_list = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
	# 	for scheme in ['flash', 'sp', 'speedymurmurs', 'waterfilling']:
	# 		run_general(scheme, trace, nflows, nruns, nlandmarks, scale_list, percentage, num_max_cache)


	if exp == 'general':
		nlandmarks = 3
		percentage =  90
		num_max_cache = 4
		scale_list = [10]
		for scheme in ['flash']:
			run_general(scheme, trace, nflows, nruns, nlandmarks, scale_list, percentage, num_max_cache)

if __name__ == "__main__":
	main()
