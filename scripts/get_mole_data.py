import json
import base64
import sys
import requests
from subprocess import call
from pprint import pprint
from bson import json_util

address = "http://localhost:5000"

if len(sys.argv) > 1:
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

pprint(result_moles)
