#!/bin/bash


rm -f *.txt *.json
cp ~/workspace/offchain-routing-code/sim/graph.txt ./
cp ~/workspace/offchain-routing-code/sim/payments.txt ./
cp ~/workspace/offchain-routing-code/sim/path.txt ./

./parse_graph graph.txt payments.txt path.txt 127.0.0.1 $1
