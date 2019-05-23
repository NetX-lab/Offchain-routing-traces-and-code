### Speedymurmurs Routing
import numpy as np
import networkx as nx
#import matplotlib.pyplot as plt
import json
import csv
import random
import operator
import sys
from datetime import datetime

random.seed(datetime.now())

def dist(c1, c2):
	common_prefix_length = 0
	shorter_length = np.minimum(len(c1), len(c2))
	for i in range(shorter_length):
		if c1[i] == c2[i]:
			common_prefix_length += 1
		else:
			break
	return len(c1) + len(c2) - 2 * common_prefix_length

# assign coordinates to all nodes using BFS
# first consider nodes with directional channels; then nodes with unidirectional channels 
def setRoute(G, landmarks, edges, coordinate, parent):
	L = len(landmarks)
	N = len(G)

	nb = {}
	for i in range(N):
		nb[i] = []
	for e in edges:
		nb[e[0]].append(e[1])

	for l in range(L):
		q = []
		root = landmarks[l]
		q.append(root)
		bi_flag = True
		child_index = np.zeros(N)
		while len(q) != 0:
			node = q.pop(0)
			for n in nb[node]:
				if n != root and len(coordinate[l][n]) == 0:
					if (G[node][n]["capacity"] > 0 and G[n][node]["capacity"] > 0) or (not bi_flag):
						parent[l][n] = node
						child_index[node] += 1
						current_index = child_index[node]
						coordinate[l][n] = coordinate[l][node] + [current_index]
						q.append(n)
			if len(q) == 0 and bi_flag:
				bi_flag = False
				for n in range(N):
					if len(coordinate[l][n]) > 0:
						q.append(n)
	return coordinate, parent

# react to channel state changes
def setCred(edges, landmarks, parent, coordinate, u, v, c, G):
	L = len(landmarks)
	N = len(G)
	old = G[u][v]["capacity"]

	reset_nodes = {}
	for l in range(L):
		reset_nodes[l] = []

	for l in range(L):
		reset = -1 # node whose coordinate should change
		## case: add link
		if old == 0 and c > 0:
			if len(coordinate[l][v]) == 0 and len(coordinate[l][u]) > 0:
				reset = v
			if len(coordinate[l][u]) == 0 and len(coordinate[l][v]) > 0:
				reset = u
			if reset == -1:
				if G[u][v]["capacity"] > 0 and G[v][u]["capacity"] > 0:
					a1 = (G[u][parent[l][u]]["capacity"] == 0) or (G[parent[l][u]][u]["capacity"] == 0)
					a2 = (G[v][parent[l][v]]["capacity"] == 0) or (G[parent[l][v]][v]["capacity"] == 0)
					if a1 and (not a2):
						reset = v
					if a2 and (not a1):
						reset = u
		## case: remove link
		if old > 0 and c == 0:
			if parent[l][u] == v:
				reset = u
			if parent[l][v] == u:
				reset = v
		## change coordinate
		if reset != -1:
			cc = coordinate[l][reset]
			coordinate[l][reset] = []
			reset_nodes[l].append(reset)
			for n in range(N):
				if len(coordinate[l][n]) > len(cc) and coordinate[l][n][0:len(cc)] == cc: # all descendants
				    coordinate[l][n] = []
				    reset_nodes[l].append(n)
			coordinate, parent = setRoute(G, landmarks, edges, coordinate, parent)
	return coordinate, parent
 
def routePay(G, edges, landmarks, coordinate, parent, src,dst, payment_size):
	probing_messages = 0
	max_path_length = 0
	fee = 0
	L = len(landmarks)
	N = len(G)
	nb = {}
	for i in range(N):
		nb[i] = []
	for e in edges:
		nb[e[0]].append(e[1])

	## split payment into L shares
	c = np.multiply(np.ones(L), float(payment_size)/float(L))
	path = {}
	fail = False

	GG = G.copy() # original graph 


	for l in range(L):
		path[l]= []
		v = src
		while (not fail) and (v != dst):
			next_hop = -1
			min_dist = N * N
			for n in nb[v]:
				c1 = coordinate[l][v]
				c2 = coordinate[l][n]
				c3 = coordinate[l][dst]
				if dist(c2, c3) < dist(c1, c3) and G[v][n]["capacity"] >= c[l]:
					if dist(c2, c3) < min_dist:
						min_dist = dist(c2, c3)
						next_hop = n
			if next_hop != -1:
				path[l].append((v,next_hop))
				G[v][next_hop]["capacity"] -= c[l]
				G[next_hop][v]["capacity"] += c[l]
				v = next_hop
			else:
				fail = True
	## routing fail, roll back
	if fail:
		for l in range(L):
			probing_messages += len(path[l])
			for e in path[l]:
				G[e[0]][e[1]]["capacity"] += c[l]
				G[e[1]][e[0]]["capacity"] -= c[l]
		return G, 0, fee, coordinate, parent, probing_messages, 0
	else:
		coordinate = {}
		parent = {}
		for l in range(L):
			probing_messages += len(path[l])
			coordinate[l] = []
			parent[l] = []
			for i in range(N):
				coordinate[l].append([])
				parent[l].append([])
		coordinate, parent = setRoute(G, landmarks, edges, coordinate, parent)

		for l in range(L):
			if len(path[l]) > max_path_length: 
       				max_path_length = len(path[l])
			for e in path[l]:
				u = e[0]
				v = e[1]
				c1 = G[u][v]["capacity"]
				c2 = G[v][u]["capacity"]
				coordinate, parent = setCred(edges, landmarks, parent, coordinate, u, v, c1, GG)
				coordinate, parent = setCred(edges, landmarks, parent, coordinate, v, u, c2, GG)
				GG[u][v]["capacity"] -= c[l]
				GG[v][u]["capacity"] += c[l]
				fee += GG[u][v]["cost"]*c[l]
				
		return G, payment_size, fee, coordinate, parent, probing_messages, max_path_length

def routing(G, payments, L=2): # input graph and number of landmarks 
	landmarks = []
	sorted_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)
	for l in range(L):
		landmarks.append(sorted_nodes[l][0])
	N = len(G)
	edges = G.edges()

	coordinate = {}
	parent = {}
	for l in range(L):
		coordinate[l] = []
		parent[l] = []
		for i in range(N):
			coordinate[l].append([])
			parent[l].append([])
	
	coordinate, parent = setRoute(G, landmarks, edges, coordinate, parent)

	throughput = 0 
	num_delivered = 0
	total_probing_messages = 0
	total_max_path_length = 0
	transaction_fees = 0
  	for payment in payments:
  		src = payment[0]
		dst = payment[1]
		payment_size = payment[2]
  		G, delivered, fee, coordinate, parent, probing_messages, max_path_length = routePay(G, edges, landmarks, coordinate, parent, src,dst, payment_size)
  		total_probing_messages += probing_messages
  		if not delivered < payment[2]:
  			total_max_path_length += max_path_length
  			num_delivered += 1
  		throughput += delivered
  		transaction_fees += fee
  	return throughput, transaction_fees/throughput, num_delivered, total_probing_messages, total_max_path_length
