import sys
import os
import hashlib

if len(sys.argv) < 2 or not os.path.isdir(sys.argv[1]):
	print "Usage:"
	print " duplicate_finder.py <path>"
	sys.exit()

hashes = {}
nodupes = True
filecount = 0

def read_in_chunks(file_object, chunk_size=1024*1024*16):
	first_iter = True
	while True:
		data = file_object.read(chunk_size)
		if not data:
			break
		if not first_iter:
			sys.stdout.write('.')
			sys.stdout.flush()
		first_iter = False
		yield data

def get_file_hash(file_object):
	hash = hashlib.sha256()
	for data in read_in_chunks(file_object):
		hash.update(data)
	return hash.hexdigest()

for (dirpath, dirnames, filenames) in os.walk(sys.argv[1]):
	for filename in filenames:
		filecount += 1
		sys.stdout.write('O')
		sys.stdout.flush()
		fullpath = ""
		try:
			fullpath = os.path.join(dirpath,filename)
			filesize = os.path.getsize(fullpath)
			if filesize == 0:
				continue
			file = open(fullpath, "r")
			hash = get_file_hash(file)
			file.close()
		except Exception as e:
			error_filename = fullpath if len(fullpath) > 0 else filename
			print
			print str(filename) + " " + type(e).__name__ + ": " + str(e)
		else:
			hashes.setdefault(str(hash) + str(filesize), list()).append(fullpath)

if filecount > 0: print
print str(filecount) + " file(s) examined"

for key in hashes.keys():
	dupes = hashes[key]
	if (len(dupes) == 1):
		continue
	nodupes = False
	print(str(len(dupes)) + " duplicates with hash: " + key)
	for filename in dupes:
		print filename
	print

if filecount > 1 and nodupes:
	print "No duplicates found"
