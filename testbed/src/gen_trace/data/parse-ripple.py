import numpy as np
from pylab import *
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

def perc_rep_trans (trans):
	nodes = []
	s_nodes = []
	d_nodes = []

	# tuple of transaction: (sender, receiver, size) 
	for t in trans: 
		s_nodes.append(t[0])
		d_nodes.append(t[1])

	s_nodes = list(set(s_nodes))
	d_nodes = list(set(d_nodes))
	nodes = list(set(s_nodes+d_nodes))

	count = np.zeros((len(s_nodes), len(d_nodes)))

	for t in trans: 
		i_src = s_nodes.index(t[0])
		i_dst = d_nodes.index(t[1])
		count[i_src][i_dst] += 1

	# iterate over each node 
	num_dup_sender = 0
	num_dup_trans = 0
	num_all_trans = 0
	for i in range(len(s_nodes)):
		s_dst = count[i]
		num_all_trans += sum(s_dst)
		dup_s = [s_dst[x] for x in range(len(s_dst)) if s_dst[x] > 1]
		if len(dup_s) > 0:
			num_dup_sender += 1
			num_dup_trans += sum(dup_s)
	
	return 1.0*num_dup_sender/len(s_nodes), 1.0*num_dup_trans/num_all_trans 



nodes = []
tmp = []
count = 0
with open('transactions-in-USD-jan-2013-aug-2016.txt', 'r') as f:
	for line in f:
		# if count > 100000: 
		# 	break  

		tmp.append((line.split()[1], line.split()[2], line.split()[4]))
		# count += 1

# sort transactions according to transaction time
sorted_tmp = sorted(tmp, key=lambda x: x[2])

initial_time = int(sorted_tmp[0][2])

ripple_trans = []
rep_nodes_list = []
rep_trans_list = []
days = 0

for t in sorted_tmp:
	ripple_trans.append((t[0], t[1], int(t[2])))

	if int(t[2]) > initial_time + 24*3600:
		rep_nodes, rep_trans = perc_rep_trans (ripple_trans)
		rep_nodes_list.append(rep_nodes)
		rep_trans_list.append(rep_trans)
		initial_time = int(t[2])
		ripple_trans = []
		days += 1
print 'days ', days

sorted_var = np.sort(rep_nodes_list)
xlabelname = 'Percentage of senders with recurring transactions'
ylabelname = 'Percentage of days'
filename = 'repeatedsenders.pdf'
cdfPlot(sorted_var, xlabelname, ylabelname, filename)

sorted_var = np.sort(rep_trans_list)
xlabelname = 'Percentage of recurring transactions'
ylabelname = 'Percentage of days'
filename = 'repeatedtrans.pdf'
cdfPlot(sorted_var, xlabelname, ylabelname, filename)
