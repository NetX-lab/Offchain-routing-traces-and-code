import random

with open('BitcoinValAll.txt') as file:
    reader = file.readlines()
    with open('BitcoinVal.txt', 'w+') as wfile:
    	count = 0
    	while count < 1000000: 
    		wfile.write(reader[random.randint(0,103168200)])
    		count += 1
file.close()
wfile.close()

