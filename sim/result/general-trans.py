from pylab import *
import sys

matplotlib.rcParams['axes.linewidth'] = 0.75

trace = sys.argv[1]
typ = sys.argv[2]


# scale_factor = ['1', '20', '40', '60', '80', '100']

volumes = []
ratios = []
msgs = []

num_flows_list = [1000, 2000, 3000, 4000, 5000, 6000]


schemes = ['sp', 'speedymurmurs', 'waterfilling', 'flash']
cnt_scheme = 0
for scheme in schemes: 
	volume = []
	ratio = []
	msg = []
	for num_flows in num_flows_list: 
		with open(trace+'-'+scheme+'-'+str(num_flows)+'.txt') as f:
			metrics =[volume, ratio, msg]

			cnt_line = 0
			for line in f:  
				data = line.split()
				metrics[cnt_line].append(float(data[1]))
				cnt_line += 1
				if cnt_line > 2:
					break
	ratio = [ele*100 for ele in ratio]
	volumes.append(volume)
	ratios.append(ratio) 
	msgs.append(msg)
	cnt_scheme += 1

font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 12}

matplotlib.rc('font', **font)



figure(figsize=(3.5, 2.5))

fg = subplot(1,1,1)# Set appropriate figure width/height


# Set appropriate margins, these values are normalized into the range [0, 1]
subplots_adjust(left = 0.18, bottom = 0.17, right = 0.95, top = 0.92, 
        wspace = 0.1, hspace = 0.1)

fg.set_frame_on(True)
fg.spines["top"].set_visible(False)
fg.spines["right"].set_visible(False)
fg.spines['bottom'].set_color('darkgrey')
fg.spines['left'].set_color('darkgrey')
fg.get_xaxis().tick_bottom () 
fg.get_yaxis().tick_left ()
#fg.xaxis.label.set_color('darkgrey')
#fg.yaxis.label.set_color('darkgrey')
fg.tick_params(axis='x', colors='grey')
fg.tick_params(axis='y', colors='grey')
if typ == 'ratio': 
	fg.set_ylim([0, 105])
grid(color='grey', linestyle=':', linewidth=0.5)

# for i in range(3):
# 	print [a/b for a, b in zip(volumes[3], volumes[i])] 

if typ == 'volume':
	plot(volumes[3], '-x', markersize=4, linewidth=1.5, color='darkorange', label='Flash', markeredgewidth=1)
	plot(volumes[2], '-o', markersize=4, linewidth=1.5, color='dodgerblue', label='Spider', markerfacecolor='none', markeredgewidth=1, markeredgecolor='dodgerblue')
	plot(volumes[1], '-|', markersize=4, linewidth=1.5, color='mediumseagreen',label='SpeedyMurmurs', markeredgewidth=1)
	plot(volumes[0], '-D', markersize=4, linewidth=1.5, color='orangered', label='Shortest Path', markerfacecolor='none', markeredgewidth=1, markeredgecolor='orangered')
if typ == 'ratio':
	plot(ratios[3], '-x', markersize=4, linewidth=1.5, color='darkorange', label='Flash', markeredgewidth=1)
	plot(ratios[2], '-o', markersize=4, linewidth=1.5, color='dodgerblue', label='Spider', markerfacecolor='none', markeredgewidth=1, markeredgecolor='dodgerblue')
	plot(ratios[1], '-|', markersize=4, linewidth=1.5, color='mediumseagreen',label='SpeedyMurmurs', markeredgewidth=1)
	plot(ratios[0], '-D', markersize=4, linewidth=1.5, color='orangered', label='Shortest Path', markerfacecolor='none', markeredgewidth=1, markeredgecolor='orangered')
# if typ == 'msg':
# 	plot(msgs[0], '-D', markersize=4, linewidth=1.5, color='orangered', label='Shortest Path', markerfacecolor='none', markeredgewidth=1, markeredgecolor='orangered')
# 	plot(msgs[1], '-|', markersize=4, linewidth=1.5, color='mediumseagreen',label='SpeedyMurmurs', markeredgewidth=1)
# 	plot(msgs[2], '-o', markersize=4, linewidth=1.5, color='dodgerblue', label='Spider', markerfacecolor='none', markeredgewidth=1, markeredgecolor='dodgerblue')
	# plot(lp[typ], '-x', markersize=4, linewidth=1.5, color='darkorange', label='Flash', markeredgewidth=1)


#majorLocator = MultipleLocator(1)
#minorLocator = MultipleLocator(.5)
#fg.xaxis.set_major_locator(majorLocator)
#fg.xaxis.set_minor_locator(minorLocator)
fg.set_xticklabels(num_flows_list)
# majorLocator = MultipleLocator(2)
# minorLocator = MultipleLocator(5)
# fg.yaxis.set_major_locator(majorLocator)
#fg.yaxis.set_minor_locator(minorLocator)
grid(True)

if typ == 'volume':
	ax = plt.gca() 
	ax.yaxis.get_major_formatter().set_powerlimits((0,1)) 


# leg = legend(loc = 'upper left', fontsize = '10', fancybox=False, frameon=True)
if trace == 'ripple' and typ == 'ratio':
	leg = legend(loc = 'lower right', fontsize = '9', fancybox=False, frameon=True)
	# leg.get_frame().set_facecolor('ghostwhite')
	leg.get_frame().set_facecolor('none')
	leg.get_frame().set_edgecolor('none')

if typ == 'volume':
	if trace == 'ripple': 
		ylabel('Succ. Volume (USD)')
	else: 
		ylabel('Succ. Volume (Satoshi)')
if typ == 'ratio':
	ylabel('Succ. Ratio (%)')
# if typ == 'msg':
# 	ylabel('Probing Messages')

xlabel('Number of transactions')

savename = trace+'-'+'general-trans-%s.pdf' % typ
savefig(savename, format='pdf')


