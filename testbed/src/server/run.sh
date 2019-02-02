#!/bin/bash


N_node=$1
algo=$2

json_suffix=".json"
neig_prefix="n"
tran_prefix="tr"
tran_suffix=".txt"
g_file="graph.txt"
log_suffix=".log"
log_prefix="lll"
path_prefix="pa"
path_suffix=".txt"


rm -f ./pid
rm -f ./*.log

for((i=1;i<=N_node;i++))
do
	cmd="nohup ./server ${i}${json_suffix} ${neig_prefix}${i}${json_suffix} ${g_file} ${tran_prefix}${i}${tran_suffix} ${path_prefix}${i}${path_suffix} ${algo} ${i}"
	log="${log_prefix}${i}${log_suffix}"
	# exec cmd
	# $cmd >${log} 2>/dev/null &
	$cmd >${log} 2>&1 &
	echo $! >> ./pid
done
