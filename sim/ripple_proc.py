import networkx as nx
import numpy as np
import csv
import random
from scipy import stats

def find_cycles(): 
	n = 0
	with open('traces/ripple/ripple_val.csv', 'r') as f: 
		csv_reader = csv.reader(f, delimiter=',')
		for row in csv_reader:
			G.add_edge(int(row[0]), int(row[1]))
			n += 1 
			if n > 2000: 
				break 
	print('cycles', list(nx.simple_cycles(G)))

# return graph 
def setup(): 
	GG = nx.DiGraph()
	# with open('data/ripple-lcc.graph_CREDIT_LINKS', 'r') as f: 
	with open('traces/ripple/jan2013-lcc-t0.graph_CREDIT_LINKS', 'r') as f: 
		for line in f: 
			source = int(line.split()[0])
			destination = int(line.split()[1])
			total_channel_cap = (float(line.split()[3])-float(line.split()[2])) + (float(line.split()[4])-float(line.split()[3]))
			if total_channel_cap > 0: 
				GG.add_edge(source, destination, capacity = total_channel_cap/2)
				GG.add_edge(destination, source, capacity = total_channel_cap/2)

	while True: 
		nodes_to_remove = []
		for node_index in list(GG.nodes()):
			if len(list(GG.neighbors(node_index))) < 2:
				nodes_to_remove.append(node_index)

		if len(nodes_to_remove) == 0: 
			break 

		for node_index in nodes_to_remove:
			GG.remove_node(node_index)

	node_list = list(GG.nodes())	

	random.seed(2)
	# make the node index be continuous
	G = nx.DiGraph()	
	for e in GG.edges(): 
		G.add_edge(node_list.index(e[0]), node_list.index(e[1]), capacity = GG[e[0]][e[1]]['capacity'], cost = random.random()*10)
		G.add_edge(node_list.index(e[1]), node_list.index(e[0]), capacity = GG[e[1]][e[0]]['capacity'], cost = random.random()*10)

	# transaction fees for 10% edges are especially high 
	random_edges = []
	random_edges = random.sample(range(G.number_of_edges()), int(G.number_of_edges()*0.1))
	i = 0
	for e in G.edges():
		if i in random_edges: 
			G[e[0]][e[1]]['cost'] = G[e[0]][e[1]]['cost']*10 
		i += 1

	listC = []
	for e in G.edges(): 
		listC.append(G[e[0]][e[1]]['capacity'])
		listC.append(G[e[1]][e[0]]['capacity'])

	print("number of nodes", len(G))
	print('average channel cap', float(sum(listC))/len(listC))
	print('num of edges', len(listC))
	
	sorted_var = np.sort(listC)
	print('medium capacity', stats.scoreatpercentile(sorted_var, 50))


	trans = []
	with open('traces/ripple/ripple_val.csv', 'r') as f: 
		csv_reader = csv.reader(f, delimiter=',')
		for row in csv_reader:
			if float(row[2]) > 0:
				src = int(row[0])%len(G)
				dst = int(row[1])%len(G)
				if src == dst: 
					continue
				trans.append((int(src), int(dst), float(row[2])))	
	print('num of transactions', len(trans))

	return G, trans

def generate_payments(seed, nflows, trans, G):
	random.seed(seed)
	payments = []

	k = 0 
	while True: 
		if not k < nflows: 
			break 
		index = random.randint(0, len(trans)-1)
		if not nx.has_path(G, trans[index][0], trans[index][1]):
			continue
		payments.append((trans[index][0], trans[index][1], trans[index][2], 1, 0))
		k += 1

	return payments
