import hashlib
import os
import csv
from pathlib import Path
from sys import argv

# Doesn't work on the firmware but work in the testing environment

# python3 firmware.py /home/reverser/Desktop/Vlne/RV130X_FW_1.0.3.44.bin_extract/2097184-19591200.squashfs_v4_le_extract /home/reverser/Desktop/Vlne/RV130X_FW_1.0.3.45.bin_extract/2097184-19591200.squashfs_v4_le_extract


def get_files(path1, path2):
	"""
	This function receive a path to a directory and turn every files in it in a dictionary {name:hashfile}
	:path1 (string): Absolute path to the directory of the first firmware
	:path2 (string): Absolute path to the directory of the Second firmware
	:return (dictionary): dict{fileName:[checksum1, checksum2]} 
	"""
	d = {}

	for file in Path(path1).rglob('*'):
		if file.is_file():
			d[os.path.basename(file)] = [hash_files(file), None]

	for  file in Path(path2).rglob('*'):
		if file.is_file():
			file_name = os.path.basename(file)
			if file_name not in d:
				d[file_name] = [None, hash_files(file)]
			else:
				d[file_name][1] = hash_files(file)
	return d


def hash_files(file_path):
	"""
	Open a file and turn it's content into binary
	:file_path (string): the path to the file to open
	:return: the hash value of the open file
	"""
	hash = hashlib.md5()
	with file_path.open("rb") as f:
		while chunk := f.read(8192):
			hash.update(chunk)
	return hash.hexdigest()


def save_in_file(dic):
	"""
	Create a csv file and save all the modified, deleted and created files detected
	:dic (dictionary): Contain all the files that need to be save and their changes
	"""

	with open('change.csv', 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)

		writer.writerow(["Type", "File Name"])

		for key in dic.keys():
			for value in dic[key]:
				writer.writerow([key, value])


def comparaison(path1, path2):
	"""
	Compare the checksum of all the files from 2 firmwares, create a csv file to save the detected modification
	:path1 (string): the absolute path to the first firmware
	:path2 (string): the absolute path to the second firmware
	"""
	dic_check = get_files(path1, path2)
	change = {"Created":[], "Deleted": [], "Modified": []}

	for file_name in dic_check:
		old_check, new_check = dic_check[file_name]
		if dic_check[file_name] == "[[":
			print(old_check, new_check)

		if old_check == None:
			change["Created"].append(file_name)
		elif new_check == None:
			change["Deleted"].append(file_name)
		elif old_check != new_check:
			change["Modified"].append(file_name)
		else:
			pass

		if "[[" in file_name:
			print(dic_check[file_name]) 

	save_in_file(change)


def main():
	path1 = Path(argv[1])
	path2 = Path(argv[2])

	comparaison(path1, path2)


if __name__ == "__main__":
	main()
