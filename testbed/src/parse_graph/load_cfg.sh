#!/bin/bash


rm -f *.txt *.json
cp ../gen_trace/graph.txt ./
cp ../gen_trace/payments.txt ./
cp ../gen_trace/path.txt ./

./parse_graph graph.txt payments.txt path.txt 127.0.0.1 $1
