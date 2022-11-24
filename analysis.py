
from pylab import *
import numpy as np
import matplotlib.font_manager
from matplotlib.ticker import ScalarFormatter
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
from sklearn import preprocessing
import csv
import sys
import os
 
elapsed = {}
timestamps = {}
starttimes = {}
errors = {}

files = []
filepath = os.path.dirname(os.path.abspath(__file__))+'\\'+sys.argv[1]
# list filestypes for all files in directory passed as argument
for file in os.listdir(filepath):
    if file.endswith(".jtl"):
        files.append(filepath+'\\'+file)

# Parse the CSV files
for file in files:
  threads = int(file.replace(filepath+'\\','').split('-')[0])
  for row in csv.DictReader(open(file)):
    if (not row['label'] in elapsed):
      elapsed[row['label']] = {}
      timestamps[row['label']] = {}
      starttimes[row['label']] = {}
      errors[row['label']] = {}
    if (not threads in elapsed[row['label']]):
      elapsed[row['label']][threads] = []
      timestamps[row['label']][threads] = []
      starttimes[row['label']][threads] = []
      errors[row['label']][threads] = []
    elapsed[row['label']][threads].append(int(row['elapsed']))
    timestamps[row['label']][threads].append(int(row['timeStamp']))
    starttimes[row['label']][threads].append(int(row['timeStamp']) - int(row['elapsed']))
    if (row['success'] != 'true'):
      errors[row['label']][threads].append(int(row['elapsed']))

# Normalize the elapsed data dictionary
for label in elapsed:
  for threads in elapsed[label]:
    # Fix the problem where arrays can have 0 samples
    if (len(elapsed[label][threads]) == 0):
      elapsed[label][threads] = [0]
    elapsed[label][threads] = np.array(elapsed[label][threads])
    elapsed[label][threads] = preprocessing.minmax_scale(elapsed[label][threads],feature_range=(0, 1), axis=0, copy=True)
    # # elapsed[label][threads] = preprocessing.normalize([elapsed[label][threads]], norm='l2')[0]
    # # elapsed[label][threads] = preprocessing.scale(elapsed[label][threads], axis=0, with_mean=True, with_std=True, copy=True)

# Normalize the timestamps data dictionary
for label in timestamps:
  for threads in timestamps[label]:
    # Fix the problem where arrays can have 0 samples
    if (len(timestamps[label][threads]) == 0):
      timestamps[label][threads] = [0]
    timestamps[label][threads] = np.array(timestamps[label][threads])
    timestamps[label][threads] = preprocessing.minmax_scale(timestamps[label][threads],feature_range=(0, 1), axis=0, copy=True)
    # timestamps[label][threads] = preprocessing.normalize([timestamps[label][threads]], norm='l2')[0]
    # timestamps[label][threads] = preprocessing.scale(timestamps[label][threads], axis=0, with_mean=True, with_std=True, copy=True)


# Normalize the starttimes data dictionary
for label in starttimes:
  for threads in starttimes[label]:
    # Fix the problem where arrays can have 0 samples
    if (len(starttimes[label][threads]) == 0):
      starttimes[label][threads] = [0]
    starttimes[label][threads] = np.array(starttimes[label][threads])
    starttimes[label][threads] = preprocessing.minmax_scale(starttimes[label][threads],feature_range=(0, 1), axis=0, copy=True)
    # starttimes[label][threads] = preprocessing.normalize([starttimes[label][threads]], norm='l2')[0]
    # starttimes[label][threads] = preprocessing.scale(starttimes[label][threads], axis=0, with_mean=True, with_std=True, copy=True)


# Normalize the errors data dictionary
for label in errors:
  for threads in errors[label]:
    # Fix the problem where arrays can have 0 samples
    if (len(errors[label][threads]) == 0):
      errors[label][threads] = [0]
    errors[label][threads] = np.array(errors[label][threads])
    errors[label][threads] = preprocessing.minmax_scale(errors[label][threads],feature_range=(0, 1), axis=0, copy=True)
    # errors[label][threads] = preprocessing.normalize([errors[label][threads]], norm='l2')[0]
    # errors[label][threads] = preprocessing.scale(errors[label][threads], axis=0, with_mean=True, with_std=True, copy=True)
    


