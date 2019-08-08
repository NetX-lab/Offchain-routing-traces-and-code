import networkx as nx
import numpy as np
import csv
import random
from scipy import stats


# returns network topology and transactions for Ripple

def setup():
	# load network
	GG = nx.DiGraph()
	with open('traces/ripple/jan2013-lcc-t0.graph_CREDIT_LINKS', 'r') as f:
		for line in f:
			source = int(line.split()[0])
			destination = int(line.split()[1])
			total_channel_cap = (float(line.split()[3])-float(line.split()[2])) + (float(line.split()[4])-float(line.split()[3]))

			# add only channels with positive capacity
			if total_channel_cap > 0:
				GG.add_edge(source, destination, capacity = total_channel_cap/2)
				GG.add_edge(destination, source, capacity = total_channel_cap/2)

	# while there are nodes with less than 2 neighbors (ie, who do not
	# take routing decisions anyways), remove them
	while True:
		nodes_to_remove = []
		for node_index in list(GG.nodes()):
			if len(list(GG.neighbors(node_index))) < 2:
				nodes_to_remove.append(node_index)

		if len(nodes_to_remove) == 0:
			break

		for node_index in nodes_to_remove:
			GG.remove_node(node_index)

	# clean-up the graph after the above pruning procedure
	# (transform GG into the final graph G)
	node_list = list(GG.nodes())
	G = nx.DiGraph()	
	for e in GG.edges(): 
		G.add_edge(node_list.index(e[0]), node_list.index(e[1]), capacity = GG[e[0]][e[1]]['capacity'], cost = random.random()*10)
		G.add_edge(node_list.index(e[1]), node_list.index(e[0]), capacity = GG[e[1]][e[0]]['capacity'], cost = random.random()*10)

	# increase transaction fees of 10% of the edges by a factor of 10
	random.seed(2)
	random_edges = random.sample(range(G.number_of_edges()), int(G.number_of_edges()*0.1))
	for (i, e) in enumerate(G.edges()):
		if i in random_edges: 
			G[e[0]][e[1]]['cost'] = G[e[0]][e[1]]['cost']*10

	# collect some data for stats printout later
	listC = []
	for e in G.edges(): 
		listC.append(G[e[0]][e[1]]['capacity'])
		listC.append(G[e[1]][e[0]]['capacity'])
	listC_sorted = np.sort(listC)

	# print stats
	print("number of nodes", len(G))
	print('average channel cap', float(sum(listC))/len(listC))
	print('num of edges', len(listC))
	print('medium capacity', stats.scoreatpercentile(listC_sorted, 50))

	# load transaction amounts and src/dst from Ripple trace
	trans = []
	with open('traces/ripple/ripple_val.csv', 'r') as f: 
		csv_reader = csv.reader(f, delimiter=',')
		for row in csv_reader:
			if float(row[2]) > 0:
				# graph has been pruned, so we need to map each transaction
				# to existing src/dst pair
				src = int(row[0]) % len(G)
				dst = int(row[1]) % len(G)

				if src == dst: 
					continue

				trans.append((int(src), int(dst), float(row[2])))

	# print stats
	print('num of transactions', len(trans))

	# return: graph of network, list of transaction information
	return G, trans


# generate payments based on Ripple dataset

def generate_payments(seed, nflows, trans, G):
	random.seed(seed)
	payments = []

	while True:
		# are we done yet?
		if len(payments) >= nflows:
			break

		# sample transactions where there exists a path between src/dst
		tx = random.choice(trans)
		if not nx.has_path(G, tx[0], tx[1]):
			continue

		payments.append((tx[0], tx[1], tx[2], 1, 0))


	return payments
