SETGOPATH=GOPATH=$(shell pwd)

build-go-scripts:
	$(SETGOPATH) go build server
	$(SETGOPATH) go build parse_graph

do-generate-trace:
	cd src/gen_trace; python test.py

do-parse-graph:
	# the parameter specifies the number of nodes (default 10, set in "src/gen_trace/test.py")
	cd src/parse_graph; ./load_cfg.sh 10

do-run-servers:
	cd src/server; ./load_cfg.sh
	# first parameter: number of nodes, second parameter: algorithm (0=flash, 1=shortest path, 2=spider)
	cd src/server; ./run.sh 10 0

do-check-running-servers:
	cd src/server; ./ana_tr.sh

do-kill-running-servers:
	cd src/server; ./kill.sh
