from pylab import *
import sys

num = sys.argv[1]

# node=50
if num == '50':
	flash = [4.415919191, 4.398534863, 4.573183643]
	min_flash = [4.186057724, 4.167597683, 4.51525831] 
	max_flash = [4.599937704, 4.55607421, 4.687916687]
	spider = [5.469876824, 5.442553797, 5.685097748]
	min_spider = [5.257104285, 5.215624862, 5.514665977] 
	max_spider = [5.580569932, 5.618110884, 5.850621205]
	shortest_path = [1, 1, 1]
#min_sp = []
#max_sp = []
# node=100
if num == '100':
	flash = [4.282444342, 4.438523715, 4.360233939]
	min_flash = [4.149103893, 4.177122716, 4.255737337] 
	max_flash = [4.432481165, 4.864348618, 4.46758384]
	spider = [5.311103284, 5.422669976, 5.445971675]
	min_spider = [5.138189754, 5.166480893, 5.349210888] 
	max_spider = [5.509163397, 5.630480911, 5.588801124]
	shortest_path = [1, 1, 1]
#min_sp = []
#max_sp = []



xaxislabel = ['rand[1000,1500)', 'rand[1500,2000)', 'rand[2000,2500)']
schemes = ['Flash', 'Spider', 'SP']

font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 16}

matplotlib.rc('font', **font)


fig, ax = plt.subplots()
N = 3
ind = np.arange(N)    # the x locations for the groups
width = 0.2      # the width of the bars: can also be len(x) sequence

#cal yerr
for i in range(N):
	min_flash[i] = flash[i]-min_flash[i]
	max_flash[i] = max_flash[i]-flash[i]
	min_spider[i] = spider[i]-min_spider[i]
	max_spider[i] = max_spider[i]-spider[i]

p1 = ax.bar(0.12 + ind, flash, width, yerr=[min_flash, max_flash], fill=False, edgecolor = 'red', ecolor = 'black', hatch="/", error_kw=dict(capsize=3))
p2 = ax.bar(0.12 + ind + width, spider, width, yerr=[min_spider, max_spider], fill=False, edgecolor = 'green', ecolor = 'black', hatch="x", error_kw=dict(capsize=3))
p3 = ax.bar(0.12 + ind + 2*width, shortest_path, width, fill=False, edgecolor = 'purple',ecolor = 'black', hatch="\\")

fig.subplots_adjust(bottom=0.11,left=0.11,right=0.99,top=0.95)

#xticks([0.12+width/2, 0.12+2.5*width, 0.12+4.5*width, 0.12+6.5*width])
ax.set_xticks(0.2 + ind + 2*width/2)
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


# ax.legend((p1[0], p2[0], p3[0]), schemes, loc=2, ncol=3)

xlabel('Link Capacity (USD)', fontsize = 16)
ylabel('Normalized Processing Delay', fontsize = 16)

# ax.autoscale_view()

plt.savefig('testbed-ovh-sum-' + num + '.eps', format='eps')





