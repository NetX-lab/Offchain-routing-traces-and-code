import numpy as np
import networkx as nx 
import random
from random import shuffle 
from itertools import islice
import sys
import time

def rank (cap, maxSet, secMaxSet): 
  largest = -sys.maxint-1
  secLargest = -sys.maxint-1

  for i in range(len(cap)):
    if (cap[i] > largest): 
      secLargest = largest
      largest = cap[i]
    elif (cap[i] > secLargest and cap[i] != largest):
      secLargest = cap[i]

  for i in range(len(cap)): 
    if (cap[i] == largest):
      maxSet.append(i)
    if (cap[i] == secLargest):
      secMaxSet.append(i)

  if (secLargest == -sys.maxint-1):
    return 0; 

  return largest-secLargest

def set_credits (val, mins): 
  sum = 0 

  for i in mins: 
    sum += i 
  if val > sum: 
    return mins 

  remainder = val 
  minsCopy = list(mins)
  res = [0]*len(minsCopy)
  creditsToAssign = 0
  diff = 0

  while (remainder > 0): 
    maxSet = []
    secMaxSet = []
    diff = rank(minsCopy, maxSet, secMaxSet)
    creditsToAssign = diff if (remainder > len(maxSet)*diff) else (remainder/len(maxSet)) 

    if (diff == 0):
      creditsToAssign = remainder/len(minsCopy)

    for index in maxSet: 
      res[index] += creditsToAssign
      minsCopy[index] -= creditsToAssign
    remainder -= creditsToAssign * len(maxSet)
  return res

def routing(G, cur_payments):  
  k = 4
  throughput = 0
  num_delivered = 0
  index = 0
  total_probing_messages = 0
  total_max_path_length = 0
  transaction_fees = 0

  for payment in cur_payments: 
    fee = 0
    src = payment[0]
    dst = payment[1]
    payment_size = payment[2]

    path_set = list(nx.edge_disjoint_paths(G, src, dst))
    index += 1
    if (len(path_set) > k):
      path_set = path_set[0:k]

    max_path_length = 0
    path_cap = [sys.maxsize]*len(path_set)
    index_p = 0
    for path in path_set: 
      total_probing_messages += len(path)-1
      if len(path)-1 > max_path_length: 
        max_path_length = len(path)-1
      for i in range(len(path)-1): 
        path_cap[index_p] = np.minimum(path_cap[index_p], G[path[i]][path[i+1]]["capacity"])
      index_p += 1

    res = set_credits(payment_size, path_cap)
    index_p = 0
    for path in path_set:
      for i in range(len(path)-1):
        G[path[i]][path[i+1]]["capacity"] -= res[index_p]
        G[path[i+1]][path[i]]["capacity"] += res[index_p]
        fee += G[path[i]][path[i+1]]["cost"]*res[index_p]
      index_p += 1

    if sum(res) < payment[2]-1e-6:
      for i in range(len(path_set)):
        p = path_set[i]
        for j in range(len(p)-1):
          G[p[j]][p[j+1]]["capacity"] += res[i]
          G[p[j+1]][p[j]]["capacity"] -= res[i] 
      # remove atomicity
      # throughput += sum(res)
    else: 
      num_delivered += 1
      throughput += payment[2]
      total_max_path_length += max_path_length
      transaction_fees += fee

  return throughput, transaction_fees/throughput, num_delivered, total_probing_messages, total_max_path_length
