import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import csv
from scipy import stats

def cdfPlot(val, xlabelname, ylabelname, filename):
	x_points = []
	for i in np.arange(0,100,10):
		x_points.append(stats.scoreatpercentile(val, i))
	x_points.append(stats.scoreatpercentile(val, 95))
	x_points.append(stats.scoreatpercentile(val, 99))
	x_points.append(stats.scoreatpercentile(val, 100))


	y_points = [0, 0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95, 0.99, 1]

	font = {'family' : 'sans-serif',
	        'weight' : 'normal',
	        'size'   : 8}
	matplotlib.rc('font', **font)

	#set appropriate figure width/height
	figure(figsize=(4.5, 2.5))
	fg = subplot(1,1,1)
	# Set appropriate margins, these values are normalized into the range [0, 1]
	subplots_adjust(left = 0.17, bottom = 0.17, right = 0.95, top = 0.95, wspace = 0.1, hspace = 0.1)
	# fg.set_yticklabels(['0','0', '0.2', '0.4', '0.6', '0.8', '1'])
	# g.tick_params(axis='both', which='major', labelsize=10)
	# majorLocator = MultipleLocator(0.2)
	# minorLocaftor = MultipleLocator(0.1)
	# fg.yaxis.set_major_locator(majorLocator)
	# fg.yaxis.set_minor_locator(minorLocator)
	grid(True)
	plot(x_points, y_points, '-x', markersize=6, linewidth=1.5, color='blue', label='Ripple')
	xlabel(xlabelname, fontsize=10)
	# xlabel('Percentage of duplicated receivers', fontsize=10)
	ylabel(ylabelname, fontsize=10)
	savefig(filename, format='pdf')



def main():  	
  	srcNodes = []
  	dstNodes = []
  	payments = []
  	microPayments = []
	with open('ripple_val.csv', 'r') as f: 
		csv_reader = csv.reader(f, delimiter=',')
		for row in csv_reader:
			# srcNodes.append(int(row[0]))
			# dstNodes.append(int(row[1]))
			# RippleSrcDst.append((int(row[0]), int(row[1])))
			# RippleVal.append(float(row[2])) 
			if float(row[2]) > 0: 
				payments.append((int(row[0]), int(row[1]), float(row[2])))

	sorted_payments = sorted(payments, key=lambda x: x[2])
	for i in range(int(0.9*len(sorted_payments))):
		microPayments.append(sorted_payments[i])
		srcNodes.append(sorted_payments[i][0])
		dstNodes.append(sorted_payments[i][1])

	srcNodes = list(set(srcNodes))
	dstNodes = list(set(dstNodes))

	count = np.zeros((len(srcNodes), len(dstNodes)))

	for tran in microPayments:
		src = tran[0] 
		dst = tran[1]
 		srcIndex = srcNodes.index(src)
 		dstIndex = dstNodes.index(dst)
 		count[srcIndex][dstIndex] += 1


 	percentageDupTransSet = [] # sender transact with the receiver more than 2 times. Element is the number of transactions 
 	percentageTransSet = [] # only for sender with more than 5 different receivers 

 	duplicateCount = 0
 	totalCount = 0
 	dupSenders = 0 # number of senders transact with any receiver more than 2 times
 	for i in range(len(srcNodes)):
		sortedList = sorted(count[i])
		nonzero = [sortedList[x] for x in range(len(sortedList)) if sortedList[x] != 0]
		duplicate = [sortedList[x] for x in range(len(sortedList)) if sortedList[x] > 1]

		if len(nonzero) > 1: 
			totalCount += 1

			if len(duplicate) > 0:
				duplicateCount += 1 

		if len(duplicate) > 0: 
			dupSenders += 1
			percentageDupTrans = 1.0*sum(duplicate)/sum(nonzero) 
			percentageDupTransSet.append(percentageDupTrans)

		if len(nonzero) > 5: # transact with more than 5 different receivers
			percentageTrans = 1.0*sum(sortedList[-5:])/sum(count[i])
			percentageTransSet.append(percentageTrans)

	print 'number of sender with duplicated transactions', dupSenders, len(srcNodes), 1.0*dupSenders/len(srcNodes)

	print 'sender with more than 1 receiver', duplicateCount, totalCount, 1.0*duplicateCount/totalCount

	print 'number of senders transacting with more than 5 different receivers', len(percentageTransSet)

	sorted_var = np.sort(percentageTransSet)
	xlabelname = 'Percentage of transactions for top 5 frequent receivers'
	ylabelname = 'CDF'
	filename = 'repeatedTranstop5.pdf'
	cdfPlot(sorted_var, xlabelname, ylabelname, filename)

	sorted_var = np.sort(percentageDupTransSet)
	xlabelname = 'Percentage of transactions for frequent receivers'
	ylabelname = 'CDF'
	filename = 'repeatedTrans.pdf'
	cdfPlot(sorted_var, xlabelname, ylabelname, filename)



if __name__ == "__main__":
	main()
