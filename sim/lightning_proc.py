import networkx as nx
import numpy as np
import csv
import random
from scipy import stats


# returns network topology and transactions for Lightning

def setup():
	# load nodes (very hacky way to non-parse the JSON ...)
	nodes = []
	with open('traces/lightning/allnodes.txt', 'r') as f:
		for line in f:
			if 'nodeid' in line:
				nodeid = line.split()[1]
				nodeid = nodeid.replace('"','').replace(',','')
				nodes.append(nodeid)

	# load channels (very hacky way to non-parse the JSON ...)
	G = nx.DiGraph()
	listC = []
	with open('traces/lightning/channels.txt', 'r') as f:
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
				G.add_edge(
					# from
					int(nodes.index(source)),
					# to
					int(nodes.index(destination)),
					# capacity according to dataset
					capacity = float(capacity),
					# transaction fees: randomly sampled
					cost = random.random()*10
				)

	# while there are nodes with less than 2 neighbors (ie, who do not
	# take routing decisions anyways), remove them
	while True: 
		nodes_to_remove = []
		for node_index in list(G.nodes()):
			if len(list(G.neighbors(node_index))) < 2:
				nodes_to_remove.append(node_index)

		if len(nodes_to_remove) == 0: 
			break

		for node_index in nodes_to_remove:
			G.remove_node(node_index)

	# "close gaps" in the enumeration of the nodes that was created
	# by the above pruning procedure
	mapping = dict(list(zip(G.nodes(), list(range(0, len(G))))))
	G = nx.relabel_nodes(G, mapping, copy=False)

	# increase transaction fees of 10% of the edges by a factor of 10
	random.seed(1)
	random_edges = random.sample(range(G.number_of_edges()), int(G.number_of_edges()*0.1))
	for (i, e) in enumerate(G.edges()):
		if i in random_edges: 
			G[e[0]][e[1]]['cost'] = G[e[0]][e[1]]['cost']*10

	# print some stats
	# (average channel cap and number of edges are not current anymore,
	# after pruning of nodes has taken place ...)
	print("number of nodes", len(G))
	print('average channel cap', float(sum(listC))/len(listC))
	print('num of edges', len(listC))
	sorted_var = np.sort(listC)
	print('medium channel capacity', stats.scoreatpercentile(sorted_var, 50))

	# load the transaction values that have been obtained from
	# an analysis of the Bitcoin blockchain
	trans = []
	with open('traces/lightning/BitcoinVal.txt', 'r') as f: 
		for line in f:
			trans.append(float(line))

	# print some stats
	print('num of transactions', len(trans))

	# return: graph of network, list of transaction values
	return G, trans


# generates src/dst pairs using the Ripple dataset
# (the Lightning/Bitcoin dataset does not provide src/dst information)
# (node numbers from Ripple are mapped to Lightning using simple modulo ...)

def get_stpair(num_nodes):
	st = []

	with open('traces/ripple/ripple_val.csv', 'r') as f: 
		csv_reader = csv.reader(f, delimiter=',')
		for row in csv_reader:
			# only for positive payments
			if float(row[2]) > 0:
				# map Ripple nodes to Lightning nodes
				src = int(row[0]) % num_nodes
				dst = int(row[1]) % num_nodes

				if src == dst: 
					continue

				st.append((int(src), int(dst)))

	return st


# generates payments based on src/dst pairs from Ripple dataset
# and transaction amounts from Bitcoin/Lightning dataset

def generate_payments(seed, nflows, trans, G):
	random.seed(seed)

	payments = []
	src_dst = get_stpair(len(G))

	while True:
		# are we done yet?
		if len(payments) >= nflows:
			break

		# sample random src/dst pair for which there exists a path
		src, dst = random.choice(src_dst)
		if not nx.has_path(G, src, dst):
			continue

		# sample transaction value
		val = random.choice(trans)

		payments.append((src, dst, val, 1, 0))


	return payments

