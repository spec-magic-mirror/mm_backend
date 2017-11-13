import json
import base64
import sys
import requests
from subprocess import call
from pprint import pprint
from bson import json_util

if len(sys.argv) < 2 or not sys.argv[1].endswith(".json"):
    print("Proper usage: python get_mole_data.py <destination .json file>")
    exit(0)

address = "http://localhost:5000"
output_fname = sys.argv[1]

if len(sys.argv) > 2:
    #address = sys.argv[3]
    address = "http://10.128.15.48:5000"

response = requests.get(address + "/get_mole_data")

json_data = json.loads(response.content, object_hook=json_util.object_hook)

result_moles = {orientation: {} for orientation in json_data}
for orientation in json_data:
    for mole_id in json_data[orientation]:
        mole_data = json_data[orientation][mole_id]
        if len(mole_data) > 1:
            result_moles[orientation][mole_id] = mole_data

with open(output_fname, 'w') as fp:
    json.dump(result_moles, fp, default=json_util.default)
#pprint(result_moles)

