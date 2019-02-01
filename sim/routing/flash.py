import numpy as np
import networkx as nx 
import random
from random import shuffle 
from itertools import islice
import sys
import time
import micro_random
import max_flow

def routing(G, cur_payments, threshold, num_max_cache): 
  throughput = 0 
  num_delivered = 0
  total_probing_messages = 0
  total_max_path_length = 0
  cache_hit = 0
  num_entry = 0
  num_active = 0
  num_micro = 0
  micro_throughput = 0
  micro_probing_messages = 0
  mega_table = [micro_random.RoutingTable() for i in range(len(G))]
  transaction_fees = 0

  for payment in cur_payments: 
    if payment[2] < threshold: # handle micro payments
      sent, fee, probing_messages, max_path_length, found = micro_random.routing(G, payment, mega_table, num_max_cache)
      cache_hit += found
      num_micro += 1
      micro_throughput += sent
      micro_probing_messages += probing_messages
      transaction_fees += fee
    else: # handle macro payments
      sent, fee, probing_messages, max_path_length = max_flow.routing(G, payment) 
      transaction_fees += fee

    throughput += sent 
    total_probing_messages += probing_messages
    if not payment[2] > sent: 
      num_delivered += 1
      total_max_path_length += max_path_length

  # routing table size: number of entries 
  for table in mega_table:
    if table.destinations: 
      num_active += 1 # number of senders who sent payments 
    for i in range(len(table.destinations)):
      # if table.paths: 
      #   print num_max_cache, table.paths
      num_entry += len(table.paths[i])

  # if there is no micropayments 
  if num_active == 0: 
    num_active = 1
  if num_micro == 0:
    num_micro = 1

  return throughput, transaction_fees/throughput, num_delivered, total_probing_messages, total_max_path_length, 1.0*cache_hit/num_micro, 1.0*num_entry/num_active, micro_throughput, micro_probing_messages

# G = nx.DiGraph()
# G.add_edge(0, 1, capacity = 10)
# G.add_edge(1, 0, capacity = 10)
# G.add_edge(0, 2, capacity = 10)
# G.add_edge(2, 0, capacity = 10)
# G.add_edge(0, 7, capacity = 10)
# G.add_edge(7, 0, capacity = 10)
# G.add_edge(1, 3, capacity = 10)
# G.add_edge(3, 1, capacity = 10)
# G.add_edge(1, 4, capacity = 10)
# G.add_edge(4, 1, capacity = 10)
# G.add_edge(2, 5, capacity = 10)
# G.add_edge(5, 2, capacity = 10)
# G.add_edge(3, 6, capacity = 10)
# G.add_edge(6, 3, capacity = 10)
# G.add_edge(4, 6, capacity = 10)
# G.add_edge(6, 4, capacity = 10)
# G.add_edge(5, 6, capacity = 10)
# G.add_edge(6, 5, capacity = 10)

# payments = []
# payments.append((6, 0, 6, 1, 0))
# payments.append((0, 6, 21, 1, 0))
# payments.append((0, 6, 26, 1, 0))

# print routing(G, payments,4)
