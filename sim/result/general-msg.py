from pylab import *
import sys


num_flows = 2000

scale_factor = ['1', '20', '40', '60', '80', '100']

volumes = []
ratios = []
msgs = []

schemes = ['sp', 'speedymurmurs', 'waterfilling', 'flash']
cnt_scheme = 0
for scheme in schemes: 
	with open(scheme+'-'+str(num_flows)+'.txt') as f:
		volume = []
		ratio = []
		msg = []
		metrics =[volume, ratio, msg]

		cnt_line = 0
		for line in f:  
			data = line.split()
			for i in range(len(data)):
				metrics[cnt_line].append(float(data[i]))
			cnt_line += 1
			if cnt_line > 2:
				break
	volumes.append(volume)
	ratios.append(ratio) 
	msgs.append(msg)
	cnt_scheme += 1

font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 12}

matplotlib.rc('font', **font)


fig, ax = plt.subplots()
N = 4
ind = np.arange(N)    # the x locations for the groups
width = 0.2      # the width of the bars: can also be len(x) sequence

msg = [sum(msgs[0])/len(msgs[1]), sum(msgs[1])/len(msgs[1]), sum(msgs[2])/len(msgs[2]), sum(msgs[3])/len(msgs[3])]
schemes = ('Shortest Paths', 'SpeedyMurmurs', 'Spider', 'Flash')

rects1 = ax.bar(0.12, msg[0], width, facecolor = 'orangered', edgecolor = 'orangered')
rects2 = ax.bar(0.12+2*width, msg[1], width, facecolor = 'mediumseagreen', edgecolor = 'mediumseagreen')
rects3 = ax.bar(0.12+2*width+2*width, msg[2], width, facecolor = 'dodgerblue', edgecolor = 'dodgerblue')
rects4 = ax.bar(0.12+2*width+2*width+2*width, msg[3], width, facecolor = 'darkorange', edgecolor = 'darkorange')

fig.subplots_adjust(bottom=0.11,left=0.11,right=0.99,top=0.95)

xticks([0.12+width/2, 0.12+2.5*width, 0.12+4.5*width, 0.12+6.5*width])
ax.set_xticklabels(schemes, rotation='horizontal', fontsize = 12)
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

xlabel('Schemes', fontsize = 14)
ylabel('Probing Messages', fontsize = 14)

plt.savefig('messages.pdf', format='pdf')





