from flask import Flask, request, make_response
import sys, base64
from mole_detector import MoleDetector
import json
from pymongo import MongoClient
from pprint import pprint

middleware = Flask(__name__)
try:
    client = MongoClient('localhost', 27017)
    db = client['MagicMirror']
except Exception as e:
    print("Couldn't connect to MongoDB: " + e.message)

@middleware.route("/", methods=["GET", "POST"])
def root():
    return 0

@middleware.route("/detect_moles", methods=["POST"])
def upload_image():
    print "Got a request to detect moles"
    file = request.files['image']
    # TODO: store data into db for future reference
    filename = file.filename
    file.save(filename)

    md = MoleDetector(base64.b64decode(filename))
    moles_file = md.map_moles()

    mole_b64 = base64.b64encode(moles_file)
    result = {"mole_file":mole_b64}
    response = json.dumps(result)
    return response

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) < 2:
        port = sys.argv[1]
    middleware.run(host="0.0.0.0", port=port, debug=True)
