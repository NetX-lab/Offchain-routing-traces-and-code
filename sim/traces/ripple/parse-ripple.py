import numpy as np
from pylab import *
from scipy import stats
import heapq

# Analysis of the recurring transactions in the Ripple trace, Figure 4, CoNEXT'19 Flash
def cdfPlot(val, xlabelname, ylabelname, filename):
	y_points = [0, 0.01, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1]
	x_points = [stats.scoreatpercentile(val.tolist(), item*100) for item in y_points]
	
	font = {'family' : 'sans-serif',
			'weight' : 'normal',
			'size'   : 14}
	matplotlib.rc('font', **font)

	#set appropriate figure width/height
	figure(figsize=(4, 3))
	fg = subplot(1,1,1)
	# Set appropriate margins, these values are normalized into the range [0, 1]
	subplots_adjust(left = 0.16, bottom = 0.26, right = 0.95, top = 0.95, wspace = 0.1, hspace = 0.1)
	fg.tick_params(axis='both', which='major', labelsize=14)
	majorLocator = MultipleLocator(0.2)
	minorLocator = MultipleLocator(0.1)
	fg.yaxis.set_major_locator(majorLocator)
	fg.yaxis.set_minor_locator(minorLocator)
	fg.xaxis.set_major_locator(majorLocator)
	fg.xaxis.set_minor_locator(minorLocator)
	fg.set_frame_on(True)
	fg.spines["top"].set_visible(False)
	# fg.spines["right"].set_visible(False)
	fg.spines['bottom'].set_color('darkgrey')
	fg.spines['left'].set_color('darkgrey')
	fg.spines['right'].set_color('white')

	grid(color='grey', linestyle=':', linewidth=0.5)

	fg.get_xaxis().tick_bottom () 
	fg.get_yaxis().tick_left ()
	fg.tick_params(axis='x', colors='grey')
	fg.tick_params(axis='y', colors='grey')

	plot(x_points, y_points, '-o', markersize=6, linewidth=1.5, markeredgewidth=0.0,  color='dodgerblue', label='Ripple')
	xlabel(xlabelname, fontsize=14)
	ylabel(ylabelname, fontsize=14)
	savefig(filename, format='pdf')

# this function returns percentage of recurring transactions and top-5 recurring transactions 
def perc_rep_trans (trans):
	s_nodes = []
	d_nodes = []

	# tuple of transaction: (sender, receiver, size) 
	for t in trans: 
		s_nodes.append(t[0])
		d_nodes.append(t[1])

	# remove duplicates
	s_nodes = list(set(s_nodes))
	d_nodes = list(set(d_nodes))
	nodes = list(set(s_nodes+d_nodes))

	count = np.zeros((len(s_nodes), len(d_nodes)))

	for t in trans: 
		i_src = s_nodes.index(t[0])
		i_dst = d_nodes.index(t[1])
		count[i_src][i_dst] += 1

	# iterate over each node 
	num_rep_trans = 0
	num_more5_rep_trans = 0
	num_top5_rep_trans = 0
	num_all_trans = 0
	for i in range(len(s_nodes)):
		s_dst = count[i]
		num_all_trans += sum(s_dst)
		rep_s = [s_dst[x] for x in range(len(s_dst)) if s_dst[x] > 1]
		if len(rep_s) > 0:
			num_rep_trans += sum(rep_s)
		if len(rep_s) > 10: 
			num_more5_rep_trans += sum(rep_s)
			num_top5_rep_trans += sum(heapq.nlargest(5, rep_s))
	return num_rep_trans, num_more5_rep_trans, num_top5_rep_trans, num_all_trans
	# return 1.0*num_rep_trans/num_all_trans, 1.0*num_top5_rep_trans/num_rep_trans  


nodes = []
tmp = []
count = 0
with open('transactions-in-USD-jan-2013-aug-2016.txt', 'r') as f:
	for line in f:
		tmp.append((line.split()[1], line.split()[2], line.split()[4]))

# sort transactions according to transaction time
sorted_tmp = sorted(tmp, key=lambda x: x[2])

initial_time = int(sorted_tmp[0][2])

ripple_trans = []
rep_trans_list = []
top5_rep_trans_list = []
days = 0

for t in sorted_tmp:
	ripple_trans.append((t[0], t[1], int(t[2])))

	if int(t[2]) > initial_time + 24*3600:
		num_rep_trans, num_more5_rep_trans, num_top5_rep_trans, num_all_trans = perc_rep_trans (ripple_trans)
		rep_trans_list.append(1.0*num_rep_trans/num_all_trans)

		if num_more5_rep_trans > 0:
		 	top5_rep_trans_list.append(1.0*num_top5_rep_trans/num_more5_rep_trans)
		initial_time = int(t[2])
		ripple_trans = []
		days += 1
print ('days ', days)


sorted_var = np.sort(rep_trans_list)
xlabelname = 'Percentage of recurring transactions'
ylabelname = 'CDF'
filename = 'repeated-trans.pdf'
cdfPlot(sorted_var, xlabelname, ylabelname, filename)

sorted_var = np.sort(top5_rep_trans_list)
xlabelname = 'Percentage of top-5 recurring transactions'
ylabelname = 'CDF'
filename = 'top5-repeated-trans.pdf'
cdfPlot(sorted_var, xlabelname, ylabelname, filename)