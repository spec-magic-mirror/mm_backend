import json
import base64
import sys
infile = open(sys.argv[1], 'r')
outfile = open(sys.argv[2], 'w')
j = json.load(infile)
data = j['mole_file']
dec_data = base64.b64decode(data)
outfile.write(dec_data)
outfile.close()
infile.close()
