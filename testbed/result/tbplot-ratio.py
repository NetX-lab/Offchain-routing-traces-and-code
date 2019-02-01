from pylab import *
import sys

num = sys.argv[1]

# node=50
if num == '50':
	flash = [65.04, 66.306, 65.906]
	min_flash = [63.51, 65.23, 64.89] 
	max_flash = [67.09, 67.47, 66.57]
	spider = [67.22, 68.554, 73.546]
	min_spider = [66.17, 67.31, 70.59] 
	max_spider = [68.29, 69.69, 74.88]
	shortest_path = [46.35, 48.586, 49.862]
	min_sp = [45.55, 46.31, 49.36]
	max_sp = [48.57, 49.7, 50.73]
# node=100

if num == '100':
	flash = [64.352, 65.77, 67.862]
	min_flash = [62.99, 61.36, 65.79] 
	max_flash = [65.79, 68.02, 69.54]
	spider = [70.328, 73, 73.706]
	min_spider = [69.29, 72.57, 73.19] 
	max_spider = [70.9, 73.35, 74.14]
	shortest_path = [54.908, 57.294, 60.308]
	min_sp = [53.23, 55.96, 59.22]
	max_sp = [57.13, 58.29, 62.11]



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
	min_sp[i] = shortest_path[i]-min_sp[i]
	max_sp[i] = max_sp[i]-shortest_path[i]
	min_spider[i] = spider[i]-min_spider[i]
	max_spider[i] = max_spider[i]-spider[i]

p1 = ax.bar(0.12 + ind, flash, width, yerr=[min_flash, max_flash], fill=False, edgecolor = 'red', ecolor = 'black', hatch="/", error_kw=dict(capsize=3))
p2 = ax.bar(0.12 + ind + width, spider, width, yerr=[min_spider, max_spider], fill=False, edgecolor = 'green', ecolor = 'black', hatch="x", error_kw=dict(capsize=3))
p3 = ax.bar(0.12 + ind + 2*width, shortest_path, width, yerr=[min_sp, max_sp], fill=False, edgecolor = 'purple',ecolor = 'black', hatch="\\", error_kw=dict(capsize=3))

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
ylabel('Succ. Ratio (%)', fontsize = 16)

# ax.autoscale_view()

plt.savefig('testbed-ratio-' + num + '.eps', format='eps')





