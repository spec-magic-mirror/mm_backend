import json
import base64
import sys
import requests
from subprocess import call

in_fname = sys.argv[1]
out_fname = sys.argv[2]
address = "http://localhost:5000"

if len(sys.argv) > 3:
    #address = sys.argv[3]
    address = "http://10.128.15.48:5000"

type = "front"

with open(in_fname, 'rb') as in_file:
    response = requests.post(address + "/detect_moles",
                             files={type: base64.b64encode(in_file.read())})

json_data = json.loads(response.content)
mole_file = json_data[type]

with open(out_fname, 'w') as out_file:
    dec_data = base64.b64decode(mole_file)
    out_file.write(dec_data)

#call(['open', out_fname])
