from pylab import *
import sys

matplotlib.rcParams['axes.linewidth'] = 0.75

trace = sys.argv[1]

typ = sys.argv[2]

num_flows = 2000

scale_factor = ['1', '10', '20', '30', '40', '50', '60']

volumes = []
ratios = []
msgs = []

schemes = ['sp', 'speedymurmurs', 'waterfilling', 'flash']
cnt_scheme = 0
for scheme in schemes: 
	with open('rawdata/'+trace+'-'+scheme+'-'+str(num_flows)+'.txt') as f:
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

for i in range(3):
	print [a/b for a, b in zip(volumes[3], volumes[i])] 


if typ == 'volume':
	plot(volumes[3][0:7], '-x', markersize=4, linewidth=1.5, color='darkorange', label='Flash', markeredgewidth=1)
	plot(volumes[2][0:7], '-o', markersize=4, linewidth=1.5, color='dodgerblue', label='Spider', markerfacecolor='none', markeredgewidth=1, markeredgecolor='dodgerblue')
	plot(volumes[1][0:7], '-|', markersize=4, linewidth=1.5, color='mediumseagreen',label='SpeedyMurmurs', markeredgewidth=1)
	plot(volumes[0][0:7], '-D', markersize=4, linewidth=1.5, color='orangered', label='Shortest Path', markerfacecolor='none', markeredgewidth=1, markeredgecolor='orangered')
if typ == 'ratio':
	plot(ratios[3][0:7], '-x', markersize=4, linewidth=1.5, color='darkorange', label='Flash', markeredgewidth=1)
	plot(ratios[2][0:7], '-o', markersize=4, linewidth=1.5, color='dodgerblue', label='Spider', markerfacecolor='none', markeredgewidth=1, markeredgecolor='dodgerblue')
	plot(ratios[1][0:7], '-|', markersize=4, linewidth=1.5, color='mediumseagreen',label='SpeedyMurmurs', markeredgewidth=1)
	plot(ratios[0][0:7], '-D', markersize=4, linewidth=1.5, color='orangered', label='Shortest Path', markerfacecolor='none', markeredgewidth=1, markeredgecolor='orangered')
# if typ == 'msg':
# 	plot(msgs[0], '-D', markersize=4, linewidth=1.5, color='orangered', label='Shortest Path', markerfacecolor='none', markeredgewidth=1, markeredgecolor='orangered')
# 	plot(msgs[1], '-|', markersize=4, linewidth=1.5, color='mediumseagreen',label='SpeedyMurmurs', markeredgewidth=1)
# 	plot(msgs[2], '-o', markersize=4, linewidth=1.5, color='dodgerblue', label='Spider', markerfacecolor='none', markeredgewidth=1, markeredgecolor='dodgerblue')
	# plot(lp[typ], '-x', markersize=4, linewidth=1.5, color='darkorange', label='Flash', markeredgewidth=1)


#majorLocator = MultipleLocator(1)
#minorLocator = MultipleLocator(.5)
#fg.xaxis.set_major_locator(majorLocator)
#fg.xaxis.set_minor_locator(minorLocator)
fg.set_xticklabels(scale_factor)
# majorLocator = MultipleLocator(2)
# minorLocator = MultipleLocator(5)
# fg.yaxis.set_major_locator(majorLocator)
#fg.yaxis.set_minor_locator(minorLocator)
grid(True)
if typ == 'volume': 
	ax = plt.gca() 
	ax.yaxis.get_major_formatter().set_powerlimits((0,1)) 



# leg = legend(loc = 'upper left', fontsize = '10', fancybox=False, frameon=True)
if typ == 'ratio' and trace == 'ripple':
	leg = legend(loc = 'lower right', fontsize = '9', fancybox=False, frameon=True)
# if typ == 'ratio' and trace == 'lightning':
# 	leg = legend(loc = 'upper left', fontsize = '10', fancybox=False, frameon=True)
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

xlabel('Capacity Scale Factor')

savename = trace+'-'+'general-scale-%s.pdf' % typ
savefig('figs/'+savename, format='pdf')



