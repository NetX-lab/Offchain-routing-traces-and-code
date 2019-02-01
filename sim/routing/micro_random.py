import numpy as np
import networkx as nx 
import csv 
import random
from random import shuffle 
import cvxpy as cp 
from itertools import islice
import sys
import time
import max_flow

class RoutingTable:
  def __init__(self):
    self.destinations = []
    self.paths = []

  def add_destination(self, destination): 
    self.destinations.append(destination)

  # add path towards to a given destination
  def add_path(self, dst, path):
    if dst not in self.destinations: 
      print 'false xxxxxxx'
    else: 
      index = self.destinations.index(dst)
      self.paths[index].append(path)

  def create_dst_entries(self, dst, path):
    self.destinations.append(dst)
    self.paths.append([path])

# function to find k shortest paths 
def k_shortest_paths(G, source, target, k):
  return list(islice(nx.shortest_simple_paths(G, source, target), k))

# return a list of paths
def get_path(mega_table, src, dst):
  table = mega_table[src]

  if dst not in table.destinations: 
    return []
  else: 
    index = table.destinations.index(dst)
    return table.paths[index]

def add_path(mega_table, src, dst, path):
  table = mega_table[src]

  if dst not in table.destinations: 
    table.create_dst_entries(dst, path)
  else: 
    table.add_path(dst, path)

# cache hit ratio vs number of flows 
# routing table size vs performance
def routing(G, payment, mega_table, num_max_cache):
  if num_max_cache == 0: 
      sent, cost_res, msgs, max_path_length = max_flow.routing(G, payment)
      return sent, cost_res, msgs, 0, 0

  src = payment[0]
  dst = payment[1]
  payment_size = payment[2]

  max_path_length = 0
  found = 1

  fee = 0
  probing_msg = 0

  all_paths = k_shortest_paths(G, src, dst, num_max_cache)

  path_set = get_path(mega_table, src, dst)

  # sample the first path towards the destination
  if not path_set:
    found = 0 
    path_set.append(all_paths[0])
    add_path(mega_table, src, dst, all_paths[0])
 
  sent_list = []
  visited_paths = []
  path = path_set[0]
  while True:
    if len(path)-1 > max_path_length: 
        max_path_length = len(path)-1

    pathCap = sys.maxsize    
    for i in range(len(path)-1): 
      pathCap = np.minimum(pathCap, G[path[i]][path[i+1]]["capacity"])

    remainning_credits = payment_size-sum(sent_list)
    sent = remainning_credits if (pathCap > remainning_credits) else pathCap

    # in the design, we probe the path if blind sending fails
    if remainning_credits > pathCap: 
      probing_msg += 1

    sent_list.append(sent)
    visited_paths.append(path)

    # update path capacity 
    for i in range(len(path)-1):
      G[path[i]][path[i+1]]["capacity"] -= sent
      G[path[i+1]][path[i]]["capacity"] += sent
      fee += G[path[i]][path[i+1]]["cost"]*sent

    if not (sum(sent_list) < payment_size and len(sent_list) < len(all_paths)):
      break 

    path_set = get_path(mega_table, src, dst)
    # still have cache paths to use
    if len(sent_list) < len(path_set):
      path = path_set[len(sent_list)]
    else: 
      rest = [i for i in all_paths if i not in path_set]
      path = rest[0]
      add_path(mega_table, src, dst, path)

  # fail, roll back 
  if sum(sent_list) < payment[2]:
    for i in range(len(visited_paths)):
      p = visited_paths[i]
      for j in range(len(p)-1):
        G[p[j]][p[j+1]]["capacity"] += sent_list[i]
        G[p[j+1]][p[j]]["capacity"] -= sent_list[i]

    # sent, cost_res, msgs, max_path_length = max_flow.routing(G, payment)
    # return sent, cost_res, probing_msg+msgs, 0, found
    return 0, 0, probing_msg, 0, found
  else: 
    return payment[2], 0, probing_msg, max_path_length, found