# Draw a separate figure for each label found in the results.
for label in elapsed:
  # Transform the lists for plotting
  plot_data = []
  throughput_data = []
  error_x = []
  error_y = []
  plot_labels = ["K8S","K3S","K8S + KubeEdge", 'K3S + KubeEdge']
  column = 1
  for thread_count in sort(list(elapsed[label].keys())):
    plot_data.append(elapsed[label][thread_count])
    # plot_labels.append(thread_count)
    test_start = starttimes[label][thread_count].min()
    test_end = timestamps[label][thread_count].max()
    test_length = (test_end - test_start) / 1000
    num_requests = len(timestamps[label][thread_count]) - len(errors[label][thread_count])
    if (test_length > 0):
      throughput_data.append(num_requests / float(test_length))
    else:
      throughput_data.append(0)
    for error in errors[label][thread_count]:
      error_x.append(column)
      error_y.append(error)
    column += 1
 

throughput_data = np.array(throughput_data)
throughput_data = preprocessing.minmax_scale(throughput_data,feature_range=(0, 1), axis=0, copy=True)
# throughput_data = preprocessing.normalize([throughput_data], norm='l2')[0]

throughput_data = np.insert(throughput_data, 0, None)  

# Start a new figure
fig = figure(figsize=(9, 6))

# Pick some colors
palegreen = matplotlib.colors.colorConverter.to_rgb('#8CFF6F')
paleblue = matplotlib.colors.colorConverter.to_rgb('#708DFF')

# Plot response time
ax1 = fig.add_subplot(111)
ax1.set_yscale('log')
bp = boxplot(plot_data, notch=0, sym='+', vert=1, whis=1.5)

# Tweak colors on the boxplot
plt.setp(bp['boxes'], color='g')
plt.setp(bp['whiskers'], color='g')
plt.setp(bp['medians'], color='black')
plt.setp(bp['fliers'], color=palegreen, marker='+')

# Now fill the boxes with desired colors
numBoxes = len(plot_data)
medians = range(numBoxes)
for i in range(numBoxes):
  box = bp['boxes'][i]
  boxX = []
  boxY = []
  for j in range(5):
    boxX.append(box.get_xdata()[j])
    boxY.append(box.get_ydata()[j])
  boxCoords = np.array(list(zip(boxX,boxY)))
  boxPolygon = Polygon(boxCoords, facecolor=palegreen)
  ax1.add_patch(boxPolygon)

# Plot the errors
if (len(error_x) > 0):
  ax1.scatter(error_x, error_y, color='r', marker='x', zorder=3)

# # Plot throughput
ax2 = ax1.twinx()
ax2.plot(throughput_data, 'o-', color=paleblue, linewidth=2, markersize=8)

# Label the axis
ax1.set_title(label)
ax1.set_xlabel('Cluster Configuration')
ax2.set_ylabel('Requests per second')
ax1.set_ylabel('Milliseconds')
ax1.set_xticks(range(1, len(plot_labels) + 1))
ax1.set_xticklabels(plot_labels)
fig.subplots_adjust(top=0.9, bottom=0.15, right=0.85, left=0.15)



# Turn off scientific notation for Y axis
#  ax1.yaxis.set_major_formatter(ScalarFormatter(False))

# Set the lower y limit to the match the first column
#ax1.set_ylim(ymin=0.9 * min(plot_data[0]))
ax1.set_ylim(bottom=0, top=1)
# ax1.set_ylim(ymin=bp['boxes'][0].get_ydata()[0])

# Draw some tick lines
ax1.yaxis.grid(True, linestyle='-', which='major', color='grey')
ax1.yaxis.grid(True, linestyle='-', which='minor', color='lightgrey')
# Hide these grid behind plot objects
#ax1.set_axisbelow(True)

# Add a legend
line1 = Line2D([], [], marker='s', color=palegreen, markersize=10, linewidth=0)
line2 = Line2D([], [], marker='o', color=paleblue, markersize=8, linewidth=2)
line3 = Line2D([], [], marker='x', color='r', linewidth=0, markeredgewidth=2)
prop = matplotlib.font_manager.FontProperties(size='small')
figlegend((line1, line2, line3), ('Response Time', 'Throughput', 'Failures'),
  'lower center', prop=prop, ncol=3)

# Write the PNG file
savefig(label)
