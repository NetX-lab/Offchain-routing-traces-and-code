from pylab import *
import sys


num_flows = 2000
trace = sys.argv[1]


schemes = [' ', 'Flash', 'Spider', ' ']

# msgs = [5584, 8040, 14223] # Ripple 

# msgs = [5075, 12141, 19253] # Lightning

msgs = [0, 8040, 14223, 0] # Ripple 
# msgs = [5075, 12141, 19253] # Lightning


font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 22}

matplotlib.rc('font', **font)

fig, ax = plt.subplots()
N = 4
ind = np.arange(N)    # the x locations for the groups
width = 0.2      # the width of the bars: can also be len(x) sequence

# msg = [msgs[0], msgs[1], msgs[2], msgs[3], msgs[4]]

rects1 = ax.bar(0.12, msgs[0], width, facecolor = 'mediumseagreen', edgecolor = 'mediumseagreen')
rects2 = ax.bar(0.12+2*width, msgs[1], width, facecolor = 'orangered', edgecolor = 'orangered')
rects3 = ax.bar(0.12+2*width+2*width, msgs[2], width, facecolor = 'dodgerblue', edgecolor = 'dodgerblue')
rects3 = ax.bar(0.12+2*width+2*width+2*width, msgs[3], width, facecolor = 'dodgerblue', edgecolor = 'dodgerblue')


fig.subplots_adjust(bottom=0.12,left=0.12,right=0.99,top=0.95)

xticks([0.12+width/2, 0.12+2.5*width, 0.12+4.5*width, 0.12+6.5*width])
ax.set_xticklabels(schemes, rotation='horizontal')
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

xlabel('Schemes', fontsize = 24)
ylabel('Number of Probing Messages', fontsize = 24)

plt.savefig('figs/'+trace+'-probing-overhead.pdf', format='pdf')





