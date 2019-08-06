import networkx as nx
import numpy as np
import csv
import random
from scipy import stats


# return graph 
def setup(): 
	nodes = []
	with open('traces/lightning/allnodes.txt', 'r') as f: 
		f.readline()
		for line in f: 
			if 'nodeid' in line: 
				nodeid = line.split()[1]
				nodeid = nodeid.replace('"','').replace(',','')
				nodes.append(nodeid)

	random.seed(1)
	# edges = []
	G = nx.DiGraph()
	listC = []
	with open('traces/lightning/channels.txt', 'r') as f: 
		f.readline()
		for line in f: 
			if 'source' in line: 
				source = line.split()[1]
				source = source.replace('"','').replace(',','')
			elif 'destination' in line: 
				destination = line.split()[1]
				destination = destination.replace('"','').replace(',','')
			elif 'satoshis' in line: 
				capacity = line.split()[1]
				capacity = capacity.replace(',','')
				listC.append(float(capacity))
				G.add_edge(int(nodes.index(source)), int(nodes.index(destination)), capacity = float(capacity), cost = random.random()*10)

	while True: 
		nodes_to_remove = []
		for node_index in list(G.nodes()):
			if len(list(G.neighbors(node_index))) < 2:
				nodes_to_remove.append(node_index)

		if len(nodes_to_remove) == 0: 
			break 

		for node_index in nodes_to_remove:
			G.remove_node(node_index)


	mapping = dict(list(zip(G.nodes(), list(range(0, len(G))))))
	G = nx.relabel_nodes(G, mapping, copy=False)

	# transaction fees for 10% edges are especially high 
	random_edges = []
	random_edges = random.sample(range(G.number_of_edges()), int(G.number_of_edges()*0.1))
	i = 0
	for e in G.edges():
		if i in random_edges: 
			G[e[0]][e[1]]['cost'] = G[e[0]][e[1]]['cost']*10 
		i += 1

	print("number of nodes", len(G))
	print('average channel cap', float(sum(listC))/len(listC))
	print('num of edges', len(listC))

	sorted_var = np.sort(listC)

	print('medium channel capacity', stats.scoreatpercentile(sorted_var, 50))

	trans = []
	# count = 0
	with open('traces/lightning/BitcoinVal.txt', 'r') as f: 
		f.readline()
		for line in f: 
			# count += 1
			# if count > 1e5: 
			# 	break
			trans.append(float(line))
	# we randomly choose 1 million trans 
	# trans = random.sample(trans, 1000000)

	print('num of transactions', len(trans))
	return G, trans

# we use src-dst pair from ripple trace
def get_stpair (num_nodes):
	st = []
	with open('traces/ripple/ripple_val.csv', 'r') as f: 
		csv_reader = csv.reader(f, delimiter=',')
		for row in csv_reader:
			if float(row[2]) > 0:
				src = int(row[0])%num_nodes
				dst = int(row[1])%num_nodes
				if src == dst: 
					continue
				st.append((int(src), int(dst)))

	return st

def generate_payments(seed, nflows, trans, G):
	random.seed(seed)
	payments = []

	src_dst = get_stpair(len(G))

	k = 0
	while True: 
		if not k < nflows: 
			break 
		index = random.randint(0, len(src_dst)-1)
		src = src_dst[index][0]
		dst = src_dst[index][1]

		if not nx.has_path(G, src, dst):
			continue
		val = random.choice(trans)
		payments.append((src, dst, val, 1, 0))
		k += 1

	return payments

