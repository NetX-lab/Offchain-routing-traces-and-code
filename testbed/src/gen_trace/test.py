import networkx as nx
import csv
import random


def main():
	# PARAMETERS

	# number of nodes in the network
	num_node = 10
	# number of payments to run through the network
	nflows = 10000
	# fraction of payments that should be "mice" payments
	percentage = 90


	# RANDOM NETWORK CONSTRUCTION

	random.seed(2)
	f1 = open("graph.txt", 'w+')
	GG = nx.watts_strogatz_graph(num_node, 8, 0.8, 1)   # num_node nodes, connected to nearest 8 neighbors in ring topology, 0.8 probability of rewiring, random seed 1
	G = nx.DiGraph()

	for e in GG.edges():
		cap_01 = random.randint(700,1000)
		cap_10 = random.randint(700,1000)
		G.add_edge(e[0], e[1], capacity=cap_01)
		G.add_edge(e[1], e[0], capacity=cap_10)
		f1.write("%d,%d,%d\n" % (e[0], e[1], cap_01))
		f1.write("%d,%d,%d\n" % (e[1], e[0], cap_10))

	f1.close()


	# PLOT GRAPH

	# pos = nx.spring_layout(G, iterations=200)
	# nx.draw(G, pos, node_color=range(10), node_size=800, cmap=plt.cm.Blues)
	# plt.show()

	node_list = list(G.nodes())


	# LOAD TRANSACTIONS FROM RIPPLE DATASET

	trans = []
	with open('data/ripple_val.csv', 'r') as f: 
		csv_reader = csv.reader(f, delimiter=',')
		for row in csv_reader:
			if float(row[2]) > 0:
				src = int(row[0]) % len(node_list)
				dst = int(row[1]) % len(node_list)

				if src == dst:
					continue

				trans.append((int(src), int(dst), float(row[2])))


	# COMPUTE THRESHOLD FOR MICE/ELEPHANT PAYMENTS

	sorted_trans = sorted(trans, key=lambda x: x[2])
	threshold = sorted_trans[int(1.0*percentage/100*(len(sorted_trans)-1))][2]
	print('threshold for ripple trace', threshold)


	# GENERATE PAYMENTS

	f2 = open("payments.txt", 'w+')
	payments = []

	for k in range(nflows):
		while True:
			index = random.randint(0, len(trans)-1)
			tx = trans[index]
			if nx.has_path(G, tx[0], tx[1]):
				break

		payments.append((tx[0], tx[1], tx[2], 1, 0))
		f2.write("%d,%d,%f\n" % (tx[0], tx[1], tx[2]))

	f2.close()


	# GENERATE PATHS FOR PAYMENTS

	f3 = open("path.txt", 'w+')
	# how many paths to compute max.
	need_num_path = 10
	path_visited = [ [ 0 for x in range(num_node) ] for y in range(num_node) ]

	for s_payment in payments:
		src = s_payment[0]
		dst = s_payment[1]

		if path_visited[src][dst] == 1:
			continue

		path_visited[src][dst] = 1
		path_set = list(nx.edge_disjoint_paths(G, src, dst))

		if (len(path_set) > need_num_path):
			path_set = path_set[0:need_num_path]

		for path in path_set:
			f3.write("%d,%d," % (src, dst))
			f3.write(",".join([ str(i) for i in path ]) + "\n")

	f3.close()
	

	# print flash.routing(G.copy(), payments, 0, 4)
	# print waterfilling.routing(G.copy(), payments)



if __name__ == "__main__":
	main()
