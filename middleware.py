from flask import Flask, request, make_response
import sys, base64
from mole_detector import MoleDetector
import json
from pymongo import MongoClient
import os
import datetime
from pprint import pprint

middleware = Flask(__name__)
try:
    client = MongoClient('localhost', 27017)
    db = client['MagicMirror']
except Exception as e:
    print("Problem with MongoDB: " + e.message)

@middleware.route("/", methods=["GET", "POST"])
def root():
    return 0

@middleware.route("/detect_moles", methods=["POST"])
def upload_image():
    print "Got a request to detect moles"
    #TODO: add support for multiple users
    user_id = db.Users.find_one({"firstName": "Mani"})['_id']
    timestamp = datetime.datetime.now()
    version = MoleDetector.version

    images = {"userId": user_id, "date": timestamp, "version": version, "images": {}}

    all_images = request.files
    for type, image_storage in all_images.iteritems():
        filename = image_storage.filename
        #filename = type
        image = image_storage.read()
        print filename
        with open(filename, 'w') as image_file:
            image_file.write(base64.b64decode(image))

        md = MoleDetector(filename)
        os.remove(filename)
        moles_file = md.map_moles()
        mole_b64 = base64.b64encode(moles_file)

        new_image = {"original": image, "moles": mole_b64}
        images['images'][type] = new_image

    # Add images to database
    db.Images.insert(images)
    result = images['images']
    for key in result.keys():
        result[key] = result[key]['moles']

    response = json.dumps(result)
    return response

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) < 2:
        port = sys.argv[1]
    middleware.run(host="0.0.0.0", port=port, debug=True)
