from pylab import *
import sys

tr = sys.argv[1]

# ripple trace
if tr == 'ripple':
	w_opt = [1.798, 1.713, 2.1]
	wo_opt = [2.712, 2.852, 2.826]

# lightning trace
if tr == 'lightning':
	w_opt = [0.992, 0.816, 0.680]
	wo_opt = [1.641, 1.343, 1.223]



xaxislabel = ['1000', '2000', '4000']
schemes = ['w/ optimization', 'w/o optimization']

font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 16}

matplotlib.rc('font', **font)


fig, ax = plt.subplots()
N = 3
ind = np.arange(N)    # the x locations for the groups
width = 0.2      # the width of the bars: can also be len(x) sequence

p1 = ax.bar(0.2+ind, w_opt, width, fill=False, edgecolor = 'red', ecolor = 'black', hatch="/")
p2 = ax.bar(0.2+ind + width, wo_opt, width, fill=False, edgecolor = 'green', ecolor = 'black', hatch="x")

fig.subplots_adjust(bottom=0.12,left=0.1,right=0.95,top=0.95)

#xticks([0.12+width/2, 0.12+2.5*width, 0.12+4.5*width, 0.12+6.5*width])
ax.set_xticks(0.2+ind + width/2)
ax.set_xticklabels(xaxislabel, rotation='horizontal', fontsize = 16)
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
# ax.yaxis.get_major_formatter().set_powerlimits((0,1)) 
# ax.grid(True)
# grid(color='grey', linestyle=':', linewidth=0.5)

if tr == 'lightning':
	ax.legend((p1[0], p2[0]), schemes, loc=1, ncol=1, frameon=False)


xlabel('Number of Transactions', fontsize = 16)
if tr == 'ripple':
	ylabel('Ratio of Transactions Fees to Volume (%)', fontsize = 16)
if tr == 'lightning':
	ylabel('Ratio of Transactions Fees to Volume (%)', fontsize = 16)

# ax.autoscale_view()

output_name='cost-' + tr + '.eps'
plt.savefig(output_name, format='eps')





