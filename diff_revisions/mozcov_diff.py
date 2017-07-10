import subprocess
import os
import time

def get_source_diff(child_revision, parent_revision):
	# Get the diff and split it into lines.
	# POSSIBLY FRAGILE
	diff, err = subprocess.Popen(['hg', 'diff', '-r', parent_revision, \
									'-r', child_revision, '-U', str(1000000)], stdout=subprocess.PIPE).communicate()
	diff = diff.splitlines()

	# Split the diff into source files.
	sources = {}
	i = 0
	while i < len(diff):
		# Get a source file name.
		line = diff[i]
		if line.startswith('--- '):
			sf = line.replace('--- a', '')
		elif line.startswith('+++ '):
			sf = line.replace('+++ b', '')
		else:
			i += 1
			continue

		# Get it's diff.
		j = i
		while (not diff[j].startswith('diff ')) and j < len(diff)-1:
			j += 1
		# Save the sources diff.
		sources[sf] = diff[i:j+1]
		# Clean the annotated file.
		cleaned = []
		for line in sources[sf]:
			if line.startswith('--- ') or line.startswith('+++ ') \
				or line.startswith('@@') or line.startswith('diff '):
				continue
			cleaned.append(line)
		sources[sf] = cleaned
		# Continue looking from the line that starts with 'diff '.
		i = j
	return sources

def get_coverage_diff(annotated_file, old_coverage=[], new_coverage=[], sorted_coverage=False,
			test_length=False, old_length=0, new_length=0, gen_coverage_html=False, sf_counter=1
			sf_name='tmp'):
	# Returns 2 lists, one containing the differences in coverage 
	# for the old version, and the other containing the differences
	# in the new version. There are 5 possible flags that can be given:
	#	1. 'ucov': Uncovered line in either file.
	#	2. 'new': New line was found here, it will appear in the old differences.
	#	3. 'rem': Removed line was found here, it will appear in the new differences.
	#	4. 'ocov': Covered in the old, appears in the old differences.
	#	5. 'ncov': Covered in the new, appears in the new differences.
	# The differences are returned as a tuple.
	#
	# INPUT:
	#		annotated_file: A file that is annotated with new and old lines.
	#					(Use |hg qdiff -U <LARGE_NUMBER>| to get a file like this).
	#		old_coverage: A list of lines covered in the old file.
	#		new_coverage: A list of lines covered in the new file.
	# OPTIONAL:
	#		sorted_coverage: If sorted code coverage is given, it changes the algorithm used
	#					and speeds up the program.
	#		test_length: If true, test the indices at the end of the run.
	#		old_length: If 'test_length' is true, check 'ofileindex' against it.
	#		new_length: If 'test_length' is true, check 'nfileindex' against it.
	print('Processing annotated file...')
	file_size = len(annotated_file)
	old_coverage_diff = ['']*file_size
	new_coverage_diff = ['']*file_size
	ofileindex = 1
	nfileindex = 1

	# Go through each line, checking if they are added or removed
	# and while keeping track of two counters 'ofileindex' and
	# 'nfileindex' to determine which line we need to look for next
	# in the coverages.
	for i in range(0, file_size):
		line = annotated_file[i]
		if line.startswith('diff ') or line.startswith('+++') or line.startswith('---') \
			or line.startswith('@@ '):
			# Skip these lines.
			continue
		elif line.startswith('+'):
			# Process new line
			# It could not have been covered by the old coverage,
			# so only check the new coverage.

			old_coverage_diff[i] = 'new'
			if nfileindex in new_coverage:
				new_coverage_diff[i] = 'ncov'
			else:
				new_coverage_diff[i] = 'ucov'

			# Go to the next new line
			nfileindex += 1

		elif line.startswith('-'):
			# Process removed line
			# It could not have been covered by the new file,
			# so only check the old coverage for it.

			new_coverage_diff[i] = 'rem'
			if ofileindex in old_coverage:
				old_coverage_diff[i] = 'ocov'
			else:
				old_coverage_diff[i] = 'ucov'

			# Go to the next old line
			ofileindex += 1

		else:
			# Process a normal line, at this point both ofileindex, and
			# nfileindex must be pointing at the same line.

			if ofileindex in old_coverage:
				old_coverage_diff[i] = 'ocov'
			else:
				old_coverage_diff[i] = 'ucov'
			if nfileindex in new_coverage:
				new_coverage_diff[i] = 'ncov'
			else:
				new_coverage_diff[i] = 'ucov'

			# Move both markers
			ofileindex += 1
			nfileindex += 1

	# As a form of sanity check, the lengths of the old and new files can be given
	# and tested against the indices that we end at. If they are not equal, then
	# something didn't work properly.
	if test_length:
		if ofileindex != old_length:
			print('ofileindex is not at the end of the file:')
			print('Index: '+ str(ofileindex) + ' ' + 'Length:' + str(old_length))
		if nfileindex != new_length:
			print('nfileindex is not at the end of the file')
			print('Index: '+ str(nfileindex) + ' ' + 'Length:' + str(new_length))
	# Generate an html if asked.
	if gen_coverage_html:
		generate_html(annotated_file, old_coverage_diff, new_coverage_diff, sf_counter)
	return (old_coverage_diff, new_coverage_diff)

