import struct
import os
import time
import sys

def log(msg):
	print(msg)
	print("Exiting in 5 seconds..")
	time.sleep(5)
	sys.exit(-1)

IPK_HEADER = {
	'magic' : 		{'size' : 4},
	'version' : 	{'size' : 4},
	'unk1' : 		{'size' : 4},
	'base_offset' : {'size' : 4},
	'num_files' : 	{'size' : 4},
	'unk2' : 		{'size' : 28}
}

def get_chunk():
	return {
	'unk1' : 		{'size' : 4},
	'size' : 		{'size' : 4},
	'z_size' : 		{'size' : 4},
	'time_stamp' : 	{'size' : 8},
	'offset' : 		{'size' : 8},
	'name_size' : 	{'size' : 4},
	'file_name' : 	{'size' : 0},
	'path_size' : 	{'size' : 4},
	'path_name' : 	{'size' : 4},
	'checksum' : 	{'size' : 4},
	'unk2' : 		{'size' : 4}
}
def unpack(file):
	#Get file header information
	for k,v in enumerate(IPK_HEADER):
		IPK_HEADER[v]['value'] = file.read(IPK_HEADER[v]['size'])

	if IPK_HEADER['magic']['value'] != b'\x50\xEC\x12\xBA':
		log("Error: This is not a valid IPK file!")

	num_files = IPK_HEADER['num_files']['value']
	file_chunks = []

	#Set the file values from the struct
	print("Log: Unpacking {} files..".format(struct.unpack('>I', num_files)[0]))
	for _ in range(struct.unpack('>I', num_files)[0]):
		chunk = get_chunk()
		for k,v in enumerate(chunk):
			if v == 'path_name':
				chunk[v]['value'] = file.read(struct.unpack('>I', chunk['path_size']['value'])[0])
			elif v == 'file_name':
				chunk[v]['value'] = file.read(struct.unpack('>I', chunk['name_size']['value'])[0])
			else:
				chunk[v]['value'] = file.read(chunk[v]['size'])

		file_chunks.append(chunk)

	#Create the directory for the extracted folders
	extracted_folder = sys.argv[1][:sys.argv[1].find('.')]
	if os.path.isdir(extracted_folder) == False:
		os.mkdir(extracted_folder)
	os.chdir(extracted_folder)

	print("Log: Extracting data to folder named '{}' in '{}'..".format(extracted_folder, os.path.dirname(sys.argv[0])))

	#Collect the raw data for the files
	base_offset = struct.unpack('>I', IPK_HEADER['base_offset']['value'])[0]
	for k,v in enumerate(file_chunks):
		offset = struct.unpack('>II', file_chunks[k]['offset']['value'])[1]
		data_size = struct.unpack('>I', file_chunks[k]['size']['value'])[0]
		path = file_chunks[k]['path_name']['value'].decode()
		file_name = file_chunks[k]['file_name']['value'].decode()

		file.seek(offset + base_offset)

		#Make the sub directories
		if os.path.isdir(path) == False:
			os.makedirs(path)

		with open(path + '\\' + file_name, 'wb') as ff:
			ff.write(file.read(data_size))

	log("Log: Program finished.")
		
#main
args = sys.argv
if len(args) <= 1:
	log("Error: Please specify a target ipk file to unpack!")

if os.path.isfile(args[1]):
	#Create a IPK class and unpack its contents
	with open(args[1], 'rb') as file:
		unpack(file)