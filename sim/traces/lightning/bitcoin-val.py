import matplotlib.pyplot as plt
from pylab import *
from scipy import stats

BitcoinVal = []
with open('BitcoinVal.txt', 'r') as f: 
	f.readline()
	for line in f: 
		BitcoinVal.append(float(line))

sorted_var = np.sort(BitcoinVal)
# sorted_var = sorted_var[0:int(0.9999*len(sorted_var))]

x_points = []
x_points.append(stats.scoreatpercentile(sorted_var, 0.01))
x_points.append(stats.scoreatpercentile(sorted_var, 0.5))
x_points.append(stats.scoreatpercentile(sorted_var, 1))
x_points.append(stats.scoreatpercentile(sorted_var, 2))
x_points.append(stats.scoreatpercentile(sorted_var, 4))
x_points.append(stats.scoreatpercentile(sorted_var, 6))
x_points.append(stats.scoreatpercentile(sorted_var, 8))
for i in np.arange(10,100,10):
    x_points.append(stats.scoreatpercentile(sorted_var, i))
x_points.append(stats.scoreatpercentile(sorted_var, 96))
x_points.append(stats.scoreatpercentile(sorted_var, 97))
x_points.append(stats.scoreatpercentile(sorted_var, 98))
x_points.append(stats.scoreatpercentile(sorted_var, 99))
x_points.append(stats.scoreatpercentile(sorted_var, 99.9))
x_points.append(stats.scoreatpercentile(sorted_var, 99.99))
x_points.append(stats.scoreatpercentile(sorted_var, 99.999))

print 'median capacity', stats.scoreatpercentile(sorted_var, 50), len(sorted_var)


# x_points = [1.0, 20811.0, 100000.0, 250000.0, 1000000.0, 1293026.0, 2839236.799999997, 7000000.0, 20000000.0, 89160000.0, 349625508.6799965, 504540323.75999594, 950000000.0, 2000000000.0, 18146198843.6765]
# y_points = [0, 0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.96, 0.97, 0.98, 0.99, 0.999, 1]
y_points = [0.0001, 0.005, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.96, 0.97, 0.98, 0.99, 0.999, 0.9999, 0.99999]


point = int(len(sorted_var)*0.9)
print sorted_var[point]
print sum(sorted_var[point:len(sorted_var)])/sum(sorted_var)

font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 14}
matplotlib.rc('font', **font)

#set appropriate figure width/height
figure(figsize=(4, 3))
fg = subplot(1,1,1)
# Set appropriate margins, these values are normalized into the range [0, 1]
subplots_adjust(left = 0.16, bottom = 0.28, right = 0.95, top = 0.95, wspace = 0.1, hspace = 0.1)
# fg.set_yticklabels(['0','0', '0.2', '0.4', '0.6', '0.8', '1'])
fg.tick_params(axis='both', which='major', labelsize=14)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
xticks(rotation=60)
majorLocator = MultipleLocator(0.2)
minorLocator = MultipleLocator(0.1)
fg.yaxis.set_major_locator(majorLocator)
fg.yaxis.set_minor_locator(minorLocator)

fg.set_frame_on(True)
fg.spines["top"].set_visible(False)
# fg.spines["right"].set_visible(False)
fg.spines['bottom'].set_color('darkgrey')
fg.spines['left'].set_color('darkgrey')
fg.spines['right'].set_color('white')

grid(color='grey', linestyle=':', linewidth=0.5)

fg.get_xaxis().tick_bottom () 
fg.get_yaxis().tick_left ()
fg.tick_params(axis='x', colors='grey')
fg.tick_params(axis='y', colors='grey')

plt.semilogx(x_points, y_points, '-o', markersize=6, linewidth=1.5, markeredgewidth=0.0,  color='dodgerblue', label='Bitcoin')
xlabel('Satoshi', fontsize=14)
ylabel('CDF', fontsize=14)
savefig('Bitcoin-CDF.pdf', format='pdf')