# Simulation 

## Getting Started 

### Source file structure

* Trace files are in [traces](traces) 
* Scheme sources are in [routing](routing)
* Scripts to process results are in [result](result) 
* 'main.py' is the main code to run experiments. Run experiments using the following command: 
```
$ python main.py <trace> <nflows> <exp>
```

### Steps
* Create a virtual environment

```bash
# check and make sure Python >=3.6
virtualenv --python python3 "reproduce" 
source "reproduce/bin/activate"
pip install --upgrade pip
```
* Install dependencies

``` bash
pip install -r requirements.txt 
```
* Take ripple trace for example, to reproduce results for Fig. 3, run

```bash
python ripple-val.py 
```
To reproduce results for Fig. 4, run 

```bash
python parse-ripple.py
```
* To generate raw data for Fig. 6, 7, 8, 10, 11, run 

```bash
bash run.sh 
```
* Run scripts in [result](result) to generate all figures in the evaluation 
