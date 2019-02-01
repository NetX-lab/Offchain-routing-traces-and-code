from pylab import *
import sys

num = sys.argv[1]

# node=50
if num == '50':
	flash = [4.204671473, 4.159551287, 4.356845343]
	min_flash = [3.970112724, 3.930160976, 4.246276783] 
	max_flash = [4.458988063, 4.334947275, 4.498226858]
	spider = [5.696601542, 5.679029243, 5.904976934]
	min_spider = [5.451196726, 5.448042409, 5.694110808] 
	max_spider = [5.867379282, 5.93401236, 6.080356367]
	shortest_path = [1, 1, 1]
#min_sp = []
#max_sp = []
# node=100

if num == '100':
	flash = [4.11673094, 4.263863536, 4.220976628]
	min_flash = [3.932552157, 4.061564087, 4.113331754] 
	max_flash = [4.298439848, 4.645313844, 4.327481132]
	spider = [5.564120852, 5.715572174, 5.738251267]
	min_spider = [5.407729133, 5.445314627, 5.584572546] 
	max_spider = [5.690647216, 5.966027157, 5.862798683]
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


#ax.legend((p1[0], p2[0], p3[0]), schemes, loc=2, ncol=3)

xlabel('Link Capacity (USD)', fontsize = 16)
ylabel('Normalized Processing Delay', fontsize = 16)

# ax.autoscale_view()

plt.savefig('testbed-ovh-short-' + num + '.eps', format='eps')





