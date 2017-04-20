from pymongo import MongoClient
import sys
import json

clear = False
for arg in sys.argv:
    if arg == "--keep" or arg == "-k":
        clear = True

try:
    client = MongoClient('localhost', 27017)
    db = client['MagicMirror']
except Exception as e:
    print("Problem with MongoDB: " + e.message)

with open("test_data.json", 'r') as test_file:
    test_json = json.load(test_file)
    if db.Users.find({"firstName":"Mani", "lastName":"Moles"}).count() == 0:
	db.Users.insert(test_json)
    else:
    	db.Users.update({"firstName":"Mani", "lastName":"Moles"}, test_json)
