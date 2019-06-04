import networkx as nx
#import matplotlib.pyplot as plt
import csv
import random
import sys
sys.path.append('./routing')
#import shortest_path
#import waterfilling
#import flash
#import speedymurmurs


def cdf_random_number(CDF, prob):
	randx = np.random.random(1)
	index = 0
	for v in prob: 
		if randx < v:
			break; 
		index += 1
	return (CDF[index]-CDF[index-1])*np.random.rand() + CDF[index-1]

def main():
	# parameters 
        num_node = 10
	nflows = 10000
	percentage = 90
	random.seed(2)
	f1 = open("graph.txt", 'w+')
	# graph 
	GG = nx.watts_strogatz_graph(num_node, 8, 0.8, 1)
	G = nx.DiGraph()
	for e in GG.edges(): 
		G.add_edge(e[0], e[1], capacity = random.randint(700,1000))
		G.add_edge(e[1], e[0], capacity = random.randint(700,1000))
		f1.write("%d,%d,%d\n" % (e[0],e[1],random.randint(700,1000)))
		f1.write("%d,%d,%d\n" % (e[1],e[0],random.randint(700,1000)))
	f1.close()

	# pos = nx.spring_layout(G, iterations=200)
	# nx.draw(G, pos, node_color=range(10), node_size=800, cmap=plt.cm.Blues)
	# plt.show()

	node_list = list(G.nodes())


	# trans
	trans = []
  	with open('data/ripple_val.csv', 'r') as f: 
		csv_reader = csv.reader(f, delimiter=',')
		for row in csv_reader:
			if float(row[2]) > 0:
				src = int(row[0])%len(node_list)
				dst = int(row[1])%len(node_list)
				if src == dst: 
					continue
				trans.append((int(src), int(dst), float(row[2])))
				


	sorted_trans = sorted(trans, key=lambda x: x[2])

	threshold = sorted_trans[int(1.0*percentage/100*(len(sorted_trans)-1))]

	print 'threshold for ripple trace', threshold[2]

	f2 = open("payments.txt", 'w+')
	# payments to send
	payments = []
	for k in range(nflows):
		index = random.randint(0, len(trans)-1)
	 	while not nx.has_path(G, trans[index][0], trans[index][1]):
	 		index = random.randint(0, len(trans)-1)
	 	payments.append((trans[index][0], trans[index][1], trans[index][2], 1, 0))

		f2.write("%d,%d,%f\n" % (trans[index][0], trans[index][1], trans[index][2]))
	f2.close()
        f3 = open("path.txt", 'w+')
        need_num_path = 10
        path_visited = [[0 for x in range(num_node)] for y in range(num_node)]
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
                for i in range(len(path)-1):
                    f3.write("%d," % (path[i]))
                f3.write("%d\n" % (path[len(path)-1]))
        f3.close()
        

	# print flash.routing(G.copy(), payments, 0, 4)
	# print waterfilling.routing(G.copy(), payments)


if __name__ == "__main__":
	main()
