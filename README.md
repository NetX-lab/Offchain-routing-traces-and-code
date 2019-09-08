# Traces and code for offchain routing

The repo contains the topology and transaction traces of some offchain networks we collect. They are used to evaluate [Flash](https://arxiv.org/abs/1902.05260), a dynamic routing solution we develop for offchain networks. 

The repo also contains our code for both simulation and testbed implementation of Flash, as well as a set of state-of-the-art routing algorithms.

We hope they would be useful for people who work on offchain networks.

## About the traces

The traces are in [sim/traces](sim/traces). It has two parts for both networks:

### Topology
* Ripple Network (1,870 nodes and 17,416 edges) 
* Lightning Network (2,511 nodes and 36,016 edges)

### Transaction Datasets
* 2.6 million transactions in Ripple (January 2013 to November 2016)
* 103 million transactions from Bitcoin for Lightning (January 2009 to October 2018)

## Getting Started 

* Testbed code: check README.md in [testbed](testbed)
* Simulation code: check README.md in [sim](sim)

### Dependencies

* Testbed code: Golang, see `Makefile`
* Simulation code: Python dependencies: Python >=3.6, and see `requirements.txt`

## Reference

Flash: Efficient Dynamic Routing for Offchain Networks. Peng Wang, Hong Xu, Xin Jin, Tao Wang.

ACM CoNEXT 2019.

[https://arxiv.org/abs/1902.05260](https://arxiv.org/abs/1902.05260).
