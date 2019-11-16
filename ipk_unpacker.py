#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import struct
from pathlib import Path
from time import sleep


ENDIANNESS = '>' # Big endian
STRUCT_SIGNS = {
	1 : 'c',
	2 : 'H',
	4 : 'I',
	8 : 'Q'
}
# Define a basic IPK file header
IPK_HEADER = {
	'magic' : 		{'size' : 4},
	'version' : 	{'size' : 4},
	'unk1' : 		{'size' : 4},
	'base_offset' : {'size' : 4},
	'num_files' : 	{'size' : 4},
	'unk2' : 		{'size' : 28}
}

def _exit(msg):
	print(msg)
	print("Exiting in 5 seconds..")
	sleep(5)
	sys.exit(-1)

# Chunks in the IPK files
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

def unpack(_bytes):
	return struct.unpack(ENDIANNESS + STRUCT_SIGNS[len(_bytes)], _bytes)[0]


# This function will handle the data extraction from the files
def extract(target_file):
	with open(target_file, 'rb') as file:
		# Get file header information
		for k, v in enumerate(IPK_HEADER):
			IPK_HEADER[v]['value'] = file.read(IPK_HEADER[v]['size'])

		# Check if this is a proper IPK file
		assert IPK_HEADER['magic']['value'] == b'\x50\xEC\x12\xBA'

		num_files = unpack(IPK_HEADER['num_files']['value'])
		print(f"Log: Found {num_files} files..")

		# Go through the file and collect the data
		file_chunks = []
		for _ in range(num_files):
			chunk = get_chunk()
			for k,v in enumerate(chunk):
				_size = chunk[v]['size']

				if v == 'path_name': _size = unpack(chunk['path_size']['value'])
				if v == 'file_name': _size = unpack(chunk['name_size']['value'])

				chunk[v]['value'] = file.read(_size)

			file_chunks.append(chunk)

		# Create the directory for the extracted folders
		ext_dir = Path(target_file.stem)
		ext_dir.mkdir(exist_ok=True)
		os.chdir(ext_dir)

		print(f"Log: Extracting data to {ext_dir.name} in {Path.cwd()}..")
		base_offset = unpack(IPK_HEADER['base_offset']['value'])

		for k, v in enumerate(file_chunks):

			# File raw data
			offset = unpack(file_chunks[k]['offset']['value'])
			data_size = unpack(file_chunks[k]['size']['value'])

			# File names and creation
			file_path = Path.cwd() / file_chunks[k]['path_name']['value'].decode() #utf8
			file_name = file_chunks[k]['file_name']['value'].decode()

			file.seek(offset + base_offset)

			# Make the sub directories
			file_path.mkdir(parents=True, exist_ok=True)

			with open(file_path / file_name, 'wb') as ff:
				ff.write(file.read(data_size))


	_exit("Log: Program finished.")
		

# Check if the proper arguements were given
args = sys.argv
if len(args) <= 1:
	_exit("Error: Please specify a target .IPK file to unpack! ie, ipk_unpack.py ipk_file")

# Check if the file exists
target_file = Path(args[1])
if not target_file.exists():
	_exit(f"Error: The file '{target_file.name}' was not found!")

# Unpack the file otherwise
extract(target_file)