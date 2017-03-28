import json
import base64
import sys
import requests
from subprocess import call

in_fname = sys.argv[1]
out_fname = sys.argv[2]

with open(in_fname, 'rb') as in_file:
    response = requests.post("http://localhost:5000/detect_moles",
                             files={"image": base64.b64encode(in_file)})

json_data = json.loads(response.content)
mole_file = json_data['mole_file']

with open(out_fname, 'w') as out_file:
    dec_data = base64.b64decode(mole_file)
    out_file.write(dec_data)

call(['open', out_fname])
