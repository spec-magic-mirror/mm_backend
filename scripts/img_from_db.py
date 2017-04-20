import json
import base64
import sys
from pymongo import MongoClient

try:
	client = MongoClient('localhost', 27017)
	db = client['MagicMirror']
except Exception as e:
	print("Problem with MongoDB: " + e.message)

num = sys.argv[2]
dest = sys.argv[1]
if dest[-1] != '/':
	dest += "/"

userId = db.Users.find_one({"firstName":"Mani"}, {"_id":1})["_id"]
image_sets = db.Images.find({"userId":userId}).sort("date").limit(int(num))
counter = 0
for images in image_sets:
	date = images["date"]
	image_data = images["images"]
	for key, val in image_data.iteritems():
		with open(dest + str(counter) + "_" + key + "_original.jpg", 'w') as img:
			img.write(base64.b64decode(val["original"]))
		with open(dest + str(counter) + "_" + key + "_moles.jpg", 'w') as img:
			img.write(base64.b64decode(val["moles"]))
		counter += 1
