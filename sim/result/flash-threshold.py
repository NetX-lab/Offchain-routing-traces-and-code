from pylab import *
import sys

trace = sys.argv[1]

matplotlib.rcParams['axes.linewidth'] = 0.75

num_flows = 2000

thresholds = ['0', '0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']

volumes = []
ratios = []
messages = []


with open('rawdata/'+trace+'-threshold.txt') as f:
	metrics =[volumes, ratios, messages]

	cnt_line = 0
	for line in f:  
		data = line.split()
		for i in range(len(data)):
			metrics[cnt_line].append(float(data[i]))
		cnt_line += 1

	ratios = [ele*100 for ele in ratios]

font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 11}

matplotlib.rc('font', **font)



figure(figsize=(3.5, 2.5))

fg = subplot(1,1,1)# Set appropriate figure width/height


# Set appropriate margins, these values are normalized into the range [0, 1]
subplots_adjust(left = 0.2, bottom = 0.17, right = 0.88, top = 0.92, 
        wspace = 0.1, hspace = 0.1)

fg.set_frame_on(True)
fg.spines["top"].set_visible(False)
# fg.spines["right"].set_visible(False)
fg.spines['bottom'].set_color('darkgrey')
fg.spines['left'].set_color('darkgrey')
fg.spines['right'].set_color('darkgrey')

grid(color='grey', linestyle=':', linewidth=0.5)

# ax1 = fg.add_subplot(111)
fg.plot(volumes, '-o', markersize=4, linewidth=1.5, color='dodgerblue', label='Success Volume', markerfacecolor='none', markeredgewidth=1, markeredgecolor='dodgerblue' )
fg.set_xlabel('Percentage of Mice Payments (%)')
if trace == 'ripple':
	fg.set_ylabel('Succ. Volume (USD)', color='dodgerblue',)
else: 
	fg.set_ylabel('Succ. Volume (Satoshi)', color='dodgerblue',)
ax = plt.gca() 
ax.yaxis.get_major_formatter().set_powerlimits((0,1)) 

fg2 = fg.twinx()  # this is the important function
fg2.plot(messages, '-D', markersize=4, linewidth=1.5, color='orangered', label='Avg Routing Table Size', markerfacecolor='none', markeredgewidth=1, markeredgecolor='orangered')
fg2.set_ylabel('Probing Messages', color='orangered',)


# leg = legend(loc = 'upper left', fontsize = '8', fancybox=False, frameon=True)
# leg.get_frame().set_facecolor('ghostwhite')
# leg.get_frame().set_edgecolor('none')

fg.get_xaxis().tick_bottom () 
fg.get_yaxis().tick_left ()
# majorLocator = MultipleLocator(2e9)
# fg.yaxis.set_major_locator(majorLocator)
# fg.set_xticks([4e9, 6e9, 8e9, 10e9, 12e9])
# fg.set_yticklabels([4, 6, 8, 10, 12])
#fg.xaxis.label.set_color('darkgrey')
#fg.yaxis.label.set_color('darkgrey')
fg.tick_params(axis='x', colors='grey')
fg.tick_params(axis='y', colors='dodgerblue')
fg2.tick_params(axis='x', colors='grey')
fg2.tick_params(axis='y', colors='orangered')

fg.set_yticks(np.linspace(fg.get_yticks()[0], fg.get_yticks()[-1], len(fg2.get_yticks())))
# fg2.set_ylim(0, 12)
majorLocator = MultipleLocator(1)
fg.xaxis.set_major_locator(majorLocator)
fg.set_xticklabels(thresholds)
# majorLocator = MultipleLocator(2)
# minorLocator = MultipleLocator(5)
# fg.yaxis.set_major_locator(majorLocator)
#fg.yaxis.set_minor_locator(minorLocator)
grid(True)

 
ax = plt.gca() 
ax.yaxis.get_major_formatter().set_powerlimits((0,1)) 

savename = trace+'-flash-threshold.pdf'
savefig('figs/'+savename, format='pdf')