def html_table(table, file):
	# Write out the coverage table into the file, styling
	# each cell specifically based on what will be there.
	file.write('<table id="table_id">')
	for sublist in table:
		file.write('  <tr><td>' + sublist[0] + '</td>')
		file.write('  <td class="colour_me">' + sublist[1] + '</td>')
		file.write('  <td style="max-width:500px">' + sublist[2] + '</td>')
		file.write('  <td class="colour_me">' + sublist[3] + '</td>')
		file.write('  </tr>')
	file.write('</table>')

sf_counter = 1
def generate_html(annotated_file, old_coverage_diff, new_coverage_diff, sf_counter, sf_name):
	# Write out an html file that shows the diff alongside the coverage in each revision
	epoch_time = str(int(time.time()))
	with open('coverage_diff_' + str(sf_counter) + '-' + epoch_time + '.html', 'w+') as html_file:
		# Set up some things for a nice interface
		html_file.write('<!DOCTYPE html>')
		html_file.write('<html>')

		html_file.write('<head>')
		html_file.write('<meta charset="UTF-8"> ')
		html_file.write('<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.js"></script>')
		html_file.write('<script type="text/javascript">')

		html_file.write('$(document).ready(function(){')
		html_file.write("""$("#table_id td.colour_me:contains('new')").css('background-color','#99ff99');""")
		html_file.write("""$("#table_id td.colour_me:contains('ucov')").css('background-color','#ff704d');""")
		html_file.write("""$("#table_id td.colour_me:contains('rem')").css('background-color','#af4134');""")
		html_file.write("""$("#table_id td.colour_me:contains('ocov')").css('background-color','#3aaf34');""")
		html_file.write("""$("#table_id td.colour_me:contains('ncov')").css('background-color','#3aaf34');""")
		html_file.write("""    $('#table_id td.colour_me').each(function(){""")
		html_file.write("""        if ($(this).text() == 'rem') {""")
		html_file.write("""            $(this).css('background-color','#ff0000');""")
		html_file.write("""        }""")
		html_file.write("""        if ($(this).text() == 'ocov') {""")
		html_file.write("""            $(this).css('background-color','#33cc33');""")
		html_file.write("""        }""")
		html_file.write("""        if ($(this).text() == 'ncov') {""")
		html_file.write("""            $(this).css('background-color','#33cc33');""")
		html_file.write("""        }""")
		html_file.write('    });')
		html_file.write('});')
		html_file.write('</script>')
		html_file.write('</head>')

		html_file.write('<body>')

		# Write out diff table here
		col_data = []
		col_data.append(['Line No.', 'Old revision', 'Source Code: ' + sf_name, 'New Revision'])
		for i in range(0, len(annotated_file)):
			col_data.append([str(i+1), old_coverage_diff[i], annotated_file[i], new_coverage_diff[i]])
		html_table(col_data, html_file)

		html_file.write('</body>')

		html_file.write('</html>')

def main():
	# Initialize some testing data here.
	old_coverage = [30,31,32, 34, 35, 36, 38, 50, 70]
	new_coverage = [30,31,32, 34, 35, 36, 38, 50, 70]
	# Get the source files changed.
	sources = get_source_diff('367217', '367214')
	count = 1
	# Get their coverage differences and generate an html of their result.
	for sf in sources:
		print(sf)
		(old_coverage_diff, new_coverage_diff) = get_coverage_diff(sources[sf], \
													old_coverage=old_coverage, new_coverage=new_coverage, \
													gen_coverage_html=True, sf_counter=count, sf_name=sf)
		count += 1

if __name__ == '__main__':
	main()