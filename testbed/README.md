## Testbed
Steps to reproduce testbed experiments:

1. generate nodes topology and requests according to real-world trace (folder [src/gen_trace](https://github.com/NetX-lab/Offchain-routing-traces-and-code/tree/master/testbed/src/gen_trace))
2. parse the trace files from step 1 to generate configuration file for each node (folder [src/parse_graph](https://github.com/NetX-lab/Offchain-routing-traces-and-code/tree/master/testbed/src/parse_graph)
3. emulate each node (i.e. unique ip/port pair) and start the experiment (folder [src/comm](https://github.com/NetX-lab/Offchain-routing-traces-and-code/tree/master/testbed/src/comm) and [src/server](https://github.com/NetX-lab/Offchain-routing-traces-and-code/tree/master/testbed/src/server))

Note that we use `golang 1.11` to write our codes. You should `go build` in `[src/parse_graph]` and `[src/server]` folders to get the excutables.

### 1. Generate trace
Using `python test.py` will generate 3 files (i.e. `graph.txt`, `payments.txt` and `path.txt`). 

| file | description | format |
|-----|-----|-----|
| `graph.txt` | node topology | `[src_node],[dst_node],[capacity]`|
| `payments.txt` | requests | `[src_node],[dst_node],[request size]` |
| `path.txt` | path | `[src_node],[dst_node],[path(several nodes)]` |

In `test.py`, you may change the size of node topology (i.e. `num_node`), number of payments (i.e. `nflows`) and request size distribution (i.e. `ripple_val.csv`).

### 2. Generate node configuration file
Using `./load_cgf.sh [#node]` (note that `[#node]` should be identical to the `num_node` used in step 1) to parse the files (i.e. `graph.txt payments.txt path.txt`) obtained from step 1 to generate configuration files for each node.

| file name format | description | format |
|-----|-----|-----|
|`[node_num].json` (e.g. `1.json`) | node configuration | json format containing `ip/port` |
|`n[node_num].json` (e.g. `n1.json`) | neighbour configuration | json format containing `ip/port` and `capacity` for each neighbour |
|`tr[node_num].txt` (e.g. `tr1.txt`) | node's requests submitted | `[src_node],[dst_node],[request size]` |
|`pa[node_num].txt` (e.g. `pa1.txt`) | path to other nodes | `[dst_node],[path(several nodes)]` | 


### 3. Start experiment
Using `./load_cgf.sh` to get the configuration files obtained from step 2. 

To start the experiment, just run `./run.sh [#num_node] [#algo]` (note that `[#num_node]` should be identical to the value used in previous steps and by using `[#algo]`, 0 is for Flash, 1 is for Shortest Path and 2 is for Spider). This progress will generate one `pid` file, which cantains the pids of our emulated nodes, and multiple log files.

In a not-that-graceful way, we can use `grep finished *.log | wc -l` to monitor whether the whole progress is done. If the output is equal to the `[#num_node]`, it is done. Otherwise, just wait and re-check.

Finally, using script `./kill.sh` to terminate the emulated nodes and analyze the results (i.e. log files) using script `./ana_tr.sh`. Below is the description of the analysis output.

| field | description |
|-----|-----|
| `s_ovh` | average executing time of small requests |
| `l_ovh` | average executing time of large requests |
| `succ` | number of successful payments |
| `fail` | number of failed payments |
| `succ_ratio` | successful ratio |
| `succ_vol` | sum of successful completed payments volume |
| `t_ovh` | average executing time of total requests|
| `n_probe` | number of PORBE msg |
| `n_commit` | number of COMMIT msg |
| `n_reverse` | number of REVERSE msg |
| `n_confirm` | number of CONFIRM msg |

