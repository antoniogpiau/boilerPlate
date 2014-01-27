import os, time, threading

PATH_TO_WATCH = 'design/images/'
QUIT_MESSAGE = 'You can type quit, if you want:'

SCRIPT_FILES_PREFIX = 'scenesImages'

IGNORED_FILES = '.DS_Store', 'navigation'

####

def get_file_names(path = PATH_TO_WATCH):
	list = []
	for file in os.listdir(path):
		if os.path.isdir(path+file) and not file in IGNORED_FILES:
			list.extend(get_file_names(path+file+'/'))

		elif os.path.isfile(path+file) and not file in IGNORED_FILES:
			list.append(path+file)

	return list

class Observer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.stop = False

	def run(self):
		before = get_file_names()

		while 1:
			if self.stop: break

			time.sleep(2)
			after = get_file_names()
			added = [file for file in after if not file in before]
			removed = [file for file in before if not file in after]

			if added or removed:
				parse(before)

			before = after

####

def parse(file_names):
	script_files_data = {}

	for file_name in file_names:
		paths = file_name.split('/')[2:] # [2:] => REMOVES 'design/images' OF THE LIST

		resolution = paths[0]
		scene_name = paths[1]
		file_name = paths[2]
		base_name = paths[2][:-4] # [:-4] => REMOVES FILE EXTENSION '.png'

		if not resolution in script_files_data:
			script_files_data[resolution] = {}

		if not scene_name in script_files_data[resolution]:
			script_files_data[resolution][scene_name] = []

		file_data = base_name.split('_')
		file_data.append(file_name)

		script_files_data[resolution][scene_name].append(file_data)
		# script_files_data[resolution][scene_name].append(paths[2])

	write_files(script_files_data)
	print 'updated!'
	print QUIT_MESSAGE

def write_files(script_files_data):
	for resolution in script_files_data:
		file = open_file_with_resolution(resolution)
		file.write(generate_file_text(script_files_data[resolution]))
		file.close()

def open_file_with_resolution(resolution):
	return open('scripts/'+SCRIPT_FILES_PREFIX+resolution+'.lua', 'w')

def generate_file_text(file_data):
	str = skip_line()
	str += 'local scenesImages = {}'
	str += skip_line(2)

	for scene_data in sorted(file_data, cmp_string_numbers_and_strings):
		str += generate_scene_text(scene_data, file_data[scene_data])

	str += 'return scenesImages'

	return str

def generate_scene_text(scene_name, scene_data):
	if not is_number(scene_name):
		scene_name = '\'' + scene_name + '\''

	str = 'scenesImages[' + scene_name + '] = {' + skip_line()

	str += indent() + 'elements = {' + skip_line()

	for image_data in scene_data:
		if len(image_data) < 5: continue
		str += indent(4) + generate_image_text(image_data) + skip_line()

	str += indent() + '},' + skip_line()
	str += '}' + skip_line(2)

	return str

def generate_image_text(image_data):
	print image_data
	return '{type = "image", filename = "' + image_data[5] + '", index = "' + image_data[4] + '", x = ' + image_data[2] + ', y = ' + image_data[3] + ' },'

def indent(number_of_spaces=2):
	str = ''
	for i in range(number_of_spaces):
		str += ' '

	return str

def skip_line(number_of_times=1):
	str = ''
	for i in range(number_of_times):
		str += '\n'

	return str

####

def cmp_string_numbers_and_strings(x, y):
	if is_number(x):
		x = int(x)
	if is_number(y):
		y = int(y)

	return cmp(x, y)

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

####

def get_user_input():
	user_input = raw_input()
	if(user_input == 'quit'):
		observer.stop = True
	else:
		get_user_input()

####

observer = Observer()
observer.start()

parse(get_file_names())
get_user_input()