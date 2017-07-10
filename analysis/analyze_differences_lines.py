import json
import os
import numpy
import matplotlib.pyplot as plt
import time

starter_dir = ''
test_type = 'multipush'

def union(a, b):
	return list(set(a) | set(b))

'''differences[sf] = {
	'in_old': diff1,
	'in_new': diff2,
	'total_old': total_old_count[sf],
	'total_new': total_new_count[sf]
}
'''

def get_sfs_buckets(data_dict):
	buckets = {}
	# For each entry in 'data_line'
	for i in data_dict:
		entry = data_dict[i]
		split_path = i.split('/')
		top_level = split_path[0]
		# If we haven't found this one before
		if split_path[0] not in buckets:
			buckets[top_level] = {}
			buckets[top_level]['count'] = 1
			buckets[top_level]['total_line_differences'] = len(entry['in_old']) + len(entry['in_old'])
			buckets[top_level]['total_lines'] = len(entry['total_old'])
		buckets[top_level]['count'] += 1
		buckets[top_level]['total_line_differences'] += (len(entry['in_old']) + len(entry['in_old']))
		buckets[top_level]['total_lines'] += len(entry['total_old'])
	return buckets

def graph_toplevels(all_buckets):
	for i in all_buckets:
		bucket = all_buckets[i]
		toplevel_names = []
		toplevel_counts = []
		for j in bucket:
			toplevel_names.append(j)
			toplevel_counts.append(bucket[j])
		f = plt.figure()
		x = range(len(toplevel_names))
		ax = f.add_axes([0.1, 0.1, 0.8, 0.8])
		ax.bar(x, toplevel_counts, align='center')
		ax.set_xticks(x)
		ax.set_xticklabels(toplevel_names, rotation='vertical')
		plt.ylabel('Number of files with differences.')
		plt.title('Differences across top-level folders in test: ' + i)
		mng = plt.get_current_fig_manager()
		mng.window.state('zoomed')
		f.show()
		f.savefig('graph_data' + i + '_' + test_type + '.png')
	plt.show(block=True)

def graph_toplevels_line_discreps(all_buckets):
	width = 0.27
	epoch_time = str(int(time.time()))
	for i in all_buckets:
		bucket = all_buckets[i]
		toplevel_names = []
		toplevel_counts = []
		toplevel_total_differences = []
		toplevel_total_lines = []
		for j in bucket:
			toplevel_names.append(j)
			toplevel_counts.append(bucket[j]['count'])
			toplevel_total_lines.append(bucket[j]['total_lines'])
			toplevel_total_differences.append(bucket[j]['total_line_differences'])
		f = plt.figure()
		ax = f.add_axes(11)
		x = range(len(toplevel_names))
		yvals = toplevel_counts
		rects1 = ax.bar(x, yvals, width, color='r')
		zvals = toplevel_total_lines
		rects2 = ax.bar(x+width, zvals, width, color='g')
		kvals = toplevel_total_differences
		rects3 = ax.bar(x+width*2, kvals, width, color='b')
		ax.set_xticks(x+width)
		ax.set_xticklabels(toplevel_names, rotation='vertical')
		ax.legend( (rects1[0], rects2[0], rects3[0]), ('y', 'z', 'k') )

		def autolabel(rects):
		    for rect in rects:
		        h = rect.get_height()
		        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h),
		                ha='center', va='bottom')

		autolabel(rects1)
		autolabel(rects2)
		autolabel(rects3)

		plt.ylabel('Number of files with differences.')
		plt.title('Differences across top-level folders in test: ' + i)
		mng = plt.get_current_fig_manager()
		mng.window.state('zoomed')
		f.show()
		f.savefig('graph_data' + i + '_' + test_type + '_' + epoch_time'.png')
	plt.show(block=True)


def graph_aggregate(all_buckets):
	epoch_time = str(int(time.time()))
	aggregate = {}
	for i in all_buckets:
		bucket = all_buckets[i]
		for i in bucket:
			if i not in aggregate:
				aggregate[i] = bucket[i]
			else:
				aggregate[i] += bucket[i]

	toplevel_names = []
	toplevel_counts = []
	for i in aggregate:
		toplevel_names.append(i)
		toplevel_counts.append(aggregate[i])

	f = plt.figure()
	x = range(len(toplevel_names))
	ax = f.add_axes([0.1, 0.1, 0.8, 0.8])
	ax.bar(x, toplevel_counts, align='center')
	ax.set_xticks(x)
	ax.set_xticklabels(toplevel_names, rotation='vertical')
	plt.ylabel('Number of files with differences.')
	plt.title('Aggregate of the number of files different across all test suites, seperated by top-level folder.')
	mng = plt.get_current_fig_manager()
	mng.window.state('zoomed')
	f.show()
	f.savefig('aggregate_data' + epoch_time + '.png')
	plt.show(block=True)

def main():
	all_buckets = {}
	starter_dir = os.getcwd()
	print(starter_dir)

	dirs = os.listdir(starter_dir)
	for testsuite_chunk in dirs:
		curdir = os.path.join(starter_dir, testsuite_chunk)
		os.chdir(curdir)
		files = [i for i in os.listdir(curdir) if os.path.isfile(os.path.join(curdir,i)) and 'data_line' in i]
		data_file = open(os.path.join(curdir, files[0])).read()
		data_dict = json.loads(data_file)
		buckets = get_sfs_buckets(data_dict)
		all_buckets[testsuite_chunk] = buckets
	print(all_buckets)

	os.chdir(starter_dir)
	graph_toplevels(all_buckets)
	graph_aggregate(all_buckets)
	graph_toplevels_line_discreps(all_buckets):
	input("Press Enter to continue...")

if __name__ == '__main__':
	main()