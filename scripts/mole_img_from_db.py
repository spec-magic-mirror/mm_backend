import json
import base64
import sys
from pymongo import MongoClient

try:
	client = MongoClient('localhost', 27017)
	db = client['MagicMirror']
except Exception as e:
	print("Problem with MongoDB: " + e.message)

dest = sys.argv[1]
if dest[-1] != '/':
	dest += "/"

userId = db.Users.find_one({"firstName":"Mani"}, {"_id":1})["_id"]
crop_ids = db.Images.find()[0]["images"]["Front"]["mole_crops"]

for crop_id in crop_ids:
	id = crop_id
        img = crop_ids[id]
	with open(dest + id + ".jpg", 'w') as img_file:
	    img_file.write(base64.b64decode(img))

