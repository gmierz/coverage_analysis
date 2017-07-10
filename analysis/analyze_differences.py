import json
import os
import numpy
import matplotlib.pyplot as plt

starter_dir = ''
test_type = 'multipush'

def get_sfs_buckets(data_dict):
	buckets = {}
	# For each source file entry in the 'data_line' file
	for i in data_dict:
		# Get the top level name
		split_path = i.split('/')
		top_level = split_path[0]
		# Add to the count
		if top_level not in buckets:
			buckets[top_level] = 0
		buckets[top_level] += 1
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

def graph_aggregate(all_buckets):
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
	f.savefig('aggregate_data.png')
	plt.show(block=True)

def main():
	# Will hold information about each top level directory in each test suite sample
	all_buckets = {}
	# Initial directory with the test folders. In 'double' or 'multipush'.
	starter_dir = os.getcwd()
	print(starter_dir)

	# Get each test suite folder
	dirs = os.listdir(starter_dir)
	for testsuite_chunk in dirs:
		# Move in a test suite folder that has been processed by an 'artifact_diffs_*.py' file.
		curdir = os.path.join(starter_dir, testsuite_chunk)
		os.chdir(curdir)
		# Get the 'data_line' file for the line level differences.
		files = [i for i in os.listdir(curdir) if os.path.isfile(os.path.join(curdir,i)) and 'data_line' in i]
		# Open the JSON into a python dict
		data_file = open(os.path.join(curdir, files[0])).read()
		data_dict = json.loads(data_file)
		# Breakdown the infomation into top-level folder information
		buckets = get_sfs_buckets(data_dict)
		# Store it for visualization later
		all_buckets[testsuite_chunk] = buckets
	print(all_buckets)

	# Return to the top folder and visalize
	os.chdir(starter_dir)
	graph_toplevels(all_buckets)
	graph_aggregate(all_buckets)
	input("Press Enter to continue...")

if __name__ == '__main__':
	main()