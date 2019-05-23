from pylab import *
import sys


num_flows = 2000
trace = sys.argv[1]


cache_paths = ['0', '2', '4', '6', '8']

volumes = []
ratios = []
hits = []
num_table_entry = []
msgs = []


with open('rawdata/'+trace+'-cache.txt') as f:
	metrics =[volumes, ratios, hits, num_table_entry, msgs]

	cnt_line = 0
	for line in f:  
		data = line.split()
		for i in range(len(data)):
			metrics[cnt_line].append(float(data[i]))
		cnt_line += 1

	ratios = [ele*100 for ele in ratios]

font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 22}

matplotlib.rc('font', **font)


fig, ax = plt.subplots()
N = 4
ind = np.arange(N)    # the x locations for the groups
width = 0.1      # the width of the bars: can also be len(x) sequence

# msg = [msgs[0], msgs[1], msgs[2], msgs[3], msgs[4]]
schemes = ('0', '2', '4', '6', '8')

# rects1 = ax.bar(0.12, msgs[0], width, facecolor = 'orangered', edgecolor = 'orangered')
# rects2 = ax.bar(0.12+2*width, msgs[1], width, facecolor = 'dodgerblue', edgecolor = 'dodgerblue')
# rects3 = ax.bar(0.12+2*width+2*width, msgs[2], width, facecolor = 'dodgerblue', edgecolor = 'dodgerblue')
# rects4 = ax.bar(0.12+2*width+2*width+2*width, msgs[3], width, facecolor = 'dodgerblue', edgecolor = 'dodgerblue')
# rects5 = ax.bar(0.12+2*width+2*width+2*width+2*width, msgs[3], width, facecolor = 'dodgerblue', edgecolor = 'dodgerblue')

rects1 = ax.bar(0.12, volumes[0], width, facecolor = 'orangered', edgecolor = 'orangered')
rects2 = ax.bar(0.12+2*width, volumes[1], width, facecolor = 'dodgerblue', edgecolor = 'dodgerblue')
rects3 = ax.bar(0.12+2*width+2*width, volumes[2], width, facecolor = 'dodgerblue', edgecolor = 'dodgerblue')
rects4 = ax.bar(0.12+2*width+2*width+2*width, volumes[3], width, facecolor = 'dodgerblue', edgecolor = 'dodgerblue')
rects5 = ax.bar(0.12+2*width+2*width+2*width+2*width, volumes[3], width, facecolor = 'dodgerblue', edgecolor = 'dodgerblue')


fig.subplots_adjust(bottom=0.11,left=0.11,right=0.99,top=0.95)

xticks([0.12+width/2, 0.12+2.5*width, 0.12+4.5*width, 0.12+6.5*width, 0.12+8.5*width])
ax.set_xticklabels(schemes, rotation='horizontal', fontsize = 20)
ax.set_frame_on(True)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines['bottom'].set_color('darkgrey')
ax.spines['left'].set_color('darkgrey')

ax.get_xaxis().tick_bottom ()
ax.get_yaxis().tick_left ()
ax.tick_params(axis='x', colors='grey')
ax.tick_params(axis='y', colors='grey')

ax = plt.gca() 
ax.yaxis.get_major_formatter().set_powerlimits((0,1)) 
# ax.grid(True)
# grid(color='grey', linestyle=':', linewidth=0.5)

# xlabel('Number of Paths Per Receiver', fontsize = 24)
# ylabel('Number of Probing Messages', fontsize = 24)

# plt.savefig('cache-overhead.pdf', format='pdf')

xlabel('Number of Paths Per Receiver', fontsize = 24)
ylabel('Succ. Volume (USD)', fontsize = 24)

plt.savefig('figs/cache-volume.pdf', format='pdf')



