import matplotlib.pyplot as plt
from pylab import *
from scipy import stats

BitcoinVal = []
count = 0 
with open('../data/BitcoinVal.txt', 'r') as f: 
	f.readline()
	for line in f: 
		count += 1
		if count > 1000000: 
			break 
		if float(line)/1e8 > 300: 
			continue
		BitcoinVal.append(float(line)/1e8)

sorted_var = np.sort(BitcoinVal)
x_points = []
for i in np.arange(0,100,10):
    x_points.append(stats.scoreatpercentile(sorted_var, i))
x_points.append(stats.scoreatpercentile(sorted_var, 96))
x_points.append(stats.scoreatpercentile(sorted_var, 97))
x_points.append(stats.scoreatpercentile(sorted_var, 98))
x_points.append(stats.scoreatpercentile(sorted_var, 99))


y_points = [ 0, 0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.96, 0.97, 0.98, 0.99]

font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 8}
matplotlib.rc('font', **font)

#set appropriate figure width/height
figure(figsize=(3.5, 3))
fg = subplot(1,1,1)
# Set appropriate margins, these values are normalized into the range [0, 1]
subplots_adjust(left = 0.17, bottom = 0.17, right = 0.95, top = 0.95, wspace = 0.1, hspace = 0.1)
# fg.set_yticklabels(['0','0', '0.2', '0.4', '0.6', '0.8', '1'])
fg.tick_params(axis='both', which='major', labelsize=10)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
xticks(rotation=60)
majorLocator = MultipleLocator(0.2)
minorLocator = MultipleLocator(0.1)
fg.yaxis.set_major_locator(majorLocator)
fg.yaxis.set_minor_locator(minorLocator)
grid(True)
plot(x_points, y_points, '-x', markersize=6, linewidth=1.5, color='blue', label='Bitcoin')
xlabel('BTC', fontsize=10)
ylabel('CDF', fontsize=10)
savefig('CDF.pdf', format='pdf')