import numpy as np
import networkx as nx 
import random
from random import shuffle 
from itertools import islice
import sys
import time

def routing(G, cur_payments):  
  throughput = 0
  transaction_fees = 0
  num_delivered = 0
  total_probing_messages = 0
  total_max_path_length = 0
  for payment in cur_payments:
    fee = 0 
    src = payment[0]
    dst = payment[1]
    payment_size = payment[2]
    path = nx.shortest_path(G, src, dst)
    total_probing_messages += len(path)-1

    path_cap = sys.maxsize
    for i in range(len(path)-1): 
      path_cap = np.minimum(path_cap, G[path[i]][path[i+1]]["capacity"])


    sent = payment_size if (path_cap > payment_size) else path_cap

    for i in range(len(path)-1):
      G[path[i]][path[i+1]]["capacity"] -= sent
      G[path[i+1]][path[i]]["capacity"] += sent

      fee += G[path[i]][path[i+1]]["cost"]*sent

    # fail, roll back 
    if sent < payment[2]:
        for i in range(len(path)-1):
          G[path[i]][path[i+1]]["capacity"] += sent
          G[path[i+1]][path[i]]["capacity"] -= sent 
        # remove atomicity
        # throughput += sent

    else: 
      total_max_path_length += len(path)-1
      num_delivered += 1
      throughput += sent
      transaction_fees += fee
  return throughput, transaction_fees/throughput, num_delivered, total_probing_messages, total_max_path_length

