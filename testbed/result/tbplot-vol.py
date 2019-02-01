from pylab import *
import sys

num = sys.argv[1]

# node=50
if num == '50':
	flash = [638760.2, 868110.8, 1048706]
	min_flash = [607099, 842550, 1018510] 
	max_flash = [668894, 921816, 1094700]
	spider = [453654.2, 597891, 740999.4]
	min_spider = [429717, 572487, 706428] 
	max_spider = [486750, 619439, 771363]
	shortest_path = [129694.2, 187491.6, 242757.6]
	min_sp = [128920, 186149, 240291]
	max_sp = [130168, 188900, 245008]

# node=100

if num == '100':
	flash = [615616.2, 874677.2, 1083428]
	min_flash = [609646, 858385, 1058480] 
	max_flash = [620520, 892741, 1109930]
	spider = [473440.6, 637105, 797594.8]
	min_spider = [458884, 615322, 785775] 
	max_spider = [485349, 658262, 810242]
	shortest_path = [169077.8, 234994.4, 297760.8]
	min_sp = [166138, 233418, 295696]
	max_sp = [171677, 237412, 300843]



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
# ax.set_frame_on(True)

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


ax.legend((p1[0], p2[0], p3[0]), schemes, loc=2, ncol=3, fancybox=False, frameon=False)

xlabel('Link Capacity (USD)', fontsize = 16)
ylabel('Succ. Volume (USD)', fontsize = 16)

# ax.autoscale_view()

plt.savefig('testbed-vol-' + num + '.eps', format='eps')





